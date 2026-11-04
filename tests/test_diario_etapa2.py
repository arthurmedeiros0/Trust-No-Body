"""Etapa 2: rascunhos, progressão real, editor e sobreposição sem perder contexto."""
import os
os.environ.setdefault('SDL_VIDEODRIVER','dummy')
os.environ.setdefault('SDL_AUDIODRIVER','dummy')
import random
import unittest
from dataclasses import asdict
from unittest.mock import Mock,patch
import pygame
from casa.visitors import VisitorSession
from casa.visitor_ui import VisitorUI
from casa.visitor_dialogue import Dialogue
from casa.diario_ui import JournalUI
from casa.diario import MARKS,CONCLUSIONS
from casa.medical_knowledge import LABELS
from casa.game import House
from casa import ui_theme as theme,face_portraits

class JournalStageTwoTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):pygame.init();pygame.display.set_mode((1280,720))

    def setUp(self):
        self.s=VisitorSession(random.Random(10));self.j=self.s.journal
        self.ui=JournalUI(self.s);self.screen=pygame.display.get_surface()

    def visit(self,key='ricardo'):
        v=self.s.visitors[key];v.arrived=True;self.s._arrive(v);return v

    def accept(self,key='ricardo'):
        v=self.visit(key);self.s.manager.current=key
        self.assertTrue(self.s.decide(v,'acolhido'));return v

    def watch(self,day):
        self.s.days.day=max(day,self.s.day);self.s.news.unlock(self.s.day)
        self.s.news.watch(self.s.news.current(day))

    def key(self,target,key):target.handle_event(pygame.event.Event(pygame.KEYDOWN,key=key))

    def click_ui(self,kind,value):
        self.ui.draw(self.screen)
        if (kind,value) not in self.ui.buttons:
            for scroll in range(0,self.ui.max_scroll+101,100):
                self.ui.scroll=scroll;self.ui.draw(self.screen)
                if (kind,value) in self.ui.buttons:break
        self.ui.handle_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN,button=1,pos=self.ui.buttons[(kind,value)].center))

    def test_waiting_and_conversation_only_create_draft(self):
        v=self.visit();d=Dialogue(v,self.s);self.assertTrue(d.ask(0))
        self.assertFalse(self.j.cases);self.assertIn(v.id,self.j.drafts)
        self.assertEqual(len(self.j.drafts[v.id].conversations),1)
        self.j.meet(v,1);self.assertEqual(len(self.j.timeline),1)
        self.ui.open(v.id);self.ui.draw(self.screen)
        self.assertIn(('draft',v.id),self.ui.buttons);self.assertNotIn(('case',v.id),self.ui.buttons)
        self.ui.close();self.ui.open();self.assertIsNone(self.ui.current_case())
        self.assertIn(v.id,self.j.drafts)

    def test_rejected_never_becomes_permanent_even_after_conversation(self):
        v=self.visit();Dialogue(v,self.s).ask(0)
        self.s.manager.current=v.id;self.assertTrue(self.s.decide(v,'rejeitado'))
        self.assertFalse(self.j.cases);self.assertNotIn(v.id,self.j.drafts)
        self.j.conversation(v,2,'Pergunta posterior','Sem ficha')
        self.assertFalse(self.j.cases);self.assertFalse(self.j.drafts)
        self.assertIn((1,'Ricardo: rejeitado.'),self.j.timeline)

    def test_draft_is_promoted_without_copying_or_losing_notes(self):
        v=self.visit();record=self.j.drafts[v.id]
        record.notes='Mãos com graxa? Preciso observar.';record.conclusion=CONCLUSIONS[2]
        record.marks['manchas_maos']=MARKS[1];Dialogue(v,self.s).ask(0)
        self.s.manager.current=v.id;self.s.days.day=3
        self.assertTrue(self.s.decide(v,'acolhido'))
        self.assertIs(record,self.j.cases[v.id]);self.assertNotIn(v.id,self.j.drafts)
        self.assertEqual(record.arrival,1);self.assertEqual(record.accepted_day,3)
        self.assertEqual(record.notes,'Mãos com graxa? Preciso observar.')
        self.assertEqual(record.conclusion,CONCLUSIONS[2]);self.assertEqual(len(record.conversations),1)
        self.assertEqual(record.marks['manchas_maos'],MARKS[1])

    def test_elimination_preserves_data_and_strikes_both_names(self):
        v=self.accept();case=self.j.cases[v.id];case.notes='Registro anterior'
        case.marks['olhos_alterados']=MARKS[2];Dialogue(v,self.s,True).ask(0)
        before=(case.notes,dict(case.marks),list(case.conversations),v.diagnosis)
        self.s.days.day=8;sanity=self.s.survival.sanity
        self.assertTrue(self.s.eliminate(v.id));self.assertEqual(case.eliminated_day,8)
        self.assertEqual(self.s.survival.sanity,sanity-(2 if v.diagnosis=='infectado' else 3))
        self.assertEqual(before,(case.notes,dict(case.marks),list(case.conversations),v.diagnosis))
        self.ui.open(v.id);self.ui.draw(self.screen)
        self.assertEqual({where for where,key,_ in self.ui.struck_names if key==v.id},{'sidebar','sheet'})
        self.assertEqual(case.situation,'eliminado')

    def test_symptoms_require_watched_bulletins_and_recap_uses_known(self):
        v=self.accept();self.ui.open(v.id)
        self.s.days.day=17;self.s.news.unlock(17);self.ui.draw(self.screen)
        self.assertFalse(self.s.medical.known)
        self.assertFalse(any(kind=='mark' for kind,_ in self.ui.buttons))
        expected=set()
        for day,new in ((4,('manchas_maos','dentes_deteriorados')),(7,('olhos_alterados',)),(10,('veias_escurecidas','palidez_anormal')),(14,('tremores_involuntarios',)),(17,())):
            self.watch(day);expected.update(new);self.assertEqual(self.s.medical.known,expected)
            self.ui.scroll=0;self.ui.draw(self.screen)
            for kind,value in self.ui.buttons:
                if kind=='mark':self.assertIn(value[0],expected)
        self.assertEqual(len(expected),6)
        # Uma recapitulação tardia aprende o conteúdo real, sem exigir os dias anteriores.
        late=VisitorSession(random.Random(2));late.days.day=14;late.news.unlock(14);late.news.watch(late.news.current(14))
        self.assertEqual(late.medical.known,set(LABELS))
        self.assertFalse(late.news.current(7).read)

    def test_manual_marks_ignore_actual_exams_and_can_be_changed(self):
        v=self.accept();self.watch(7);self.ui.open(v.id)
        case=self.j.cases[v.id];actual=dict(v.symptoms)
        view=VisitorUI(v,None,lambda *a:False,knowledge=self.s.medical,session=self.s)
        view.page='investigate';rect=view.layout()['olhos_alterados'][0]
        view.handle_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN,button=1,pos=rect.center))
        self.assertEqual(case.examined_days['olhos_alterados'],7)
        self.assertEqual(case.marks['olhos_alterados'],MARKS[0])
        self.s.days.day=9;self.j.examination(v,'olhos_alterados',9)
        self.assertEqual(case.examined_days['olhos_alterados'],7)
        for value in (MARKS[1],MARKS[2],MARKS[0]):
            self.click_ui('mark',('olhos_alterados',value));self.assertEqual(case.marks['olhos_alterados'],value)
        self.assertEqual(v.symptoms,actual)

    def test_exam_status_does_not_read_results_or_call_classifier(self):
        v=self.accept();self.watch(7)
        self.s.medical.observe(v,'olhos_alterados');self.j.examination(v,'olhos_alterados',7)
        self.s.diagnosticar_visitante=Mock(side_effect=AssertionError('Não deve diagnosticar'))
        self.s.medical.status=Mock(side_effect=AssertionError('Não deve ler resultado'))
        self.ui.open(v.id);self.ui.scroll=220
        with patch.object(theme,'text',wraps=theme.text) as drawing:
            self.ui.draw(self.screen)
            texts=[args.args[1] for args in drawing.call_args_list]
            self.assertIn('Exame realizado · dia 7',texts)
        self.s.diagnosticar_visitante.assert_not_called();self.s.medical.status.assert_not_called()
        record=asdict(self.j.cases[v.id])
        for field in ('symptoms','diagnosis','infection_pattern'):self.assertNotIn(field,record)

    def test_watched_news_patterns_and_chronological_timeline(self):
        self.s.days.day=17;self.s.news.unlock(17);self.watch(17);self.watch(7)
        self.ui.tab='Noticiários'
        with patch.object(theme,'text',wraps=theme.text) as drawing:
            self.ui.draw(self.screen)
            text='\n'.join(args.args[1] for args in drawing.call_args_list)
            self.assertIn('Primeiro padrão',text);self.assertIn('Terceiro padrão',text)
            self.assertNotIn('Segundo padrão',text)
            future=next(b for b in self.s.news.bulletins if b.day==20)
            self.assertNotIn(future.headline,text)
        self.j.timeline=[(7,'Mais tarde'),(1,'Mais cedo'),(7,'Mesmo dia')]
        self.ui.tab='Linha do Tempo';self.ui.scroll=0
        with patch.object(theme,'text',wraps=theme.text) as drawing:
            self.ui.draw(self.screen)
            texts=[args.args[1] for args in drawing.call_args_list]
            self.assertLess(texts.index('Mais cedo'),texts.index('Mais tarde'))
            self.assertLess(texts.index('Mais tarde'),texts.index('Mesmo dia'))

    def test_normal_face_shared_with_stage_one(self):
        v=self.accept();self.ui.open(v.id)
        with patch.object(face_portraits,'draw',wraps=face_portraits.draw) as draw:
            self.ui.draw(self.screen);draw.assert_called_once()
            self.assertIs(draw.call_args.args[1],v.definition)
            self.assertGreaterEqual(draw.call_args.args[2].width,140)

    def test_editor_unicode_arrows_j_and_separate_records(self):
        self.accept();self.accept('laura');self.ui.open('ricardo');self.ui.change_tab('Anotações')
        self.ui.focus(True)
        self.ui.handle_event(pygame.event.Event(pygame.TEXTINPUT,text='Antônio e João.\nOutra observação.'))
        before=self.ui.cursor;self.key(self.ui,pygame.K_UP);self.assertLess(self.ui.cursor,before)
        self.key(self.ui,pygame.K_DOWN);self.assertEqual(self.ui.cursor,before)
        self.key(self.ui,pygame.K_j);self.assertTrue(self.ui.active)
        self.ui.handle_event(pygame.event.Event(pygame.TEXTINPUT,text='J'))
        self.key(self.ui,pygame.K_LEFT);self.key(self.ui,pygame.K_DELETE)
        self.key(self.ui,pygame.K_BACKSPACE);self.key(self.ui,pygame.K_RETURN)
        saved=self.j.cases['ricardo'].notes
        self.ui.select('laura');self.assertFalse(self.ui.editing);self.ui.focus(True)
        self.ui.handle_event(pygame.event.Event(pygame.TEXTINPUT,text='Texto da Laura'))
        self.ui.select('ricardo');self.assertEqual(self.j.cases['ricardo'].notes,saved)
        self.ui.close();self.ui.open('ricardo');self.assertEqual(self.j.cases['ricardo'].notes,saved)
        self.assertEqual(self.j.cases['laura'].notes,'Texto da Laura')

    def test_long_editor_scroll_cursor_bounds_and_all_character_positions(self):
        self.accept();self.ui.open('ricardo');self.ui.change_tab('Anotações');self.ui.focus(True)
        text=('Observação com acentuação e palavraextensissima. '*100)+'\n'
        self.ui.handle_event(pygame.event.Event(pygame.TEXTINPUT,text=text));self.ui.draw(self.screen)
        positions=self.ui.note_layout(text)
        self.assertEqual([p[0] for p in positions],list(range(len(text)+1)))
        self.assertGreater(self.ui.max_scroll,0)
        _,x,y=positions[self.ui.cursor]
        self.assertTrue(self.ui.notes_area.top<=y-self.ui.scroll<self.ui.notes_area.bottom)
        for _,x,_ in positions:self.assertTrue(self.ui.notes_area.left<=x<=self.ui.notes_area.right)
        for _ in range(20):self.key(self.ui,pygame.K_UP)
        self.assertGreaterEqual(self.ui.scroll,0)

    def test_persistence_through_days_and_fresh_session(self):
        v=self.accept();case=self.j.cases[v.id];case.notes='Suspeita preservada';case.marks['manchas_maos']=MARKS[1]
        self.watch(4);Dialogue(v,self.s).ask(0)
        self.s.manager.plan={};self.s.survival.add_supplies(100,100)
        self.s.days.close_day();self.s.days.advance()
        self.assertEqual(case.notes,'Suspeita preservada');self.assertEqual(case.marks['manchas_maos'],MARKS[1])
        self.assertTrue(case.conversations);self.assertIn('boletim_04',self.j.watched)
        fresh=VisitorSession(random.Random(10)).journal
        self.assertFalse(fresh.cases);self.assertFalse(fresh.drafts);self.assertFalse(fresh.timeline)

    def test_layout_all_tabs_seven_names_and_scroll_limits(self):
        for key in self.s.visitors:self.accept(key)
        self.watch(17);self.ui.open()
        for tab in self.ui.TABS:
            self.ui.change_tab(tab)
            for value in (0,250,999999):
                self.ui.scroll=value;self.ui.draw(self.screen)
                rects=list(self.ui.buttons.items())
                for (kind,_),rect in rects:
                    self.assertTrue(self.screen.get_rect().contains(rect))
                    if kind in ('mark','conclusion'):self.assertTrue(self.ui.body.contains(rect))
                for i,(_,a) in enumerate(rects):
                    for _,b in rects[i+1:]:self.assertFalse(a.colliderect(b))
                self.assertLessEqual(self.ui.scroll,self.ui.max_scroll)
                self.assertEqual(self.screen.get_clip(),self.screen.get_rect())

class JournalModalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):pygame.init();pygame.display.set_mode((1280,720))

    def setUp(self):
        self.g=House();self.g.dialog='';self.g.visitor_session.medical.discoveries.clear()

    def key(self,key):self.g.handle_event(pygame.event.Event(pygame.KEYDOWN,key=key))

    def door(self):
        s=self.g.visitor_session;s.news.watch(s.news.current(1));self.g.observing=True
        return self.g.peephole.visitor_ui

    def test_shortcut_every_room_movement_capture_and_j_close(self):
        for room in self.g.scenes:
            self.g.change_room(room);before=self.g.player.feet.copy()
            self.key(pygame.K_j);self.assertTrue(self.g.journal_ui.active)
            self.g.update((1,1),.2);self.assertEqual(before,self.g.player.feet)
            self.g.draw(pygame.display.get_surface());self.assertTrue(self.g.captures_escape)
            self.key(pygame.K_j);self.assertFalse(self.g.journal_ui.active)
            self.assertEqual(self.g.room,room)

    def test_every_door_stage_returns_same_object_and_full_context(self):
        view=self.door();view.dialogue.ask(0)
        view.response='Resposta extensa para preservar a página. '*80
        for stage in ('intro','talk','answer','investigate','image','confirm'):
            self.g.visitor_session.medical.known.update(LABELS)
            view.page=stage;view.feature='olhos_alterados';view.decision='rejeitado';view.text_page=1
            view.layout() # O contexto inicial precisa representar uma pagina valida.
            before=(view.page,view.feature,view.decision,view.response,view.text_page,set(view.dialogue.progress.asked))
            self.key(pygame.K_j);self.assertTrue(self.g.journal_ui.active)
            self.assertIn(view.visitor.id,self.g.journal_ui.available_records())
            self.assertFalse(self.g.visitor_session.journal.cases)
            self.g.draw(pygame.display.get_surface())
            self.key(pygame.K_ESCAPE);self.assertFalse(self.g.journal_ui.active)
            self.assertIs(self.g.peephole.visitor_ui,view)
            self.assertEqual(before,(view.page,view.feature,view.decision,view.response,view.text_page,set(view.dialogue.progress.asked)))
            self.assertTrue(self.g.observing)

    def test_resident_context_click_capture_and_topmost_layer(self):
        view=self.door();self.g.observing=False
        self.assertTrue(self.g.decide_visitor(view.visitor,'acolhido'))
        self.g.resident_ui=VisitorUI(view.visitor,view.assets,self.g.eliminate_resident,knowledge=self.g.visitor_session.medical,resident=True,session=self.g.visitor_session)
        inside=self.g.resident_ui;inside.page='confirm';inside.decision='eliminado'
        self.key(pygame.K_j);self.assertTrue(self.g.journal_ui.active)
        pos=inside.layout()['confirm'][0].center
        self.g.handle_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN,button=1,pos=pos))
        self.assertEqual(view.visitor.state,'acolhido');self.assertIs(self.g.resident_ui,inside)
        order=[]
        with patch.object(inside,'draw',side_effect=lambda *a:order.append('resident')),patch.object(self.g.journal_ui,'draw',side_effect=lambda *a:order.append('journal')):
            self.g.draw(pygame.display.get_surface())
        self.assertEqual(order,['resident','journal'])
        self.key(pygame.K_ESCAPE);self.assertIs(self.g.resident_ui,inside);self.assertEqual(inside.page,'confirm')

    def test_icon_and_bedroom_object_and_blocked_transitions(self):
        self.g.handle_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN,button=1,pos=self.g.journal_ui.access_rect.center))
        self.assertTrue(self.g.journal_ui.active);self.key(pygame.K_ESCAPE)
        self.g.player.feet=self.g.scene.point((200,425));self.g.interact();self.assertTrue(self.g.journal_ui.active)
        self.key(pygame.K_ESCAPE);self.g.fade.start(lambda:None)
        self.key(pygame.K_j);self.assertFalse(self.g.journal_ui.active)
        self.g.fade=self.g.fade.__class__();self.g.inventory.active=True
        self.key(pygame.K_j);self.assertFalse(self.g.journal_ui.active)
        self.g.inventory.active=False;self.g.visitor_session.survival.alive=False
        self.key(pygame.K_j);self.assertFalse(self.g.journal_ui.active)

    def test_icon_tooltip_and_hud_do_not_overlap(self):
        rect=self.g.journal_ui.access_rect
        hud=pygame.Rect(490,18,*self.g.small.size(self.g.survival_hud()))
        self.assertFalse(hud.colliderect(rect))
        with patch('pygame.mouse.get_pos',return_value=rect.center),patch.object(theme,'text',wraps=theme.text) as drawing:
            self.g.draw(pygame.display.get_surface())
            self.assertIn('Di\u00e1rio [J]',[args.args[1] for args in drawing.call_args_list])

    def test_sleep_and_victory_block_shortcut(self):
        self.g.sleep_transition.start(lambda:None)
        self.key(pygame.K_j);self.assertFalse(self.g.journal_ui.active)
        self.g.sleep_transition.phase=''
        self.g.visitor_session.survival.won=True
        self.key(pygame.K_j);self.assertFalse(self.g.journal_ui.active)

    def test_j_inside_text_is_character_and_underlying_response_is_unchanged(self):
        view=self.door();view.open_conversation();response=view.response
        self.key(pygame.K_j);journal=self.g.journal_ui;journal.change_tab('Anotações');journal.focus(True)
        self.key(pygame.K_j)
        self.g.handle_event(pygame.event.Event(pygame.TEXTINPUT,text='João já chegou.'))
        self.assertTrue(journal.active);self.assertIn('João',self.g.visitor_session.journal.drafts[view.visitor.id].notes)
        self.key(pygame.K_ESCAPE);self.assertEqual(view.response,response)
        self.assertEqual(view.page,'intro');self.assertFalse(journal.editing)

if __name__=='__main__':unittest.main()
