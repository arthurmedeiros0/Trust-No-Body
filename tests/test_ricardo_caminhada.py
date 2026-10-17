"""Originais, transparencia e animacao independente da fisica do morador."""
import copy
import hashlib
import json
import random
import unittest
from pathlib import Path
from PIL import Image,ImageDraw
import pygame
from casa.config import ROOT
from casa.game import House
from casa.resident import Resident
from casa.collisions import feet_rect
from casa.visitor_image_processing import remove_black,clean_external_specks,refine_hand_wrists,EXAM_SIZE,EXAM_BACKGROUND,PROCESSING_VERSION

class WalkTests(unittest.TestCase):
    def setUp(self):
        self.game=House();self.assets=self.game.visitor_assets['ricardo']
        self.base=ROOT/'personagens/visitantes/ricardo'

    def test_nine_originals_manifest_and_twelve_processed_frames(self):
        manifest=json.loads((ROOT/'dados/animacoes/ricardo.json').read_text(encoding='utf-8'))
        self.assertEqual(set(manifest['frames']),{'frente','costas','direita'})
        self.assertEqual(len(list((self.base/'sprites_movimento').glob('*.png'))),9)
        for frames in manifest['frames'].values():
            self.assertEqual(len(frames),3)
            for frame in frames:
                self.assertEqual(hashlib.sha256((self.base/'sprites_movimento'/frame['original']).read_bytes()).hexdigest(),frame['sha256'])
        for direction,frames in self.assets.walk.items():
            self.assertEqual(len(frames),3)
            for index,surface in enumerate(frames,1):
                path=self.base/f'andando/{direction}/{index}.png'
                with Image.open(path) as image:
                    self.assertEqual(image.size,(64,96));self.assertEqual(image.mode,'RGBA')
                    box=image.getbbox();self.assertEqual(box[3],94)
                    self.assertEqual(box[3]-box[1],88)
                    self.assertLessEqual(abs((box[0]+box[2])/2-32),1)
                self.assertEqual(surface.get_at((0,0)).a,0)
            self.assertEqual(len({pygame.image.tobytes(surface,'RGBA') for surface in frames}),3)
        self.assertTrue((self.base/'andando/comparacao.png').exists())

    def test_left_is_independent_sheet_pose_and_coat_stays_light(self):
        for right,left in zip(self.assets.walk['direita'],self.assets.walk['esquerda']):
            self.assertNotEqual(pygame.image.tobytes(pygame.transform.flip(right,True,False),'RGBA'),pygame.image.tobytes(left,'RGBA'))
        for frames in self.assets.walk.values():
            for image in frames:
                light=sum(1 for y in range(96) for x in range(64) if image.get_at((x,y)).a>200 and min(image.get_at((x,y))[:3])>150)
                self.assertGreater(light,50)

    def test_border_black_removal_preserves_internal_dark_details(self):
        image=Image.new('RGBA',(40,40),'black');draw=ImageDraw.Draw(image)
        draw.rectangle((8,8,31,31),fill=(225,210,200))
        draw.rectangle((15,15,24,24),fill=(0,0,0))
        result=remove_black(image)
        self.assertEqual(result.size,(24,24))
        self.assertEqual(result.getpixel((10,10)),(0,0,0,255))
        # Ilha externa branca e detalhe branco conectado a silhueta.
        canvas=Image.new('RGBA',(40,40))
        draw=ImageDraw.Draw(canvas);draw.rectangle((10,10,30,30),fill='black')
        draw.rectangle((14,14,18,18),fill='white');draw.rectangle((2,2,3,3),fill='white')
        cleaned=clean_external_specks(canvas)
        self.assertEqual(cleaned.getpixel((2,2))[3],0)
        self.assertEqual(cleaned.getpixel((15,15)),(255,255,255,255))

    def test_animation_all_directions_three_frames_and_rest(self):
        actor=Resident('ricardo','sala',(0,0))
        actor.moving=True
        for direction,frames in self.assets.walk.items():
            actor.direction=direction
            for index in range(6):
                actor.animation_elapsed=index*actor.frame_seconds+.001
                self.assertIs(actor.image(self.assets),frames[index%3])
        actor.rest()
        self.assertEqual(actor.animation_elapsed,0)
        self.assertIs(actor.image(self.assets),self.assets.sprites[actor.direction])

    def test_wrist_mask_removes_external_gray_but_keeps_skin_highlights_and_coat(self):
        image=Image.new('RGBA',(200,200));draw=ImageDraw.Draw(image)
        for left in (37,112):
            draw.rectangle((left,88,left+51,143),fill='black')
            draw.rectangle((left+3,90,left+48,140),fill=(210,135,90))
            draw.rectangle((left,145,left+51,160),fill=(50,65,100))
            draw.rectangle((left,161,left+51,199),fill='white')
        draw.rectangle((20,115,23,118),fill=(190,190,190))
        draw.rectangle((60,110,64,114),fill='white')
        result=refine_hand_wrists(image)
        self.assertEqual(result.getpixel((21,116))[3],0)
        self.assertEqual(result.getpixel((60,112)),(255,255,255,255))
        self.assertEqual(result.getpixel((60,170)),(255,255,255,255))
        self.assertEqual(result.getpixel((50,120)),image.getpixel((50,120)))

    def test_fps_and_direction_reset_keep_feet_and_hitbox(self):
        class Free:
            def allows(self,feet):return True
        results=[]
        for fps in (30,60,120):
            actor=Resident('ricardo','sala',(0,0),settings={'radius':1000},rng=random.Random(7))
            actor.walking=True;actor.direction='direita';actor.velocity.update(actor.speed,0);actor.remaining=2
            for _ in range(fps):actor.update(1/fps,Free())
            results.append((actor.feet.copy(),actor.animation_elapsed,actor.image(self.assets)))
            rect=feet_rect(actor.feet);position=actor.feet.copy()
            for _ in range(10):actor.image(self.assets)
            self.assertEqual(rect,feet_rect(actor.feet));self.assertEqual(position,actor.feet)
            actor._choose(Free());self.assertEqual(actor.animation_elapsed,0)
            actor.update(.02,Free())
            self.assertIs(actor.image(self.assets),self.assets.walk[actor.direction][0])
        self.assertLess(results[0][0].distance_to(results[-1][0]),.0001)
        self.assertAlmostEqual(results[0][1],results[-1][1],places=5)
        self.assertIs(results[0][2],results[-1][2])

    def test_rendering_uses_animation_without_changing_shadow_or_symptoms(self):
        visitor=self.game.visitor_session.visitors['ricardo'];symptoms=copy.deepcopy(visitor.symptoms)
        self.assertTrue(self.game.decide_visitor(visitor,'acolhido'))
        self.game.change_room('sala');actor=self.game.residents['ricardo']
        actor.moving=True;actor.animation_elapsed=.2;actor.direction='direita'
        before=actor.feet.copy();shadow=self.game.visitor_shadow
        self.game.draw(pygame.display.get_surface())
        self.assertEqual(actor.feet,before);self.assertIs(self.game.visitor_shadow,shadow)
        self.assertEqual(visitor.symptoms,symptoms);self.assertEqual(visitor.diagnosis,'diagnostico_pendente')
        for feature,variants in self.assets.investigation.items():
            for variant,image in variants.items():
                self.assertEqual(image.get_size(),EXAM_SIZE)
                self.assertEqual(tuple(image.get_at((0,0))),EXAM_BACKGROUND)
                self.assertTrue(list((self.base/'investigacao_processada'/feature).glob(variant+'_'+PROCESSING_VERSION+'_*.png')))
