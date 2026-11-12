"""Limites nas coordenadas das artes e acessibilidade das interações."""
import os
os.environ.setdefault('SDL_VIDEODRIVER','dummy')
os.environ.setdefault('SDL_AUDIODRIVER','dummy')

from collections import deque
import unittest
import pygame

from casa.config import DOOR_X
from casa.game import House
from casa.interactions import nearest
from casa.resident import free_spawn


class RoomHitboxTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        pygame.display.set_mode((1280,720))
        cls.game=House()
        cls.game.dialog=''

    def scene(self,room):
        return self.game.scenes[room]

    def point(self,room,source):
        return self.scene(room).point(source)

    def allowed(self,room,source):
        return self.scene(room).collisions.allows(self.point(room,source))

    def reachable(self,room):
        scene=self.scene(room)
        origin=scene.spawn
        queue=deque([(0,0)])
        seen={(0,0)}
        points=[]
        while queue:
            x,y=queue.popleft()
            point=origin+pygame.Vector2(x*8,y*8)
            points.append(point)
            for nx,ny in ((x+1,y),(x-1,y),(x,y+1),(x,y-1)):
                candidate=origin+pygame.Vector2(nx*8,ny*8)
                if (nx,ny) not in seen and scene.collisions.allows(candidate):
                    seen.add((nx,ny));queue.append((nx,ny))
        return points

    def test_fridge_base_blocks_all_floor_sides_but_interaction_stays_reachable(self):
        scene=self.scene('cozinha')
        block=next(item for item in scene.collision_data['obstacles'] if item['id']=='geladeira')
        self.assertEqual(block['rect'],[1264,315,112,91])
        for x in (1270,1300,1340,1370):
            for y in (375,390,405):
                self.assertFalse(self.allowed('cozinha',(x,y)),(x,y))
        self.assertTrue(self.allowed('cozinha',(1290,435)))
        self.assertTrue(self.allowed('cozinha',(1235,390)))
        game=self.game
        game.change_room('cozinha',self.point('cozinha',(1290,435)))
        self.assertEqual(game.nearest_interaction().action,'fridge')
        game.visitor_session.intro.fridge_checked=False
        game.interact()
        self.assertTrue(game.visitor_session.intro.fridge_checked)
        self.assertIn('geladeira',game.dialog)
        game.dialog=''

    def test_movement_cannot_cross_fridge_or_room_outer_edges(self):
        game=self.game
        player=game.player
        for start,vector in (((1290,435),(0,-1)),((1235,390),(1,0)),((1235,430),(1,-1))):
            player.feet=self.point('cozinha',start)
            self.assertTrue(self.scene('cozinha').collisions.allows(player.feet),start)
            for dt in (1/120,1/30,.4,2):
                player.update(vector,dt,self.scene('cozinha').collisions)
                self.assertTrue(self.scene('cozinha').collisions.allows(player.feet))
            source=self.scene('cozinha').source_point(player.feet)
            self.assertFalse(1264<source.x<1376 and 365<source.y<406)
        for room,start,vector in (('quarto',(350,458),(0,1)),('quarto',(450,458),(0,1)),
                                  ('quarto',(403,470),(0,1)),('quarto',(130,310),(-1,0)),
                                  ('cozinha',(1210,430),(1,0))):
            player.feet=self.point(room,start)
            self.assertTrue(self.scene(room).collisions.allows(player.feet),(room,start))
            player.update(vector,2,self.scene(room).collisions)
            self.assertTrue(self.scene(room).collisions.allows(player.feet),(room,start))

    def test_bedroom_black_exterior_forbidden_door_kept_open(self):
        for source in ((340,488),(455,488),(85,325),(680,330),(300,485),(500,485)):
            self.assertFalse(self.allowed('quarto',source),source)
        for source in ((403,452),(403,482),(403,488),(350,421),(450,421)):
            self.assertTrue(self.allowed('quarto',source),source)
        self.assertTrue(self.allowed('quarto',(403,482)))

    def test_kitchen_table_island_and_walls_keep_walkable_gaps(self):
        for source in ((180,580),(510,580),(340,405),(340,765),
                       (625,570),(1115,570),(850,430),(850,760)):
            self.assertTrue(self.allowed('cozinha',source),source)
        for source in ((140,390),(1390,700),(800,350),(500,820),
                       (300,570),(850,570)):
            self.assertFalse(self.allowed('cozinha',source),source)
        points=self.reachable('cozinha')
        scene=self.scene('cozinha')
        for source in ((180,580),(510,580),(340,405),(340,765),
                       (625,570),(1115,570),(850,430),(850,760)):
            target=scene.point(source)
            self.assertTrue(any(p.distance_to(target)<14 for p in points),source)

    def test_routes_interactions_spawns_and_day_night(self):
        for room in ('quarto','cozinha'):
            scene=self.scene(room)
            self.assertTrue(scene.collisions.allows(scene.spawn))
            self.assertIsNotNone(free_spawn(scene,scene.spawn))
            points=self.reachable(room)
            for item in scene.interactions:
                self.assertTrue(any(nearest(scene.interactions,p) is item for p in points),(room,item.action))
            self.assertEqual(scene.images['dia'].get_size(),scene.images['noite'].get_size())
            self.assertEqual(scene.images['dia'].get_size(),scene.rect.size)
        game=self.game
        for room,exit_source in (('quarto',(403,482)),('cozinha',(768,866))):
            game.change_room(room,self.point(room,exit_source))
            self.assertEqual(game.nearest_interaction().action,'exit')
            game.interact();game.update((0,0),.23);game.update((0,0),.23)
            self.assertEqual(game.room,'corredor')
            game.player.feet=game.scene.point((DOOR_X[room],235))
            game.interact();game.update((0,0),.23);game.update((0,0),.23)
            self.assertEqual(game.room,room)
            self.assertTrue(game.scene.collisions.allows(game.player.feet))


if __name__=='__main__':
    unittest.main()
