"""Observacao frontal: fundo, camada futura de visitante, interface."""
import pygame
from . import ui_theme as theme
from .config import ROOT,PEEPHOLE_IMAGES,PEEPHOLE_VIEWPORT,FUTURE_VISITOR_POSITION,FUTURE_VISITOR_SCALE

class Peephole:
    def __init__(self):
        viewport=pygame.Rect(PEEPHOLE_VIEWPORT)
        self.images={}
        self.rects={}
        for period,file in PEEPHOLE_IMAGES.items():
            original=pygame.image.load(str(ROOT/'cenarios/olho_magico'/file)).convert()
            scale=min(viewport.width/original.get_width(),viewport.height/original.get_height())
            size=(round(original.get_width()*scale),round(original.get_height()*scale))
            self.images[period]=pygame.transform.scale(original,size)
            self.rects[period]=self.images[period].get_rect(center=viewport.center)
        self.visitor_layer=pygame.sprite.Group()  # Sem personagens nesta etapa.
        self.visitor_position=FUTURE_VISITOR_POSITION
        self.visitor_scale=FUTURE_VISITOR_SCALE
        self.font=pygame.font.Font(None,27)
        self.back_button=pygame.Rect(1070,650,170,44)
        self.visitor_ui=None

    def handle_event(self,event):
        if self.visitor_ui and self.visitor_ui.visitor.state=='aguardando':
            return self.visitor_ui.handle_event(event)
        if event.type==pygame.KEYDOWN and event.key==pygame.K_ESCAPE:return 'back'
        if event.type==pygame.MOUSEBUTTONDOWN and event.button==1:
            if self.back_button.collidepoint(event.pos):return 'back'
        return None

    def draw_visitors(self,screen):
        # Uma futura entidade recebe anchor/scale; nenhuma e criada aqui.
        if self.visitor_ui:self.visitor_ui.draw_portrait(screen)
        for visitor in self.visitor_layer:
            size=tuple(max(1,round(v*self.visitor_scale)) for v in visitor.image.get_size())
            image=pygame.transform.scale(visitor.image,size)
            screen.blit(image,image.get_rect(midbottom=self.visitor_position))

    def draw(self,screen,period):
        screen.fill('#101419')
        screen.blit(self.images[period],self.rects[period])
        self.draw_visitors(screen)
        if self.visitor_ui and self.visitor_ui.visitor.state=='aguardando':
            self.visitor_ui.draw(screen)
            return
        theme.button(screen,self.back_button,'Voltar',typeface=self.font)
