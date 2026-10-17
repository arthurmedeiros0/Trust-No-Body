"""Regressoes de sala inferior, hitbox, banheiro e sombra."""
import unittest
import pygame
from support import exploration_house as House
from casa.collisions import feet_rect
from casa.config import ROOMS,PLAYER_HITBOX,SHADOW_SIZE,SHADOW_OPACITY,SHADOW_OFFSET_Y

class FeetAndRoomTests(unittest.TestCase):
    def setUp(self):
        self.game=House()

    def test_feet_hitbox_is_frame_independent(self):
        player=self.game.player
        player.feet.update(650,400)
        expected=feet_rect(player.feet)
        self.assertEqual(expected.size,PLAYER_HITBOX)
        self.assertEqual(expected.midbottom,(650,400))
        for direction in player.cycles:
            player.direction=direction;player.moving=True
            for frame in range(6):
                player.elapsed=frame*.14
                self.assertEqual(feet_rect(player.feet),expected)
        player.feet+=pygame.Vector2(21,17)
        self.assertEqual(feet_rect(player.feet),expected.move(21,17))
        self.assertLess(expected.height,player.image.get_height()/4)

    def test_living_room_lower_entry_and_upper_passage(self):
        game=self.game
        hall=game.scene
        game.player.feet=hall.point((294,235))
        game.interact();game.update((0,0),.23);game.update((0,0),.23)
        self.assertEqual(game.room,'sala')
        scene=game.scene
        self.assertLess(scene.source_point(game.player.feet).distance_to((343,636)),.01)
        self.assertTrue(scene.collisions.allows(game.player.feet))
        game.interact();game.update((0,0),.23);game.update((0,0),.23)
        self.assertEqual(game.room,'corredor')
        game.change_room('sala')
        game.player.feet=scene.point(pygame.Vector2(ROOMS['sala']['upper_door'])+pygame.Vector2(0,30))
        self.assertTrue(scene.collisions.allows(game.player.feet))
        game.interact()
        self.assertTrue(game.fade.active)
        game.update((0,0),.23);game.update((0,0),.23)
        self.assertEqual(game.room,'entrada')
        self.assertEqual(len(scene.interactions),2)

    def test_walk_between_sofa_and_table_both_directions(self):
        game=self.game;game.change_room('sala');scene=game.scene
        # Percorre a lacuna real entre as bases dos moveis; nao so testa um ponto.
        for start,direction in [((335,425),(1,0)),((620,425),(-1,0))]:
            game.player.feet=scene.point(start)
            self.assertTrue(scene.collisions.allows(game.player.feet))
            for _ in range(60):game.update(direction,1/60)
            self.assertTrue(scene.collisions.allows(game.player.feet))
            source=scene.source_point(game.player.feet)
            self.assertAlmostEqual(source.y,425,places=3)
            if direction[0]>0:self.assertGreater(source.x,620)
            else:self.assertLess(source.x,335)
        for label in ('sofa','mesa_centro','poltrona','mesinha_lateral'):
            rect=pygame.Rect(scene.transform_rect(next(obj['rect'] for obj in scene.collision_data['obstacles'] if obj['id']==label)))
            self.assertFalse(scene.collisions.allows(pygame.Vector2(rect.center)))

    def test_bathroom_obstacles_and_lower_door(self):
        game=self.game;game.change_room('banheiro');scene=game.scene
        for period in ('dia','noite'):
            game.period=period
            for obj in scene.collision_data['obstacles']:
                label,rect=obj['id'],obj['rect']
                block=pygame.Rect(scene.transform_rect(rect))
                self.assertFalse(scene.collisions.allows(pygame.Vector2(block.center)),label)
            for point in [(300,320),(380,390),(374,478),(374,516)]:
                self.assertTrue(scene.collisions.allows(scene.point(point)),point)
            for point in [(290,510),(450,510),(175,400),(580,400),(374,550)]:
                self.assertFalse(scene.collisions.allows(scene.point(point)),point)
            # Movimento efetivo contra bases de cada categoria de movel.
            for label,start,direction in [
                ('pia_armario',(280,300),(0,-1)),('vaso',(400,300),(0,-1)),
                ('lixeira',(447,278),(0,-1)),('box',(445,330),(1,0)),
                ('estante',(260,320),(-1,0)),('cesto_esquerdo',(260,400),(-1,0)),
                ('cesto_direito',(470,400),(1,0))]:
                game.player.feet=scene.point(start)
                self.assertTrue(scene.collisions.allows(game.player.feet),label)
                before=game.player.feet.copy()
                game.update(direction,.6)
                self.assertTrue(scene.collisions.allows(game.player.feet),label)
                self.assertLess(game.player.feet.distance_to(before),132-5,label)
        game.player.feet=scene.spawn.copy();game.interact()
        game.update((0,0),.23);game.update((0,0),.23)
        self.assertEqual(game.room,'corredor')

    def test_shadow_alpha_position_and_draw_order(self):
        player=self.game.player;shadow=player.shadow
        self.assertEqual(shadow.surface.get_size(),SHADOW_SIZE)
        self.assertEqual(shadow.surface.get_at((0,0)).a,0)
        self.assertEqual(shadow.surface.get_at((SHADOW_SIZE[0]//2,SHADOW_SIZE[1]//2)).a,SHADOW_OPACITY)
        self.assertGreater(SHADOW_OPACITY,0);self.assertLess(SHADOW_OPACITY,255)
        class Recorder:
            def __init__(self):self.calls=[]
            def blit(self,surface,position):self.calls.append((surface,position))
        for room in self.game.scenes:
            self.game.change_room(room)
            camera=self.game.scene.camera_for(player.feet)
            rect=shadow.rect(player.feet,camera)
            self.assertEqual(rect.center,(round(player.feet.x-camera.x),round(player.feet.y-camera.y+SHADOW_OFFSET_Y)))
            self.assertEqual(rect.size,SHADOW_SIZE)
            before=feet_rect(player.feet)
            recorder=Recorder();player.draw(recorder,camera)
            self.assertIs(recorder.calls[0][0],shadow.surface)
            self.assertIs(recorder.calls[1][0],player.image)
            self.assertEqual(feet_rect(player.feet),before)
        rect=shadow.rect(player.feet)
        self.assertEqual(shadow.rect(player.feet+pygame.Vector2(30,20)),rect.move(30,20))
