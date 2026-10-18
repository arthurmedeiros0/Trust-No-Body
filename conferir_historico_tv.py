"""Reproduz boletim perdido, primeira leitura tardia e status da lista."""
import os
os.environ.setdefault('SDL_VIDEODRIVER','dummy')
import pygame
from casa.game import House
from casa.config import ROOT


def main():
    pygame.init();screen=pygame.display.set_mode((1280,720));game=House();game.dialog=''
    session=game.visitor_session
    game.news.watch(game.news.current(1))
    session.survival.add_supplies(30,30) # Apenas roteiro de teste para isolar a TV.
    while game.days.day<5:
        if session.manager.current:game.decide_visitor(session.visitors[session.manager.current],'acolhido')
        game.dialog='';game.change_room('quarto',game.scenes['quarto'].point((345,365)))
        game.handle_event(pygame.event.Event(pygame.KEYUP,key=pygame.K_e))
        game.interact();assert game.sleep_option
        game.confirm_sleep();game.update((0,0),3)
    assert not session.medical.known
    game.dialog='';ui=game.television;ui.open();ui.choose('history')
    def capture(name):game.draw(screen);pygame.image.save(screen,str(ROOT/'docs'/name))
    capture('historico_nao_assistidas.png')
    ui.choose('news:boletim_04');capture('historico_boletim_antigo.png')
    assert session.medical.known=={'manchas_maos','dentes_deteriorados'}
    ui.choose('back');capture('historico_assistida.png')
    for _ in range(2):game.handle_event(pygame.event.Event(pygame.KEYDOWN,key=pygame.K_ESCAPE))
    capture('historico_descoberta_tardia.png')
    assert 'NOVAS INVESTIGAÇÕES' in game.dialog
    pygame.quit()


if __name__=='__main__':main()
