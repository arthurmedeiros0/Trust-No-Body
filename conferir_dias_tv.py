"""Capturas do sono e do noticiario usando a interface real do Pygame."""
import os
os.environ.setdefault('SDL_VIDEODRIVER','dummy')
import pygame
from casa.game import House
from casa.config import ROOT


def main():
    pygame.init();screen=pygame.display.set_mode((1280,720))
    game=House();game.handle_event(pygame.event.Event(pygame.KEYDOWN,key=pygame.K_RETURN))
    game.news.watch(game.news.current(1))
    game.change_room('quarto',game.scenes['quarto'].point((345,365)))
    game.decide_visitor(game.visitor_session.visitors['ricardo'],'acolhido')
    game.visitor_session.survival.add_supplies(100,100) # Apenas roteiro de captura para dias avancados.
    def capture(name):game.draw(screen);pygame.image.save(screen,str(ROOT/'docs'/name))
    game.interact();capture('sono_confirmacao.png')
    game.confirm_sleep();game.update((0,0),.5);capture('sono_dia_2.png')
    game.update((0,0),3);capture('sono_acordou.png')
    game.television.open();capture('tv_menu.png')
    game.television.choose('current')
    for day in range(3,21):
        pending=game.visitor_session.manager.current
        if pending:game.decide_visitor(game.visitor_session.visitors[pending],'acolhido')
        game.days.advance()
        if day in (4,7,14,17,20):
            game.television.choose('current');capture(f'tv_dia_{day}.png')
    game.television.choose('history');capture('tv_historico.png')
    pygame.quit()

if __name__=='__main__':main()
