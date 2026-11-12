"""Exploracao da casa. Execute: python main.py. Testes: python main.py --smoke-test."""
import argparse
import os


class GameFlow:
    """Encaminha menu, introdução e partida sem sobrepor seus eventos."""
    def __init__(self, house_factory, development=False):
        from casa.menu import GameMenu
        self.menu=GameMenu()
        self.house_factory=house_factory
        self.development=development
        self.game=None
        self.intro=None

    def handle_event(self,event):
        import pygame
        from casa.intro_ui import IntroUI
        if self.intro is not None:
            if self.intro.handle_event(event):
                self.intro=None
                self.game=self.house_factory(development=self.development)
                self.game.defer_restart=True
            return None
        if self.game is None or self.menu.page=='pause':
            action=self.menu.handle_event(event)
            if action:
                kind,_,_=action
                if kind=='quit':return 'quit'
                if kind=='normal':
                    self.intro=IntroUI()
                    self.menu.page='playing'
                elif kind=='main':self.game=None
                elif kind=='resume':self.menu.page='playing'
            return None
        if event.type==pygame.KEYDOWN and event.key==pygame.K_F1:
            self.menu.page='pause';self.menu.selected=0;return None
        if event.type==pygame.KEYDOWN and event.key==pygame.K_ESCAPE and not self.game.captures_escape:
            self.menu.page='pause';self.menu.selected=0;return None
        if self.game.handle_event(event)=='restart':
            self.game=None
            self.intro=IntroUI()
        return None

    def update(self,movement,dt):
        if self.intro is not None:self.intro.update(dt)
        elif self.game is not None and self.menu.page=='playing':self.game.update(movement,dt)

    def draw(self,screen):
        if self.intro is not None:self.intro.draw(screen)
        elif self.game is None or self.menu.page in ('main','pause'):self.menu.draw(screen)
        else:self.game.draw(screen)

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
        flow=GameFlow(House,args.dev)
        clock=pygame.time.Clock();running=True

        while running:
            dt=min(clock.tick(FPS)/1000,.05)
            for event in pygame.event.get():
                if event.type==pygame.QUIT:running=False;continue
                if flow.handle_event(event)=='quit':running=False
            keys=pygame.key.get_pressed()
            movement=(int(keys[pygame.K_d] or keys[pygame.K_RIGHT])-int(keys[pygame.K_a] or keys[pygame.K_LEFT]),
                      int(keys[pygame.K_s] or keys[pygame.K_DOWN])-int(keys[pygame.K_w] or keys[pygame.K_UP]))
            flow.update(movement,dt)
            flow.draw(screen)
            pygame.display.flip()
    finally:
        pygame.quit()

if __name__=='__main__':
    main()
