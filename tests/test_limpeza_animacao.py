"""Mascara conservadora, idle reconstruido e fase lateral independente do FPS."""
import unittest
from PIL import Image,ImageDraw,ImageOps
import pygame
from casa.config import ROOT
from support import exploration_house as House
from casa.sprite_cleanup import clean_sprite,reference_idle
from casa.collisions import feet_rect


class SpritePolishTests(unittest.TestCase):
    def test_official_lateral_reference_is_the_loaded_idle(self):
        expected=reference_idle(ROOT/'personagens/protagonista/referencias/protagonista_parado_lado.png')
        with Image.open(ROOT/'personagens/protagonista/processados/parado/direita.png') as actual:
            self.assertEqual(actual.tobytes(),expected.tobytes())

    def test_verified_hook_residue_beside_front_shoe_removed(self):
        base=ROOT/'personagens/protagonista/processados'
        for name,right in (('parado/frente',17),('andando/frente/2',20)):
            with Image.open(base/(name+'.png')) as image:
                self.assertIsNone(image.getchannel('A').crop((0,86,right,94)).getbbox())

    def test_walks_keep_original_body_pixels(self):
        from restaurar_sprites_integros import BASELINE
        for character in ('personagens/protagonista/processados',):
            for direction in ('frente','costas','direita','esquerda'):
                for n in (1,2,3):
                    path=ROOT/character/f'andando/{direction}/{n}.png'
                    with Image.open(BASELINE/path.relative_to(ROOT)) as original:
                        original=original.convert('RGBA')
                        mask=pygame.mask.from_surface(pygame.image.frombytes(original.tobytes(),original.size,'RGBA'))
                        principal=max(mask.connected_components(),key=lambda part:part.count())
                        dy=94-principal.get_bounding_rects()[0].bottom
                        with Image.open(path) as actual:
                            for y in range(96):
                                for x in range(64):
                                    if not principal.get_at((x,y)):continue
                                    if character.endswith('processados') and direction=='frente' and n==2 and x<20 and y+dy>=86:continue
                                    self.assertEqual(actual.getpixel((x,y+dy)),original.getpixel((x,y)),str(path))

    def test_ricardo_rest_uses_idle_at_exact_end_and_with_stale_moving_flag(self):
        from casa.resident import Resident
        assets=House().visitor_assets['ricardo']
        class Free:
            def allows(self,feet):return True
        for direction,vector in (('frente',(0,34)),('costas',(0,-34)),('direita',(34,0)),('esquerda',(-34,0))):
            actor=Resident('ricardo','sala',(0,0),direction=direction)
            actor.walking=True;actor.remaining=.1;actor.velocity.update(vector)
            actor.update(.1,Free())
            self.assertFalse(actor.walking);self.assertFalse(actor.moving)
            self.assertEqual(actor.animation_elapsed,0)
            self.assertIs(actor.image(assets),assets.sprites[direction])
            actor.moving=True;actor.animation_elapsed=9
            self.assertIs(actor.image(assets),assets.sprites[direction])
        self.assertEqual(pygame.image.tobytes(assets.sprites['esquerda'],'RGBA'),
                         pygame.image.tobytes(pygame.transform.flip(assets.sprites['direita'],True,False),'RGBA'))

    def test_cleanup_discards_detached_noise_and_thin_ground_spur_preserves_colors(self):
        image=Image.new('RGBA',(64,96));draw=ImageDraw.Draw(image)
        draw.rectangle((20,6,43,93),fill=(0,0,0,255))
        draw.rectangle((26,30,37,60),fill=(240,230,220,255))
        draw.rectangle((20,91,43,93),fill=(220,200,180,255))
        draw.point((2,90),fill='white')
        draw.line((16,87,20,87),fill=(10,12,11,255))
        result=clean_sprite(image)
        self.assertEqual(result.getpixel((2,90))[3],0)
        self.assertEqual(result.getpixel((16,87))[3],0)
        self.assertEqual(result.getpixel((30,20)),(0,0,0,255))
        self.assertEqual(result.getpixel((30,40)),(240,230,220,255))
        self.assertEqual(result.getpixel((30,93)),(220,200,180,255))

    def test_all_32_sprites_one_component_and_aligned_feet(self):
        for character,prefix in (('protagonista/processados','parado'),('visitantes/ricardo','sprites')):
            base=ROOT/'personagens'/character
            for direction in ('frente','costas','esquerda','direita'):
                numbers=(1,2) if character=='visitantes/ricardo' else (1,2,3)
                for path in [base/f'{prefix}/{direction}.png',*[base/f'andando/{direction}/{n}.png' for n in numbers]]:
                    surface=pygame.image.load(str(path))
                    self.assertEqual(surface.get_size(),(64,96))
                    mask=pygame.mask.from_surface(surface)
                    parts=mask.connected_components()
                    principal=max(parts,key=lambda part:part.count()).get_bounding_rects()[0]
                    self.assertTrue(all(principal.contains(part.get_bounding_rects()[0]) for part in parts),str(path))
                    box=surface.get_bounding_rect()
                    self.assertEqual(box.bottom,94,str(path))
                    self.assertIn(box.height,range(84,89) if character=='visitantes/ricardo' else (87,88),str(path))

    def test_classic_player_and_unchanged_resident_cycles(self):
        game=House();player=game.player
        for right,left in zip(player.walk['direita'],player.walk['esquerda']):
            self.assertEqual(pygame.image.tobytes(pygame.transform.flip(right,True,False),'RGBA'),pygame.image.tobytes(left,'RGBA'))
        for direction in ('esquerda','direita'):
            idle=pygame.image.tobytes(player.idle[direction],'RGBA')
            self.assertTrue(all(pygame.image.tobytes(frame,'RGBA')!=idle for frame in player.walk[direction]))
            for cycles,sprites,walk in ((player.cycles,player.idle,player.walk),
                                       (game.visitor_assets['ricardo'].cycles,game.visitor_assets['ricardo'].sprites,game.visitor_assets['ricardo'].walk)):
                first=1 if direction=='esquerda' else 0
                expected=((walk[direction][0],sprites[direction],walk[direction][1],sprites[direction],walk[direction][2],sprites[direction])
                          if cycles is player.cycles else (sprites[direction],walk[direction][0],sprites[direction],walk[direction][1]))
                self.assertEqual(cycles[direction],expected)

    def test_player_animation_phase_at_30_60_120_fps_and_restart(self):
        class Free:
            def allows(self,feet):return True
        results=[]
        for fps in (30,60,120):
            player=House().player;origin=player.feet.copy()
            for _ in range(fps):player.update((1,0),1/fps,Free())
            results.append((player.feet-origin,player.elapsed,player.image))
            before=feet_rect(player.feet)
            player.stop();self.assertIs(player.image,player.idle['direita'])
            self.assertEqual(before,feet_rect(player.feet))
            player.update((1,0),.01,Free());self.assertIs(player.image,player.walk['direita'][0])
        for position,elapsed,image in results:
            self.assertLess(position.distance_to(results[0][0]),.0001)
            self.assertAlmostEqual(elapsed,results[0][1])
            self.assertEqual(pygame.image.tobytes(image,'RGBA'),pygame.image.tobytes(results[0][2],'RGBA'))
