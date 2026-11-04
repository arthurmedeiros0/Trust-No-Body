"""Integração do padrão 17, sem replicar as expressões do grupo."""
import random
import unittest
from casa.config import ROOT
from casa.visitors import VisitorSession,PATTERN_CONDITIONS,PROTOCOL_NEWS
from casa.menu import GameMenu
from casa.medical_knowledge import LABELS
from logica_infeccao import diagnosticar


class ThirdPatternTests(unittest.TestCase):
    def test_generation_all_patterns_and_healthy_for_all_seven(self):
        before=(ROOT/'logica_infeccao.py').read_bytes()
        found=set()
        for seed in range(50):
            s=VisitorSession(random.Random(seed))
            for v in s.visitors.values():
                self.assertEqual(set(v.definition['investigation']),set(LABELS))
                actual=frozenset(news for news in PROTOCOL_NEWS if diagnosticar(v.symptoms,{news})=='infectado')
                self.assertEqual(v.infection_patterns,actual)
                if v.diagnosis=='infectado':
                    self.assertIn(v.infection_pattern,actual);found.add(v.infection_pattern)
                else:self.assertEqual(actual,frozenset());self.assertIsNone(v.infection_pattern)
                self.assertEqual(s.diagnosticar_visitante(v.id),'inconclusivo')
        self.assertEqual(found,set(PROTOCOL_NEWS))
        self.assertEqual(before,(ROOT/'logica_infeccao.py').read_bytes())

    def session(self):
        s=VisitorSession(random.Random(4));v=s.visitors['ricardo']
        s.set_condition(v,random.Random(5),'infectado','boletim_17',exclusive=True)
        s.news.watch(s.news.current(1));s.decide(v,'acolhido')
        s.manager.plan={v.id:1};s.survival.add_supplies(100,100)
        return s

    def test_third_pattern_first_exposure_17_defeat_18_without_reading(self):
        s=self.session();v=s.visitors['ricardo']
        before=(v.diagnosis,v.infection_pattern,v.infection_patterns,v.symptoms.copy())
        for day in range(1,17):
            self.assertEqual(s.day,day);self.assertTrue(s.days.advance())
            self.assertEqual(s.survival.infection_exposure,0)
        self.assertFalse(s.news.current(17).read)
        self.assertTrue(s.days.close_day());self.assertEqual(s.survival.infection_exposure,1)
        s.days.close_day();self.assertEqual(s.survival.infection_exposure,1)
        s.days.advance();self.assertFalse(s.days.close_day())
        self.assertEqual(s.survival.defeat_day,18)
        self.assertEqual(before,(v.diagnosis,v.infection_pattern,v.infection_patterns,v.symptoms))

    def test_diagnosis_only_after_reading_17_and_observing_all_required_signs(self):
        s=self.session();v=s.visitors['ricardo']
        s.days.day=14;s.news.unlock(14)
        s.news.watch(s.news.current(14));s.news.watch(next(b for b in s.news.history if b.day==7))
        for feature in LABELS:s.medical.observe(v,feature)
        self.assertEqual(s.diagnosticar_visitante(v.id),'inconclusivo')
        self.assertFalse(s.news.watch(next(b for b in s.news.bulletins if b.day==17)))
        s.days.day=17;s.news.unlock(17)
        self.assertEqual(s.diagnosticar_visitante(v.id),'inconclusivo')
        s.news.watch(s.news.current(17))
        self.assertEqual(s.diagnosticar_visitante(v.id),'infectado')
        s.medical.observations[v.id].clear()
        self.assertEqual(s.diagnosticar_visitante(v.id),'inconclusivo')

    def test_eliminating_third_pattern_after_first_exposure_resets_counter(self):
        s=self.session()
        for _ in range(17):self.assertTrue(s.days.advance())
        self.assertEqual(s.survival.infection_exposure,1)
        self.assertTrue(s.eliminate('ricardo'))
        self.assertTrue(s.days.close_day());self.assertEqual(s.survival.infection_exposure,0)

    def test_test_menu_can_select_each_exclusive_pattern_for_every_visitor(self):
        s=VisitorSession(random.Random(2));menu=GameMenu(s.visitors)
        for key in s.visitors:
            menu.choose('test');menu.choose(key)
            self.assertIn('condition',dict(menu.entries()))
            for index,(condition,news) in enumerate(PATTERN_CONDITIONS.items(),3):
                menu.condition=index
                self.assertEqual(menu.choose('start'),('test',key,condition))
                v=s.start_test(key,condition,random.Random(9))
                self.assertEqual(v.infection_pattern,news)
                self.assertEqual(v.infection_patterns,frozenset((news,)))
                self.assertEqual(s.day,1)
                for feature in LABELS:s.medical.observe(v,feature)
                self.assertEqual(s.diagnosticar_visitante(key),'infectado')
        self.assertFalse(s.knowledge.published)

    def test_day_17_news_exact_title_and_history_reading(self):
        s=VisitorSession(random.Random(1));s.news.unlock(18)
        bulletin=next(b for b in s.news.history if b.id=='boletim_17')
        self.assertEqual(bulletin.day,17)
        self.assertEqual(bulletin.headline,'URGENTE — Cientistas identificam terceiro padrão de infecção')
        self.assertEqual(bulletin.paragraphs,[
            'Após novas análises, pesquisadores identificaram uma manifestação da doença que não corresponde aos dois padrões divulgados anteriormente.',
            'Os novos casos apresentam uma combinação específica de olhos alterados, tremores involuntários e ausência de manchas nas mãos.',
            'Autoridades alertam que a ausência de manchas não deve ser considerada uma garantia de segurança. O novo padrão amplia o protocolo oficial de identificação de infectados.'])
        self.assertTrue(s.news.watch(bulletin))
        self.assertIn('boletim_17',s.knowledge.published)
