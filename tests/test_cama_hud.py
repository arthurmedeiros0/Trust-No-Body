"""Bordas da cama e noites reais sem antecipar privacao."""
import unittest
from unittest.mock import patch
import pygame
from casa.game import House
from casa.interactions import nearest
from casa.visitors import Visitor


class BedAndHUDTests(unittest.TestCase):
    def test_visitor_supplies_rescue_critical_day_without_early_consumption(self):
        for resource,critical_day,limit in (('water',3,2),('food',4,3)):
            with self.subTest(resource=resource):
                self.setUp()
                game=self.game;session=game.visitor_session;state=session.survival
                state.add_supplies(20 if resource=='water' else 0,20 if resource=='food' else 0)
                for _ in range(critical_day-1):self.sleep()
                needs=state.people['protagonista']
                counter='thirst' if resource=='water' else 'hunger'
                self.assertEqual(getattr(needs,counter),limit-1)
                game.dialog=''
                before=(needs.hunger,needs.thirst,state.sanity,state.loneliness,state.food,state.water)
                for _ in range(4):
                    game.handle_event(pygame.event.Event(pygame.KEYDOWN,key=pygame.K_F6))
                    game.survival_hud();game.update((0,0),5)
                self.assertEqual((needs.hunger,needs.thirst,state.sanity,state.loneliness,state.food,state.water),before)
                visitor=Visitor({'id':'resgate'}, {},1,1,arrived=True)
                session.visitors[visitor.id]=visitor
                self.assertTrue(session.decide(visitor,'acolhido'))
                self.assertEqual(getattr(state.predicted_needs(game.days.day,session.living_ids),counter),0)
                self.assertEqual(getattr(needs,counter),limit-1)
                self.sleep()
                self.assertTrue(state.alive);self.assertEqual(game.days.day,critical_day+1)
                self.assertEqual(getattr(needs,counter),0)
                self.assertEqual(len(state.reports),critical_day)

    def setUp(self):
        self.game=House()
        self.game.dialog=''
        self.game.news.watch(self.game.news.current(1))
        self.game.decide_visitor(self.game.visitor_session.visitors['ricardo'],'rejeitado')

    def sleep(self):
        game=self.game
        game.dialog=''
        game.change_room('quarto',game.scene.point((345,365)))
        game.handle_event(pygame.event.Event(pygame.KEYUP,key=pygame.K_e))
        game.handle_event(pygame.event.Event(pygame.KEYDOWN,key=pygame.K_e))
        self.assertTrue(game.sleep_option)
        game.confirm_sleep()
        game.update((0,0),3)

    def test_bed_edges_distance_collision_and_far_away(self):
        game=self.game;scene=game.scene
        bed=next(i for i in scene.interactions if i.action=='sleep')
        self.assertEqual(bed.region,pygame.Rect(scene.transform_rect((232,125,131,215))))
        # Todas as bordas alcancaveis do piso: ambos os lados e os pes.
        for source in ((215,245),(383,245),(299,365),(215,230),(383,220)):
            with self.subTest(source=source):
                feet=scene.point(source)
                self.assertTrue(scene.collisions.allows(feet))
                self.assertIs(nearest(scene.interactions,feet),bed)
                game.player.feet=feet;game.sleep_held=False;game.dialog=''
                game.interact();self.assertTrue(game.sleep_option)
        self.assertFalse(scene.collisions.allows(scene.point((299,260))))
        self.assertGreater(bed.distance(scene.point((500,400))),bed.radius)
        self.assertEqual(bed.distance(pygame.Vector2(bed.region.center)),0)
        # A cabeceira esta acima do piso: nao altera colisoes para criar acesso.
        self.assertFalse(scene.collisions.allows(scene.point((299,120))))

    def test_debug_draws_bed_region_with_camera(self):
        scene=self.game.scene;screen=pygame.display.get_surface()
        bed=next(i for i in scene.interactions if i.action=='sleep')
        camera=pygame.Vector2(17,9)
        with patch('casa.scenes.pygame.draw.rect',wraps=pygame.draw.rect) as draw:
            scene.draw(screen,'dia',True,camera)
        self.assertTrue(any(call.args[1]=='#edcf65' and call.args[2]==bed.region.move(-17,-9) for call in draw.call_args_list))

    def test_day_three_is_fully_playable_and_thirst_only_at_its_end(self):
        game=self.game;state=game.visitor_session.survival
        needs=state.people['protagonista']
        self.assertEqual((needs.hunger,needs.thirst),(0,0))
        self.sleep()
        self.assertEqual((needs.hunger,needs.thirst),(0,0))
        self.assertEqual(state.sanity,7);self.assertEqual(state.loneliness,1)
        self.sleep()
        self.assertEqual(game.days.day,3);self.assertTrue(state.alive)
        self.assertEqual((needs.hunger,needs.thirst),(1,1))
        self.assertIn("Sede: 2/2",game.survival_hud())
        game.dialog='';game.change_room('corredor')
        before=game.player.feet.copy();game.update((1,0),.1)
        self.assertNotEqual(before,game.player.feet)
        for _ in range(100):game.update((0,0),10)
        game.news.watch(game.news.current(2))
        self.assertTrue(state.alive);self.assertEqual(needs.thirst,1)
        game.change_room('quarto');self.sleep()
        self.assertFalse(state.alive);self.assertEqual(state.defeat_day,3)
        self.assertEqual(len(state.reports),3);self.assertEqual(game.days.day,3)

    def test_water_on_third_day_resets_thirst_and_hunger_ends_fourth_day(self):
        state=self.game.visitor_session.survival
        self.sleep();self.sleep();state.add_supplies(0,1) # Estoque exclusivo deste teste.
        self.sleep()
        self.assertTrue(state.alive);self.assertEqual(self.game.days.day,4)
        needs=state.people['protagonista']
        self.assertEqual((needs.hunger,needs.thirst),(2,0))
        self.sleep()
        self.assertFalse(state.alive);self.assertEqual(state.defeat_day,4)
        self.assertIn('comida',state.defeat_cause)

    def test_repeated_confirmation_does_not_consume_twice(self):
        state=self.game.visitor_session.survival
        state.add_supplies(.5,.5)
        self.sleep()
        for _ in range(10):self.game.confirm_sleep();self.game.update((0,0),1)
        self.assertEqual(self.game.days.day,2);self.assertEqual(len(state.reports),1)
        self.assertEqual((state.food,state.water),(.5,.5))
        needs=state.people['protagonista']
        self.assertEqual((needs.hunger,needs.thirst),(0,0))

    def test_hud_reads_live_state_all_rooms_and_fits_header(self):
        game=self.game;state=game.visitor_session.survival
        self.sleep();state.change_sanity(-2)
        expected='Dia 2/20 | Sanidade: 5/8 | Fome: 1/3 dias | Sede: 1/2 dias'
        for room in game.scenes:
            game.change_room(room)
            self.assertEqual(game.survival_hud(),expected)
            for debug in (False,True):
                game.debug=debug;game.draw(pygame.display.get_surface())
        self.assertLessEqual(490+game.small.size(expected)[0],1260)
        self.assertLess(18+game.small.get_height(),game.scene.viewport.top)

    def test_fridge_opens_same_stock_only_inventory(self):
        game=self.game;state=game.visitor_session.survival
        game.change_room('cozinha',game.scenes['cozinha'].point((635,250)))
        game.interact();self.assertIn('geladeira está vazia',game.dialog)
        game.dialog='';state.add_supplies(2.5,1.5);game.interact()
        self.assertTrue(game.inventory.active)
        with patch.object(game.inventory,'line',wraps=game.inventory.line) as line:
            game.inventory.draw(pygame.display.get_surface())
        self.assertEqual([c.args[1] for c in line.call_args_list],['Comida: 2,5 latas','Água: 1,5 garrafas'])
        game.handle_event(pygame.event.Event(pygame.KEYDOWN,key=pygame.K_ESCAPE))
        game.handle_event(pygame.event.Event(pygame.KEYDOWN,key=pygame.K_i))
        self.assertTrue(game.inventory.active)
        self.assertEqual((state.food,state.water),(2.5,1.5))
