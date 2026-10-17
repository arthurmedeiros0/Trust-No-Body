"""Exploracao da casa. Execute: python main.py. Testes: python main.py --smoke-test."""
import argparse
import os

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--smoke-test',action='store_true')
    parser.add_argument('--dev',action='store_true',help='Habilita editor de colisoes com F4')
    args=parser.parse_args()
    if args.smoke_test:
        os.environ['SDL_VIDEODRIVER']='dummy'
        os.environ['SDL_AUDIODRIVER']='dummy'
    import pygame
    from casa.config import WINDOW,FPS
    from casa.game import House
    pygame.init()
    try:
        screen=pygame.display.set_mode(WINDOW)
        pygame.display.set_caption('Trust No Body - exploracao da casa')
        if args.smoke_test:
            import unittest
            suite=unittest.defaultTestLoader.discover(str(__import__('pathlib').Path(__file__).resolve().parent/'tests'))
            result=unittest.TextTestRunner(verbosity=2).run(suite)
            if not result.wasSuccessful(): raise SystemExit(1)
            return
        game=House(development=args.dev);clock=pygame.time.Clock();running=True
        while running:
            dt=min(clock.tick(FPS)/1000,.05)
            for event in pygame.event.get():
                if event.type==pygame.QUIT or (event.type==pygame.KEYDOWN and event.key==pygame.K_ESCAPE and not game.captures_escape):
                    running=False
                else: game.handle_event(event)
            keys=pygame.key.get_pressed()
            movement=(int(keys[pygame.K_d] or keys[pygame.K_RIGHT])-int(keys[pygame.K_a] or keys[pygame.K_LEFT]),
                      int(keys[pygame.K_s] or keys[pygame.K_DOWN])-int(keys[pygame.K_w] or keys[pygame.K_UP]))
            game.update(movement,dt);game.draw(screen);pygame.display.flip()
    finally:
        pygame.quit()

if __name__=='__main__':
    main()
