"""Orientacao e pose parada de chegada em todas as passagens."""
import unittest
from support import exploration_house as House
from casa.config import DOOR_X,CORRIDOR_RETURN_Y

class ArrivalDirectionTests(unittest.TestCase):
    def setUp(self):self.game=House()

    def cross(self,room,point,target,direction,arrival):
        game=self.game
        game.change_room(room)
        game.player.feet=game.scene.point(point)
        game.player.direction='direita'
        game.player.moving=True
        game.player.elapsed=.57
        game.interact()
        self.assertTrue(game.fade.active)
        game.update((1,0),.23)
        self.assertEqual(game.room,target)
        self.assertEqual(game.player.direction,direction)
        self.assertFalse(game.player.moving)
        self.assertEqual(game.player.elapsed,0)
        self.assertIs(game.player.image,game.player.idle[direction])
        expected=game.scene.point(arrival) if arrival else game.scene.spawn
        self.assertLess(game.player.feet.distance_to(expected),.001)
        self.assertTrue(game.scene.collisions.allows(game.player.feet))
        game.update((1,0),.23)
        self.assertFalse(game.fade.active)
        self.assertIs(game.player.image,game.player.idle[direction])
        self.assertLess(game.player.feet.distance_to(expected),.001)

    def test_all_corridor_connections_both_ways(self):
        for room,x in DOOR_X.items():
            with self.subTest(room=room):
                self.cross('corredor',(x,235),room,'costas',None)
                spawn=self.game.scene.config['spawn']
                self.cross(room,spawn,'corredor','frente',(x,CORRIDOR_RETURN_Y))

    def test_sala_entrada_both_ways(self):
        self.cross('sala',(826,274),'entrada','costas',None)
        self.cross('entrada',(768,870),'sala','frente',(826,274))

    def test_connection_direction_override_is_used_by_each_transition_type(self):
        # Comprova que a orientacao vem da conexao, sem regra fixa no destino.
        for room,point,action in [('corredor',(569,235),'door'),
                                  ('quarto',(403,452),'exit'),
                                  ('sala',(826,274),'passage')]:
            with self.subTest(action=action):
                game=self.game;game.change_room(room)
                item=min((item for item in game.scene.interactions if item.action==action),
                         key=lambda item:item.distance(game.scene.point(point)))
                original=item.direction
                try:
                    item.direction='esquerda'
                    game.player.feet=game.scene.point(point)
                    game.interact();game.update((0,0),.23);game.update((0,0),.23)
                    self.assertEqual(game.player.direction,'esquerda')
                    self.assertIs(game.player.image,game.player.idle['esquerda'])
                finally:item.direction=original
