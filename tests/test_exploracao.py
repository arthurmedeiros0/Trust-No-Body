"""Verifica exploracao real, acessibilidade e preservacao dos recursos."""
import hashlib
import json
import unittest
from collections import deque
from PIL import Image,ImageChops,ImageOps
import pygame
from casa.config import ROOT,ROOMS,DOOR_X,FRAME_TIME,SPEED
from support import exploration_house as House
from casa.interactions import nearest

class ExplorationTests(unittest.TestCase):
    def setUp(self):
        self.game=House()

    def reachable(self, scene):
        # Busca no piso real, usando o mesmo teste de colisao do jogador.
        step=6
        origin=scene.spawn
        queue=deque([(0,0)]);seen={(0,0)};points=[]
        while queue:
            x,y=queue.popleft();point=origin+pygame.Vector2(x*step,y*step)
            points.append(point)
            for nx,ny in ((x-1,y),(x+1,y),(x,y-1),(x,y+1)):
                if (nx,ny) not in seen and scene.collisions.allows(origin+pygame.Vector2(nx*step,ny*step)):
                    seen.add((nx,ny));queue.append((nx,ny))
        return points

    def test_assets_and_originals(self):
        base=ROOT/'personagens/protagonista'
        self.assertEqual(len(list((base/'originais').glob('*.png'))),13)
        self.assertEqual(list(base.glob('*.png')),[])
        for row in json.loads((base/'processados/manifesto.json').read_text(encoding='utf-8')):
            self.assertEqual(hashlib.sha256((base/'originais'/row['original']).read_bytes()).hexdigest(),row['sha256'])
        sprites=list((base/'processados/parado').glob('*.png'))+list((base/'processados/andando').glob('*/*.png'))
        self.assertEqual(len(sprites),16)
        for path in sprites:
            im=Image.open(path)
            self.assertEqual(im.size,(64,96));self.assertEqual(im.mode,'RGBA')
            self.assertEqual(im.getbbox()[3],94)
            self.assertEqual(im.getchannel('A').getextrema()[0],0)
            self.assertGreaterEqual(im.getchannel('A').getextrema()[1],250)
        sheet=json.loads((ROOT/'dados/sheets/protagonista.json').read_text(encoding='utf-8'))
        for asset in sheet['assets']:
            self.assertEqual(hashlib.sha256((ROOT/asset['destino']).read_bytes()).hexdigest(),asset['sha256'])

    def test_all_interactions_reachable_from_spawn(self):
        for name,scene in self.game.scenes.items():
            self.assertTrue(scene.collisions.allows(scene.spawn),name)
            points=self.reachable(scene)
            for item in scene.interactions:
                self.assertTrue(any(nearest(scene.interactions,p) is item for p in points),(name,item.label))

    def test_doors_return_fade_and_period(self):
        game=self.game
        for name,x in DOOR_X.items():
            game.player.feet=game.scene.point((x,235))
            self.assertTrue(game.scene.collisions.allows(game.player.feet))
            game.handle_event(pygame.event.Event(pygame.KEYDOWN,key=pygame.K_e))
            self.assertTrue(game.fade.active)
            self.assertEqual(game.room,'corredor')
            game.update((1,0),.23)
            self.assertEqual(game.room,name)
            self.assertTrue(game.fade.active)
            game.update((0,0),.23)
            self.assertFalse(game.fade.active)
            before=game.player.feet.copy()
            game.handle_event(pygame.event.Event(pygame.KEYDOWN,key=pygame.K_F6))
            self.assertEqual(game.period,'noite')
            self.assertEqual(game.player.feet,before)
            game.handle_event(pygame.event.Event(pygame.KEYDOWN,key=pygame.K_F6))
            self.assertEqual(game.period,'dia')
            game.handle_event(pygame.event.Event(pygame.KEYDOWN,key=pygame.K_e))
            game.update((0,0),.23);game.update((0,0),.23)
            self.assertEqual(game.room,'corredor')
            self.assertLess(game.player.feet.distance_to(game.scene.point((x,235))),.01)

    def test_collision_and_movement(self):
        game=self.game;player=game.player
        for direction,vector in [('frente',(0,1)),('costas',(0,-1)),('direita',(1,0)),('esquerda',(-1,0))]:
            player.feet=game.scene.point((650,246))
            player.update(vector,.01,game.scene.collisions)
            self.assertEqual(player.direction,direction)
            for frame in range(len(player.cycles[direction])):
                player.elapsed=frame*FRAME_TIME+.001
                self.assertIs(player.image,player.cycles[direction][frame])
            player.update((0,0),.01,game.scene.collisions)
            self.assertIs(player.image,player.idle[direction])
        player.feet=game.scene.point((650,246));before=player.feet.copy()
        player.update((1,1),.02,game.scene.collisions)
        self.assertAlmostEqual(player.feet.distance_to(before),SPEED*.02,places=5)
        # Console: nao atravessa nem com um dt muito maior que um frame.
        player.feet=game.scene.point((850,248))
        player.update((0,-1),2,game.scene.collisions)
        self.assertTrue(game.scene.collisions.allows(player.feet))
        self.assertGreaterEqual(player.feet.y-10,game.scene.collisions.blocks[1].bottom-1)
        player.update((-1,0),20,game.scene.collisions)
        self.assertTrue(game.scene.collisions.allows(player.feet))
        self.assertGreaterEqual(player.feet.x-10,game.scene.collisions.floor.left-1)
        # Deslocamento equivalente em diferentes taxas de atualizacao.
        positions=[]
        for fps in (30,60,120):
            player.feet=game.scene.point((650,246))
            for _ in range(fps//5): player.update((1,0),1/fps,game.scene.collisions)
            positions.append(player.feet.copy())
        self.assertLess(positions[0].distance_to(positions[-1]),.01)

    def test_messages_sleep_and_render(self):
        game=self.game
        for room in ('quarto','cozinha'):
            game.change_room(room)
            points=self.reachable(game.scene)
            for item in game.scene.interactions:
                if item.action not in ('message','sleep'): continue
                game.player.feet=next(p for p in points if nearest(game.scene.interactions,p) is item)
                game.interact();self.assertTrue(game.dialog)
                if item.action=='sleep':
                    self.assertFalse(game.sleep_option) # Ricardo ainda aguarda na porta.
                    game.handle_event(pygame.event.Event(pygame.KEYDOWN,key=pygame.K_s))
                    self.assertEqual(game.days.day,1);self.assertIn('visitante',game.dialog)
                game.handle_event(pygame.event.Event(pygame.KEYDOWN,key=pygame.K_RETURN))
                self.assertFalse(game.dialog)
        for room in ROOMS:
            game.change_room(room)
            for period in ('dia','noite'):
                game.period=period;game.debug=True
                game.draw(pygame.display.get_surface())
        self.assertNotEqual(ROOMS['sala']['images']['dia'],ROOMS['sala']['images']['noite'])
