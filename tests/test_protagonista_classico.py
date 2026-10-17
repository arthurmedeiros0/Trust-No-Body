"""Restaura bytes/cadencia anteriores as sheets sem tocar nos assets recentes."""
import hashlib
import json
import unittest
from PIL import Image
import pygame
from casa.config import ROOT,PLAYER_ASSET_ROOT,FRAME_TIME
from support import exploration_house as House


class ClassicTests(unittest.TestCase):
    def test_original_bytes_and_loaded_frames_in_every_direction(self):
        record=json.loads((ROOT/'dados/protagonista_classico.json').read_text(encoding='utf-8'))
        self.assertEqual(len(record['sprites']),16)
        self.assertEqual(FRAME_TIME,.14)
        game=House()
        for name,digest in record['sprites'].items():
            path=ROOT/name;relative=path.relative_to(PLAYER_ASSET_ROOT)
            source=ROOT/record['origem']/relative
            self.assertEqual(path.read_bytes(),source.read_bytes())
            self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(),digest)
            with Image.open(path) as image:self.assertEqual(image.size,(64,96))
            parts=relative.parts
            actual=game.player.idle[parts[1][:-4]] if parts[0]=='parado' else game.player.walk[parts[1]][int(path.stem)-1]
            expected=pygame.image.load(str(source)).convert_alpha()
            self.assertEqual(pygame.image.tobytes(actual,'RGBA'),pygame.image.tobytes(expected,'RGBA'))

    def test_recent_protagonist_files_preserved(self):
        record=json.loads((ROOT/'dados/protagonista_classico.json').read_text(encoding='utf-8'))
        preserved=json.loads((ROOT/record['backup_validacao']/'preservados.json').read_text(encoding='utf-8'))
        for name,digest in preserved.items():
            if not name.replace('\\','/').startswith('personagens/protagonista/'):continue
            self.assertEqual(hashlib.sha256((ROOT/name).read_bytes()).hexdigest(),digest,name)
