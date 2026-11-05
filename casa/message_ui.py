"""Painel narrativo compacto, com paginação e ações compartilhadas."""
import pygame
from . import ui_theme as ui

class MessageUI:
    def __init__(self):
        self.value=None;self.page=0

    def prepare(self,value,confirmation=False,kind='narrative'):
        if self.value!=value:self.value=value;self.page=0
        self.confirmation=confirmation;self.kind=kind
        lines=ui.wrapped_lines(value,872,ui.font(25))
        height=min(260,max(26,len(lines)*26))
        self.box=pygame.Rect(180,676-(height+132),920,height+132)
        self.body=pygame.Rect(204,self.box.y+52,872,height)
        self.pages=ui.text_pages(value,self.body,ui.font(25))
        self.page=min(self.page,len(self.pages)-1)
        y=self.box.bottom-56
        self.buttons={'close':(pygame.Rect(876,y,200,36),'Cancelar' if confirmation else 'Continuar')}
        if confirmation:self.buttons['confirm']=(pygame.Rect(660,y,200,36),'Dormir [S / Enter]')
        if self.page:self.buttons['prev']=(pygame.Rect(204,y,110,36),'Anterior')
        if self.page<len(self.pages)-1:self.buttons['next']=(pygame.Rect(330,y,110,36),'Próxima')

    def handle_event(self,event):
        if event.type==pygame.MOUSEBUTTONDOWN and event.button==1:
            key=next((k for k,(r,_) in self.buttons.items() if r.collidepoint(event.pos)),None)
            if key in ('prev','next'):self.page+=1 if key=='next' else -1;return 'handled'
            if key=='close':return 'close' if self.confirmation else self.advance()
            return key
        if event.type!=pygame.KEYDOWN:return None
        if event.key in (pygame.K_LEFT,pygame.K_PAGEUP):self.page=max(0,self.page-1);return 'handled'
        if event.key in (pygame.K_RIGHT,pygame.K_PAGEDOWN):self.page=min(len(self.pages)-1,self.page+1);return 'handled'
        if event.key==pygame.K_ESCAPE:return 'close'
        if self.confirmation and event.key in (pygame.K_s,pygame.K_RETURN):return 'confirm'
        if event.key==pygame.K_n:return 'close'
        if event.key in (pygame.K_RETURN,pygame.K_SPACE):return self.advance()
        return 'handled'

    def advance(self):
        if self.page<len(self.pages)-1:self.page+=1;return 'handled'
        return 'close'

    def draw(self,screen):
        accent=ui.PAPER if self.kind in ('important','confirmation') else ui.MUTED
        ui.panel(screen,self.box,accent=accent)
        labels={'narrative':'RELATO','info':'INFORMAÇÃO','important':'ATENÇÃO','summary':'RESUMO DO DIA','confirmation':'ENCERRAR O DIA'}
        ui.text(screen,labels[self.kind],(204,self.box.y+20,700,24),ui.font(20),accent,line_height=22)
        ui.text(screen,self.value,self.body,ui.font(25),page=self.page)
        for rect,label in self.buttons.values():ui.button(screen,rect,label,typeface=ui.font(22))
        if len(self.pages)>1:ui.text(screen,f'{self.page+1} / {len(self.pages)}',(466,self.box.bottom-48,120,24),ui.font(20),ui.MUTED)
