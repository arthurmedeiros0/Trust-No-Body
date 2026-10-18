"""Personagens simulados apenas em testes; nenhum cadastro novo na partida."""
import copy
import json
import random
import unittest
from unittest.mock import patch
from types import SimpleNamespace
import pygame
from casa.config import ROOT
from casa.visitors import Visitor,VisitorSession
from casa.visitor_schedule import VisitorManager,ArrivalRules
from casa.visitor_registry import readiness
from casa.game import House


def simulated(count):
    definition=json.loads((ROOT/'dados/visitantes/ricardo.json').read_text(encoding='utf-8'))
    definitions=[definition]
    for number in range(count):
        other=copy.deepcopy(definition)
        other['id']=f'teste_{number}';other['name']=f'Simulado {number}'
        definitions.append(other)
    return definitions


def session(count,seed=1,rules=None):
    return VisitorSession(random.Random(seed),simulated(count),rules,asset_check=lambda definition:'')


class ArrivalTests(unittest.TestCase):
    def test_only_ricardo_introduction_and_empty_early_opportunities(self):
        state=VisitorSession(random.Random(1),simulated(0));manager=state.manager
        self.assertEqual(manager.plan,{'ricardo':1})
        self.assertEqual(manager.opportunities,{2:[],3:[]})
        self.assertFalse(state.visitors['ricardo'].arrived)
        state.news.watch(state.news.current(1))
        self.assertEqual(manager.current,'ricardo');self.assertEqual(manager.seen,{'ricardo'})
        self.assertTrue(state.decide(state.visitors['ricardo'],'rejeitado'))
        state.survival.add_supplies(10,10) # Fixture exclusiva; permite isolar o calendario.
        self.assertTrue(state.days.advance());self.assertTrue(state.days.advance())
        self.assertEqual(manager.opportunity_results,{2:'sem_candidatos',3:'sem_candidatos'})
        self.assertIsNone(manager.current)

    def test_random_plan_once_unique_bounded_and_early_guarantee(self):
        plans=set()
        for seed in range(12):
            state=session(25,seed);manager=state.manager
            self.assertEqual(manager.plan['ricardo'],1)
            days=[day for key,day in manager.plan.items() if key!='ricardo']
            self.assertTrue(any(day in (2,3) for day in days))
            self.assertTrue(all(2<=day<=20 for day in days))
            self.assertEqual(len(days),len(set(days)))
            before=copy.deepcopy(manager.plan)
            for day in range(1,21):manager.activate(day,True)
            self.assertEqual(manager.plan,before)
            plans.add(tuple(sorted(manager.plan.items())))
        self.assertGreater(len(plans),1)
        self.assertEqual(session(6,3).manager.plan,session(6,3).manager.plan)

    def test_accept_and_reject_never_return_or_reroll_or_duplicate_resources(self):
        for decision in ('acolhido','rejeitado'):
            state=session(3);manager=state.manager
            snapshot={key:(copy.deepcopy(v.symptoms),v.food,v.water) for key,v in state.visitors.items()}
            state.news.watch(state.news.current(1));visitor=state.visitors['ricardo']
            self.assertTrue(state.decide(visitor,decision))
            stock=(state.survival.food,state.survival.water)
            self.assertFalse(state.decide(visitor,'acolhido'))
            self.assertFalse(state.decide(visitor,'rejeitado'))
            for day in range(2,21):
                manager.activate(day,True)
                if manager.current:
                    other=state.visitors[manager.current]
                    self.assertNotEqual(other.id,'ricardo')
                    state.decide(other,'rejeitado')
            self.assertEqual((state.survival.food,state.survival.water),stock)
            self.assertEqual({key:(v.symptoms,v.food,v.water) for key,v in state.visitors.items()},snapshot)
            self.assertEqual(manager.residents,['ricardo'] if decision=='acolhido' else [])
            self.assertIn('ricardo',manager.accepted if decision=='acolhido' else manager.rejected)

    def test_queue_does_not_replace_current_and_only_one_arrives_at_a_time(self):
        state=session(3,rules=ArrivalRules(first_day=2,last_day=2,max_per_day=3))
        manager=state.manager
        self.assertIsNone(manager.activate(2,False)) # Ricardo precisa ser o primeiro.
        state.news.watch(state.news.current(1))
        state.decide(state.visitors['ricardo'],'rejeitado')
        first=manager.activate(2,True)
        self.assertIsNotNone(first);self.assertEqual(len(manager.queue),2)
        for _ in range(10):self.assertIsNone(manager.activate(2,True))
        self.assertEqual(manager.current,first.id)
        pending=list(manager.queue)
        self.assertFalse(any(state.visitors[key].arrived for key in pending))
        self.assertFalse(state.decide(state.visitors[pending[0]],'acolhido'))
        self.assertTrue(state.decide(first,'rejeitado'))
        self.assertEqual(manager.current,pending[0])
        state.decide(state.visitors[pending[0]],'acolhido')
        self.assertEqual(manager.current,pending[1])
        state.decide(state.visitors[pending[1]],'rejeitado')
        self.assertIsNone(manager.current)
        self.assertEqual(len(manager.seen),4)

    def test_registry_blocks_missing_images_dialogue_and_walks(self):
        definition=simulated(0)[0]
        self.assertEqual(readiness(definition),'')
        for change in ({'portrait':'nao_existe.png'},{'id':'sem_dialogos'},
                       {'internal_sprite_manifest':'nao_existe.json'},
                       {'sprites':{}},{'investigation':{}}):
            incomplete={**definition,**change}
            self.assertTrue(readiness(incomplete))
        bad={**definition,'id':'incompleto','portrait':'nao_existe.png'}
        state=VisitorSession(random.Random(1),[definition,bad])
        self.assertIn('incompleto',state.unavailable)
        self.assertNotIn('incompleto',state.manager.plan)

    def test_duplicate_ids_and_invalid_configuration_fail_explicitly(self):
        definition=simulated(0)[0]
        with self.assertRaises(ValueError):VisitorSession(definitions=[definition,definition],asset_check=lambda d:'')
        for parameters in ({'first_day':1},{'last_day':21},{'max_per_day':0}):
            with self.assertRaises(ValueError):ArrivalRules(**parameters)

    def test_day_start_presents_dynamic_ui_and_room_changes_keep_waiting(self):
        state=session(2,rules=ArrivalRules(first_day=2,last_day=2,max_per_day=2))
        # Apenas objetos simulados: UI sem arquivos narrativos ficticios no disco.
        with patch('casa.game.VisitorSession',return_value=state),patch('casa.game.VisitorUI',side_effect=lambda visitor,assets,callback,**kwargs:SimpleNamespace(visitor=visitor,assets=assets)):
            game=House();game.dialog=''
            state.news.watch(state.news.current(1))
            ricardo=state.visitors['ricardo']
            self.assertTrue(game.decide_visitor(ricardo,'acolhido'))
            actor=game.residents['ricardo'];symptoms=copy.deepcopy(ricardo.symptoms)
            game.change_room('quarto',game.scenes['quarto'].point((345,365)))
            game.interact();game.confirm_sleep();game.update((0,0),3)
            self.assertEqual(game.days.day,2)
            current=state.manager.current
            self.assertNotEqual(current,'ricardo')
            self.assertEqual(game.peephole.visitor_ui.visitor.id,current)
            self.assertIs(game.peephole.visitor_ui.assets,game.visitor_assets[current])
            self.assertTrue(game.sleep_block_reason())
            for room in game.scenes:game.change_room(room)
            self.assertEqual(state.manager.current,current)
            self.assertIs(game.residents['ricardo'],actor);self.assertEqual(ricardo.symptoms,symptoms)
            self.assertTrue(game.decide_visitor(state.visitors[current],'rejeitado'))
            self.assertNotEqual(state.manager.current,current)
            self.assertEqual(game.peephole.visitor_ui.visitor.id,state.manager.current)
