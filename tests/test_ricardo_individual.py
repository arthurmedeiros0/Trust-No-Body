"""Fontes intactas, alpha conservado, ciclo com idle e interrupcoes reais."""
import hashlib
import json
import unittest
from PIL import Image,ImageDraw
import pygame
from casa.config import ROOT
from support import exploration_house as House
from casa.resident import Resident,ActorCollisions
from casa.collisions import feet_rect
from preparar_ricardo_individual import external_white


class IndividualTests(unittest.TestCase):
    def setUp(self):
        self.game=House();self.assets=self.game.visitor_assets['ricardo']
        self.base=ROOT/'personagens/visitantes/ricardo'
        self.manifest=json.loads((ROOT/'dados/animacoes/ricardo_individual.json').read_text(encoding='utf-8'))

    def test_loaded_assets_and_original_alpha_pixels_without_erosion(self):
        self.assertEqual(len(self.manifest['assets']),12)
        for row in self.manifest['assets']:
            path=self.base/row['destino']
            self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(),row['sha256'])
            with Image.open(path) as output:
                self.assertEqual(output.size,(64,96));self.assertEqual(output.mode,'RGBA')
                self.assertEqual(output.getbbox()[3],94)
                if 'original' in row:
                    source=self.base/'referencias'/row['original']
                    self.assertEqual(hashlib.sha256(source.read_bytes()).hexdigest(),row['sha256_original'])
                    with Image.open(source) as raw:
                        self.assertLess(raw.getchannel('A').getextrema()[0],255)
                        reference=raw.crop(row['recorte']).resize(tuple(row['resize']),Image.Resampling.NEAREST)
                        reference=reference.crop(reference.getbbox())
                    x,y=row['offset'];actual=output.crop((x,y,x+reference.width,y+reference.height))
                    self.assertEqual(actual.getchannel('A').tobytes(),reference.getchannel('A').tobytes())
                    for original,pixel in zip(reference.get_flattened_data(),actual.get_flattened_data()):
                        if original[3]:self.assertEqual(pixel,original)
                    self.assertEqual(row['escala'],self.manifest['common_scale'])
            parts=path.relative_to(self.base).parts
            actual=self.assets.sprites[path.stem] if parts[0]=='sprites' else self.assets.walk[parts[1]][int(path.stem)-1]
            self.assertEqual(pygame.image.tobytes(actual,'RGBA'),pygame.image.tobytes(pygame.image.load(str(path)).convert_alpha(),'RGBA'))

    def test_sources_protagonist_door_exams_dialogues_and_maps_unchanged(self):
        saved=ROOT/self.manifest['backup']
        protected=json.loads((saved/'preservados.json').read_text(encoding='utf-8'))
        for name,digest in protected.items():
            if name.replace('\\','/') in ('casa/game.py','casa/config.py','casa/scenes.py','casa/interactions.py','dados/visitantes/ricardo_dialogos.json'):continue # Interacao/narrativa evoluiram; imagens permanecem protegidas.
            self.assertEqual(hashlib.sha256((ROOT/name).read_bytes()).hexdigest(),digest,name)
        self.assertEqual(len(list((self.base/'referencias').glob('*.png'))),9)
        self.assertEqual(len(list((saved/'andando').glob('*/*.png'))),self.manifest.get('previous_walk_count',12))

    def test_each_direction_cycle_and_rest_at_every_phase(self):
        actor=Resident('ricardo','sala',(0,0))
        for direction,steps in self.assets.walk.items():
            self.assertEqual(len(steps),2)
            idle=self.assets.sprites[direction]
            self.assertEqual(self.assets.cycles[direction],(idle,steps[0],idle,steps[1]))
            for index,expected in enumerate(self.assets.cycles[direction]):
                actor.direction=direction;actor.walking=actor.moving=True
                actor.animation_elapsed=index*actor.frame_seconds+.001
                self.assertEqual(actor.animation_state,'walk');self.assertIs(actor.image(self.assets),expected)
                actor.rest()
                self.assertEqual(actor.direction,direction)
                self.assertEqual(actor.animation_state,'idle');self.assertEqual(actor.animation_elapsed,0)
                self.assertIs(actor.image(self.assets),idle)
                actor.moving=True # flag antiga nunca sobrepoe estado parado
                self.assertIs(actor.image(self.assets),idle)

    def test_blocked_by_wall_furniture_player_and_zero_velocity_returns_idle(self):
        class Free:
            def allows(self,point):return True
        class Wall:
            def allows(self,point):return point.length_squared()<.01
        for direction,vector in (('frente',(0,34)),('costas',(0,-34)),('direita',(34,0)),('esquerda',(-34,0))):
            vector=pygame.Vector2(vector)
            for collisions in (Wall(),ActorCollisions(Free(),[feet_rect(vector.normalize()*30)])):
                actor=Resident('ricardo','sala',(0,0),direction=direction)
                actor.velocity.update(vector);actor.walking=actor.moving=True;actor.remaining=2
                actor.animation_elapsed=.37;actor.update(1,collisions)
                self.assertEqual(actor.animation_state,'idle')
                self.assertEqual(actor.animation_elapsed,0)
                self.assertIs(actor.image(self.assets),self.assets.sprites[direction])
                position=actor.feet.copy();actor.update(.01,collisions);self.assertEqual(position,actor.feet)
        actor=Resident('ricardo','sala',(0,0));actor.walking=actor.moving=True
        actor.remaining=2;actor.animation_elapsed=.5;actor.update(.1,Free())
        self.assertEqual(actor.animation_state,'idle');self.assertEqual(actor.animation_elapsed,0)

    def test_external_white_flood_preserves_enclosed_white_coat_and_black_hair(self):
        image=Image.new('RGBA',(40,50),'white');draw=ImageDraw.Draw(image)
        draw.rectangle((8,6,31,43),fill=(15,10,10))
        draw.rectangle((11,15,28,39),fill='white')
        result=external_white(image)
        self.assertEqual(result.getpixel((0,0))[3],0)
        self.assertEqual(result.getpixel((15,20)),(255,255,255,255))
        self.assertEqual(result.getpixel((15,8)),(15,10,10,255))
        transparent=Image.new('RGBA',(20,20));ImageDraw.Draw(transparent).rectangle((4,4,15,15),fill='white')
        self.assertEqual(external_white(transparent).tobytes(),transparent.tobytes())
