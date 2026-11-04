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
    from casa.menu import GameMenu
    from casa.visitors import VisitorSession
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
        catalogue=VisitorSession()
        available=set(catalogue.visitors)-set(catalogue.unavailable)
        menu=GameMenu(available)
        game=None;mode=None;test_choice=None
        clock=pygame.time.Clock();running=True

        def start_game(kind,character=None,condition=None):
            house=House(development=args.dev)
            if kind=='test':
                house.dialog=''
                house.visitor_session.start_test(character,condition)
                house.change_room('entrada')
                house.observing=True
            return house

        while running:
            dt=min(clock.tick(FPS)/1000,.05)
            for event in pygame.event.get():
                if event.type==pygame.QUIT:running=False;continue
                if game is None or menu.page=='pause':
                    action=menu.handle_event(event)
                    if action:
                        kind,character,condition=action
                        if kind=='quit':running=False
                        elif kind in ('normal','test'):
                            game=start_game(kind,character,condition)
                            mode=kind;test_choice=(character,condition) if kind=='test' else None
                            menu.mode=kind
                            menu.page='playing'
                        elif kind=='restart' and test_choice:
                            game=start_game('test',*test_choice)
                            menu.page='playing'
                        elif kind=='main':game=None;mode=None
                        elif kind=='resume':menu.page='playing'
                    continue
                if event.type==pygame.KEYDOWN and event.key==pygame.K_F1:
                    menu.page='pause';menu.selected=0;continue
                if event.type==pygame.KEYDOWN and event.key==pygame.K_ESCAPE and not game.captures_escape:
                    menu.page='pause';menu.selected=0;continue
                game.handle_event(event)
            if game is None or menu.page in ('main','select','setup','pause'):
                menu.draw(screen)
            else:
                keys=pygame.key.get_pressed()
                movement=(int(keys[pygame.K_d] or keys[pygame.K_RIGHT])-int(keys[pygame.K_a] or keys[pygame.K_LEFT]),
                          int(keys[pygame.K_s] or keys[pygame.K_DOWN])-int(keys[pygame.K_w] or keys[pygame.K_UP]))
                game.update(movement,dt);game.draw(screen)
                if mode=='test':
                    visitor=game.visitor_session.visitors[test_choice[0]]
                    label=f'MODO TESTE | {visitor.definition["name"]} | condição real: {visitor.diagnosis} | F1: opções'
                    pygame.draw.rect(screen,'#172027',(0,0,1280,34))
                    screen.blit(game.small.render(label,True,'#f1e6c8'),(20,8))
            pygame.display.flip()
    finally:
        pygame.quit()

if __name__=='__main__':
    main()
