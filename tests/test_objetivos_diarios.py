"""Percurso guiado e regressões das regras existentes."""
import os
os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')
os.environ.setdefault('SDL_AUDIODRIVER', 'dummy')

import random
import time
import unittest
from unittest.mock import patch

import pygame
from casa import hud, ui_theme
from casa.game import House
from casa.objectives import ObjectiveGuide
from casa.visitors import VisitorSession


class DailyObjectivesTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        cls.screen = pygame.display.set_mode((1280, 720))

    def setUp(self):
        self.session = VisitorSession(random.Random(7))
        self.guide = ObjectiveGuide(self.session)

    def watch(self, day):
        bulletin = self.session.news.current(day)
        self.assertTrue(self.session.news.watch(bulletin))
        return bulletin

    def enter(self, day):
        self.session.days.day = day
        self.session.news.unlock(day)
        self.session.manager.activate(day, True)

    def resolve(self, decision='rejeitado'):
        current = self.session.manager.current
        if current:
            self.assertTrue(self.session.decide(self.session.visitors[current], decision))

    def test_guided_days_one_to_seven_and_real_arrivals(self):
        started = time.perf_counter()
        self.assertIn('geladeira', self.guide.current().action)
        self.session.intro.fridge_checked = True
        self.assertIn('noticiário', self.guide.current().action)
        self.watch(1)
        self.assertEqual(self.session.manager.current, 'ricardo')
        self.assertIn('porta', self.guide.current().action)
        self.session.intro.door_checked = True
        self.assertIn('decida', self.guide.current().action)
        self.resolve()
        self.assertIn('durma', self.guide.current().action)

        self.enter(2)
        self.assertEqual(self.session.manager.current, 'laura')
        self.assertIn('noticiário', self.guide.current().action)
        self.watch(2)
        self.assertIn('visitante', self.guide.current().action)
        self.resolve()
        self.assertIn('durma', self.guide.current().action)

        self.enter(3)
        self.assertIsNone(self.session.manager.current)
        self.assertIn('noticiário', self.guide.current().action)
        self.watch(3)
        self.assertIn('durma', self.guide.current().action)

        self.enter(4)
        self.assertIn('características', self.guide.current().hint)
        self.assertNotIn('manchas_maos', self.session.medical.known)
        self.assertTrue(self.session.manager.current)
        self.watch(4)
        self.assertIn('manchas_maos', self.session.medical.known)
        self.assertIn('manchas', self.guide.current().hint)
        self.resolve()
        self.assertIn('durma', self.guide.current().action)

        self.enter(5)
        self.watch(5)
        self.assertIsNone(self.session.manager.current)
        self.assertIn('diário', self.guide.current().hint)
        self.assertIn('durma', self.guide.current().action)

        self.enter(6)
        self.watch(6)
        self.assertTrue(self.session.manager.current)
        self.assertIn('visitante', self.guide.current().action)
        self.resolve()
        self.assertIn('durma', self.guide.current().action)

        self.enter(7)
        self.assertIn('infecção', self.guide.current().hint)
        self.assertNotIn('padrão', self.guide.current().hint)
        self.watch(7)
        self.assertIn('padrão', self.guide.current().hint)
        self.assertIn('diário', self.guide.current().hint)
        self.assertNotIn('infectado', self.guide.opening())
        self.assertLess(time.perf_counter() - started, 10)

    def test_later_days_read_state_and_acceptance_choices(self):
        self.session.intro.fridge_checked = True
        self.watch(1)
        self.resolve('acolhido')
        for day in range(2, 21):
            self.enter(day)
            self.assertIn('noticiário', self.guide.current().action)
            self.watch(day)
            if self.session.manager.current:
                self.assertIn('visitante', self.guide.current().action)
                self.resolve('acolhido' if day == 4 else 'rejeitado')
            self.assertIn('durma', self.guide.current().action)
            if day in (10, 14, 17):
                self.assertTrue(self.guide.current().hint)
            if day in (14, 17):
                self.assertIn('padrão', self.guide.current().hint)
        self.assertEqual(len(self.session.decisions), len(self.session.manager.plan))

    def test_feature_hint_requires_actual_learning_and_watching(self):
        self.session.intro.fridge_checked = True
        self.watch(1)
        self.resolve()
        self.enter(4)
        self.assertNotIn('manchas nas mãos', self.guide.current().hint)
        self.session.news.current(4).read = True
        self.assertNotIn('manchas', self.guide.current().hint)
        self.session.news.current(4).read = False
        self.watch(4)
        self.assertIn('manchas', self.guide.current().hint)

    def test_opening_after_summary_once_and_hud_refresh(self):
        game = House()
        game.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN))
        self.assertEqual(game.objective_ui.objective_day, 1)
        self.assertIn('geladeira', game.objective_notice)
        self.assertFalse(game.dialog)
        game.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE))
        self.assertFalse(game.objective_notice)
        game.change_room('cozinha')
        game.change_room('sala')
        self.assertFalse(game.dialog)

        with patch.object(ui_theme, 'text', wraps=ui_theme.text) as drawn:
            hud.draw(self.screen, game)
        self.assertTrue(any('geladeira' in str(call.args[1]) for call in drawn.call_args_list))
        game.visitor_session.intro.fridge_checked = True
        with patch.object(ui_theme, 'text', wraps=ui_theme.text) as drawn:
            hud.draw(self.screen, game)
        self.assertTrue(any('noticiário' in str(call.args[1]) for call in drawn.call_args_list))

        game.visitor_session.news.watch(game.news.current(1))
        game.visitor_session.decide(game.visitor_session.visitors['ricardo'], 'rejeitado')
        game.visitor_session.survival.add_supplies(30, 30)
        game.change_room('quarto')
        game.sleep_option = True
        game.confirm_sleep()
        game.update((0, 0), 3)
        self.assertEqual(game.days.day, 2)
        self.assertEqual(game.dialog_kind, 'summary')
        game.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN))
        self.assertEqual(game.objective_ui.objective_day, 2)
        self.assertIn('noticiário', game.objective_notice)
        game.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE))
        game.change_room('sala')
        self.assertFalse(game.dialog)

    def test_sleep_rules_unchanged(self):
        game = House()
        self.assertIn('noticiário', game.sleep_block_reason())
        game.news.watch(game.news.current(1))
        self.assertIn('visitante', game.sleep_block_reason())
        game.visitor_session.decide(game.visitor_session.visitors['ricardo'], 'rejeitado')
        self.assertEqual(game.sleep_block_reason(), '')


if __name__ == '__main__':
    unittest.main()
