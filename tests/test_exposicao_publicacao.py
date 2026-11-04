"""A exposição segue os boletins publicados, sem antecipar conhecimento."""
import random
import unittest
from itertools import product
from unittest.mock import patch
from casa.visitors import VisitorSession
from casa.medical_knowledge import LABELS
from logica_infeccao import diagnosticar


def pattern(first,second):
    # Encontra uma evidência real usando a função do grupo, sem copiar regras.
    for values in product((False,True),repeat=len(LABELS)):
        symptoms=dict(zip(LABELS,values))
        if ((diagnosticar(symptoms,{'boletim_07'})=='infectado')==first and
            (diagnosticar(symptoms,{'boletim_14'})=='infectado')==second):
            return symptoms
    raise AssertionError('Padrão de teste não encontrado na lógica do grupo')


class PublicationExposureTests(unittest.TestCase):
    def session(self,first=True,second=False):
        s=VisitorSession(random.Random(9))
        v=s.visitors['ricardo'];v.diagnosis='infectado';v.symptoms=pattern(first,second)
        s.news.watch(s.news.current(1));self.assertTrue(s.decide(v,'acolhido'))
        # Isola exposição: companhia e suprimentos reais suficientes; sem agenda futura.
        s.manager.plan={v.id:1}
        s.survival.add_supplies(100,100)
        return s

    def test_first_pattern_day_one_through_eight_without_reading(self):
        s=self.session()
        for day in range(1,7):
            self.assertEqual(s.day,day)
            self.assertTrue(s.days.advance())
            self.assertEqual(s.survival.infection_exposure,0)
            self.assertTrue(s.survival.alive)
        self.assertEqual(s.day,7)
        self.assertFalse(s.news.current(7).read)
        self.assertEqual(s.medical.observations,{})
        self.assertEqual(s.diagnosticar_visitante('ricardo'),'inconclusivo')
        self.assertTrue(s.days.close_day())
        self.assertEqual(s.survival.infection_exposure,1)
        s.days.close_day();self.assertEqual(s.survival.infection_exposure,1)
        self.assertTrue(s.days.advance());self.assertEqual(s.day,8)
        self.assertFalse(s.days.close_day())
        self.assertFalse(s.survival.alive);self.assertEqual(s.survival.defeat_day,8)

    def test_second_pattern_exclusively_day_one_through_fifteen(self):
        s=self.session(False,True)
        for day in range(1,14):
            self.assertEqual(s.day,day);self.assertTrue(s.days.advance())
            self.assertEqual(s.survival.infection_exposure,0)
        self.assertFalse(s.news.current(14).read)
        self.assertTrue(s.days.advance())
        self.assertEqual(s.survival.infection_exposure,1)
        self.assertEqual(s.day,15)
        self.assertFalse(s.days.advance())
        self.assertEqual(s.survival.defeat_day,15)

    def test_both_patterns_use_day_seven_and_no_retroactive_count(self):
        s=self.session(True,True)
        for _ in range(6):self.assertTrue(s.days.advance())
        self.assertEqual(s.survival.infection_exposure,0)
        s.days.close_day();self.assertEqual(s.survival.infection_exposure,1)
        s.days.advance();s.days.close_day()
        self.assertEqual(s.survival.defeat_day,8)

    def test_elimination_of_only_relevant_infected_interrupts_exposure(self):
        s=self.session();other=s.visitors['laura']
        other.diagnosis='infectado';other.symptoms=pattern(False,True)
        other.arrived=True;self.assertTrue(s.decide(other,'acolhido'))
        for _ in range(7):self.assertTrue(s.days.advance())
        self.assertEqual(s.day,8);self.assertEqual(s.survival.infection_exposure,1)
        self.assertTrue(s.eliminate('ricardo'))
        self.assertTrue(s.days.close_day())
        self.assertEqual(s.survival.infection_exposure,0)
        for _ in range(6):self.assertTrue(s.days.advance())
        self.assertEqual(s.day,14)
        self.assertTrue(s.days.advance());self.assertEqual(s.survival.infection_exposure,1)
        self.assertFalse(s.days.advance());self.assertEqual(s.survival.defeat_day,15)

    def test_multiple_relevant_residents_count_once_and_interfaces_do_not_reset(self):
        s=self.session();other=s.visitors['laura']
        other.diagnosis='infectado';other.symptoms=pattern(True,False)
        other.arrived=True;s.decide(other,'acolhido')
        for _ in range(7):self.assertTrue(s.days.advance())
        self.assertEqual(s.survival.infection_exposure,1)
        from casa.game import House
        game=House();game.visitor_session=s
        game.days=s.days;game.inventory.session=s
        for room in game.scenes:game.change_room(room)
        game.inventory.active=True;game.update((0,0),1)
        s.diagnosticar_visitante('ricardo');s.diagnosticar_visitante('laura')
        self.assertEqual(s.survival.infection_exposure,1)
        s.days.close_day();self.assertEqual(s.survival.infection_exposure,2)

    def test_healthy_never_exposes_even_with_infected_looking_test_data(self):
        s=self.session()
        # A condição real é uma guarda independente da avaliação dos sintomas.
        s.visitors['ricardo'].diagnosis='saudavel'
        for _ in range(20):s.days.advance()
        self.assertEqual(s.survival.infection_exposure,0)
        self.assertTrue(s.survival.won)

    def test_diagnosis_requires_watched_news_and_observed_symptoms(self):
        s=self.session()
        for _ in range(6):s.days.advance()
        self.assertEqual(s.diagnosticar_visitante('ricardo'),'inconclusivo')
        s.news.watch(s.news.current(7))
        self.assertEqual(s.diagnosticar_visitante('ricardo'),'inconclusivo')
        v=s.visitors['ricardo']
        for feature in s.medical.known:s.medical.observe(v,feature)
        self.assertEqual(s.diagnosticar_visitante(v.id),'infectado')
        self.assertEqual(s.survival.infection_exposure,0)
        s.days.close_day();self.assertEqual(s.survival.infection_exposure,1)

    def test_world_validation_uses_real_data_and_only_published_news(self):
        s=self.session(False,True)
        s.days.day=7
        with patch('casa.visitors.infection_logic.diagnosticar',wraps=diagnosticar) as diagnose:
            s.days.close_day()
            symptoms,news=diagnose.call_args.args
            self.assertEqual(symptoms,s.visitors['ricardo'].symptoms)
            self.assertIn('boletim_07',news)
            self.assertNotIn('boletim_14',news)
            self.assertNotIn('boletim_17',news)
        self.assertEqual(s.survival.infection_exposure,0)
