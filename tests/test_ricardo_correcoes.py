"""Recortes, paineis padronizados e colisao mutua do morador."""
import copy
import random
import unittest
from PIL import Image,ImageDraw
import pygame
from support import exploration_house as House
from casa.collisions import feet_rect
from casa.resident import ActorCollisions,Resident
from casa.visitor_image_processing import remove_white,EXAM_SIZE,EXAM_BACKGROUND

class RicardoCorrectionTests(unittest.TestCase):
    def setUp(self):
        self.game=House();self.visitor=self.game.visitor_session.visitors['ricardo']

    def accept(self):
        self.assertTrue(self.game.decide_visitor(self.visitor,'acolhido'))
        self.game.change_room('sala')
        self.actor=self.game.residents['ricardo']
        self.actor.rng=random.Random(73)
        return self.actor

    def test_investigation_twelve_matching_dark_panels(self):
        assets=self.game.visitor_assets['ricardo']
        self.assertEqual(len(assets.investigation),6)
        for variants in assets.investigation.values():
            self.assertEqual(set(variants),{'normal','alterado'})
            for image in variants.values():
                self.assertEqual(image.get_size(),EXAM_SIZE)
                for point in ((0,0),(899,0),(0,459),(899,459),(10,10)):
                    self.assertEqual(tuple(image.get_at(point)),EXAM_BACKGROUND)
        hands=assets.investigation['manchas_maos']['normal']
        # Area acima dos dedos: fundo uniforme, sem o branco original.
        self.assertEqual(tuple(hands.get_at((250,25))),EXAM_BACKGROUND)
        self.assertNotEqual(pygame.image.tobytes(hands,'RGBA'),pygame.image.tobytes(assets.investigation['manchas_maos']['alterado'],'RGBA'))

    def test_white_matte_is_removed_without_erasing_internal_coat(self):
        image=Image.new('RGBA',(40,40),'white');draw=ImageDraw.Draw(image)
        draw.rectangle((8,8,31,31),fill=(210,210,210))  # Borda contaminada pelo branco.
        draw.rectangle((10,10,29,29),fill='black')
        draw.rectangle((15,15,24,24),fill='white')  # Jaleco cercado pelo contorno.
        result=remove_white(image)
        self.assertEqual(result.size,(24,24))
        self.assertLess(result.getpixel((0,0))[3],100)
        self.assertLess(max(result.getpixel((0,0))[:3]),30)
        self.assertEqual(result.getpixel((10,10)),(255,255,255,255))
        definition=self.visitor.definition
        portrait=self.game.visitor_assets['ricardo'].portrait
        self.assertEqual(portrait.get_height(),definition['portrait_height'])
        self.assertEqual(definition['portrait_anchor'],[640,625])

    def test_safe_spawn_distant_from_player_and_doors(self):
        actor=self.accept();scene=self.game.scene
        self.assertTrue(scene.collisions.allows(actor.feet))
        self.assertFalse(feet_rect(actor.feet).colliderect(feet_rect(self.game.player.feet)))
        self.assertGreater(actor.feet.distance_to(self.game.player.feet),150)
        self.assertGreater(actor.feet.distance_to(scene.spawn),actor.radius+35)
        self.assertGreater(actor.feet.distance_to(scene.point((826,274))),actor.radius+35)
        self.assertIs(self.game.resident_positions['ricardo'],actor.feet)

    def test_npc_moves_slowly_stays_in_room_and_never_crosses_furniture(self):
        actor=self.accept();scene=self.game.scene
        start=actor.feet.copy();positions=set();directions=set();before=copy.deepcopy(self.visitor.symptoms)
        for _ in range(2400):
            previous=actor.feet.copy();self.game.update((0,0),1/30)
            self.assertLessEqual(actor.feet.distance_to(previous),actor.speed/30+.001)
            self.assertTrue(scene.collisions.allows(actor.feet))
            self.assertFalse(feet_rect(actor.feet).colliderect(feet_rect(self.game.player.feet)))
            self.assertLessEqual(actor.feet.distance_to(actor.origin),actor.radius+.001)
            positions.add((round(actor.feet.x),round(actor.feet.y)));directions.add(actor.direction)
        self.assertGreater(len(positions),10);self.assertGreater(len(directions),1)
        self.assertEqual(actor.room,'sala');self.assertEqual(self.game.room,'sala')
        self.assertEqual(self.visitor.symptoms,before)
        self.assertEqual(self.visitor.diagnosis,'diagnostico_pendente')

    def test_player_cannot_walk_through_waiting_npc(self):
        actor=self.accept();actor.remaining=100
        self.game.player.feet=actor.feet-pygame.Vector2(55,0)
        self.assertTrue(self.game.scene.collisions.allows(self.game.player.feet))
        for _ in range(90):
            self.game.update((1,0),1/60)
            self.assertFalse(feet_rect(actor.feet).colliderect(feet_rect(self.game.player.feet)))
        self.assertLessEqual(self.game.player.feet.x,actor.feet.x-19)
        self.assertGreater(self.game.player.feet.x,actor.feet.x-25)

    def test_acceptance_uses_alternative_when_player_occupies_preferred_point(self):
        self.game.change_room('sala')
        preferred=self.game.scene.point(self.visitor.definition['room_position'])
        self.game.player.feet=preferred.copy()
        actor=self.accept()
        self.assertNotEqual(actor.feet,preferred)
        self.assertTrue(self.game.scene.collisions.allows(actor.feet))
        self.assertFalse(feet_rect(actor.feet).colliderect(feet_rect(self.game.player.feet).inflate(24,24)))

    def test_npc_cannot_walk_through_player(self):
        actor=self.accept();self.game.player.feet=actor.feet+pygame.Vector2(40,0)
        self.assertTrue(self.game.scene.collisions.allows(self.game.player.feet))
        start=actor.feet.copy();actor.walking=True;actor.remaining=1.4
        actor.direction='direita';actor.velocity.update(actor.speed,0)
        for _ in range(70):
            self.game.update((0,0),1/60)
            self.assertFalse(feet_rect(actor.feet).colliderect(feet_rect(self.game.player.feet)))
        self.assertLessEqual(actor.feet.x,start.x+21)
        self.assertFalse(actor.walking)

    def test_large_npc_step_cannot_tunnel_and_pause_interfaces(self):
        actor=self.accept();scene=self.game.scene
        self.game.player.feet=scene.spawn.copy()
        actor.walking=True;actor.direction='costas';actor.velocity.update(0,-actor.speed);actor.remaining=10
        for _ in range(80):
            self.game.update((0,0),.25)
            self.assertTrue(scene.collisions.allows(actor.feet))
        position=actor.feet.copy();timer=actor.remaining
        self.game.observing=True;self.game.update((0,0),10)
        self.assertEqual(actor.feet,position);self.assertEqual(actor.remaining,timer)
        self.game.observing=False;self.game.change_room('quarto');self.game.update((0,0),10)
        self.assertEqual(actor.feet,position)

    def test_rejected_visitor_has_no_actor_and_other_rooms_are_unaffected(self):
        self.assertTrue(self.game.decide_visitor(self.visitor,'rejeitado'))
        self.assertFalse(self.game.residents)
        for room,scene in self.game.scenes.items():
            self.game.change_room(room)
            self.assertTrue(scene.collisions.allows(self.game.player.feet))
            self.game.update((0,0),.1)
            self.assertFalse(self.game.residents)
