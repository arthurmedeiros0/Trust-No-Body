"""Menu principal e pausa; apresentação sem acesso ao estado clínico."""
import pygame
from .config import ROOT
from . import ui_theme as ui

class GameMenu:
    def __init__(self, available=()):
        self.page='main';self.mode=None;self.selected=0;self.hover=None
        self.logo_original=pygame.image.load(str(ROOT/'logo/logo.png')).convert_alpha()
        # Escala nearest-neighbor, mantendo a proporção e o fundo preto da arte.
        ratio=min(430/self.logo_original.get_width(),430/self.logo_original.get_height())
        self.logo=pygame.transform.scale(self.logo_original,tuple(round(n*ratio) for n in self.logo_original.get_size()))

    def entries(self):
        return [('normal','JOGAR'),('quit','SAIR')] if self.page=='main' else [('resume','CONTINUAR'),('main','MENU PRINCIPAL')]

    def rectangles(self):
        return {key:pygame.Rect(510,502+i*60,260,44) for i,(key,_) in enumerate(self.entries())}

    def choose(self,key):
        if key not in dict(self.entries()):return None
        if key=='main':self.page='main';self.selected=0
        return (key,None,None)

    def handle_event(self,event):
        if event.type==pygame.MOUSEMOTION:
            self.hover=next((key for key,r in self.rectangles().items() if r.collidepoint(event.pos)),None)
            if self.hover:self.selected=list(self.rectangles()).index(self.hover)
        if event.type==pygame.MOUSEBUTTONDOWN and event.button==1:
            return self.choose(next((key for key,r in self.rectangles().items() if r.collidepoint(event.pos)),None))
        if event.type==pygame.KEYDOWN:
            if event.key==pygame.K_ESCAPE and self.page=='pause':return self.choose('resume')
            if event.key in (pygame.K_DOWN,pygame.K_s):self.selected=(self.selected+1)%len(self.entries())
            elif event.key in (pygame.K_UP,pygame.K_w):self.selected=(self.selected-1)%len(self.entries())
            elif event.key in (pygame.K_RETURN,pygame.K_SPACE):return self.choose(self.entries()[self.selected][0])
        return None

    def draw(self,screen):
        screen.fill('#000000')
        # Luz e linhas discretas deixam a arte original integrar-se ao preto.
        for x in (96,1183):
            pygame.draw.line(screen,'#20272b',(x,96),(x,620))
            pygame.draw.line(screen,'#655340',(x,330),(x,390),2)
        screen.blit(self.logo,self.logo.get_rect(midtop=(640,42)))
        if self.page=='pause':
            ui.text(screen,'PAUSA',pygame.Rect(510,462,260,28),ui.font(26),ui.PAPER)
        for i,(key,label) in enumerate(self.entries()):
            ui.button(screen,self.rectangles()[key],label,selected=i==self.selected,typeface=ui.font(25))
        hint=ui.font(20).render('W/S ou setas · Enter · Mouse'+(' · ESC: continuar' if self.page=='pause' else ''),True,ui.MUTED)
        screen.blit(hint,hint.get_rect(center=(640,654)))
