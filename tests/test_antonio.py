"""Integração de Antônio nos mesmos sistemas de visitantes e moradores."""
import random
import unittest
import pygame
from casa.game import House
from casa.visitors import VisitorSession
from casa.visitor_assets import load_assets
from casa.visitor_dialogue import Dialogue
from casa.menu import GameMenu
from casa.collisions import feet_rect


class AntonioTests(unittest.TestCase):
    def test_conditions_schedule_and_stable_examinations(self):
        benign=set()
        for seed in range(20):
            session=VisitorSession(random.Random(seed))
            self.assertNotIn('antonio',session.unavailable)
            self.assertIn('antonio',session.manager.plan)
            for condition in ('saudavel','infectado','aleatoria'):
                visitor=session.start_test('antonio',condition,random.Random(seed))
                self.assertIn(visitor.diagnosis,('saudavel','infectado'))
                if condition!='aleatoria':self.assertEqual(visitor.diagnosis,condition)
                snapshot=visitor.symptoms.copy()
                for feature in snapshot:
                    session.medical.observe(visitor,feature)
                    session.medical.observe(visitor,feature)
                self.assertEqual(visitor.symptoms,snapshot)
                if condition=='saudavel':
                    benign.update(k for k,v in snapshot.items() if v)
                    self.assertFalse(snapshot['olhos_alterados'])
                    self.assertFalse(snapshot['veias_escurecidas'])
        self.assertTrue({'palidez_anormal','tremores_involuntarios','manchas_maos'}<=benign)

    def test_assets_dialogue_menu_and_frames(self):
        session=VisitorSession(random.Random(5))
        visitor=session.start_test('antonio')
        assets=load_assets(visitor.definition)
        self.assertEqual(visitor.definition['asset_root'],'personagens/visitantes/antonio')
        for direction,frames in assets.walk.items():
            self.assertEqual(len(frames),2)
            for frame in [assets.sprites[direction],*frames]:
                self.assertEqual(frame.get_bounding_rect(min_alpha=1).bottom,94)
            if direction=='esquerda':
                for left,right in zip(frames,assets.walk['direita']):
                    mirrored=pygame.transform.flip(right,True,False)
                    self.assertEqual(pygame.image.tobytes(left.subsurface(left.get_bounding_rect(min_alpha=1)),'RGBA'),pygame.image.tobytes(mirrored.subsurface(mirrored.get_bounding_rect(min_alpha=1)),'RGBA'))
        dialogue=Dialogue(visitor,session)
        self.assertIn('Antônio',dialogue.intro())
        for index in range(len(dialogue.data['questions'])):
            self.assertTrue(dialogue.answer(index))
        menu=GameMenu(session.visitors)
        menu.choose('test');menu.choose('antonio')
        self.assertIn('condition',dict(menu.entries()))
        menu.choose('condition')
        self.assertEqual(menu.choose('start'),('test','antonio','saudavel'))

    def test_real_door_accept_reject_render_movement_and_resources(self):
        for decision in ('acolhido','rejeitado'):
            game=House();session=game.visitor_session
            visitor=session.start_test('antonio','infectado',random.Random(9))
            ui=game.peephole.visitor_ui
            self.assertIs(ui.visitor,visitor)
            snapshot=visitor.symptoms.copy()
            for feature in visitor.symptoms:
                ui.feature=feature
                for altered in (False,True):
                    visitor.symptoms[feature]=altered
                    self.assertIs(ui.examination_image(),game.visitor_assets['antonio'].investigation[feature]['alterado' if altered else 'normal'])
            visitor.symptoms=snapshot
            ui.draw(pygame.display.get_surface())
            before=(session.survival.food,session.survival.water)
            self.assertTrue(game.decide_visitor(visitor,decision))
            self.assertFalse(game.decide_visitor(visitor,decision))
            if decision=='rejeitado':
                self.assertNotIn('antonio',game.residents)
                self.assertEqual(before,(session.survival.food,session.survival.water))
                continue
            self.assertEqual((session.survival.food,session.survival.water),(before[0]+visitor.food,before[1]+visitor.water))
            self.assertIn('antonio',session.living_ids)
            self.assertIn('antonio',session.survival.people)
            game.change_room('sala');game.dialog=''
            actor=game.residents['antonio'];actor.rng=random.Random(6)
            start=actor.feet.copy();moved=False
            for _ in range(600):
                game.update((0,0),1/60)
                moved |= actor.feet.distance_to(start)>1
                self.assertTrue(game.scene.collisions.allows(actor.feet))
                self.assertFalse(feet_rect(actor.feet).colliderect(feet_rect(game.player.feet)))
            self.assertTrue(moved)
            actor.rest()
            self.assertIs(actor.image(game.visitor_assets['antonio']),game.visitor_assets['antonio'].sprites[actor.direction])
            game.draw(pygame.display.get_surface())
            self.assertEqual(snapshot,visitor.symptoms)
