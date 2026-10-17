"""Novas sheets, integracao e preservacao dos recursos protegidos."""
import hashlib
import json
import unittest
from PIL import Image,ImageDraw
import pygame
from casa.config import ROOT
from casa.game import House
from preparar_sheets import transparent

class SheetTests(unittest.TestCase):
    def test_sources_outputs_and_foot_alignment(self):
        for character,count in (('protagonista',21),('ricardo',25)):
            manifest=json.loads((ROOT/f'dados/sheets/{character}.json').read_text(encoding='utf-8'))
            self.assertEqual(len(manifest['assets']),count)
            self.assertEqual(hashlib.sha256((ROOT/manifest['source']).read_bytes()).hexdigest(),manifest['source_sha256'])
            for row in manifest['assets']:
                path=ROOT/row['destino']
                self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(),row['sha256'])
                with Image.open(path) as image:
                    self.assertEqual(image.mode,'RGBA')
                    if '/andando/' in row['destino'] or '/parado/' in row['destino'] or '/sprites/' in row['destino']:
                        self.assertEqual(image.size,(64,96))
                        self.assertEqual(image.getbbox()[1::2],(6,94))

    def test_door_exams_and_previous_design_preserved(self):
        backup=ROOT/'backups/sheets_20261017_150406_128619'
        protected=json.loads((backup/'preservados.json').read_text(encoding='utf-8'))
        self.assertGreater(len(protected),12)
        for name,digest in protected.items():
            self.assertEqual(hashlib.sha256((ROOT/name).read_bytes()).hexdigest(),digest,name)
        self.assertEqual(len(list((backup/'personagens/protagonista/processados/parado').glob('*.png'))),4)
        self.assertEqual(len(list((backup/'personagens/visitantes/ricardo/andando').glob('*/*.png'))),12)

    def test_game_loads_sheet_pixels_without_white_background_processing(self):
        game=House()
        assets=game.visitor_assets['ricardo']
        for direction in ('frente','costas','direita','esquerda'):
            for surface,path in ((assets.sprites[direction],f'personagens/visitantes/ricardo/sprites/{direction}.png'),
                                 (game.player.idle[direction],f'personagens/protagonista/processados/parado/{direction}.png')):
                expected=pygame.image.load(str(ROOT/path)).convert_alpha()
                self.assertEqual(pygame.image.tobytes(surface,'RGBA'),pygame.image.tobytes(expected,'RGBA'))

    def test_background_connectivity_preserves_dark_interior(self):
        image=Image.new('RGBA',(40,60),(10,13,12,255));draw=ImageDraw.Draw(image)
        draw.rectangle((8,8,31,51),fill=(150,80,40))
        draw.rectangle((13,15,26,43),fill=(0,0,0))
        result=transparent(image,True)
        self.assertEqual(result.getpixel((10,20)),(0,0,0,255))
        self.assertEqual(result.size,(24,44))
