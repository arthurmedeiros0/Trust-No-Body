"""Escala uniforme em memoria, apoio dos pes e preservacao da simulacao."""
import unittest
import pygame
from support import exploration_house as House
from casa.collisions import feet_rect
from casa.resident_render import resident_frame,RICARDO_VISUAL_SCALE


class ResidentScaleTests(unittest.TestCase):
    def setUp(self):
        self.game=House();self.assets=self.game.visitor_assets['ricardo']

    def test_every_idle_and_step_same_scale_and_exact_ground_anchor(self):
        self.assertEqual(RICARDO_VISUAL_SCALE,1.08)
        for direction in self.assets.sprites:
            for source in [self.assets.sprites[direction],*self.assets.walk[direction]]:
                original=pygame.image.tobytes(source,'RGBA')
                image,anchor=resident_frame('ricardo',source)
                self.assertEqual(image.get_size(),(69,104))
                self.assertEqual(anchor,(34,102))
                self.assertEqual(image.get_bounding_rect().bottom,anchor[1])
                self.assertEqual(pygame.image.tobytes(image,'RGBA'),pygame.image.tobytes(pygame.transform.scale(source,(69,104)),'RGBA'))
                self.assertEqual(pygame.image.tobytes(source,'RGBA'),original)
                self.assertIs(resident_frame('ricardo',source)[0],image)
        for source in self.game.player.idle.values():
            self.assertIs(resident_frame('outro',source)[0],source)

    def test_actual_draw_keeps_feet_collision_shadow_cycle_and_portrait(self):
        game=self.game;game.change_room('sala')
        game.decide_visitor(game.visitor_session.visitors['ricardo'],'acolhido')
        actor=game.residents['ricardo'];camera=game.scene.camera_for(game.player.feet)
        position=actor.feet.copy();hitbox=feet_rect(position)
        shadow=game.visitor_shadow;shadow_rect=shadow.rect(position,camera)
        portrait=self.assets.portrait
        class Recorder:
            def __init__(self):self.calls=[]
            def blit(self,surface,point):self.calls.append((surface,point))
        for direction,cycle in self.assets.cycles.items():
            actor.direction=direction
            for index,expected in enumerate(cycle):
                actor.walking=actor.moving=True;actor.animation_elapsed=index*actor.frame_seconds+.001
                self.assertIs(actor.image(self.assets),expected)
                recorder=Recorder()
                game.draw_residents(recorder,camera,foreground=position.y>game.player.feet.y)
                image,anchor=resident_frame('ricardo',expected)
                self.assertIs(recorder.calls[0][0],shadow.surface)
                self.assertIs(recorder.calls[1][0],image)
                self.assertEqual(recorder.calls[1][1],(round(position.x-camera.x)-anchor[0],round(position.y-camera.y)-anchor[1]))
                self.assertEqual(actor.feet,position);self.assertEqual(feet_rect(actor.feet),hitbox)
                self.assertEqual(shadow.rect(actor.feet,camera),shadow_rect)
            actor.rest()
            self.assertIs(actor.image(self.assets),self.assets.sprites[direction])
        self.assertIs(self.assets.portrait,portrait)
