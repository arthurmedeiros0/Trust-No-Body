"""Regressoes dos cantos, moveis, camera e novos cenarios."""
import hashlib
import json
import unittest
import pygame
from casa.config import ROOT,ROOMS,SCENE_SCALE,FRAME_TIME,PLAYER_SIZE
from support import exploration_house as House
from casa.interactions import nearest

class CorrectionTests(unittest.TestCase):
    def setUp(self):
        self.game=House()

    def test_lateral_idle_step_cycle_and_stop(self):
        player=self.game.player
        for direction,vector in [('esquerda',(-1,0)),('direita',(1,0))]:
            player.feet=self.game.scene.point((650,246))
            player.update(vector,.01,self.game.scene.collisions)
            expected=[player.walk[direction][0],player.idle[direction],
                      player.walk[direction][1],player.idle[direction],
                      player.walk[direction][2],player.idle[direction]]
            for frame,image in enumerate(expected*2):
                player.elapsed=frame*FRAME_TIME+.001
                self.assertIs(player.image,image)
            player.update((0,0),.01,self.game.scene.collisions)
            self.assertIs(player.image,player.idle[direction])
            self.assertEqual(player.elapsed,0)
            player.update(vector,.01,self.game.scene.collisions)
            self.assertIs(player.image,expected[0])
        # A mudanca de direcao reinicia a animacao sem reaproveitar fase anterior.
        player.elapsed=.57
        player.update((-1,0),.01,self.game.scene.collisions)
        self.assertIs(player.image,player.walk['esquerda'][0])

    def test_corridor_lower_corners_in_both_periods(self):
        game=self.game;scene=game.scene
        for period in ('dia','noite'):
            game.period=period
            for x in (145,1580):
                self.assertFalse(scene.collisions.allows(scene.point((x,270))))
                game.player.feet=scene.point((x,240))
                self.assertTrue(scene.collisions.allows(game.player.feet))
                game.update((0,1),1)
                self.assertTrue(scene.collisions.allows(game.player.feet))
                source=scene.source_point(game.player.feet)
                self.assertLessEqual(source.y,252)  # tolerancia de um pixel apos rasterizacao
            # Corredor central continua livre; nao bloquear a faixa inteira.
            self.assertTrue(scene.collisions.allows(scene.point((650,266))))
            for door in scene.interactions:
                point=scene.point((scene.source_point(door.point).x,235))
                self.assertTrue(scene.collisions.allows(point))
                self.assertIs(nearest(scene.interactions,point),door)

    def test_trash_and_chair_block_movement_with_free_sidewalk(self):
        for room,label,start,side in [('banheiro','lixeira',(447,278),(415,278)),
                                       ('quarto','cadeira',(599,430),(560,380))]:
            game=self.game;game.change_room(room);scene=game.scene
            block=pygame.Rect(scene.transform_rect(next(obj['rect'] for obj in scene.collision_data['obstacles'] if obj['id']==label)))
            self.assertFalse(scene.collisions.allows(pygame.Vector2(block.center)))
            self.assertTrue(scene.collisions.allows(scene.point(side)))
            game.player.feet=scene.point(start)
            self.assertTrue(scene.collisions.allows(game.player.feet))
            game.update((0,-1),.5)
            self.assertTrue(scene.collisions.allows(game.player.feet))
            self.assertGreaterEqual(game.player.feet.y-10,block.bottom-1)
            self.assertLess(game.player.feet.y-10,block.bottom+5)

    def test_scale_camera_mapping_and_fixed_player(self):
        game=self.game
        for name,scene in game.scenes.items():
            game.change_room(name)
            self.assertEqual(game.player.image.get_size(),PLAYER_SIZE)
            self.assertAlmostEqual(scene.scale,SCENE_SCALE*ROOMS[name]['art_scale'])
            expected=ROOMS[name]['source_size']
            self.assertEqual(scene.source_size,expected)
            self.assertLess(abs(scene.rect.width/expected[0]-scene.rect.height/expected[1]),.002)
            point=pygame.Vector2(ROOMS[name]['spawn'])
            self.assertLess(scene.source_point(scene.point(point)).distance_to(point),.00001)
            self.assertLessEqual(scene.rect.height,scene.viewport.height)
            for period in ('dia','noite'):
                before=game.player.feet.copy()
                game.period=period
                game.draw(pygame.display.get_surface())
                self.assertEqual(game.player.feet,before)
        scene=game.scenes['corredor']
        self.assertGreater(scene.rect.width,scene.viewport.width)
        cameras=[]
        for x in (220,1490):
            feet=scene.point((x,240));camera=scene.camera_for(feet)
            shown=feet-camera
            self.assertTrue(scene.viewport.collidepoint(shown))
            self.assertLessEqual(scene.rect.left-camera.x,scene.viewport.left)
            self.assertGreaterEqual(scene.rect.right-camera.x,scene.viewport.right)
            # O mesmo offset e aplicado a piso, arte, objetos e jogador.
            cameras.append(camera.x)
        self.assertLess(cameras[0],cameras[1])
        debug=game.debug
        game.handle_event(pygame.event.Event(pygame.KEYDOWN,key=pygame.K_F3))
        self.assertNotEqual(game.debug,debug)
        game.handle_event(pygame.event.Event(pygame.KEYDOWN,key=pygame.K_F3))
        self.assertEqual(game.debug,debug)

    def test_new_living_room_and_resource_integrity(self):
        scene=self.game.scenes['sala']
        self.assertEqual(scene.source_size,(1053,724))
        self.assertIn('corrigida',ROOMS['sala']['images']['dia'])
        self.assertNotEqual(pygame.image.tobytes(scene.images['dia'],'RGB'),
                            pygame.image.tobytes(scene.images['noite'],'RGB'))
        for rect in (obj['rect'] for obj in scene.collision_data['obstacles']):
            block=pygame.Rect(scene.transform_rect(rect))
            self.assertFalse(scene.collisions.allows(pygame.Vector2(block.center)))
        self.assertEqual(len(scene.interactions),2)
        before=json.loads((ROOT/'docs/hashes_antes_correcoes.json').read_text(encoding='utf-8'))
        for path,digest in before.items():
            if path.replace('\\','/').startswith('personagens/protagonista/processados/'):
                # Design anterior preservado no backup; novo design tem manifesto proprio.
                archived=ROOT/'backups/sheets_20261017_150406_128619'/path
                self.assertEqual(hashlib.sha256(archived.read_bytes()).hexdigest(),digest,path)
                continue
            self.assertEqual(hashlib.sha256((ROOT/path).read_bytes()).hexdigest(),digest,path)
