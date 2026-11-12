"""F3/F6 ficam indisponíveis na partida comum e disponíveis em DEBUG."""
import os
os.environ.setdefault('SDL_VIDEODRIVER','dummy')
os.environ.setdefault('SDL_AUDIODRIVER','dummy')

import unittest
from unittest.mock import patch
import pygame
from casa import config
from casa.game import House


def press(game,key):
    game.handle_event(pygame.event.Event(pygame.KEYDOWN,key=key))


class DebugShortcutTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        cls.screen=pygame.display.set_mode((1280,720))

    def test_release_blocks_shortcuts_in_all_event_branches(self):
        self.assertFalse(config.DEBUG)
        for context in ('free','dialog','objective','television','peephole','sleep','fade','editor'):
            game=House(development=context=='editor')
            game.dialog=''
            if context=='dialog':game.dialog='Mensagem narrativa.'
            elif context=='objective':game.objective_notice='Objetivo do dia.'
            elif context=='television':game.television.active=True
            elif context=='peephole':game.observing=True
            elif context=='sleep':game.sleep_transition.phase='hold'
            elif context=='fade':game.fade.phase='out'
            elif context=='editor':game.editor.active=True
            for key in (pygame.K_F3,pygame.K_F6):
                press(game,key)
            self.assertEqual(game.period,'dia',context)
            self.assertFalse(game.debug,context)
            if context=='dialog':self.assertEqual(game.dialog,'Mensagem narrativa.')
            if context=='objective':self.assertEqual(game.objective_notice,'Objetivo do dia.')

    def test_collision_overlay_is_hidden_in_release(self):
        game=House();game.dialog=''
        game.debug=True  # Mesmo um estado interno antigo não expõe as hitboxes.
        with patch.object(game.scene,'draw',wraps=game.scene.draw) as drawing:
            game.draw(self.screen)
        self.assertFalse(drawing.call_args.args[2])

    def test_debug_setting_restores_shortcuts_for_development(self):
        with patch.object(config,'DEBUG',True):
            game=House();game.dialog=''
            press(game,pygame.K_F3)
            self.assertTrue(game.debug)
            press(game,pygame.K_F6)
            self.assertEqual(game.period,'noite')
            with patch.object(game.scene,'draw',wraps=game.scene.draw) as drawing:
                game.draw(self.screen)
            self.assertTrue(drawing.call_args.args[2])
            game.television.active=True
            press(game,pygame.K_F3)
            press(game,pygame.K_F6)
            self.assertFalse(game.debug)
            self.assertEqual(game.period,'dia')

    def test_sleep_still_restores_day_without_shortcut(self):
        game=House();game.dialog=''
        game.period='noite'
        game.news.watch(game.news.current(1))
        game.visitor_session.decide(game.visitor_session.visitors['ricardo'],'rejeitado')
        game.visitor_session.survival.add_supplies(20,20)
        game.sleep_option=True
        game.confirm_sleep()
        game.update((0,0),3)
        self.assertEqual(game.days.day,2)
        self.assertEqual(game.period,'dia')


if __name__=='__main__':
    unittest.main()
