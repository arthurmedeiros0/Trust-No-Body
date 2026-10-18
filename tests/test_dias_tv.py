"""Calendario manual, sono modal e noticias sem inferencia matematica."""
import copy
import unittest
from unittest.mock import patch
import pygame
from support import exploration_house as House
from casa.days import DayCycle
from casa.interactions import nearest


class DaysAndTelevisionTests(unittest.TestCase):
    def setUp(self):self.game=House()

    def key(self,key):self.game.handle_event(pygame.event.Event(pygame.KEYDOWN,key=key))

    def resolve(self,decision='rejeitado'):
        visitor=self.game.visitor_session.visitors['ricardo']
        self.assertTrue(self.game.decide_visitor(visitor,decision))
        return visitor

    def bed(self):
        game=self.game;scene=game.scenes['quarto']
        if game.dialog.startswith('Resumo do dia anterior'):self.key(pygame.K_RETURN)
        game.change_room('quarto',scene.point((345,365)))
        self.assertTrue(scene.collisions.allows(game.player.feet))
        self.assertEqual(nearest(scene.interactions,game.player.feet).action,'sleep')
        game.handle_event(pygame.event.Event(pygame.KEYUP,key=pygame.K_e))
        self.key(pygame.K_e)

    def finish_sleep(self):
        self.key(pygame.K_s);self.game.update((1,0),3)
        self.assertFalse(self.game.sleep_transition.active)

    def tv(self):
        game=self.game;scene=game.scenes['quarto']
        game.change_room('quarto',scene.point((135,267)))
        self.assertTrue(scene.collisions.allows(game.player.feet))
        self.assertEqual(nearest(scene.interactions,game.player.feet).action,'television')
        self.key(pygame.K_e);self.assertTrue(game.television.active)

    def click_tv(self,key):
        ui=self.game.television
        rect=next(rect for name,rect,label in ui.layout() if name==key)
        self.game.handle_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN,button=1,pos=rect.center))

    def test_initial_state_no_clock_advance_and_f6_does_not_unlock(self):
        game=self.game
        self.assertEqual(game.days.day,1);self.assertEqual(game.period,'dia')
        self.assertEqual(game.visitor_session.day,1)
        available=[b.id for b in game.news.bulletins if b.available]
        for _ in range(5):self.key(pygame.K_F6);game.update((0,0),100)
        self.assertEqual(game.days.day,1)
        self.assertEqual([b.id for b in game.news.bulletins if b.available],available)
        self.assertFalse(game.news.history)

    def test_waiting_visitor_blocks_sleep_and_cancel_never_advances(self):
        self.bed();self.assertFalse(self.game.sleep_option)
        self.assertIn('visitante',self.game.dialog)
        self.key(pygame.K_ESCAPE);self.resolve()
        self.bed();self.assertTrue(self.game.sleep_option)
        self.key(pygame.K_n)
        self.assertEqual(self.game.days.day,1);self.assertFalse(self.game.dialog)
        self.bed();self.key(pygame.K_ESCAPE)
        self.assertEqual(self.game.days.day,1)

    def test_sleep_fade_midpoint_arrival_and_held_e_exactly_one_day(self):
        self.resolve();self.bed();self.game.period='noite'
        start=self.game.player.feet.copy();self.key(pygame.K_s)
        self.game.update((1,0),.2)
        self.assertEqual(self.game.days.day,1);self.assertEqual(self.game.player.feet,start)
        self.game.update((1,0),.3)
        self.assertEqual(self.game.days.day,2);self.assertEqual(self.game.sleep_transition.phase,'hold')
        self.assertEqual(self.game.period,'dia');self.assertEqual(self.game.room,'quarto')
        self.assertTrue(self.game.scene.collisions.allows(self.game.player.feet))
        self.assertEqual(self.game.player.direction,'frente');self.assertFalse(self.game.player.moving)
        self.game.draw(pygame.display.get_surface())
        self.game.update((1,0),3)
        for _ in range(8):self.key(pygame.K_e);self.key(pygame.K_s)
        self.assertEqual(self.game.days.day,2);self.assertFalse(self.game.sleep_transition.active)
        self.assertFalse(self.game.sleep_option)

    def test_mouse_confirmation_and_cancel(self):
        self.resolve();self.bed()
        self.game.handle_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN,button=1,pos=(800,630)))
        self.assertEqual(self.game.days.day,1);self.assertFalse(self.game.sleep_option)
        self.bed()
        self.game.handle_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN,button=1,pos=(450,630)))
        self.game.update((0,0),3);self.assertEqual(self.game.days.day,2)

    def test_events_once_and_day20_does_not_end_game_or_advance(self):
        self.resolve('acolhido');events=[]
        for event in ('day_end','day_start'):
            self.game.days.subscribe(event,lambda data,name=event:events.append((name,data.day,data.previous_day,data.next_day)))
        for day in range(2,21):
            self.bed();self.finish_sleep();self.assertEqual(self.game.days.day,day)
        self.assertEqual(len(events),38)
        self.assertEqual(events[:2],[('day_end',1,1,2),('day_start',2,1,2)])
        self.bed();self.assertFalse(self.game.sleep_option)
        self.assertIn('20',self.game.dialog);self.key(pygame.K_ESCAPE)
        self.assertFalse(self.game.days.advance());self.assertEqual(len(events),38)
        self.tv();self.click_tv('current')
        self.assertIn('cura',self.game.television.bulletin.headline)

    def test_tv_current_published_history_no_future_and_escape(self):
        self.tv();self.assertEqual(self.game.news.history,[])
        before=self.game.player.feet.copy();self.game.update((1,0),2)
        self.assertEqual(self.game.player.feet,before)
        self.click_tv('current');self.assertTrue(self.game.news.current(1).read)
        self.key(pygame.K_ESCAPE);self.assertEqual(self.game.television.page,'root')
        for _ in range(3):self.game.days.advance()
        self.click_tv('history');self.assertEqual([b.day for b in self.game.news.history],[3,2,1])
        self.assertNotIn('news:boletim_04',[k for k,_,_ in self.game.television.layout()])
        self.game.television.choose('news:boletim_20');self.assertEqual(self.game.television.page,'history')
        self.click_tv('news:boletim_01');self.assertEqual(self.game.television.bulletin.day,1)
        self.key(pygame.K_ESCAPE);self.key(pygame.K_ESCAPE)
        self.click_tv('current');self.assertEqual(self.game.television.bulletin.day,4)
        self.assertEqual([b.day for b in self.game.news.history],[3,2,1])
        self.assertEqual(set(self.game.visitor_session.knowledge.published),{'boletim_01','boletim_04'})
        self.key(pygame.K_ESCAPE);self.key(pygame.K_ESCAPE);self.assertFalse(self.game.television.active)

    def test_all_20_bulletins_pagination_and_narrative_schedule(self):
        self.resolve('acolhido') # Companhia e estoque da fixture permitem isolar o calendario.
        for day in range(1,21):
            if day>1:self.game.days.advance()
            self.game.news.watch(self.game.news.current(day))
        ui=self.game.television;ui.open();ui.choose('history')
        found=set()
        for _ in range(3):
            found.update(k for k,_,_ in ui.layout() if k.startswith('news:'));ui.choose('next')
        self.assertEqual(len(found),19)
        self.assertNotIn('news:boletim_20',found)
        data={b.day:' '.join(b.paragraphs).lower() for b in self.game.news.bulletins}
        self.assertIn('ausência de alterações oculares',data[7]);self.assertIn('três condições',data[7])
        self.assertIn('não significa estar saudável',data[7])
        self.assertIn('ausência de tremores involuntários',data[14]);self.assertIn('independente',data[14])
        self.assertIn('protocolo completo',data[17]);self.assertIn('tratamento',data[20])
        for day in range(1,7):self.assertNotIn('combinação das três',data[day])
        self.game.draw(pygame.display.get_surface())

    def test_accepted_and_rejected_visitor_preserved_no_randomization(self):
        for decision in ('acolhido','rejeitado'):
            self.game=House();visitor=self.resolve(decision)
            identity=id(visitor);snapshot=copy.deepcopy(vars(visitor))
            actors=dict(self.game.residents)
            positions={k:a.feet.copy() for k,a in actors.items()}
            self.bed()
            with patch('casa.visitors.random.getrandbits',side_effect=AssertionError('novo sorteio')):
                self.finish_sleep()
            self.assertEqual(id(self.game.visitor_session.visitors['ricardo']),identity)
            self.assertEqual(vars(visitor),snapshot)
            self.assertEqual(self.game.residents,actors)
            for key,actor in actors.items():self.assertEqual(actor.feet,positions[key])
            self.assertEqual(self.game.visitor_session.day,2)

    def test_modal_guards_and_f6_inside_tv_does_not_change_news(self):
        self.resolve();self.tv();self.game.interact();self.assertFalse(self.game.sleep_option)
        self.click_tv('current');current=self.game.television.bulletin
        self.key(pygame.K_F6);self.assertEqual(self.game.television.bulletin,current)
        self.assertEqual(self.game.days.day,1)
        self.key(pygame.K_F3);self.assertTrue(self.game.debug)
        self.key(pygame.K_ESCAPE);self.key(pygame.K_ESCAPE)
        self.bed();self.key(pygame.K_s)
        for _ in range(5):self.game.confirm_sleep();self.game.interact()
        self.game.update((0,0),30);self.assertEqual(self.game.days.day,2)

    def test_day_transition_duration_is_fps_independent(self):
        for fps in (30,60,120):
            self.game=House();self.resolve();self.bed();self.key(pygame.K_s)
            for _ in range(fps*3):self.game.update((0,0),1/fps)
            self.assertEqual(self.game.days.day,2);self.assertFalse(self.game.sleep_transition.active)
