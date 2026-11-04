"""Capturas reproduzíveis das interfaces em 1280x720, sem alterar a partida real."""
import os
os.environ.setdefault('SDL_VIDEODRIVER','dummy')
os.environ.setdefault('SDL_AUDIODRIVER','dummy')
from pathlib import Path
import pygame
from casa.game import House
from casa.visitor_ui import VisitorUI
from casa import face_portraits,ui_theme as ui

def main():
    pygame.init();screen=pygame.display.set_mode((1280,720))
    output=Path('docs/interfaces_etapa1');output.mkdir(parents=True,exist_ok=True)
    game=House();session=game.visitor_session
    game.dialog='';session.news.watch(session.news.current(1));game.observing=True
    visitor=session.visitors['ricardo'];view=game.peephole.visitor_ui
    def capture(name):
        game.draw(screen);pygame.image.save(screen,str(output/name))
    capture('01_acoes_porta.png')
    view.visitor.talked=True;view.open_conversation();capture('02_conversa_apresentacao.png')
    view.page='talk';capture('03_perguntas.png')
    view.dialogue.ask(0);view.page='answer';view.response=view.dialogue.progress.answer_text;capture('04_resposta.png')
    session.medical.known.update(visitor.definition['investigation']);view.page='investigate';capture('05_inspecao.png')
    view.feature='olhos_alterados';view.knowledge.observe(visitor,view.feature);view.page='image';capture('06_exame.png')
    view.page='confirm';view.decision='acolhido';capture('07_confirmar_acolhimento.png')
    # Estado de demonstração: nenhum evento da simulação é processado.
    game.decide_visitor(visitor,'acolhido');game.observing=False
    game.change_room(visitor.definition['room'])
    game.resident_ui=VisitorUI(visitor,game.visitor_assets[visitor.id],lambda *a:False,knowledge=session.medical,resident=True,session=session)
    game.resident_ui.open_conversation();capture('08_conversa_morador.png')
    game.resident_ui.reset();capture('09_acoes_morador.png')
    game.resident_ui.page='confirm';game.resident_ui.decision='eliminado';capture('10_eliminacao.png')
    game.resident_ui=None
    session.days.day=17;session.news.unlock(17);game.television.open();capture('11_tv_inicio.png')
    game.television.choose('current');capture('12_tv_atual.png')
    game.television.choose('history');capture('13_tv_arquivo.png')
    game.television.choose('news:boletim_07');capture('14_tv_antiga.png')
    screen.fill(ui.INK)
    for i,v in enumerate(session.visitors.values()):
        x=40+i*174
        face_portraits.draw(screen,v.definition,(x,240,156,190))
        ui.text(screen,v.definition['name'],pygame.Rect(x,452,156,32),ui.font(25),ui.PAPER)
    pygame.image.save(screen,str(output/'15_retratos_normais.png'))
    pygame.quit()

if __name__=='__main__':main()
