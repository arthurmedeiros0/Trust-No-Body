"""Captura a nova partida real, estoque do visitante, sono e derrota sem alterar PNGs."""
import os
os.environ.setdefault('SDL_VIDEODRIVER','dummy')
import pygame
from casa.game import House
from casa.config import ROOT


def main():
    pygame.init();screen=pygame.display.set_mode((1280,720));game=House()
    def key(key):game.handle_event(pygame.event.Event(pygame.KEYDOWN,key=key))
    def save(name):game.draw(screen);pygame.image.save(screen,str(ROOT/'docs'/name))
    save('sobrevivencia_intro.png');key(pygame.K_RETURN)
    key(pygame.K_i);save('sobrevivencia_inventario_zero.png');key(pygame.K_i)
    game.change_room('cozinha',game.scenes['cozinha'].point((635,250)))
    game.interact();save('sobrevivencia_geladeira.png');key(pygame.K_RETURN)
    game.change_room('quarto',game.scenes['quarto'].point((135,267)))
    key(pygame.K_e);game.television.choose('current');save('sobrevivencia_lockdown.png')
    key(pygame.K_ESCAPE);key(pygame.K_ESCAPE)
    game.change_room('entrada',game.scenes['entrada'].point((768,402)))
    game.interact();game.update((0,0),1)
    assert game.observing and not game.visitor_session.intro.objective
    ui=game.peephole.visitor_ui
    game.handle_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN,button=1,pos=ui.layout()['talk'][0].center))
    save('sobrevivencia_ricardo_dialogo.png')
    game.decide_visitor(game.visitor_session.visitors['ricardo'],'acolhido')
    game.observing=False
    key(pygame.K_i);save('sobrevivencia_inventario_ricardo.png');key(pygame.K_i)
    game.change_room('quarto',game.scenes['quarto'].point((345,365)))
    game.interact();game.confirm_sleep();game.update((0,0),3);save('sobrevivencia_resumo.png')
    game=House();key(pygame.K_RETURN);game.news.watch(game.news.current(1))
    game.decide_visitor(game.visitor_session.visitors['ricardo'],'rejeitado')
    for _ in range(3):
        if game.dialog:key(pygame.K_RETURN)
        pending=game.visitor_session.manager.current
        if pending:game.decide_visitor(game.visitor_session.visitors[pending],'rejeitado')
        game.change_room('quarto',game.scenes['quarto'].point((345,365)))
        game.handle_event(pygame.event.Event(pygame.KEYUP,key=pygame.K_e))
        game.interact();game.confirm_sleep();game.update((0,0),3)
    assert not game.visitor_session.survival.alive
    save('sobrevivencia_derrota.png');pygame.quit()

if __name__=='__main__':main()
