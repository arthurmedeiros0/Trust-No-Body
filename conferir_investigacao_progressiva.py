"""Capturas reais da interface; avancos tardios usam estoque somente deste roteiro."""
import os
os.environ.setdefault('SDL_VIDEODRIVER','dummy')
import pygame
from casa.game import House
from casa.config import ROOT


def main():
    pygame.init();screen=pygame.display.set_mode((1280,720));game=House();game.dialog=''
    session=game.visitor_session
    def key(key):game.handle_event(pygame.event.Event(pygame.KEYDOWN,key=key))
    def capture(name):game.draw(screen);pygame.image.save(screen,str(ROOT/'docs'/name))
    def click(ui,key):game.handle_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN,button=1,pos=ui.layout()[key][0].center))
    def resolve():
        if session.manager.current:game.decide_visitor(session.visitors[session.manager.current],'acolhido')
    def sleep():
        game.dialog='';resolve()
        game.change_room('quarto',game.scenes['quarto'].point((345,365)))
        game.handle_event(pygame.event.Event(pygame.KEYUP,key=pygame.K_e))
        game.interact();assert game.sleep_option
        game.confirm_sleep();game.update((0,0),3)
    def approach(visitor_id):
        actor=game.residents[visitor_id];game.change_room(actor.room);game.dialog=''
        for offset in ((30,0),(-30,0),(0,30),(0,-30)):
            game.player.feet=actor.feet+pygame.Vector2(offset)
            if game.scene.collisions.allows(game.player.feet) and game.nearest_interaction().target==visitor_id:break
        game.interact();assert game.resident_ui
    game.news.watch(game.news.current(1))
    game.change_room('entrada',game.scenes['entrada'].point((768,402)))
    game.interact();game.update((0,0),1);game.update((0,0),1)
    capture('investigacao_porta_bloqueada.png')
    resolve();game.observing=False
    session.survival.add_supplies(100,100) # Exclusivo do roteiro de validacao, nunca da partida.
    approach('ricardo');capture('investigacao_morador_dia1.png');key(pygame.K_ESCAPE)
    while game.days.day<4:sleep()
    game.dialog='';game.television.open();game.television.choose('current')
    capture('investigacao_tv_dia4.png');key(pygame.K_ESCAPE);key(pygame.K_ESCAPE)
    capture('investigacao_descoberta.png');key(pygame.K_RETURN)
    approach('ricardo');click(game.resident_ui,'investigate');capture('investigacao_ricardo_dia4.png')
    click(game.resident_ui,'manchas_maos');capture('investigacao_ricardo_maos.png')
    key(pygame.K_ESCAPE);key(pygame.K_ESCAPE);key(pygame.K_ESCAPE)
    while game.days.day<14:sleep()
    game.dialog='';game.television.open();game.television.choose('current')
    key(pygame.K_ESCAPE);key(pygame.K_ESCAPE);key(pygame.K_RETURN)
    approach('laura');click(game.resident_ui,'investigate');capture('investigacao_laura_dia14.png')
    click(game.resident_ui,'olhos_alterados');capture('investigacao_laura_olhos.png')
    pygame.quit()


if __name__=='__main__':main()
