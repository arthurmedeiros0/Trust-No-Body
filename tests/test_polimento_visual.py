import os
os.environ.setdefault('SDL_VIDEODRIVER','dummy')
os.environ.setdefault('SDL_AUDIODRIVER','dummy')
import unittest
import pygame
from casa.menu import GameMenu
from casa.message_ui import MessageUI

class PolishTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init();pygame.display.set_mode((1280,720))

    def test_menu_logo_mouse_keyboard_and_removed_test(self):
        menu=GameMenu()
        self.assertEqual([key for key,_ in menu.entries()],['normal','quit'])
        self.assertAlmostEqual(menu.logo.get_width()/menu.logo.get_height(),menu.logo_original.get_width()/menu.logo_original.get_height(),places=2)
        self.assertEqual(menu.handle_event(pygame.event.Event(pygame.KEYDOWN,key=pygame.K_RETURN))[0],'normal')
        menu.handle_event(pygame.event.Event(pygame.KEYDOWN,key=pygame.K_DOWN))
        self.assertEqual(menu.handle_event(pygame.event.Event(pygame.KEYDOWN,key=pygame.K_SPACE))[0],'quit')
        for key,rect in menu.rectangles().items():
            self.assertEqual(menu.handle_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN,button=1,pos=rect.center))[0],key)
        self.assertIsNone(menu.choose('test'))
        menu.draw(pygame.display.get_surface())

    def test_message_sizes_complete_pages_controls_and_confirmation(self):
        view=MessageUI();view.prepare('Uma frase curta.')
        short=view.box.height
        value='Uma mensagem extensa precisa preservar todas as palavras. '*240
        view.prepare(value)
        self.assertGreater(view.box.height,short)
        self.assertLess(view.box.height,400)
        self.assertGreater(len(view.pages),1)
        self.assertEqual(' '.join(line for page in view.pages for line in page).split(),value.split())
        for index in range(len(view.pages)):
            view.page=index;view.prepare(value)
            for rect,_ in view.buttons.values():self.assertFalse(view.body.colliderect(rect))
            view.draw(pygame.display.get_surface())
        view.prepare('Dormir?',True,'confirmation')
        self.assertEqual(view.page,0)
        self.assertEqual(view.handle_event(pygame.event.Event(pygame.KEYDOWN,key=pygame.K_RETURN)),'confirm')
        self.assertEqual(view.handle_event(pygame.event.Event(pygame.KEYDOWN,key=pygame.K_ESCAPE)),'close')
