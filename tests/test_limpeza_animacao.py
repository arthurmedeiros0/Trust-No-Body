"""Mascara conservadora, idle reconstruido e fase lateral independente do FPS."""
import unittest
from PIL import Image,ImageDraw,ImageOps
import pygame
from casa.config import ROOT
from casa.game import House
from casa.sprite_cleanup import clean_sprite
from casa.collisions import feet_rect


class SpritePolishTests(unittest.TestCase):
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
                for path in [base/f'{prefix}/{direction}.png',*[base/f'andando/{direction}/{n}.png' for n in (1,2,3)]]:
                    surface=pygame.image.load(str(path))
                    self.assertEqual(surface.get_size(),(64,96))
                    mask=pygame.mask.from_surface(surface)
                    self.assertEqual(len(mask.connected_components()),1,str(path))
                    box=mask.get_bounding_rects()[0]
                    self.assertEqual(box.bottom,94,str(path))
                    self.assertIn(box.height,(87,88),str(path))

    def test_lateral_idle_mirrored_and_distinct_from_walk(self):
        game=House();player=game.player
        self.assertEqual(pygame.image.tobytes(pygame.transform.flip(player.idle['direita'],True,False),'RGBA'),
                         pygame.image.tobytes(player.idle['esquerda'],'RGBA'))
        for direction in ('esquerda','direita'):
            idle=pygame.image.tobytes(player.idle[direction],'RGBA')
            self.assertTrue(all(pygame.image.tobytes(frame,'RGBA')!=idle for frame in player.walk[direction]))
            for cycles,sprites,walk in ((player.cycles,player.idle,player.walk),
                                       (game.visitor_assets['ricardo'].cycles,game.visitor_assets['ricardo'].sprites,game.visitor_assets['ricardo'].walk)):
                first=1 if direction=='esquerda' else 0
                self.assertEqual(cycles[direction],(sprites[direction],walk[direction][first],sprites[direction],walk[direction][2]))

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
            player.update((1,0),.01,Free());self.assertIs(player.image,player.idle['direita'])
        for position,elapsed,image in results:
            self.assertLess(position.distance_to(results[0][0]),.0001)
            self.assertAlmostEqual(elapsed,results[0][1])
            self.assertEqual(pygame.image.tobytes(image,'RGBA'),pygame.image.tobytes(results[0][2],'RGBA'))
