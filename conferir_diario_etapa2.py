"""Capturas da Etapa 2 em sessão de demonstração, sem modificar dados originais."""
import os
os.environ.setdefault('SDL_VIDEODRIVER','dummy')
os.environ.setdefault('SDL_AUDIODRIVER','dummy')
from pathlib import Path
import pygame
from casa.game import House
from casa.visitor_dialogue import Dialogue
from casa.diario import MARKS,CONCLUSIONS

def main():
    pygame.init();screen=pygame.display.set_mode((1280,720))
    out=Path('docs/diario_etapa2');out.mkdir(parents=True,exist_ok=True)
    g=House();g.dialog='';s=g.visitor_session;j=g.journal_ui
    def capture(name):
        g.draw(screen);pygame.image.save(screen,str(out/name))
    def watch(day):
        s.days.day=day;s.news.unlock(day);s.news.watch(s.news.current(day));s.medical.discoveries.clear()
    g.open_journal();capture('01_diario_vazio.png');j.close()
    watch(1);g.observing=True;view=g.peephole.visitor_ui;view.open_conversation()
    g.open_journal();capture('02_rascunho_sem_sintomas.png');j.close()
    watch(4);g.open_journal();capture('03_dois_sintomas.png');j.close()
    watch(7);view.dialogue.ask(0);view.page='answer';view.response=view.dialogue.progress.answer_text
    before=(view.page,view.response,view.text_page)
    g.open_journal();capture('04_rascunho_conversa.png');j.close()
    assert before==(view.page,view.response,view.text_page)
    capture('05_conversa_restaurada.png')
    view.page='investigate'
    view.handle_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN,button=1,pos=view.layout()['olhos_alterados'][0].center))
    g.open_journal();j.scroll=240;capture('06_exame_sem_preenchimento.png')
    draft=s.journal.drafts[view.visitor.id]
    draft.notes='Anotação de teste: comparar os relatos e rever a imagem examinada.'
    draft.marks['manchas_maos']=MARKS[1];draft.conclusion=CONCLUSIONS[1]
    j.close();capture('07_imagem_restaurada.png')
    assert g.decide_visitor(view.visitor,'acolhido')
    g.observing=False;g.change_room(view.visitor.definition['room'])
    g.open_journal();j.select(view.visitor.id);j.scroll=0;capture('08_ficha_acolhido.png')
    j.change_tab('Anotações');capture('09_editor.png')
    j.focus(True);j.cursor=len(draft.notes)
    j.handle_event(pygame.event.Event(pygame.TEXTINPUT,text='\nObservação de demonstração, com acentos. '*45))
    capture('10_editor_longo.png');j.close()
    watch(14);watch(17);g.open_journal();j.change_tab('Noticiários');capture('11_recortes.png')
    j.scroll=j.max_scroll;capture('12_terceiro_padrao.png')
    j.change_tab('Linha do Tempo');capture('13_linha_do_tempo.png');j.close()
    s.eliminate(view.visitor.id)
    g.open_journal();j.change_tab('Personagens');j.select(view.visitor.id);j.scroll=0;capture('14_eliminado.png')
    j.close();g.change_room('corredor');capture('15_acesso_rapido.png')
    # Lista cheia em outra sessão de demonstração: mesmos eventos de acolhimento.
    for key,v in s.visitors.items():
        if key==view.visitor.id:continue
        v.arrived=True;s._arrive(v);s.manager.current=key;s.decide(v,'acolhido')
    j.open();j.select('laura');j.change_tab('Personagens')
    screen.fill('#111820');j.draw(screen);pygame.image.save(screen,str(out/'16_sete_fichas.png'))
    pygame.quit()

if __name__=='__main__':main()
