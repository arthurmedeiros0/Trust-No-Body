"""Racoes, limites, introducao real e transferencias sem logica de infeccao."""
import copy
import random
import unittest
from unittest.mock import patch
import pygame
from casa.survival import Survival
from casa.game import House
from casa.visitors import Visitor,VisitorSession
from support import without_future_arrivals


class SurvivalUnitTests(unittest.TestCase):
    def test_forecast_is_pure_respects_ration_order_and_preserves_history(self):
        state=Survival();ids=['protagonista','outro']
        self.assertEqual(vars(state.predicted_needs(1,ids)),dict(hunger=0,thirst=0))
        state.close_day(1,ids);state.close_day(2,ids)
        snapshot=copy.deepcopy(vars(state))
        for _ in range(20):
            self.assertEqual(vars(state.predicted_needs(3,ids)),dict(hunger=2,thirst=2))
        self.assertEqual(vars(state),snapshot)
        state.add_supplies(.5,.5)
        self.assertEqual(vars(state.predicted_needs(3,ids)),dict(hunger=0,thirst=0))
        self.assertEqual(vars(state.people['protagonista']),dict(hunger=1,thirst=1))
        state.ration_policy=lambda people:['outro','protagonista']
        self.assertEqual(vars(state.predicted_needs(3,ids)),dict(hunger=2,thirst=2))
        state.ration_policy=lambda people:['protagonista','outro']
        state.close_day(3,ids)
        self.assertEqual(vars(state.predicted_needs(3,ids)),dict(hunger=0,thirst=0))
        self.assertTrue(state.alive)

    def test_critical_forecast_survives_exploration_then_recovers_or_dies_at_sleep(self):
        for resource,limit,last_day in (('water',2,2),('food',3,3)):
            for recover in (False,True):
                with self.subTest(resource=resource,recover=recover):
                    state=Survival()
                    state.add_supplies(20 if resource=='water' else 0,
                                       20 if resource=='food' else 0)
                    # Companhia isola a privacao da derrota independente por solidao.
                    ids=['protagonista','outro']
                    for day in range(1,last_day+1):
                        state.close_day(day,ids)
                        self.assertTrue(state.alive)
                    needs=state.people['protagonista']
                    counter='thirst' if resource=='water' else 'hunger'
                    self.assertEqual(getattr(needs,counter),limit-1)
                    self.assertEqual(getattr(state.predicted_needs(last_day+1,ids),counter),limit)
                    if recover:state.add_supplies(.5 if resource=='food' else 0,.5 if resource=='water' else 0)
                    report=state.close_day(last_day+1,ids)
                    self.assertEqual(state.alive,recover)
                    self.assertEqual(getattr(needs,counter),0 if recover else limit)
                    self.assertIs(state.close_day(last_day+1,ids),report)
                    self.assertEqual(state.alive,recover)
                    self.assertGreaterEqual(state.food,0);self.assertGreaterEqual(state.water,0)

    def test_day_one_tolerance_for_all_residents_and_normal_day_two(self):
        for count in (1,2,5):
            state=Survival();state.add_supplies(10,10)
            ids=['protagonista']+[f'morador_{i}' for i in range(count-1)]
            report=state.close_day(1,ids)
            self.assertEqual((state.food,state.water),(10,10))
            self.assertEqual((report.food,report.water),(0,0))
            self.assertFalse(report.hungry or report.thirsty)
            for needs in state.people.values():self.assertEqual((needs.hunger,needs.thirst),(0,0))
            self.assertEqual(state.sanity,7 if count==1 else 8)
            self.assertEqual(state.loneliness,1 if count==1 else 0)
            self.assertIs(state.close_day(1,ids),report)
            report=state.close_day(2,ids)
            self.assertEqual((report.food,report.water),(count*.5,count*.5))

    def test_sanity_from_day_one_partial_company_and_no_zero_defeat(self):
        state=Survival();state.add_supplies(20,20)
        for day in (1,2,3):
            state.close_day(day,['protagonista'])
            self.assertEqual(state.sanity,8-day)
            self.assertEqual(state.loneliness,day)
        state.close_day(4,['protagonista','outro'])
        self.assertEqual(state.sanity,6);self.assertEqual(state.loneliness,0)
        state.close_day(4,['protagonista','outro']);self.assertEqual(state.sanity,6)
        state.change_sanity(-100)
        state.close_day(5,['protagonista'])
        self.assertEqual(state.sanity,0);self.assertTrue(state.alive)
        state.close_day(6,['protagonista'],company_seen=True)
        self.assertEqual(state.sanity,1);self.assertEqual(state.loneliness,0)

    def test_initial_values_and_any_household_size(self):
        for count in (1,2,3,5,12):
            state=Survival();self.assertEqual((state.food,state.water,state.sanity),(0,0,8))
            state.add_supplies(20,20)
            ids=['protagonista']+[f'morador_{i}' for i in range(count-1)]
            report=state.close_day(2,ids)
            self.assertEqual((report.food,report.water),(count*.5,count*.5))
            self.assertEqual(state.food,20-count*.5)
            self.assertEqual(state.water,20-count*.5)

    def test_shortage_priority_zero_floor_and_separate_rations(self):
        state=Survival();state.add_supplies(1,.5)
        report=state.close_day(2,['zeta','protagonista','alfa'])
        self.assertEqual((state.food,state.water),(0,0))
        self.assertEqual((report.food,report.water),(1,.5))
        self.assertEqual(state.people['protagonista'].hunger,0)
        self.assertEqual(state.people['protagonista'].thirst,0)
        self.assertEqual(state.people['alfa'].hunger,0)
        self.assertEqual(state.people['alfa'].thirst,1)
        self.assertEqual(state.people['zeta'].hunger,1)
        before=copy.deepcopy(vars(state))
        self.assertIs(state.close_day(2,['protagonista']),report)
        self.assertEqual(vars(state),before)

    def test_reset_hunger_and_thirst_independently(self):
        state=Survival();state.close_day(2,['protagonista'])
        self.assertEqual((state.people['protagonista'].hunger,state.people['protagonista'].thirst),(1,1))
        state.add_supplies(0,.5);state.close_day(3,['protagonista'])
        self.assertEqual((state.people['protagonista'].hunger,state.people['protagonista'].thirst),(2,0))
        state.add_supplies(.5,.5);state.close_day(4,['protagonista'])
        self.assertEqual((state.people['protagonista'].hunger,state.people['protagonista'].thirst),(0,0))

    def test_death_hunger_three_thirst_two_loneliness_five(self):
        for kind,limit,food,water in (('comida',4,0,20),('água',3,20,0),('solidão',5,20,20)):
            state=Survival();state.add_supplies(food,water)
            for day in range(1,limit+1):
                state.close_day(day,['protagonista'])
                self.assertEqual(state.alive,day<limit)
            self.assertIn(kind,state.defeat_cause);self.assertEqual(state.defeat_day,limit)

    def test_company_resets_loneliness_sanity_once_and_zero_is_not_death(self):
        state=Survival();state.add_supplies(50,50);state.change_sanity(-20)
        self.assertEqual(state.sanity,0);self.assertTrue(state.alive)
        state.close_day(2,['protagonista']);self.assertEqual(state.loneliness,1)
        state.close_day(3,['protagonista','a','b','c'])
        self.assertEqual(state.loneliness,0);self.assertEqual(state.sanity,1)
        state.close_day(3,['protagonista','a','b','c']);self.assertEqual(state.sanity,1)
        state.change_sanity(99);self.assertEqual(state.sanity,8)
        state.close_day(4,['protagonista'],company_seen=True)
        self.assertEqual(state.loneliness,0)

    def test_invalid_resources_and_configurable_ration_order(self):
        state=Survival()
        for food,water in ((-.5,0),(0,-1),(.2,0)):
            with self.assertRaises(ValueError):state.add_supplies(food,water)
        state.add_supplies(.5,.5)
        state.ration_policy=lambda ids:['alfa','protagonista']
        state.close_day(2,['protagonista','alfa'])
        self.assertEqual(state.people['alfa'].hunger,0)
        self.assertEqual(state.people['protagonista'].hunger,1)


class SurvivalGameTests(unittest.TestCase):
    def setUp(self):self.game=House()

    def key(self,key):self.game.handle_event(pygame.event.Event(pygame.KEYDOWN,key=key))

    def introduction(self):
        self.key(pygame.K_RETURN)
        self.game.news.watch(self.game.news.current(1))

    def sleep(self):
        game=self.game
        without_future_arrivals(game)
        if game.dialog:self.key(pygame.K_RETURN)
        game.change_room('quarto',game.scenes['quarto'].point((345,365)))
        game.handle_event(pygame.event.Event(pygame.KEYUP,key=pygame.K_e))
        self.key(pygame.K_e);self.assertTrue(game.sleep_option)
        self.key(pygame.K_s);game.update((0,0),3)

    def test_real_new_game_starts_bedroom_empty_and_visitor_absent(self):
        game=self.game;session=game.visitor_session
        self.assertEqual(game.room,'quarto');self.assertEqual(game.days.day,1)
        self.assertEqual((session.survival.food,session.survival.water,session.survival.sanity),(0,0,8))
        self.assertEqual(session.living_ids,['protagonista'])
        self.assertEqual(session.survival.people['protagonista'].hunger,0)
        self.assertIsNone(game.peephole.visitor_ui)
        visitor=session.visitors['ricardo']
        self.assertFalse(visitor.arrived);self.assertFalse(game.decide_visitor(visitor,'acolhido'))
        self.assertIn('fome',game.dialog)
        self.assertIn('geladeira',session.intro.objective)
        game.draw(pygame.display.get_surface())

    def test_fridge_never_generates_and_first_broadcast_brings_ricardo_once(self):
        game=self.game;session=game.visitor_session;self.key(pygame.K_RETURN)
        game.change_room('cozinha',game.scenes['cozinha'].point((635,250)))
        game.interact();self.assertIn('geladeira está vazia',game.dialog)
        self.assertIn('garrafa de água',game.dialog)
        self.assertIn('noticiário',session.intro.objective)
        self.key(pygame.K_RETURN);game.interact()
        self.assertEqual((session.survival.food,session.survival.water),(0,0))
        self.key(pygame.K_RETURN)
        game.television.open();game.television.choose('current')
        self.assertTrue(session.visitors['ricardo'].arrived)
        self.assertIsNotNone(game.peephole.visitor_ui)
        ui=game.peephole.visitor_ui;game.news.watch(game.news.current(1))
        self.assertIs(game.peephole.visitor_ui,ui)
        self.assertIn('porta',session.intro.objective)
        text=' '.join(game.news.current(1).paragraphs).lower()
        for word in ('letal','lockdown','proibida','zonas vermelhas','abastecimento','abrigos'):self.assertIn(word,text)

    def test_accept_transfer_once_rejection_no_transfer_and_no_eviction(self):
        for decision in ('acolhido','rejeitado'):
            self.game=House();self.introduction()
            session=self.game.visitor_session;visitor=session.visitors['ricardo']
            self.assertIn(visitor.food,(2,3));self.assertIn(visitor.water,(2,3))
            symptoms=copy.deepcopy(visitor.symptoms)
            self.assertTrue(self.game.decide_visitor(visitor,decision))
            expected=(visitor.food,visitor.water) if decision=='acolhido' else (0,0)
            self.assertEqual((session.survival.food,session.survival.water),expected)
            self.assertEqual(len(session.living_ids),2 if decision=='acolhido' else 1)
            self.assertFalse(self.game.decide_visitor(visitor,'acolhido'))
            self.assertFalse(self.game.decide_visitor(visitor,'rejeitado'))
            self.assertEqual(visitor.symptoms,symptoms)
            if decision=='acolhido':self.assertEqual((visitor.available_food,visitor.available_water),(0,0))

    def test_sleep_consumes_once_summary_preserves_visitor_and_npc(self):
        self.introduction();game=self.game;session=game.visitor_session
        visitor=session.visitors['ricardo'];game.decide_visitor(visitor,'acolhido')
        snapshot=copy.deepcopy(vars(visitor));actor=game.residents['ricardo'];feet=actor.feet.copy()
        stocks=(session.survival.food,session.survival.water)
        with patch('casa.visitors.random.getrandbits',side_effect=AssertionError('novo sorteio')):self.sleep()
        self.assertEqual(game.days.day,2)
        self.assertEqual((session.survival.food,session.survival.water),stocks)
        self.assertEqual(vars(visitor),snapshot);self.assertEqual(actor.feet,feet)
        self.assertIn('Resumo do dia anterior',game.dialog)
        self.assertEqual(len(session.survival.reports),1)
        game.confirm_sleep();game.update((0,0),10)
        self.assertEqual(game.days.day,2);self.assertEqual(len(session.survival.reports),1)

    def test_defeat_does_not_advance_day_and_restart_resets_real_state(self):
        self.introduction();self.game.decide_visitor(self.game.visitor_session.visitors['ricardo'],'rejeitado')
        self.sleep();self.assertEqual(self.game.days.day,2)
        self.sleep();self.assertEqual(self.game.days.day,3)
        self.sleep();game=self.game
        self.assertFalse(game.visitor_session.survival.alive)
        self.assertEqual(game.days.day,3);self.assertEqual(game.visitor_session.survival.defeat_day,3)
        self.assertEqual(len(game.visitor_session.survival.reports),3)
        game.draw(pygame.display.get_surface())
        self.key(pygame.K_i);self.assertFalse(game.inventory.active)
        old=game.visitor_session
        with patch('casa.visitors.random.getrandbits',return_value=1) as roll:self.key(pygame.K_RETURN)
        self.assertEqual(roll.call_count,sum(len(v.symptoms) for v in old.visitors.values()));self.assertIsNot(game.visitor_session,old)
        self.assertEqual(game.room,'quarto');self.assertEqual(game.days.day,1)
        self.assertEqual((game.visitor_session.survival.food,game.visitor_session.survival.water),(0,0))
        self.assertEqual(game.visitor_session.survival.sanity,8)
        self.assertIsNone(game.peephole.visitor_ui);self.assertFalse(game.residents)

    def test_inventory_pauses_and_closes_i_or_escape(self):
        self.key(pygame.K_RETURN);self.key(pygame.K_i)
        self.assertTrue(self.game.inventory.active);self.assertTrue(self.game.captures_escape)
        before=self.game.player.feet.copy();self.game.update((1,0),5)
        self.assertEqual(self.game.player.feet,before)
        self.game.draw(pygame.display.get_surface())
        self.key(pygame.K_ESCAPE);self.assertFalse(self.game.inventory.active)
        self.key(pygame.K_i);self.key(pygame.K_i);self.assertFalse(self.game.inventory.active)

    def test_multiple_living_residents_and_dead_excluded(self):
        self.introduction();session=self.game.visitor_session
        session.decide(session.visitors['ricardo'],'rejeitado')
        for name in ('zeta','alfa'):
            visitor=Visitor({'id':name}, {},2,2,arrived=True)
            session.visitors[name]=visitor;self.assertTrue(session.decide(visitor,'acolhido'))
        session.visitors['zeta'].alive=False
        self.assertEqual(session.living_ids,['protagonista','alfa'])
        report=session.survival.close_day(2,session.living_ids)
        self.assertEqual(report.food,1);self.assertEqual(report.water,1)
        self.assertEqual(session.survival.people['zeta'].hunger,0)

    def test_medical_schedule_preserved_and_new_context_not_diagnostics(self):
        self.introduction();news=self.game.news.bulletins
        self.assertIn('recusam',news[2].paragraphs[0]);self.assertIn('fatais',news[5].paragraphs[0])
        for day,term in ((4,'preliminares'),(7,'três condições'),(10,'ainda não'),(14,'independente'),(17,'protocolo completo'),(20,'tratamento')):
            self.assertIn(term,' '.join(news[day-1].paragraphs))
        self.assertEqual(self.game.visitor_session.visitors['ricardo'].diagnosis,'diagnostico_pendente')
