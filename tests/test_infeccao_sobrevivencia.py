"""Condição real, exposição, eliminação e encerramento da campanha."""
import copy
import random
import unittest
from unittest.mock import patch
import pygame
from casa.config import ROOT
from casa.game import House
from casa.medical_knowledge import LABELS
from casa.visitors import VisitorSession,PROTOCOL_NEWS
from casa.visitor_assets import load_assets
from casa.visitor_ui import VisitorUI
from logica_infeccao import diagnosticar


class InfectionSurvivalTests(unittest.TestCase):
    def session(self,condition='infectado'):
        s=VisitorSession(random.Random(42))
        s.set_condition(s.visitors['ricardo'],random.Random(4),condition)
        s.news.watch(s.news.current(1))
        s.decide(s.visitors['ricardo'],'acolhido')
        s.test_mode=True  # Isola exposição/recursos da chegada de novos visitantes.
        s.survival.add_supplies(100,100)
        return s

    def test_all_seven_conditions_consistent_for_many_seeds(self):
        conditions=set();benign=set()
        for seed in range(100):
            s=VisitorSession(random.Random(seed))
            self.assertEqual(len(s.visitors),7)
            self.assertFalse(s.knowledge.published)
            self.assertFalse(s.medical.observations)
            for v in s.visitors.values():
                self.assertEqual(set(v.symptoms),set(LABELS))
                self.assertIn(v.diagnosis,('saudavel','infectado'))
                result=diagnosticar(v.symptoms,set(PROTOCOL_NEWS))
                self.assertEqual(result=='infectado',v.diagnosis=='infectado',(seed,v.id))
                conditions.add(v.diagnosis)
                if v.diagnosis=='saudavel':benign.update(k for k,value in v.symptoms.items() if value)
                self.assertEqual(s.diagnosticar_visitante(v.id),'inconclusivo')
        self.assertEqual(conditions,{'saudavel','infectado'})
        self.assertEqual(benign,set(LABELS))

    def test_selected_conditions_consistent_and_no_observation_resampling(self):
        s=VisitorSession(random.Random(4))
        for key in ('gabriel','antonio'):
            for condition in ('saudavel','infectado'):
                for seed in range(25):
                    v=s.start_test(key,condition,random.Random(seed))
                    self.assertEqual(v.diagnosis,condition)
                    self.assertEqual(diagnosticar(v.symptoms,set(PROTOCOL_NEWS))=='infectado',condition=='infectado')
                    before=(v.diagnosis,copy.deepcopy(v.symptoms))
                    with patch.object(VisitorSession,'set_condition',side_effect=AssertionError('ressorteio')):
                        for feature in v.symptoms:s.medical.observe(v,feature)
                        s.diagnosticar_visitante(key)
                    self.assertEqual((v.diagnosis,v.symptoms),before)
        s.start_test('gabriel','saudavel',random.Random(8))
        self.assertNotIn('gabriel',s.medical.observations)
        self.assertFalse(s.visitors['gabriel'].examined)

    def test_first_night_and_second_night_defeat_idempotently(self):
        s=self.session()
        s.days.day=17;s.news.unlock(17)  # Ambos os padrões já foram publicados.
        self.assertEqual(s.diagnosticar_visitante('ricardo'),'inconclusivo')
        self.assertTrue(s.days.close_day())
        self.assertEqual(s.survival.infection_exposure,1)
        self.assertTrue(s.survival.alive)
        self.assertTrue(s.days.close_day())
        self.assertEqual(s.survival.infection_exposure,1)
        self.assertTrue(s.days.advance())
        self.assertFalse(s.days.close_day())
        self.assertFalse(s.survival.alive)
        self.assertEqual(s.survival.defeat_day,18)
        self.assertIn('infecção foi fatal',s.survival.defeat_cause)
        before=(s.survival.food,s.survival.water,s.survival.infection_exposure)
        self.assertFalse(s.days.advance());s.days.close_day()
        self.assertEqual(before,(s.survival.food,s.survival.water,s.survival.infection_exposure))

    def test_multiple_infected_count_only_once_and_elimination_interrupts(self):
        s=self.session();other=s.visitors['laura']
        s.days.day=17;s.news.unlock(17)
        s.set_condition(other,random.Random(0),'infectado')
        other.arrived=True;self.assertTrue(s.decide(other,'acolhido'))
        s.days.advance()
        self.assertEqual(s.survival.infection_exposure,1)
        self.assertTrue(s.eliminate('ricardo'))
        self.assertTrue(s.eliminate('laura'))
        self.assertTrue(s.days.close_day())
        self.assertEqual(s.survival.infection_exposure,0)
        self.assertTrue(s.survival.alive)
        self.assertEqual(s.survival.loneliness,1)
        self.assertEqual(s.last_report.residents,1)
        self.assertEqual(s.last_report.food,.5)
        self.assertEqual(s.last_report.water,.5)

    def test_remaining_infected_still_causes_defeat(self):
        s=self.session();other=s.visitors['laura']
        s.days.day=17;s.news.unlock(17)
        s.set_condition(other,random.Random(0),'infectado')
        other.arrived=True;s.decide(other,'acolhido')
        s.days.advance();s.eliminate('ricardo');s.days.close_day()
        self.assertFalse(s.survival.alive)

    def test_rejected_or_waiting_infected_do_not_expose(self):
        for decision in ('rejeitado',None):
            with self.subTest(decision=decision):
                s=VisitorSession(random.Random(4))
                s.set_condition(s.visitors['ricardo'],random.Random(0),'infectado')
                s.news.watch(s.news.current(1))
                if decision:s.decide(s.visitors['ricardo'],decision)
                s.days.day=17;s.news.unlock(17)
                s.days.close_day()
                self.assertEqual(s.survival.infection_exposure,0)

    def test_elimination_cost_uses_real_condition_once_and_removes_needs(self):
        for condition,cost in (('infectado',2),('saudavel',3)):
            with self.subTest(condition=condition):
                s=self.session(condition);v=s.visitors['ricardo']
                before=(s.survival.food,s.survival.water)
                with patch.object(s,'diagnosticar_visitante',return_value='inconclusivo'):
                    self.assertTrue(s.eliminate(v.id))
                self.assertEqual(s.survival.sanity,8-cost)
                self.assertFalse(v.alive);self.assertEqual(v.state,'eliminado')
                self.assertNotIn(v.id,s.living_ids)
                self.assertNotIn(v.id,s.survival.people)
                self.assertFalse(s.company_seen_today)
                self.assertNotIn(v.id,s.manager.residents)
                self.assertEqual(before,(s.survival.food,s.survival.water))
                self.assertFalse(s.eliminate(v.id));self.assertEqual(s.survival.sanity,8-cost)
                self.assertFalse(s.eliminate('inexistente'))

    def test_win_only_after_final_day_and_restart_interface(self):
        s=self.session('saudavel')
        for day in range(1,20):
            self.assertEqual(s.day,day);self.assertTrue(s.days.advance())
        self.assertFalse(s.survival.won)
        self.assertFalse(s.days.advance())
        self.assertTrue(s.survival.won);self.assertTrue(s.survival.alive)
        self.assertEqual(s.survival.victory_day,20)
        self.assertEqual(s.last_report.day,20)
        before=(s.survival.food,s.survival.water)
        s.days.close_day();s.days.advance()
        self.assertEqual(before,(s.survival.food,s.survival.water))
        self.assertFalse(s.eliminate('ricardo'))

    def test_all_losses_override_victory_on_day_twenty(self):
        for cause in ('infection','thirst','hunger','loneliness'):
            with self.subTest(cause=cause):
                s=self.session('infectado' if cause=='infection' else 'saudavel')
                s.days.day=20
                if cause=='infection':s.survival.infection_exposure=1
                if cause=='thirst':s.survival._water=0;s.survival.people['protagonista'].thirst=1
                if cause=='hunger':s.survival._food=0;s.survival.people['protagonista'].hunger=2
                if cause=='loneliness':s.eliminate('ricardo');s.survival.loneliness=4
                self.assertFalse(s.days.close_day())
                self.assertFalse(s.survival.won);self.assertFalse(s.survival.alive)
                self.assertEqual(s.survival.defeat_day,20)

    def test_future_healthy_result_is_forwarded_without_using_real_condition(self):
        s=self.session()
        ui=VisitorUI(s.visitors['ricardo'],None,lambda *args:False,knowledge=s.medical,session=s)
        s.medical.known.update(LABELS);ui.page='investigate'
        with patch('casa.visitors.infection_logic.diagnosticar',return_value='saudavel') as diagnose:
            self.assertIsNone(ui.diagnosis_indicator())
            diagnose.assert_not_called()
        self.assertEqual(s.visitors['ricardo'].diagnosis,'infectado')


class InfectionInterfaceTests(unittest.TestCase):
    def click(self,ui,key):
        ui.handle_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN,button=1,pos=ui.layout()[key][0].center))

    def test_marina_six_real_images_normal_and_test_modes(self):
        s=VisitorSession(random.Random(7));v=s.visitors['marina']
        self.assertNotIn(v.id,s.unavailable)
        self.assertEqual(set(v.definition['investigation_features']),set(LABELS))
        self.assertEqual(set(v.definition['investigation']),set(LABELS))
        assets=load_assets(v.definition)
        ui=VisitorUI(v,assets,lambda *args:False,knowledge=s.medical,session=s)
        ui.page='investigate'
        self.assertNotIn('tremores_involuntarios',ui.layout())
        s.news.unlock(14);s.news.watch(s.news.current(14))
        self.assertIn('tremores_involuntarios',ui.layout())
        for altered,name in ((False,'mao_normal.png'),(True,'mao_tremendo.png')):
            v.symptoms['tremores_involuntarios']=altered
            self.click(ui,'tremores_involuntarios')
            image=ui.examination_image()
            original=pygame.image.load(str(ROOT/v.definition['asset_root']/'investigacao'/name)).convert_alpha()
            self.assertEqual(pygame.image.tobytes(image,'RGBA'),pygame.image.tobytes(original,'RGBA'))
            ui.draw(pygame.display.get_surface());self.click(ui,'back')
        s.start_test('marina')
        self.assertEqual(set(ui.layout()),set(LABELS)|{'back'})

    def test_resident_confirmation_cancel_eliminate_and_no_movement(self):
        game=House();s=game.visitor_session
        s.news.watch(s.news.current(1));v=s.visitors['ricardo']
        s.set_condition(v,random.Random(0),'infectado')
        self.assertTrue(game.decide_visitor(v,'acolhido'))
        actor=game.residents[v.id]
        game.dialog='';game.change_room(actor.room,actor.feet+pygame.Vector2(0,-20))
        game.interact();ui=game.resident_ui
        self.assertIsNotNone(ui)
        self.click(ui,'eliminate');self.assertTrue(v.alive)
        ui.draw(pygame.display.get_surface())
        self.click(ui,'back');self.assertTrue(v.alive)
        self.click(ui,'eliminate');self.click(ui,'confirm')
        self.assertFalse(v.alive);self.assertIsNone(game.resident_ui)
        self.assertNotIn(v.id,game.residents);self.assertNotIn(v.id,game.resident_positions)
        self.assertTrue(game.fade.active)
        before=actor.feet.copy();game.update((0,0),1);game.update((0,0),1)
        self.assertEqual(actor.feet,before)
        self.assertTrue(game.dialog)
        game.draw(pygame.display.get_surface())

    def test_victory_and_infection_defeat_screens_restart_and_freeze(self):
        for won in (True,False):
            with self.subTest(won=won):
                game=House();s=game.visitor_session
                s.days.day=20;s.intro.broadcast_seen=True
                s.company_seen_today=True;s.survival.add_supplies(100,100)
                v=s.visitors['ricardo']
                s.set_condition(v,random.Random(0),'saudavel' if won else 'infectado')
                v.arrived=True;s.decide(v,'acolhido')
                if not won:s.survival.infection_exposure=1
                game.dialog='';game.sleep_option=True
                game.confirm_sleep()
                self.assertEqual(s.survival.won,won)
                self.assertEqual(s.survival.alive,won)
                self.assertEqual(s.last_report.day,20)
                before=game.player.feet.copy();game.update((1,0),5)
                self.assertEqual(game.player.feet,before)
                game.draw(pygame.display.get_surface())
                game.handle_event(pygame.event.Event(pygame.KEYDOWN,key=pygame.K_RETURN))
                self.assertIsNot(game.visitor_session,s)
                self.assertEqual(game.days.day,1)
                self.assertFalse(game.visitor_session.survival.won)
