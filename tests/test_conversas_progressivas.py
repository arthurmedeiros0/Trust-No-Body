"""Duas perguntas pendentes, resposta separada e progresso por contexto."""
import random
import unittest
import pygame
from casa.visitors import VisitorSession
from casa.visitor_ui import VisitorUI
from casa.visitor_assets import load_assets
from casa.config import ROOT


class ProgressiveConversationTests(unittest.TestCase):
    def setUp(self):self.session=VisitorSession(random.Random(7))

    def ui(self,key='ricardo',resident=False):
        return VisitorUI(self.session.visitors[key],None,lambda *args:False,
                         knowledge=self.session.medical,session=self.session,resident=resident)

    def click(self,ui,key):
        ui.handle_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN,button=1,pos=ui.layout()[key][0].center))

    def finish_response(self,ui):
        while ui.page in ('intro','answer'):self.click(ui,'continue')

    def test_every_question_reachable_in_any_order_all_visitors_both_contexts(self):
        originals={p:p.read_bytes() for p in (ROOT/'dados/visitantes').glob('*_dialogos.json')}
        for key in self.session.visitors:
            for resident in (False,True):
                with self.subTest(visitor=key,resident=resident):
                    ui=self.ui(key,resident);self.click(ui,'talk');self.finish_response(ui)
                    asked=set();count=len(ui.dialogue.data['questions'])
                    while len(asked)<count:
                        pending=[i for i in range(count) if i not in asked][:2]
                        visible=[int(k) for k in ui.layout() if k.isdigit()]
                        self.assertEqual(visible,pending);self.assertLessEqual(len(visible),2)
                        chosen=visible[-1] if len(asked)%2==0 else visible[0]
                        self.click(ui,str(chosen));asked.add(chosen)
                        self.assertEqual(ui.page,'answer')
                        self.assertFalse(any(k.isdigit() for k in ui.layout()))
                        self.assertEqual(ui.response,ui.dialogue.answer(chosen))
                        self.assertEqual(ui.dialogue.progress.question,chosen)
                        self.assertEqual(ui.dialogue.progress.asked,asked)
                        self.finish_response(ui)
                    self.assertEqual(ui.dialogue.pending(),[])
                    ui.draw(pygame.display.get_surface())
                    self.click(ui,'back');self.click(ui,'talk')
                    self.assertEqual(ui.page,'talk');self.assertFalse(ui.dialogue.pending())
        self.assertEqual(originals,{p:p.read_bytes() for p in originals})

    def test_unselected_question_persists_and_answer_resumes_after_recreating_ui(self):
        ui=self.ui();self.click(ui,'talk');self.finish_response(ui)
        self.assertEqual(ui.dialogue.pending(),[0,1])
        self.click(ui,'1');response=ui.response
        self.click(ui,'back')
        ui=self.ui();self.click(ui,'talk')
        self.assertEqual(ui.page,'answer');self.assertEqual(ui.response,response)
        self.finish_response(ui);self.assertEqual(ui.dialogue.pending(),[0,2])
        self.click(ui,'0');self.finish_response(ui)
        self.assertEqual(ui.dialogue.pending(),[2,3])

    def test_door_resident_other_visitors_and_new_session_have_separate_progress(self):
        door=self.ui();self.click(door,'talk');self.finish_response(door);self.click(door,'0')
        resident=self.ui(resident=True);self.click(resident,'talk')
        self.assertEqual(resident.response,resident.dialogue.intro())
        self.finish_response(resident);self.assertEqual(resident.dialogue.pending(),[0,1])
        self.assertEqual(door.dialogue.progress.asked,{0})
        self.assertFalse(self.ui('laura').dialogue.progress.asked)
        self.assertFalse(VisitorSession(random.Random(7)).visitors['ricardo'].conversations)

    def test_long_response_restores_page_and_continue_reads_every_page(self):
        ui=self.ui();self.click(ui,'talk');self.finish_response(ui)
        ui.dialogue.data['questions'][0]['answer']='Uma lembrança longa. '*200
        self.click(ui,'0');self.click(ui,'text_next');self.assertEqual(ui.text_page,1)
        text=ui.response;self.click(ui,'back')
        ui=self.ui();self.click(ui,'talk')
        self.assertEqual(ui.text_page,1);self.assertEqual(ui.response,text)
        self.click(ui,'continue');self.assertEqual(ui.text_page,2);self.assertEqual(ui.page,'answer')
        self.finish_response(ui);self.assertEqual(ui.dialogue.pending(),[1,2])

    def test_conversation_geometry_preserves_portrait_and_separates_regions(self):
        for key in self.session.visitors:
            ui=self.ui(key);ui.assets=load_assets(ui.visitor.definition)
            original=pygame.image.tobytes(ui.assets.portrait,'RGBA')
            self.click(ui,'talk')
            for stage in ('intro','talk','answer'):
                self.assertEqual(ui.page,stage)
                for rect,_ in ui.layout().values():
                    self.assertTrue(pygame.Rect(0,0,1280,720).contains(rect))
                    if stage!='talk':self.assertFalse(ui.speech_rect().inflate(24,16).colliderect(rect))
                ui.draw_portrait(pygame.display.get_surface());ui.draw(pygame.display.get_surface())
                if stage=='intro':self.finish_response(ui)
                elif stage=='talk':self.click(ui,'0')
            self.assertEqual(original,pygame.image.tobytes(ui.assets.portrait,'RGBA'))

    def test_dynamic_supplies_and_decisions_do_not_require_exhausting_questions(self):
        ui=self.ui('laura');self.click(ui,'talk');self.finish_response(ui)
        self.click(ui,'0');self.finish_response(ui)
        self.click(ui,'2')
        v=ui.visitor
        self.assertIn(str(v.food)+' lata',ui.response);self.assertIn(str(v.water)+' garrafa',ui.response)
        from casa.game import House
        for decision,button in (('acolhido','accept'),('rejeitado','reject')):
            game=House();s=game.visitor_session;s.start_test('ricardo','padrao_3')
            door=game.peephole.visitor_ui
            self.click(door,'talk');self.click(door,'back')
            self.assertFalse(door.dialogue.progress.asked)
            self.click(door,'investigate');self.click(door,'olhos_alterados');self.click(door,'back');self.click(door,'back')
            self.click(door,button);self.click(door,'confirm')
            self.assertEqual(s.visitors['ricardo'].state,decision)
