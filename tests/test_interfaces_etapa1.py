"""Regressões visuais e funcionais da Etapa 1, sem substituir as regras do jogo."""
import os
os.environ.setdefault('SDL_VIDEODRIVER','dummy')
os.environ.setdefault('SDL_AUDIODRIVER','dummy')
import random
import unittest
from unittest.mock import patch
import pygame
from casa.visitors import VisitorSession
from casa.visitor_ui import VisitorUI
from casa.visitor_assets import load_assets,fit
from casa.television import Television
from casa import face_portraits,ui_theme as theme,visitor_presentation as presentation

class InterfaceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init();pygame.display.set_mode((1280,720))

    def setUp(self):
        self.session=VisitorSession(random.Random(8))
        self.screen=pygame.display.get_surface()

    def view(self,key='ricardo',resident=False):
        v=self.session.visitors[key]
        return VisitorUI(v,load_assets(v.definition),lambda *a:False,knowledge=self.session.medical,resident=resident,session=self.session)

    def click(self,view,key):
        view.handle_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN,button=1,pos=view.layout()[key][0].center))

    def geometry(self,entries):
        rects=[rect for rect,_ in entries.values()]
        for i,rect in enumerate(rects):
            self.assertTrue(self.screen.get_rect().contains(rect))
            for other in rects[i+1:]:self.assertFalse(rect.colliderect(other))

    def test_normal_faces_for_all_seven_and_missing_asset_fallback(self):
        for v in self.session.visitors.values():
            with self.subTest(visitor=v.id):
                image=face_portraits.face(v.definition)
                self.assertIsNotNone(image)
                d=v.definition
                normal=str(face_portraits.ROOT/d['asset_root']/d['investigation']['palidez_anormal']['normal'])
                with patch.object(face_portraits,'_load',return_value=image) as loader:
                    self.assertIs(face_portraits.face(d),image)
                    self.assertEqual(loader.call_args.args[0],normal)
                before=pygame.image.tobytes(image,'RGBA')
                face_portraits.draw(self.screen,d,(20,20,124,146))
                self.assertEqual(before,pygame.image.tobytes(image,'RGBA'))
                fitted=fit(image,(116,138))
                self.assertLess(abs(fitted.get_width()/fitted.get_height()-image.get_width()/image.get_height()),.03)
        face_portraits.draw(self.screen,{'id':'missing','name':'Sem rosto'},(0,0,124,146))
        with patch.object(face_portraits,'_load',side_effect=pygame.error('missing')):
            face_portraits.draw(self.screen,self.session.visitors['ricardo'].definition,(0,0,124,146))

    def test_dialogue_states_layout_and_two_choices_for_all_visitors(self):
        for key in self.session.visitors:
            for resident in (False,True):
                view=self.view(key,resident);self.click(view,'talk')
                while view.page=='intro':self.click(view,'continue')
                seen=set()
                while view.dialogue.pending():
                    entries=view.layout();self.geometry(entries)
                    questions=[k for k in entries if k.isdigit()]
                    self.assertLessEqual(len(questions),2)
                    selected=int(questions[-1]);self.assertNotIn(selected,seen);seen.add(selected)
                    self.click(view,str(selected))
                    while view.page=='answer':
                        self.geometry(view.layout())
                        view.draw(self.screen);self.click(view,'continue')
                self.assertEqual(len(seen),len(view.dialogue.data['questions']))
                self.assertEqual(view.dialogue.progress.asked,seen)

    def test_inspection_layout_scales_with_count_and_every_image_keeps_ratio(self):
        for key in self.session.visitors:
            view=self.view(key);features=list(view.visitor.definition['investigation'])
            for count in range(1,7):
                view.knowledge.known=set(features[:count]);view.page='investigate'
                self.geometry(view.layout());view.draw(self.screen)
                self.assertEqual(len(view.layout()),count+1)
            for feature in features:
                view.page='investigate';self.click(view,feature)
                self.assertIn(feature,view.visitor.examined)
                source=view.examination_image();image=fit(source,(1056,428))
                self.assertLess(abs(image.get_width()/image.get_height()-source.get_width()/source.get_height()),.03)
                view.draw(self.screen)
                case=self.session.journal.cases.get(key)
                if case:self.assertEqual(set(case.marks.values()),{'Não verificado'})

    def test_danger_is_separated_and_confirmation_has_no_secret_or_penalty(self):
        v=self.session.visitors['ricardo'];v.state='acolhido'
        view=self.view(resident=True);actions=view.layout();danger=actions['eliminate'][0]
        for key in ('talk','investigate'):
            if key in actions:self.assertGreaterEqual(danger.left-actions[key][0].right,40)
        self.click(view,'eliminate');self.geometry(view.layout())
        speech=view.speech().lower()
        for hidden in ('infectado','saudável','saudavel','-2','-3'):self.assertNotIn(hidden,speech)
        self.assertIn('irreversível',speech)
        self.assertEqual(view.layout()['confirm'][1],'Confirmar eliminação')
        view.draw(self.screen)

    def test_decisions_work_without_exhausting_questions(self):
        for decision,button in (('acolhido','accept'),('rejeitado','reject')):
            s=VisitorSession(random.Random(8));v=s.visitors['ricardo'];v.arrived=True;s.manager.current=v.id
            s._arrive(v)
            view=VisitorUI(v,None,s.decide,knowledge=s.medical,session=s)
            self.click(view,'talk');self.click(view,'back');self.click(view,button);self.click(view,'confirm')
            self.assertEqual(v.state,decision);self.assertFalse(view.dialogue.progress.asked)
            if decision=='acolhido':
                before=s.survival.sanity
                inside=VisitorUI(v,None,lambda visitor,action:s.eliminate(visitor.id),resident=True,session=s)
                self.click(inside,'eliminate');self.click(inside,'confirm')
                self.assertEqual(v.state,'eliminado');self.assertLess(s.survival.sanity,before)

    def test_all_bulletins_are_complete_paginated_and_originals_preserved(self):
        s=self.session;tv=Television(s.news,s.days);s.news.unlock(20)
        originals=[(b.headline,list(b.paragraphs),b.day,tuple(b.investigations)) for b in s.news.bulletins]
        for b in s.news.bulletins:
            s.days.day=b.day;tv.choose('current')
            pages=tv.report_pages()
            self.assertEqual(' '.join(line for page in pages for line in page).split(),' '.join(b.paragraphs).split())
            self.assertLessEqual(len(theme.wrapped_lines(b.headline,948,tv.headline)),2)
            self.assertLessEqual(len(theme.wrapped_lines(b.headline,704,theme.font(22))),2)
            for page in range(len(pages)):
                tv.report_page=page;tv.draw(self.screen)
                self.geometry({key:(rect,label) for key,rect,label in tv.layout()})
        self.assertEqual(originals,[(b.headline,list(b.paragraphs),b.day,tuple(b.investigations)) for b in s.news.bulletins])

    def test_tv_history_navigation_and_watch_unlocks_only_chosen_bulletin(self):
        s=self.session;s.days.day=17;s.news.unlock(17)
        tv=Television(s.news,s.days);tv.open();tv.choose('history')
        found=set()
        for _ in range(3):
            found.update(key for key,_,_ in tv.layout() if key.startswith('news:'));tv.choose('next')
        self.assertEqual(len(found),16);self.assertFalse(any(b.read for b in s.news.bulletins))
        tv.choose('news:boletim_07');self.assertEqual(tv.bulletin.day,7)
        self.assertTrue(tv.bulletin.read);self.assertIn('manchas_maos',s.medical.known)
        self.assertFalse(s.news.current(17).read)
        tv.choose('back');self.assertEqual(tv.page,'history')
        tv.choose('back');tv.choose('current');self.assertEqual(tv.bulletin.day,17)
        self.assertEqual(set(s.knowledge.published),{'boletim_07','boletim_17'})

    def test_long_tv_pages_keyboard_mouse_and_bounds(self):
        s=self.session;tv=Television(s.news,s.days);tv.open();tv.choose('current')
        b=tv.bulletin;original=b.paragraphs
        try:
            b.paragraphs=['Uma transmissão extensa precisa preservar cada palavra. '*120]
            count=len(tv.report_pages());self.assertGreater(count,1)
            tv.handle_event(pygame.event.Event(pygame.KEYDOWN,key=pygame.K_RIGHT));self.assertEqual(tv.report_page,1)
            tv.handle_event(pygame.event.Event(pygame.MOUSEWHEEL,y=-1));self.assertEqual(tv.report_page,2)
            for _ in range(count+2):tv.choose('report_next')
            self.assertEqual(tv.report_page,count-1);self.assertTrue(tv.disabled('report_next'))
            tv.draw(self.screen)
            for _ in range(count+2):tv.choose('report_prev')
            self.assertEqual(tv.report_page,0)
        finally:b.paragraphs=original

    def test_shared_button_hover_pressed_disabled_and_clipping(self):
        rect=pygame.Rect(10,10,200,44)
        images=[]
        for point,down,disabled in (((0,0),False,False),((20,20),False,False),((20,20),True,False),((20,20),False,True)):
            with patch('pygame.mouse.get_pos',return_value=point),patch('pygame.mouse.get_pressed',return_value=(down,False,False)):
                image=pygame.Surface((230,80));theme.button(image,rect,'Eliminar',danger=True,disabled=disabled)
                images.append(pygame.image.tobytes(image,'RGB'))
        self.assertEqual(len(set(images)),4)
        clip=pygame.Rect(20,20,40,40);self.screen.set_clip(clip)
        theme.text(self.screen,'Uma fala longa. '*100,pygame.Rect(10,10,80,80))
        self.assertEqual(self.screen.get_clip(),clip);self.screen.set_clip(None)

if __name__=='__main__':unittest.main()
