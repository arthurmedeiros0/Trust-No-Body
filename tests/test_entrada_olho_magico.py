"""Entrada/sala e cena independente de observacao da rua."""
import copy
import tempfile
import unittest
from unittest.mock import patch
import pygame
from casa.config import ROOT,ROOMS,PLAYER_SIZE
from support import exploration_house as House
from casa.collision_data import save,load
from casa.interactions import nearest

class EntranceTests(unittest.TestCase):
    def setUp(self):self.game=House()

    def key(self,key):self.game.handle_event(pygame.event.Event(pygame.KEYDOWN,key=key))

    def finish(self):
        self.game.update((1,0),.23);self.game.update((1,0),.23)
        self.assertFalse(self.game.fade.active)

    def open_view(self):
        game=self.game;game.change_room('entrada')
        game.player.feet=game.scene.point((768,445))
        self.assertTrue(game.scene.collisions.allows(game.player.feet))
        self.key(pygame.K_e);self.assertTrue(game.fade.active)
        self.finish();self.assertTrue(game.observing)

    def test_sala_entrada_return_and_lower_door(self):
        game=self.game;game.change_room('sala')
        game.player.feet=game.scene.point((826,274))
        self.key(pygame.K_e);self.assertEqual(game.room,'sala');self.finish()
        self.assertEqual(game.room,'entrada')
        self.assertEqual(game.player.direction,'costas')
        self.assertLess(game.scene.source_point(game.player.feet).distance_to((768,870)),.01)
        self.assertTrue(game.scene.collisions.allows(game.player.feet))
        self.assertEqual(game.player.image.get_size(),PLAYER_SIZE)
        self.key(pygame.K_e);self.finish()
        self.assertEqual(game.room,'sala')
        self.assertLess(game.scene.source_point(game.player.feet).distance_to((826,274)),.01)
        self.assertEqual(game.player.direction,'frente')
        game.player.feet=game.scene.spawn.copy();self.key(pygame.K_e);self.finish()
        self.assertEqual(game.room,'corredor')

    def test_observe_freezes_position_hides_player_and_esc_returns(self):
        self.open_view();game=self.game
        before=game.player.feet.copy();direction=game.player.direction
        game.update((1,-1),2)
        self.assertEqual(game.player.feet,before)
        self.assertFalse(game.player.moving)
        with patch.object(game.player,'draw') as draw:
            game.draw(pygame.display.get_surface());draw.assert_not_called()
        self.assertTrue(game.captures_escape)
        self.key(pygame.K_ESCAPE);self.finish()
        self.assertFalse(game.observing)
        self.assertEqual(game.room,'entrada');self.assertEqual(game.player.feet,before)
        self.assertEqual(game.player.direction,direction)

    def test_buttons_and_day_night_in_view(self):
        # A interface antiga de observar continua disponivel sem visitante.
        self.game.visitor_session.visitors['ricardo'].state='rejeitado'
        self.open_view();game=self.game;before=game.player.feet.copy();collisions=game.scene.collisions
        game.handle_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN,button=1,pos=game.peephole.observe_button.center))
        self.assertTrue(game.peephole.observing)
        self.assertNotEqual(pygame.image.tobytes(game.peephole.images['dia'],'RGB'),pygame.image.tobytes(game.peephole.images['noite'],'RGB'))
        for period in ('noite','dia'):
            self.key(pygame.K_F6);self.assertEqual(game.period,period)
            game.draw(pygame.display.get_surface())
            self.assertEqual(game.player.feet,before);self.assertIs(game.scene.collisions,collisions)
        game.handle_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN,button=1,pos=game.peephole.back_button.center))
        self.finish();self.assertFalse(game.observing);self.assertEqual(game.player.feet,before)

    def test_entrada_closed_door_obstacles_period_and_editor(self):
        game=self.game;game.change_room('entrada');scene=game.scene
        for obj in scene.collision_data['obstacles']:
            rect=pygame.Rect(scene.transform_rect(obj['rect']))
            self.assertFalse(scene.collisions.allows(pygame.Vector2(rect.center)),obj['id'])
        game.player.feet=scene.point((768,470))
        game.update((0,-1),1)
        self.assertTrue(scene.collisions.allows(game.player.feet))
        self.assertGreaterEqual(scene.source_point(game.player.feet).y,365)
        self.assertEqual(nearest(scene.interactions,game.player.feet).action,'peephole')
        before=game.player.feet.copy();collisions=scene.collisions
        self.key(pygame.K_F6);self.assertEqual(game.player.feet,before);self.assertIs(scene.collisions,collisions)
        developer=House(development=True);developer.change_room('entrada')
        developer.handle_event(pygame.event.Event(pygame.KEYDOWN,key=pygame.K_F4))
        self.assertTrue(developer.editor.active)
        developer.draw(pygame.display.get_surface())
        with tempfile.TemporaryDirectory() as directory:
            save(scene.collision_data,directory)
            self.assertEqual(load('entrada',scene.source_size,directory),scene.collision_data)

    def test_observation_layer_order_and_original_assets(self):
        game=self.game;view=game.peephole
        self.assertFalse(view.visitor_layer)
        calls=[]
        with patch.object(view,'draw_visitors',side_effect=lambda screen:calls.append('visitor')):
            class SurfaceRecorder:
                def fill(self,*args):calls.append('background_clear')
                def blit(self,surface,*args):calls.append('background' if surface is view.images['dia'] else 'ui_text')
            # draw.rect requer Surface real; apenas captura ordem da camada.
            with patch('casa.peephole.pygame.draw.rect',side_effect=lambda *args,**kwargs:calls.append('ui')):
                view.draw(SurfaceRecorder(),'dia')
        self.assertLess(calls.index('background'),calls.index('visitor'))
        self.assertLess(calls.index('visitor'),calls.index('ui'))
        for folder in ('entrada','olho_magico'):
            originals=[p for p in (ROOT/'cenarios'/folder).glob('*.png') if p.name not in ('dia.png','noite.png')]
            self.assertEqual(len(originals),2)
            for period in ('dia','noite'):
                alias=(ROOT/'cenarios'/folder/(period+'.png')).read_bytes()
                self.assertTrue(any(p.read_bytes()==alias for p in originals))
