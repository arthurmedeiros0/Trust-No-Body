"""Fluxo menu -> apresentação -> dia 1, sem atravessar eventos."""
import os
os.environ.setdefault('SDL_VIDEODRIVER','dummy')
os.environ.setdefault('SDL_AUDIODRIVER','dummy')

import unittest
import pygame
from main import GameFlow
from casa.game import House
from casa.intro_ui import IntroUI,HEADER,TITLE,PARAGRAPHS,QUESTION,CONTINUE
from casa import ui_theme as ui


def key(code):
    return pygame.event.Event(pygame.KEYDOWN,key=code)


class IntroNarrativeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        cls.screen=pygame.display.set_mode((1280,720))

    def test_exact_copy_layout_and_immediate_skip(self):
        self.assertEqual(HEADER,'TRANSMISSÃO INTERROMPIDA')
        self.assertEqual(TITLE,'O INÍCIO DO FIM')
        self.assertEqual(PARAGRAPHS,(
            'Um vírus desconhecido se espalhou rapidamente. O governo decretou um lockdown imediato.',
            'Você está sozinho, sem suprimentos. Para sobreviver, talvez precise abrir a porta para desconhecidos.'))
        self.assertEqual(QUESTION,'Mas em quem você pode confiar?')
        self.assertEqual(CONTINUE,'ENTER — CONTINUAR')
        view=IntroUI()
        self.assertTrue(view.panel.contains(view.button))
        for value,size,width in ((HEADER,22,710),(TITLE,56,780),
                                 (PARAGRAPHS[0],27,760),(PARAGRAPHS[1],27,760),
                                 (QUESTION,30,760)):
            self.assertTrue(all(ui.font(size).size(line)[0]<=width for line in ui.wrapped_lines(value,width,ui.font(size))))
        view.draw(self.screen)
        self.assertTrue(view.handle_event(key(pygame.K_ESCAPE)))
        self.assertFalse(view.handle_event(key(pygame.K_ESCAPE)))

    def test_menu_click_and_all_continue_controls_start_once(self):
        for event_factory in (
            lambda view:key(pygame.K_RETURN),
            lambda view:key(pygame.K_SPACE),
            lambda view:key(pygame.K_ESCAPE),
            lambda view:pygame.event.Event(pygame.MOUSEBUTTONDOWN,button=1,pos=view.button.center),
        ):
            created=[]
            class FakeHouse:
                def __init__(self,development=False):
                    created.append(self)
                    self.defer_restart=False
                    self.captures_escape=False
                    self.moves=[]
                def update(self,movement,dt):self.moves.append(movement)
                def handle_event(self,event):return None
                def draw(self,screen):screen.fill('#12202a')
            flow=GameFlow(FakeHouse)
            self.assertEqual(flow.menu.page,'main')
            play=flow.menu.rectangles()['normal'].center
            flow.handle_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN,button=1,pos=play))
            self.assertIsNotNone(flow.intro)
            self.assertIsNone(flow.game)
            flow.update((1,0),.016)
            flow.draw(self.screen)
            flow.handle_event(key(pygame.K_e))
            flow.handle_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN,button=1,pos=(600,300)))
            self.assertFalse(created)
            view=flow.intro
            flow.handle_event(event_factory(view))
            self.assertIsNone(flow.intro)
            self.assertEqual(len(created),1)
            self.assertFalse(view.handle_event(event_factory(view)))
            self.assertEqual(len(created),1)
            flow.update((1,0),.016)
            self.assertEqual(created[0].moves,[(1,0)])

    def test_original_story_objective_news_and_restart_flow(self):
        flow=GameFlow(House)
        flow.handle_event(key(pygame.K_RETURN))  # Jogar selecionado no menu.
        self.assertIsNotNone(flow.intro)
        self.assertIsNone(flow.game)
        flow.handle_event(key(pygame.K_RETURN))
        game=flow.game
        self.assertIsNotNone(game)
        self.assertEqual(game.days.day,1)
        self.assertEqual(game.room,'quarto')
        self.assertEqual(game.dialog,'Você acorda com uma sensação de fome. Não se lembra da última vez que fez uma refeição de verdade.')
        self.assertIn('geladeira',game.objectives.current().action)
        flow.handle_event(key(pygame.K_RETURN))
        self.assertIn('geladeira',game.objective_notice)
        flow.handle_event(key(pygame.K_RETURN))
        self.assertFalse(game.objective_notice)
        game.visitor_session.intro.fridge_checked=True
        game.news.watch(game.news.current(1))
        self.assertEqual(game.visitor_session.manager.current,'ricardo')
        game.visitor_session.intro.door_checked=True
        self.assertTrue(game.visitor_session.decide(game.visitor_session.visitors['ricardo'],'acolhido'))
        game.visitor_session.survival.add_supplies(30,30)
        game.sleep_option=True
        game.confirm_sleep()
        game.update((0,0),3)
        self.assertEqual(game.days.day,2)
        self.assertIsNone(flow.intro)
        game.visitor_session.survival.alive=False
        flow.handle_event(key(pygame.K_r))
        self.assertIsNone(flow.game)
        self.assertIsNotNone(flow.intro)
        flow.handle_event(key(pygame.K_SPACE))
        self.assertIsNot(flow.game,game)
        self.assertEqual(flow.game.days.day,1)
        self.assertIn('fome',flow.game.dialog)


if __name__=='__main__':
    unittest.main()
