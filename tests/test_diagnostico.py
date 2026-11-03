"""Contrato da integração; as regras matemáticas pertencem ao grupo."""
import copy
import random
import unittest
from types import SimpleNamespace
from unittest.mock import Mock,patch
import pygame
from casa.visitors import VisitorSession
from casa.visitor_ui import VisitorUI


class DiagnosisTests(unittest.TestCase):
    def setUp(self):
        self.session=VisitorSession(random.Random(42))
        self.visitor=self.session.visitors['ricardo']
        self.session.medical.known.update(self.visitor.symptoms)

    def test_observed_only_copies_and_different_visitors(self):
        s=self.session
        self.visitor.symptoms['manchas_maos']=False
        s.medical.observe(self.visitor,'manchas_maos')
        before=copy.deepcopy(self.visitor)
        def fake(symptoms,news):
            self.assertEqual(symptoms,{'manchas_maos':False})
            self.assertEqual(news,set())
            symptoms.clear();news.add('externa')
            return 'infectado'
        with patch('casa.visitors.infection_logic',SimpleNamespace(diagnosticar=fake)):
            self.assertEqual(s.diagnosticar_visitante('ricardo'),'infectado')
        self.assertEqual(s.medical.observations['ricardo'],{'manchas_maos':False})
        self.assertEqual(self.visitor,before)
        self.assertEqual(s.knowledge.published,{})
        with patch('casa.visitors.infection_logic',SimpleNamespace(diagnosticar=Mock(return_value='inconclusivo'))) as logic:
            s.diagnosticar_visitante('laura')
            logic.diagnosticar.assert_called_once_with({},set())
        with self.assertRaises(KeyError):s.diagnosticar_visitante('inexistente')

    def test_day_does_not_grant_news_but_history_does(self):
        s=self.session
        s.days.day=18;s.news.unlock(18)
        with patch('casa.visitors.infection_logic',SimpleNamespace(diagnosticar=Mock(return_value='inconclusivo'))) as logic:
            s.diagnosticar_visitante('ricardo')
            logic.diagnosticar.assert_called_with({},set())
            for day in (7,14,17):
                s.news.watch(next(b for b in s.news.history if b.day==day))
                s.diagnosticar_visitante('ricardo')
                self.assertEqual(logic.diagnosticar.call_args.args[1],set(s.knowledge.published))
        self.assertEqual(set(s.knowledge.published),{'boletim_07','boletim_14','boletim_17'})

    def test_test_mode_provides_protocol_without_reading_or_advancing(self):
        s=self.session
        for key in set(s.visitors)-set(s.unavailable):
            visitor=s.start_test(key)
            self.assertTrue(set(visitor.definition['investigation'])<=s.medical.known)
            with patch('casa.visitors.infection_logic',SimpleNamespace(diagnosticar=Mock(return_value='inconclusivo'))) as logic:
                s.diagnosticar_visitante(key)
                logic.diagnosticar.assert_called_once_with({}, {'boletim_07','boletim_14','boletim_17'})
        self.assertEqual(s.day,1)
        self.assertFalse(s.knowledge.published)
        self.assertFalse(any(b.read for b in s.news.bulletins))
        self.assertFalse(VisitorSession(random.Random(42)).test_mode)

    def test_missing_incompatible_and_pending_function(self):
        for logic in (None,SimpleNamespace(),SimpleNamespace(diagnosticar=lambda x: 'infectado'),
                      SimpleNamespace(diagnosticar=lambda a,b: None)):
            with self.subTest(logic=logic),patch('casa.visitors.infection_logic',logic):
                self.assertEqual(self.session.diagnosticar_visitante('ricardo'),'inconclusivo')

    def test_ui_refreshes_after_observation_and_news_without_changing_real_state(self):
        s=self.session
        ui=VisitorUI(self.visitor,None,lambda *args:False,knowledge=s.medical,session=s)
        state=self.visitor.diagnosis
        self.assertIsNone(ui.diagnosis_indicator())
        ui.page='investigate'
        # Simula só o retorno do grupo; nenhuma implicação é reproduzida aqui.
        with patch('casa.visitors.infection_logic',SimpleNamespace(diagnosticar=Mock(side_effect=['inconclusivo','inconclusivo','infectado']))) as logic:
            self.assertEqual(ui.diagnosis_indicator(),'Diagnóstico inconclusivo')
            rect=ui.layout()['manchas_maos'][0]
            ui.handle_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN,button=1,pos=rect.center))
            self.assertEqual(ui.page,'image')
            self.assertEqual(ui.diagnosis_indicator(),'Diagnóstico inconclusivo')
            self.assertEqual(logic.diagnosticar.call_args.args[0],{'manchas_maos':self.visitor.symptoms['manchas_maos']})
            s.news.unlock(7);s.news.watch(s.news.current(7))
            self.assertEqual(ui.diagnosis_indicator(),'PADRÃO DE INFECÇÃO IDENTIFICADO')
            self.assertEqual(logic.diagnosticar.call_args.args[1],{'boletim_07'})
        self.assertEqual(self.visitor.diagnosis,state)
        s.medical.known.clear()
        self.assertIsNone(ui.diagnosis_indicator())

    def test_available_module_delegation(self):
        from casa.visitors import infection_logic
        if not callable(getattr(infection_logic,'diagnosticar',None)):
            self.skipTest('Função do grupo ainda indisponível')
        with patch.object(infection_logic,'diagnosticar',wraps=infection_logic.diagnosticar) as diagnose:
            self.session.diagnosticar_visitante('ricardo')
            diagnose.assert_called_once_with({},set())
