"""Calendário real e cenários de recursos sem suprimentos artificiais."""
import copy
import json
import random
import unittest
from casa.config import ROOT
from casa.visitors import VisitorSession


class CalendarBalanceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.definitions=[json.loads(p.read_text(encoding='utf-8'))
                         for p in sorted((ROOT/'dados/visitantes').glob('*.json'))
                         if not p.stem.endswith('_dialogos')]

    def session(self,seed):
        return VisitorSession(random.Random(seed),self.definitions,asset_check=lambda d:'')

    def simulate(self,seed,policy):
        state=self.session(seed)
        # Isola o balanço de recursos: a exposição agora tem derrota própria.
        for visitor in state.visitors.values():
            state.set_condition(visitor,random.Random(seed),'saudavel')
        state.news.watch(state.news.current(1))
        seen=[]
        while state.survival.alive:
            if state.manager.current:
                visitor=state.visitors[state.manager.current]
                seen.append((state.day,visitor.id))
                state.decide(visitor,'acolhido' if policy(state,visitor) else 'rejeitado')
            if state.day==20:
                state.days.close_day()
                break
            state.days.advance()
        return state,seen

    def test_500_seeds_calendar_order_unique_and_decisions_do_not_change_plan(self):
        orders=set()
        for seed in range(500):
            state=self.session(seed);manager=state.manager
            snapshot=copy.deepcopy(manager.plan)
            self.assertEqual(snapshot['ricardo'],1)
            self.assertEqual(snapshot['laura'],2)
            self.assertEqual(sorted(snapshot.values()),[1,2,4,6,9,13,17])
            orders.add(tuple(sorted(snapshot,key=snapshot.get)))
            self.assertIsNone(manager.activate(1,False))
            for day in range(1,21):
                manager.activate(day,True)
                if manager.current:
                    v=state.visitors[manager.current]
                    self.assertEqual(v.arrival_day,day)
                    state.decide(v,'acolhido' if (seed+day)%2 else 'rejeitado')
                for _ in range(2):manager.activate(day,True)
                self.assertEqual(manager.plan,snapshot)
            self.assertEqual(len(manager.seen),7)
        self.assertGreater(len(orders),50)

    def test_resources_allow_success_and_failure_without_guarantee(self):
        winners=0;reject_days=set();selective_winners=0
        for seed in range(500):
            state,seen=self.simulate(seed,lambda s,v:True)
            winners+=state.survival.alive
            self.assertEqual(len(seen),len({key for _,key in seen}))
            rejected,_=self.simulate(seed,lambda s,v:False)
            reject_days.add(rejected.day)
            selective,_=self.simulate(seed,lambda s,v:v.id=='ricardo' or min(s.survival.food,s.survival.water)<5)
            selective_winners+=selective.survival.alive
        self.assertGreater(winners,250)
        self.assertLess(winners,500)
        self.assertGreater(selective_winners,0)
        self.assertEqual(reject_days,{3})

    def test_test_mode_immediate_and_no_calendar_arrivals(self):
        for key in ('ricardo','laura','antonio','gabriel','helena','daniel','marina'):
            state=self.session(3)
            visitor=state.start_test(key)
            self.assertEqual(state.day,1)
            self.assertTrue(visitor.arrived)
            state.news.watch(state.news.current(1))
            self.assertEqual(state.manager.current,key)
            state.decide(visitor,'acolhido')
            state.survival.add_supplies(100,100)
            for _ in range(5):state.days.advance()
            self.assertEqual(state.manager.seen,{key})
            self.assertIsNone(state.manager.current)

    def test_delayed_activation_recovers_due_visitor(self):
        state=self.session(4);state.news.watch(state.news.current(1))
        state.decide(state.visitors['ricardo'],'rejeitado')
        self.assertEqual(state.manager.activate(3,True).id,'laura')
        state.manager.activate(4,True)
        self.assertEqual(len(state.manager.queue),1)
        state.decide(state.visitors['laura'],'rejeitado')
        self.assertEqual(state.visitors[state.manager.current].arrival_day,4)

    def test_real_sleep_transitions_present_every_scheduled_visitor(self):
        import pygame
        from casa.game import House
        game=House();state=game.visitor_session
        state.set_condition(state.visitors['ricardo'],random.Random(0),'saudavel')
        state.news.watch(state.news.current(1))
        self.assertTrue(game.decide_visitor(state.visitors['ricardo'],'acolhido'))
        # Isola transições visuais da simulação de recursos testada acima.
        state.survival.add_supplies(100,100)
        seen={'ricardo'}
        while state.day<20:
            game.dialog=''
            game.change_room('quarto',game.scenes['quarto'].point((345,365)))
            game.handle_event(pygame.event.Event(pygame.KEYUP,key=pygame.K_e))
            game.interact();self.assertTrue(game.sleep_option,game.dialog)
            game.confirm_sleep();game.update((0,0),3)
            planned=[key for key,day in state.manager.plan.items() if day==state.day]
            if planned:
                key=planned[0]
                self.assertEqual(state.manager.current,key)
                self.assertEqual(game.peephole.visitor_ui.visitor.id,key)
                self.assertTrue(game.sleep_block_reason())
                for room in game.scenes:game.change_room(room)
                self.assertEqual(state.manager.current,key)
                self.assertNotIn(key,seen);seen.add(key)
                self.assertTrue(game.decide_visitor(state.visitors[key],'rejeitado'))
        self.assertEqual(seen,set(state.visitors))
