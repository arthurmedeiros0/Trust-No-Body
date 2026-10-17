"""WASD/setas: mover. ESC: sair. --smoke-test: verificacao sem janela."""
import argparse
import os
from casa.animation import animation_cycles
from casa.shadow import Shadow
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SIZE = (1280, 720)
FPS = 60
FRAME_SECONDS = 0.14
SPEED = 220


def load_sprites(pygame):
    base = ROOT / 'personagens/protagonista/processados'
    idle, walk = {}, {}
    for direction in ('frente','costas','direita','esquerda'):
        idle[direction] = pygame.image.load(str(base/f'parado/{direction}.png')).convert_alpha()
        walk[direction] = [pygame.image.load(str(base/f'andando/{direction}/{n}.png')).convert_alpha() for n in range(1,4)]
    return idle, walk


class Player:
    def __init__(self, pygame, idle, walk):
        self.pg, self.idle, self.walk = pygame, idle, walk
        self.cycles = animation_cycles(idle,walk)
        self.shadow = Shadow()
        self.position = pygame.Vector2(608,312)
        self.direction = 'frente'
        self.elapsed = 0.0
        self.moving = False

    def update(self, movement, dt):
        vector = self.pg.Vector2(movement)
        moving = vector.length_squared() > 0
        if moving:
            direction = ('direita' if vector.x > 0 else 'esquerda') if vector.x else ('frente' if vector.y > 0 else 'costas')
            if direction != self.direction or not self.moving:
                self.elapsed = 0
            self.direction = direction
            self.position += vector.normalize()*SPEED*dt
            self.elapsed += dt
        else:
            self.elapsed = 0
        self.moving = moving
        self.position.x = max(0,min(SIZE[0]-64,self.position.x))
        self.position.y = max(0,min(SIZE[1]-96,self.position.y))

    @property
    def image(self):
        return self.cycles[self.direction][int(self.elapsed/FRAME_SECONDS)%len(self.cycles[self.direction])] if self.moving else self.idle[self.direction]


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--smoke-test',action='store_true')
    args=parser.parse_args()
    if args.smoke_test:
        os.environ['SDL_VIDEODRIVER']='dummy'
        os.environ['SDL_AUDIODRIVER']='dummy'
    import pygame
    pygame.init()
    try:
        screen=pygame.display.set_mode(SIZE)
        pygame.display.set_caption('Trust No Body - teste de movimentacao')
        idle,walk=load_sprites(pygame)
        player=Player(pygame,idle,walk)
        clock=pygame.time.Clock()
        font=pygame.font.Font(None,24)
        if args.smoke_test:
            for direction,vector in [('frente',(0,1)),('costas',(0,-1)),('direita',(1,0)),('esquerda',(-1,0))]:
                player.update(vector,0)
                assert player.direction == direction
                for frame in range(len(player.cycles[direction])):
                    player.elapsed=frame*FRAME_SECONDS+0.001
                    assert player.image is player.cycles[direction][frame]
                player.update((0,0),0)
                assert player.image is idle[direction]
                player.update(vector,100)
                assert 0 <= player.position.x <= 1216 and 0 <= player.position.y <= 624
            player.position.update(400,300)
            start=player.position.copy();player.update((1,1),1)
            assert abs(player.position.distance_to(start)-SPEED)<0.001
            for surface in [*idle.values(),*[im for frames in walk.values() for im in frames]]:
                assert surface.get_size()==(64,96)
            screen.blit(player.image,player.position);pygame.display.flip()
            print('OK: 16 sprites, quatro direcoes, tres quadros, repouso, diagonal e limites.')
            return
        running=True
        while running:
            dt=min(clock.tick(FPS)/1000,0.05)
            for event in pygame.event.get():
                if event.type == pygame.QUIT or (event.type==pygame.KEYDOWN and event.key==pygame.K_ESCAPE):
                    running=False
            keys=pygame.key.get_pressed()
            movement=(int(keys[pygame.K_d] or keys[pygame.K_RIGHT])-int(keys[pygame.K_a] or keys[pygame.K_LEFT]),
                      int(keys[pygame.K_s] or keys[pygame.K_DOWN])-int(keys[pygame.K_w] or keys[pygame.K_UP]))
            player.update(movement,dt)
            screen.fill('#283a36')
            for x in range(0,SIZE[0],64): pygame.draw.line(screen,'#30433d',(x,0),(x,SIZE[1]))
            for y in range(0,SIZE[1],64): pygame.draw.line(screen,'#30433d',(0,y),(SIZE[0],y))
            player.shadow.draw(screen,player.position+pygame.Vector2(32,94))
            screen.blit(player.image,(round(player.position.x),round(player.position.y)))
            screen.blit(font.render('WASD / Setas: mover    ESC: sair',True,'#e8eadc'),(20,20))
            pygame.display.flip()
    finally:
        pygame.quit()


if __name__=='__main__':
    main()
