"""Limites reais de renderização e acesso integral às falas dos sete visitantes."""
import random
import unittest
import pygame
from casa.visitors import VisitorSession
from casa.visitor_ui import VisitorUI
from casa.visitor_assets import load_assets


class PaginatedDialogueTests(unittest.TestCase):
    def setUp(self):
        self.session=VisitorSession(random.Random(8))

    def ui(self,key='ricardo',resident=False):
        return VisitorUI(self.session.visitors[key],None,lambda *args:False,
                         resident=resident,knowledge=self.session.medical,session=self.session)

    def click(self,ui,key):
        ui.handle_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN,button=1,pos=ui.layout()[key][0].center))

    def assert_readable(self,ui,text):
        ui.response=text
        rect=ui.speech_rect()
        pages=ui.text_pages(text,rect)
        self.assertEqual(' '.join(line for page in pages for line in page).split(),text.split())
        for page in pages:
            self.assertLessEqual(len(page)*max(26,ui.font.get_linesize()),rect.height)
            for line in page:self.assertLessEqual(ui.font.size(line)[0],rect.width)
        for page in range(len(pages)):
            self.assertEqual(ui.text_page,page)
            for button,_ in ui.layout().values():
                self.assertFalse(rect.inflate(24,16).colliderect(button))
            ui.draw(pygame.display.get_surface())
            if page<len(pages)-1:self.click(ui,'text_next')
        self.assertNotIn('text_next',ui.layout())

    def test_all_original_intros_answers_and_resident_lines_fit_without_loss(self):
        for key in self.session.visitors:
            for resident in (False,True):
                with self.subTest(visitor=key,resident=resident):
                    ui=self.ui(key,resident);self.click(ui,'talk')
                    self.assert_readable(ui,ui.dialogue.intro())
                    self.click(ui,'continue')
                    for index,item in enumerate(ui.dialogue.data['questions']):
                        button,_=ui.layout()[str(index)]
                        self.assertLessEqual(ui.small.size(item['question'])[0],button.width-8)
                        self.assertLessEqual(ui.small.get_height(),button.height-2)
                        self.click(ui,str(index));self.assertEqual(ui.text_page,0)
                        self.assert_readable(ui,ui.dialogue.answer(index))
                        self.click(ui,'continue')

    def test_short_and_very_long_responses_root_talk_and_confirmation(self):
        for resident in (False,True):
            ui=self.ui(resident=resident)
            for page in ('root','intro'):
                ui.page=page
                for text in ('Sim.','\n\n'.join(['Uma fala extensa precisa continuar legível sem perder palavras.']*90)):
                    with self.subTest(resident=resident,page=page,long=len(text)>10):
                        self.assert_readable(ui,text)
            ui.decision='eliminado' if resident else 'acolhido';ui.page='confirm';ui.text_page=0
            if not resident:ui.dialogue.data['before_decision']=['Uma recordação muito longa. '*150]
            pages=ui.text_pages(ui.speech(),ui.speech_rect())
            for index in range(len(pages)):
                ui.text_page=index
                for button,_ in ui.layout().values():
                    self.assertFalse(ui.speech_rect().inflate(24,16).colliderect(button))
                ui.draw(pygame.display.get_surface())

    def test_renderer_clips_height_width_and_preserves_caller_clip(self):
        ui=self.ui();screen=pygame.Surface((320,220),pygame.SRCALPHA)
        rect=pygame.Rect(35,40,160,52)
        clip=pygame.Rect(40,45,140,90)
        for page in range(len(ui.text_pages('Palavra longa e outras palavras. '*100,rect))):
            screen.fill((0,0,0,0));screen.set_clip(clip)
            ui.text(screen,'Palavra longa e outras palavras. '*100,rect,page)
            bounds=screen.get_bounding_rect()
            self.assertTrue(bounds.width>0)
            self.assertTrue(rect.contains(bounds));self.assertTrue(clip.contains(bounds))
            self.assertEqual(screen.get_clip(),clip)

    def test_long_unbroken_word_and_paragraphs_preserve_every_character(self):
        ui=self.ui();rect=pygame.Rect(0,0,120,52)
        word='abcdef'*100
        pages=ui.text_pages(word,rect)
        self.assertEqual(''.join(line for page in pages for line in page),word)
        for page in pages:
            for line in page:self.assertLessEqual(ui.font.size(line)[0],rect.width)
        lines=ui.wrapped_lines('Primeiro parágrafo.\n\nSegundo parágrafo.',180)
        self.assertIn('',lines)

    def test_mouse_keyboard_navigation_bounds_and_new_answer_resets_page(self):
        ui=self.ui();ui.page='intro';ui.response='Uma fala longa. '*200
        ui.handle_event(pygame.event.Event(pygame.KEYDOWN,key=pygame.K_LEFT))
        self.assertEqual(ui.text_page,0)
        self.click(ui,'text_next');self.assertEqual(ui.text_page,1)
        ui.handle_event(pygame.event.Event(pygame.KEYDOWN,key=pygame.K_PAGEDOWN))
        self.assertEqual(ui.text_page,2)
        self.click(ui,'text_prev');self.assertEqual(ui.text_page,1)
        while ui.page=='intro':self.click(ui,'continue')
        self.click(ui,'0');self.assertEqual(ui.text_page,0)
        self.assertEqual(ui.response,ui.dialogue.answer(0))
        ui.response='Uma fala longa. '*200;self.click(ui,'text_next')
        ui.handle_event(pygame.event.Event(pygame.KEYDOWN,key=pygame.K_ESCAPE))
        self.assertEqual(ui.page,'root');self.assertEqual(ui.text_page,0)
        self.assertTrue({'talk','accept','reject','back'}<=set(ui.layout()))

    def test_portrait_identity_and_dimensions_preserved_across_dialogue_pages(self):
        ui=self.ui();ui.assets=load_assets(ui.visitor.definition)
        portrait=ui.assets.portrait;size=portrait.get_size()
        pixels=pygame.image.tobytes(portrait,'RGBA')
        self.click(ui,'talk');ui.response='Uma fala longa. '*200
        screen=pygame.display.get_surface()
        for _ in range(3):
            ui.draw_portrait(screen);ui.draw(screen);self.click(ui,'text_next')
        self.assertIs(ui.assets.portrait,portrait)
        self.assertEqual(portrait.get_size(),size)
        self.assertEqual(pygame.image.tobytes(portrait,'RGBA'),pixels)
