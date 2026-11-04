"""Diário: privacidade, eventos reais, controles e persistência da sessão."""
import os
os.environ.setdefault('SDL_VIDEODRIVER','dummy')
os.environ.setdefault('SDL_AUDIODRIVER','dummy')
import random
import unittest
from unittest.mock import Mock
import pygame
from casa.visitors import VisitorSession
from casa.visitor_dialogue import Dialogue
from casa.visitor_ui import VisitorUI
from casa.diario_ui import JournalUI
from casa.diario import MARKS,CONCLUSIONS,PATTERNS
from casa.game import House

class JournalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init();pygame.display.set_mode((1280,720))

    def setUp(self):
        self.session=VisitorSession(random.Random(7))
        self.j=self.session.journal
        self.ui=JournalUI(self.session)

    def arrive(self,key='ricardo'):
        v=self.session.visitors[key];v.arrived=True;self.session._arrive(v)
        return v

    def click(self,kind,value):
        self.ui.draw(pygame.display.get_surface())
        rect=self.ui.buttons[(kind,value)]
        self.ui.handle_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN,button=1,pos=rect.center))

    def test_only_encountered_and_independent_cases(self):
        self.assertFalse(self.j.cases)
        self.arrive();self.arrive('laura');self.arrive()
        self.assertEqual(list(self.j.cases),['ricardo','laura'])
        self.assertEqual(len(self.j.timeline),2)
        self.ui.open()
        for key in self.j.cases:
            self.click('case',key);self.assertEqual(self.ui.selected,key)
            self.assertEqual(set(self.j.cases[key].marks.values()),{MARKS[0]})

    def test_exams_do_not_fill_manual_marks_and_wrong_conclusions_persist(self):
        v=self.arrive();self.ui.open();case=self.j.cases[v.id]
        self.session.medical.learn(v.symptoms)
        for key in v.symptoms:self.session.medical.observe(v,key)
        self.assertEqual(set(case.marks.values()),{MARKS[0]})
        for key in case.marks:
            for expected in (MARKS[1],MARKS[2],MARKS[0],MARKS[1]):
                self.click('mark',key);self.assertEqual(case.marks[key],expected)
        self.ui.scroll=180;self.click('conclusion','');self.click('conclusion','')
        self.assertEqual(case.conclusion,CONCLUSIONS[2])
        self.session.set_condition(v,random.Random(3),'infectado')
        actual=v.diagnosis
        self.ui.handle_event(pygame.event.Event(pygame.KEYDOWN,key=pygame.K_ESCAPE))
        self.ui.open();self.assertEqual(case.conclusion,CONCLUSIONS[2]);self.assertEqual(v.diagnosis,actual)

    def test_watched_history_patterns_and_timeline(self):
        self.session.news.unlock(17)
        self.ui.tab='Noticiários';self.ui.draw(pygame.display.get_surface())
        self.assertFalse(self.j.watched)
        for day in (7,14,17):
            b=self.session.news.current(day);self.session.news.watch(b);self.session.news.watch(b)
            self.assertIn(b.id,self.j.watched);self.assertIn(b.id,PATTERNS)
        self.assertEqual(len(self.j.watched),3)
        self.assertEqual(sum('Assistiu' in t for _,t in self.j.timeline),3)
        self.assertFalse(any(b.read for b in self.session.news.bulletins if b.day not in (7,14,17)))
        self.ui.draw(pygame.display.get_surface())

    def test_dynamic_answers_snapshot_and_no_future_questions(self):
        v=self.arrive('marina');d=Dialogue(v,self.session)
        self.assertFalse(self.j.cases[v.id].conversations)
        self.assertTrue(d.ask(d.pending()[0]))
        records=self.j.cases[v.id].conversations
        self.assertEqual(len(records),1)
        self.assertEqual(records[0][2],d.progress.answer_text)
        original=records[0]
        self.arrive();self.session.visitors['ricardo'].state='rejeitado'
        self.assertEqual(records[0],original)
        self.assertFalse(d.ask(d.progress.question));self.assertEqual(len(records),1)

    def test_unicode_editing_cursor_scroll_and_reopen(self):
        self.arrive();self.ui.open();self.ui.tab='Anotações';self.ui.focus(True)
        def key(k):self.ui.handle_event(pygame.event.Event(pygame.KEYDOWN,key=k))
        def text(t):self.ui.handle_event(pygame.event.Event(pygame.TEXTINPUT,text=t))
        text('Antônio, mãos e saúde.');key(pygame.K_LEFT);key(pygame.K_BACKSPACE);text('!')
        case=self.j.cases['ricardo'];self.assertIn('Antônio',case.notes)
        key(pygame.K_END);key(pygame.K_RETURN);text('observação longa '*800)
        self.ui.draw(pygame.display.get_surface());self.assertGreater(self.ui.max_scroll,0)
        saved=case.notes;key(pygame.K_ESCAPE);self.ui.open();self.assertEqual(case.notes,saved)
        self.assertFalse(self.ui.editing)

    def test_decisions_days_new_session_and_internal_logic(self):
        v=self.arrive();self.session.manager.current=v.id
        case=self.j.cases[v.id];case.notes='Minha suspeita';case.conclusion=CONCLUSIONS[1]
        self.assertTrue(self.session.decide(v,'acolhido'))
        self.assertEqual(case.situation,'acolhido')
        self.session.survival.add_supplies(100,100)
        self.session.intro.broadcast_seen=True
        self.session.days.close_day();self.session.days.advance()
        self.assertEqual(case.notes,'Minha suspeita')
        self.assertTrue(self.session.eliminate(v.id));self.assertEqual(case.situation,'eliminado')
        self.assertEqual(self.session.diagnosticar_visitante(v.id),'inconclusivo')
        self.assertFalse(VisitorSession(random.Random(7)).journal.cases)
        self.assertFalse(any(v.diagnosis in text for _,text in self.j.timeline))

    def test_room_range_modal_movement_escape_and_restart(self):
        game=House();game.dialog='';game.visitor_session.medical.discoveries.clear()
        item=next(i for i in game.scene.interactions if i.action=='journal')
        self.assertEqual(item.point,game.scene.point((160,390)))
        for period in ('dia','noite'):
            game.period=period;game.player.feet=game.scene.point((200,425))
            self.assertTrue(game.scene.collisions.allows(game.player.feet))
            self.assertEqual(game.nearest_interaction(),item)
            game.interact();self.assertTrue(game.journal_ui.active)
            before=game.player.feet.copy();game.update((1,0),.2)
            self.assertEqual(game.player.feet,before);self.assertTrue(game.captures_escape)
            game.handle_event(pygame.event.Event(pygame.KEYDOWN,key=pygame.K_i))
            self.assertFalse(game.inventory.active)
            game.handle_event(pygame.event.Event(pygame.KEYDOWN,key=pygame.K_ESCAPE))
            self.assertFalse(game.journal_ui.active)
        game.player.feet=game.scene.point((450,360));game.interact();self.assertFalse(game.journal_ui.active)
        game.change_room('sala');game.interact();self.assertFalse(game.journal_ui.active)
        game.visitor_session.survival.alive=False
        game.handle_event(pygame.event.Event(pygame.KEYDOWN,key=pygame.K_r))
        self.assertFalse(game.visitor_session.journal.cases)

    def test_rejection_is_known_without_hidden_condition(self):
        v=self.arrive();self.session.manager.current=v.id
        self.assertTrue(self.session.decide(v,'rejeitado'))
        self.assertEqual(self.j.cases[v.id].situation,'rejeitado')
        self.assertEqual(self.j.timeline[-1],(1,'Ricardo: rejeitado.'))

    def test_all_sections_long_pages_and_all_visitors_render(self):
        for key in self.session.visitors:self.arrive(key)
        self.ui.open()
        screen=pygame.display.get_surface()
        for key in self.j.cases:
            self.ui.selected=key
            for tab in self.ui.TABS:
                self.ui.tab=tab;self.ui.scroll=0;self.ui.draw(screen)
                self.ui.scroll=self.ui.max_scroll;self.ui.draw(screen)
                self.assertEqual(screen.get_clip(),screen.get_rect())
                for (kind,_),rect in self.ui.buttons.items():
                    self.assertTrue(screen.get_rect().contains(rect))
                    if kind in ('mark','conclusion'):self.assertTrue(self.ui.body.contains(rect))

    def test_diagnostic_ui_never_calls_internal_classifier(self):
        v=self.arrive();ui=VisitorUI(v,None,lambda *a:False,session=self.session)
        self.session.diagnosticar_visitante=Mock(side_effect=AssertionError('diagnosis leaked'))
        for page in ('root','investigate','image'):
            ui.page=page;self.assertIsNone(ui.diagnosis_indicator())
        self.session.diagnosticar_visitante.assert_not_called()

if __name__=='__main__':unittest.main()

