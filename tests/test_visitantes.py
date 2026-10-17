"""Dados, recursos, interfaces e decisoes; nenhuma regra de infeccao."""
import ast
import copy
import hashlib
import json
import random
import unittest
from unittest.mock import patch
from PIL import Image
import pygame
from casa.config import ROOT
from casa.game import House
from casa.visitors import VisitorSession
from casa.visitor_assets import remove_border_white

class VisitorTests(unittest.TestCase):
    def setUp(self):
        self.game=House();self.ui=self.game.peephole.visitor_ui;self.visitor=self.ui.visitor
        self.game.change_room('entrada');self.game.observing=True

    def click(self,key):
        rect,_=self.ui.layout()[key]
        self.game.handle_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN,button=1,pos=rect.center))

    def esc(self):self.game.handle_event(pygame.event.Event(pygame.KEYDOWN,key=pygame.K_ESCAPE))

    def test_randomization_only_at_session_start_and_ranges(self):
        rng=random.Random(42)
        a=VisitorSession(rng).visitors['ricardo']
        b=VisitorSession(rng).visitors['ricardo']
        self.assertEqual(len(a.symptoms),6)
        self.assertTrue(all(type(value) is bool for value in a.symptoms.values()))
        self.assertIn(a.food,range(4));self.assertIn(a.water,range(4))
        self.assertIsNot(a.symptoms,b.symptoms)
        # Comprova as chamadas de sorteio por partida, sem testar deducoes.
        with patch('casa.visitors.random.getrandbits',return_value=1) as symptoms,patch('casa.visitors.random.randint',return_value=3) as supplies:
            session=VisitorSession()
            self.assertEqual(symptoms.call_count,6);self.assertEqual(supplies.call_count,2)
            self.assertTrue(all(v for v in session.visitors['ricardo'].symptoms.values()))
        before=(copy.deepcopy(self.visitor.symptoms),self.visitor.food,self.visitor.water)
        with patch('casa.visitors.random.getrandbits',side_effect=AssertionError('Nao ressorteie')):
            self.click('investigate');self.click('manchas_maos');self.esc();self.esc()
            self.click('talk');self.click('3');self.esc()
        self.assertEqual(before,(self.visitor.symptoms,self.visitor.food,self.visitor.water))

    def test_comment_only_logic_placeholder_and_pending_state(self):
        self.assertEqual(ast.parse((ROOT/'logica_infeccao.py').read_text(encoding='utf-8-sig')).body,[])
        self.assertEqual(self.visitor.diagnosis,'diagnostico_pendente')
        self.assertEqual(self.game.visitor_session.knowledge.published,{})
        self.game.visitor_session.knowledge.published['noticia_teste']={'texto':'Conteudo a ser escrito pelo grupo'}
        self.assertEqual(self.visitor.diagnosis,'diagnostico_pendente')

    def test_all_six_features_both_visual_variants_and_seen_mark(self):
        self.click('investigate')
        for feature in self.visitor.symptoms:
            for value,variant in [(False,'normal'),(True,'alterado')]:
                self.visitor.symptoms[feature]=value
                self.click(feature)
                self.assertEqual(self.ui.page,'image')
                self.assertIs(self.ui.examination_image(),self.ui.assets.investigation[feature][variant])
                self.game.draw(pygame.display.get_surface())
                self.assertIn(feature,self.visitor.examined)
                self.esc();self.assertEqual(self.ui.page,'investigate')
                self.assertIn('[visto]',self.ui.layout()[feature][1])
        self.assertEqual(self.visitor.diagnosis,'diagnostico_pendente')

    def test_dialogue_resources_and_escape_hierarchy(self):
        before=self.game.player.feet.copy()
        self.click('talk')
        self.assertTrue(self.visitor.talked)
        self.assertIn('Ricardo',self.ui.response)
        self.assertIn('hospital',self.ui.response)
        for index in range(4):
            self.click(str(index));self.assertTrue(self.ui.response)
            self.game.draw(pygame.display.get_surface())
        self.assertIn(str(self.visitor.food),self.ui.response)
        self.assertIn(str(self.visitor.water),self.ui.response)
        self.game.update((1,1),1);self.assertEqual(self.game.player.feet,before)
        self.esc();self.assertEqual(self.ui.page,'root');self.assertTrue(self.game.observing)
        self.esc();self.assertTrue(self.game.fade.active)
        self.game.update((0,0),.23);self.game.update((0,0),.23)
        self.assertFalse(self.game.observing);self.assertEqual(self.game.player.feet,before)

    def test_accept_confirmation_retains_data_and_places_resident(self):
        before=(copy.deepcopy(self.visitor.symptoms),self.visitor.food,self.visitor.water)
        self.click('accept');self.assertEqual(self.visitor.state,'aguardando')
        self.assertEqual(self.ui.page,'root')
        self.click('talk');self.esc();self.click('accept')
        self.assertEqual(self.ui.page,'confirm');self.assertEqual(self.visitor.state,'aguardando')
        self.click('back');self.assertEqual(self.visitor.state,'aguardando')
        self.click('accept');self.click('confirm')
        self.assertEqual(self.visitor.state,'acolhido')
        feet=self.game.resident_positions[self.visitor.id]
        self.assertTrue(self.game.scenes['sala'].collisions.allows(feet))
        self.assertFalse(self.game.decide_visitor(self.visitor,'acolhido'))
        self.assertEqual(len(self.game.visitor_session.decisions),1)
        self.assertEqual(before,(self.visitor.symptoms,self.visitor.food,self.visitor.water))
        self.assertEqual(self.visitor.diagnosis,'diagnostico_pendente')
        self.game.change_room('sala');self.game.observing=False
        with patch.object(self.game.visitor_shadow,'draw',wraps=self.game.visitor_shadow.draw) as draw:
            self.game.draw(pygame.display.get_surface());self.assertTrue(draw.called)
        with patch.object(self.ui,'draw_portrait',wraps=self.ui.draw_portrait):
            surface=pygame.Surface((1280,720),pygame.SRCALPHA)
            self.ui.draw_portrait(surface);self.assertEqual(surface.get_bounding_rect().size,(0,0))

    def test_reject_confirmation_registers_and_does_not_respawn(self):
        self.click('investigate');self.click('olhos_alterados');self.esc();self.esc()
        self.click('reject');self.assertEqual(self.visitor.state,'aguardando')
        self.click('confirm');self.assertEqual(self.visitor.state,'rejeitado')
        self.assertEqual(self.game.visitor_session.decisions[0]['decision'],'rejeitado')
        self.assertFalse(self.game.decide_visitor(self.visitor,'acolhido'))
        self.game.observing=False;self.game.observing=True
        surface=pygame.Surface((1280,720),pygame.SRCALPHA)
        self.ui.draw_portrait(surface);self.assertEqual(surface.get_bounding_rect().size,(0,0))
        self.assertNotIn(self.visitor.id,self.game.resident_positions)
        self.assertEqual(self.visitor.diagnosis,'diagnostico_pendente')

    def test_originals_transparency_and_preserved_white_coat(self):
        base=ROOT/'personagens/visitantes/ricardo'
        manifest=json.loads((ROOT/'dados/visitantes/ricardo_originais.sha256').read_text(encoding='utf-8'))
        self.assertEqual(len(manifest),17)
        for path,digest in manifest.items():self.assertEqual(hashlib.sha256((base/path).read_bytes()).hexdigest(),digest)
        portrait=self.ui.assets.portrait
        self.assertEqual(portrait.get_at((0,0)).a,0)
        white=0
        for y in range(portrait.get_height()):
            for x in range(portrait.get_width()):
                p=portrait.get_at((x,y))
                if p.a>240 and min(p.r,p.g,p.b)>180:white+=1
        self.assertGreater(white,100)
        # Fundo branco e jaleco branco separados por contorno escuro.
        image=Image.new('RGBA',(20,20),'white')
        from PIL import ImageDraw
        draw=ImageDraw.Draw(image);draw.rectangle((4,4,15,15),fill='black');draw.rectangle((6,6,13,13),fill='white')
        result=remove_border_white(image)
        self.assertEqual(result.getpixel((5,5))[3],255)
        for sprite in self.ui.assets.sprites.values():self.assertEqual(sprite.get_size(),(64,96))
