"""Geometria, leitura sem efeitos colaterais e duração original da transição."""
import os
os.environ.setdefault('SDL_VIDEODRIVER','dummy')
os.environ.setdefault('SDL_AUDIODRIVER','dummy')
import unittest
from unittest.mock import patch
from types import SimpleNamespace
import pygame
from casa.game import House
from casa.sleep import SleepTransition
from casa import hud,ui_theme as ui


class HeaderAndTransitionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init();cls.screen=pygame.display.set_mode((1280,720))

    def test_transition_duration_callback_once_day_refresh_and_cache(self):
        days=SimpleNamespace(day=3)
        view=SleepTransition(days);events=[]
        def advance():
            days.day+=1;events.append(days.day)
        view.start(advance)
        view.update(.44);self.assertEqual(days.day,3)
        view.update(.01);self.assertEqual(days.day,4)
        self.assertEqual(view.phase,'hold')
        view.update(.8);view.draw(self.screen)
        first=view.card
        self.assertEqual(view.card_key,((1280,720),4))
        view.draw(self.screen);self.assertIs(first,view.card)
        for elapsed in (0,.11,.8,1.48,1.599):
            view.elapsed=elapsed;view.draw(self.screen)
            self.assertGreaterEqual(view.card.get_alpha(),0)
            self.assertLessEqual(view.card.get_alpha(),255)
        view.elapsed=.8
        view.update(.8);self.assertEqual(view.phase,'in')
        view.update(.45);self.assertFalse(view.active)
        view.update(30);self.assertEqual(events,[4])
        days.day=20;view.day_card((1280,720))
        self.assertEqual(view.card_key,((1280,720),20))
        self.assertIsNot(first,view.card)

    def test_header_geometry_live_values_and_drawing_all_rooms_periods(self):
        game=House();game.dialog=''
        state=game.visitor_session.survival
        state.people['protagonista'].hunger=1
        state.people['protagonista'].thirst=1
        state.change_sanity(-2)
        before=(state.sanity,state.food,state.water,repr(state.people),len(state.reports))
        values=dict(hud.status_values(game))
        self.assertEqual(values['DIA'],'01 / 20')
        self.assertEqual(values['SANIDADE'],'6 / 8')
        self.assertIn('Fome: '+values['FOME'].replace(' / ','/'),game.survival_hud())
        self.assertIn('Sede: '+values['SEDE'].replace(' / ','/'),game.survival_hud())
        for width in (1024,1280,1600):
            diary=pygame.Rect(width-82,9,56,44)
            location,status,cells=hud.layout(width,diary)
            self.assertFalse(location.colliderect(status))
            self.assertFalse(status.colliderect(diary))
            for i,cell in enumerate(cells):
                self.assertTrue(status.contains(cell))
                for other in cells[i+1:]:self.assertFalse(cell.colliderect(other))
        for room in game.scenes:
            game.change_room(room)
            for period in ('dia','noite'):
                game.period=period
                with patch.object(ui,'text',wraps=ui.text) as draw:
                    game.draw(self.screen)
                texts=[call.args[1] for call in draw.call_args_list]
                self.assertIn(f'{room.capitalize()}  /  {period.capitalize()}',texts)
        self.assertEqual(before,(state.sanity,state.food,state.water,repr(state.people),len(state.reports)))
        game.handle_event(pygame.event.Event(pygame.KEYDOWN,key=pygame.K_j))
        self.assertTrue(game.journal_ui.active)
        game.handle_event(pygame.event.Event(pygame.KEYDOWN,key=pygame.K_ESCAPE))
        game.handle_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN,button=1,pos=game.journal_ui.access_rect.center))
        self.assertTrue(game.journal_ui.active)

    def test_status_refreshes_day_resources_and_sanity_without_cached_values(self):
        game=House()
        state=game.visitor_session.survival
        game.days.day=20
        state.change_sanity(-5)
        state.people['protagonista'].hunger=1
        state.people['protagonista'].thirst=0
        first=dict(hud.status_values(game))
        self.assertEqual(first['DIA'],'20 / 20')
        self.assertEqual(first['SANIDADE'],'3 / 8')
        self.assertEqual(first['FOME'],'2 / 3 dias')
        self.assertEqual(first['SEDE'],'1 / 2 dias')
        state.add_supplies(10,10)
        second=dict(hud.status_values(game))
        self.assertEqual(second['FOME'],'0 / 3 dias')
        self.assertEqual(second['SEDE'],'0 / 2 dias')
        self.assertEqual(state.people['protagonista'].hunger,1)
        self.assertEqual(state.people['protagonista'].thirst,0)
