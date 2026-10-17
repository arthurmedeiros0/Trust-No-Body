"""Capturas reproduziveis da cama, HUD e suprimentos; sem alterar assets."""
import os
os.environ.setdefault('SDL_VIDEODRIVER','dummy')
import pygame
from casa.game import House
from casa.config import ROOT


def main():
    pygame.init()
    screen=pygame.display.set_mode((1280,720))
    game=House();game.dialog=''
    game.news.watch(game.news.current(1))
    game.decide_visitor(game.visitor_session.visitors['ricardo'],'rejeitado')
    game.debug=True
    game.player.feet=game.scene.point((383,245))
    game.draw(screen);pygame.image.save(screen,str(ROOT/'docs/cama_interacao_f3.png'))
    game.interact();assert game.sleep_option
    game.confirm_sleep();game.update((0,0),3)
    assert game.days.day==2 and game.visitor_session.survival.alive
    game.dialog='';game.debug=False
    game.draw(screen);pygame.image.save(screen,str(ROOT/'docs/hud_dia2.png'))
    game.inventory.active=True
    game.draw(screen);pygame.image.save(screen,str(ROOT/'docs/suprimentos_simplificado.png'))
    pygame.quit()


if __name__=='__main__':main()
