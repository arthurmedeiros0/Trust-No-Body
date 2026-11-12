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
from casa.objectives import Objective
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

    def test_hud_height_follows_wrapped_action_and_hint(self):
        journal = pygame.Rect(1198, 9, 56, 44)
        short = Objective('Assista ao noticiário no quarto.')
        detail = Objective(short.action, 'Opcional: consulte o diário e compare os sintomas com o padrão divulgado.')
        small, status, _ = hud.layout(1280, journal, short)
        larger, _, _ = hud.layout(1280, journal, detail)
        self.assertLess(small.height, 80)
        self.assertGreater(larger.height, small.height)
        self.assertLess(larger.height, 110)
        self.assertFalse(small.colliderect(status))
        self.assertFalse(larger.colliderect(status))
        self.assertFalse(larger.colliderect(journal))
        for objective, panel in ((short, small), (detail, larger)):
            _, action_height, hint_y, hint_height = hud.objective_size(panel.width, objective)
            self.assertLessEqual(34 + action_height, panel.bottom)
            if objective.hint:self.assertLessEqual(hint_y + hint_height, panel.bottom)

    def test_news_location_matches_bedroom_interaction(self):
        from casa.config import ROOMS
        self.assertTrue(any(item['action']=='television' for item in ROOMS['quarto']['interactions']))
        self.assertTrue(any(item['action']=='fridge' for item in ROOMS['cozinha']['interactions']))
        self.assertTrue(any(item['action']=='peephole' for item in ROOMS['entrada']['interactions']))
        self.session.intro.fridge_checked=True
        for day in (1, 4, 7, 20):
            self.session.days.day=day
            self.session.news.unlock(day)
            self.assertIn('no quarto', self.guide.current().action)
            self.assertNotIn('na sala', self.guide.current().action)

    def test_objective_modal_mouse_keys_and_exploration_recovery(self):
        for closing_key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_ESCAPE):
            game=House()
            game.handle_event(pygame.event.Event(pygame.KEYDOWN,key=pygame.K_RETURN))
            self.assertTrue(game.objective_notice)
            feet=game.player.feet.copy()
            game.update((1,0),.5)
            self.assertEqual(game.player.feet,feet)
            self.assertTrue(game.captures_escape)
            game.handle_event(pygame.event.Event(pygame.KEYDOWN,key=pygame.K_j))
            game.handle_event(pygame.event.Event(pygame.KEYDOWN,key=pygame.K_i))
            game.handle_event(pygame.event.Event(pygame.KEYDOWN,key=pygame.K_e))
            self.assertFalse(game.journal_ui.active)
            self.assertFalse(game.inventory.active)
            self.assertFalse(game.sleep_option)
            self.assertTrue(game.objective_notice)
            game.handle_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN,button=1,pos=game.journal_ui.access_rect.center))
            self.assertFalse(game.journal_ui.active)
            self.assertTrue(game.objective_notice)
            game.handle_event(pygame.event.Event(pygame.KEYDOWN,key=closing_key))
            self.assertFalse(game.objective_notice)
            self.assertFalse(game.captures_escape)
            game.handle_event(pygame.event.Event(pygame.KEYDOWN,key=pygame.K_j))
            self.assertTrue(game.journal_ui.active)

        game=House()
        game.handle_event(pygame.event.Event(pygame.KEYDOWN,key=pygame.K_RETURN))
        game.objective_ui.prepare(game.objective_notice,kind='objective')
        self.assertLess(game.objective_ui.box.width,800)
        self.assertLess(game.objective_ui.box.height,160)
        button=game.objective_ui.buttons['close'][0]
        game.handle_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN,button=1,pos=button.center))
        self.assertFalse(game.objective_notice)
        game.change_room('cozinha')
        game.change_room('quarto')
        self.assertFalse(game.objective_notice)

    def test_real_sleep_path_reaches_day_seven_with_modal_closure(self):
        game=House()
        enter=pygame.event.Event(pygame.KEYDOWN,key=pygame.K_RETURN)
        game.handle_event(enter)  # relato inicial
        game.handle_event(enter)  # objetivo do dia 1
        game.visitor_session.intro.fridge_checked=True
        game.visitor_session.survival.add_supplies(100,100)
        for day in range(1,7):
            self.assertEqual(game.days.day,day)
            self.assertIn('noticiário',game.objectives.current().action)
            game.news.watch(game.news.current(day))
            if day==1:game.visitor_session.intro.door_checked=True
            while game.visitor_session.manager.current:
                visitor=game.visitor_session.visitors[game.visitor_session.manager.current]
                self.assertTrue(game.visitor_session.decide(visitor,'acolhido' if visitor.id=='ricardo' else 'rejeitado'))
            self.assertIn('durma',game.objectives.current().action)
            game.change_room('quarto')
            game.sleep_option=True
            game.confirm_sleep()
            game.update((0,0),3)
            self.assertEqual(game.days.day,day+1)
            self.assertEqual(game.dialog_kind,'summary')
            game.handle_event(enter)
            self.assertEqual(game.objective_ui.objective_day,day+1)
            self.assertTrue(game.objective_notice)
            game.handle_event(enter)
            self.assertFalse(game.objective_notice)
        self.assertEqual(game.days.day,7)
        self.assertIn('infecção',game.objectives.current().hint)
        game.news.watch(game.news.current(7))
        self.assertIn('padrão',game.objectives.current().hint)


if __name__ == '__main__':
    unittest.main()
