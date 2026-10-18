"""Laura real: originais, agenda, exames, animacao, moradores e sobrevivencia."""
import copy
import hashlib
import json
import random
import unittest
from PIL import Image,ImageOps
import pygame
from casa.config import ROOT
from casa.game import House
from casa.visitors import VisitorSession
from casa.visitor_registry import readiness
from casa.visitor_ui import VisitorUI
from casa.visitor_dialogue import Dialogue
from casa.visitor_assets import load_assets
from casa.resident import Resident,ActorCollisions
from casa.collisions import feet_rect
from casa.resident_render import resident_frame

BASE=ROOT/'personagens/visitantes/laura'


class LauraTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.definition=json.loads((ROOT/'dados/visitantes/laura.json').read_text(encoding='utf-8'))
        cls.manifest=json.loads((ROOT/'dados/animacoes/laura.json').read_text(encoding='utf-8'))
        cls.assets=load_assets(cls.definition)

    def new_game(self):
        game=House();game.dialog=''
        game.news.watch(game.news.current(1))
        return game

    def sleep(self,game):
        game.dialog='';game.change_room('quarto',game.scenes['quarto'].point((345,365)))
        game.handle_event(pygame.event.Event(pygame.KEYUP,key=pygame.K_e))
        game.interact();self.assertTrue(game.sleep_option,game.dialog)
        game.confirm_sleep();game.update((0,0),3)

    def arrive(self,accept_ricardo=True):
        game=self.new_game();state=game.visitor_session
        self.assertEqual(state.manager.current,'ricardo')
        self.assertTrue(game.decide_visitor(state.visitors['ricardo'],'acolhido' if accept_ricardo else 'rejeitado'))
        planned=state.visitors['laura'].arrival_day
        while game.days.day<planned:self.sleep(game)
        self.assertEqual(state.manager.current,'laura')
        return game

    def test_originals_and_derived_hashes_and_exact_nearest_pixels(self):
        self.assertEqual(len(self.manifest['source_hashes']),21)
        for name,value in self.manifest['source_hashes'].items():
            self.assertEqual(hashlib.sha256((BASE/name).read_bytes()).hexdigest(),value,name)
        for name,value in self.manifest['output_hashes'].items():
            self.assertEqual(hashlib.sha256((BASE/name).read_bytes()).hexdigest(),value,name)
        for record in self.manifest['records']:
            with Image.open(BASE/record['source']) as source:
                image=source.convert('RGBA').crop(record['crop']).resize(tuple(record['size']),Image.Resampling.NEAREST)
            image=image.crop(image.getbbox());expected=Image.new('RGBA',(64,96))
            expected.alpha_composite(image,tuple(record['offset']))
            with Image.open(BASE/record['output']) as actual:self.assertEqual(actual.tobytes(),expected.tobytes())
        with Image.open(BASE/'porta/porta.png') as source,Image.open(BASE/'processados/porta.png') as actual:
            self.assertEqual(actual.tobytes(),source.crop(source.getbbox()).tobytes())

    def test_frames_feet_mirror_height_scale_and_portrait(self):
        heights=[]
        for direction in ('frente','costas','direita','esquerda'):
            for frame in [self.assets.sprites[direction],*self.assets.walk[direction]]:
                self.assertEqual(frame.get_size(),(64,96))
                rect=frame.get_bounding_rect(min_alpha=1)
                self.assertEqual(rect.bottom,94);heights.append(rect.height)
                scaled,anchor=resident_frame('laura',frame,self.definition['visual_scale'])
                self.assertIs(scaled,frame);self.assertEqual(anchor,(32,94))
            for left,right in zip([self.assets.sprites['esquerda'],*self.assets.walk['esquerda']],
                                  [self.assets.sprites['direita'],*self.assets.walk['direita']]):
                self.assertEqual(pygame.image.tobytes(left,'RGBA'),pygame.image.tobytes(pygame.transform.flip(right,True,False),'RGBA'))
        self.assertLessEqual(max(heights)-min(heights),1)
        self.assertLess(self.assets.portrait.get_height(),490)
        self.assertEqual(readiness(self.definition),'')

    def test_step_idle_step_idle_and_immediate_rest_all_directions(self):
        actor=Resident('laura','sala',(400,400),settings=self.definition['resident'])
        for direction,steps in self.assets.walk.items():
            idle=self.assets.sprites[direction]
            self.assertEqual(self.assets.cycles[direction],(steps[0],idle,steps[1],idle))
            for fps in (30,60,120):
                actor.direction=direction;actor.walking=actor.moving=True
                actor.animation_elapsed=37/fps
                expected=self.assets.cycles[direction][int(actor.animation_elapsed/.18)%4]
                self.assertIs(actor.image(self.assets),expected)
                actor.rest();self.assertIs(actor.image(self.assets),idle)

    def test_exact_investigation_mapping_and_shared_normal_face(self):
        expected={
            'manchas_maos':('mao_sem_mancha.png','mao_mancha.png'),
            'dentes_deteriorados':('dente_branco.png','dente_amarelo.png'),
            'olhos_alterados':('rosto_normal.png','olho_vermelho.png'),
            'veias_escurecidas':('pescoco_normal.png','pescoco_veia_roxa.png'),
            'palidez_anormal':('rosto_normal.png','rosto_palido.png'),
            'tremores_involuntarios':('mao_normal.png','mao_tremendo.png')}
        visitor=VisitorSession(random.Random(10)).visitors['laura']
        ui=VisitorUI(visitor,self.assets,lambda *args:False)
        ui.knowledge.learn(self.definition['investigation'])
        for feature,pair in expected.items():
            ui.feature=feature
            for altered,name in enumerate(pair):
                visitor.symptoms[feature]=bool(altered)
                variant='alterado' if altered else 'normal'
                self.assertEqual(self.definition['investigation'][feature][variant].split('/')[-1],name)
                self.assertIs(ui.examination_image(),self.assets.investigation[feature][variant])
        self.assertIs(self.assets.investigation['olhos_alterados']['normal'],self.assets.investigation['palidez_anormal']['normal'])
        self.assertEqual(visitor.diagnosis,'diagnostico_pendente')

    def test_schedule_once_first_ricardo_then_laura_two_or_three(self):
        dates=set()
        for seed in range(16):
            state=VisitorSession(random.Random(seed));plan=copy.deepcopy(state.manager.plan)
            dates.add(plan['laura']);self.assertEqual(plan['ricardo'],1)
            state.news.watch(state.news.current(1))
            self.assertEqual(state.manager.current,'ricardo')
            for _ in range(10):state.manager.activate(1,True)
            self.assertEqual(state.manager.plan,plan)
            self.assertFalse(state.visitors['laura'].arrived)
        self.assertEqual(dates,{2,3})

    def test_dialogue_personality_supplies_and_confirmation(self):
        game=self.arrive();visitor=game.visitor_session.visitors['laura']
        self.assertIn(visitor.food,(1,2));self.assertIn(visitor.water,(1,2))
        ui=game.peephole.visitor_ui;dialogue=Dialogue(visitor)
        self.assertIn('família',dialogue.intro())
        answer=dialogue.answer(2)
        self.assertIn(str(visitor.food)+' lata',answer);self.assertIn(str(visitor.water)+' garrafa',answer)
        ui.page='confirm';ui.decision='acolhido'
        ui.draw(pygame.display.get_surface())
        self.assertIn('lugar seguro',' '.join(dialogue.data['before_decision']))

    def test_accept_two_residents_once_sleep_counts_three_and_preserves_symptoms(self):
        game=self.arrive();state=game.visitor_session;visitor=state.visitors['laura']
        snapshot=copy.deepcopy(visitor.symptoms);ricardo=game.residents['ricardo']
        before=(state.survival.food,state.survival.water)
        self.assertTrue(game.decide_visitor(visitor,'acolhido'))
        self.assertEqual((state.survival.food,state.survival.water),(before[0]+visitor.food,before[1]+visitor.water))
        self.assertEqual(len(state.living_ids),3)
        self.assertFalse(game.decide_visitor(visitor,'acolhido'));self.assertFalse(game.decide_visitor(visitor,'rejeitado'))
        self.assertIs(game.residents['ricardo'],ricardo)
        state.survival.change_sanity(-3);previous=state.survival.sanity
        day=game.days.day;self.sleep(game)
        report=state.survival.reports[day]
        self.assertEqual((report.food,report.water),(1.5,1.5))
        self.assertEqual(state.survival.sanity,previous+1);self.assertEqual(state.survival.loneliness,0)
        self.assertEqual(visitor.symptoms,snapshot)
        self.assertIsNone(state.manager.current)
        game.change_room('sala');game.dialog=''
        game.draw(pygame.display.get_surface())
        self.assertEqual(visitor.symptoms,snapshot)

    def test_rejected_laura_never_returns_or_transfers_resources(self):
        game=self.arrive(False);state=game.visitor_session;visitor=state.visitors['laura']
        before=(state.survival.food,state.survival.water)
        self.assertTrue(game.decide_visitor(visitor,'rejeitado'))
        self.assertEqual((state.survival.food,state.survival.water),before)
        self.assertNotIn('laura',game.residents)
        for day in range(2,21):state.manager.activate(day,True)
        self.assertIsNone(state.manager.current)
        self.assertEqual(state.manager.seen,{'ricardo','laura'})

    def test_both_npcs_move_collide_and_keep_independent_images(self):
        game=self.arrive();state=game.visitor_session
        game.decide_visitor(state.visitors['laura'],'acolhido')
        game.dialog='';game.change_room('sala')
        scene=game.scene;actors=list(game.residents.values());moved=set()
        positions={a.visitor_id:a.feet.copy() for a in actors}
        for _ in range(600):
            game.update((0,0),1/60)
            for actor in actors:
                self.assertTrue(scene.collisions.allows(actor.feet))
                self.assertFalse(feet_rect(actor.feet).colliderect(feet_rect(game.player.feet)))
                if actor.feet.distance_to(positions[actor.visitor_id])>1:moved.add(actor.visitor_id)
            self.assertFalse(feet_rect(actors[0].feet).colliderect(feet_rect(actors[1].feet)))
        self.assertEqual(moved,{'ricardo','laura'})
        self.assertIsNot(actors[0].image(game.visitor_assets[actors[0].visitor_id]),actors[1].image(game.visitor_assets[actors[1].visitor_id]))
