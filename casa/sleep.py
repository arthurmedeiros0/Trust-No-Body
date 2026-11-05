"""Fade de sono nao bloqueante, com cartela de novo dia e retorno ao quarto."""
import pygame
from .transitions import Fade
from . import ui_theme as ui


class SleepTransition(Fade):
    DURATION=.45
    HOLD=1.6

    def __init__(self,days):
        super().__init__();self.days=days
        self.title=pygame.font.Font(None,76)
        self.subtitle=pygame.font.Font(None,28)
        self.card=None
        self.card_key=None

    def day_card(self,size):
        """Cache da cartela; nenhuma alocação de textura por quadro."""
        key=(size,self.days.day)
        if key==self.card_key:return self.card
        self.card_key=key
        card=pygame.Surface(size);card.fill('#080c11')
        width,height=size
        box=pygame.Rect(0,0,min(820,width-80),300)
        box.center=(width//2,height//2)
        # Textura estática, sob a leitura; moldura em blocos como as outras UIs.
        for y in range(0,height,6):
            pygame.draw.line(card,'#0b1118',(0,y),(width,y))
        ui.panel(card,box,color=ui.INK,alpha=255)
        for x,y,dx,dy in ((box.left,box.top,1,1),(box.right-1,box.top,-1,1),
                          (box.left,box.bottom-1,1,-1),(box.right-1,box.bottom-1,-1,-1)):
            pygame.draw.lines(card,ui.PAPER,False,[(x,y+dy*16),(x,y),(x+dx*16,y)])
        heading=ui.font(20).render('UM NOVO DIA',True,ui.MUTED)
        card.blit(heading,heading.get_rect(center=(box.centerx,box.y+46)))
        title=self.title.render(f'DIA {self.days.day}',True,ui.PAPER)
        card.blit(title,title.get_rect(center=(box.centerx,box.y+115)))
        pygame.draw.line(card,ui.BORDER,(box.centerx-100,box.y+170),(box.centerx+100,box.y+170))
        pygame.draw.rect(card,ui.PAPER,(box.centerx-3,box.y+168,6,5))
        phrase='Mais um dia começa. A situação lá fora continua incerta.'
        lines=ui.wrapped_lines(phrase,box.width-96,self.subtitle)
        for i,line in enumerate(lines):
            text=self.subtitle.render(line,True,ui.TEXT)
            card.blit(text,text.get_rect(center=(box.centerx,box.y+214+i*30)))
        self.card=card
        return card

    def update(self,dt):
        if not self.active:return
        self.elapsed+=max(0,dt)
        while self.active:
            duration=self.HOLD if self.phase=='hold' else self.DURATION
            if self.elapsed<duration:break
            self.elapsed-=duration
            if self.phase=='out':
                callback=self.pending;self.pending=None;callback();self.phase='hold'
            elif self.phase=='hold':self.phase='in'
            else:self.phase='';self.elapsed=0

    def draw(self,screen):
        if self.phase=='hold':
            screen.fill('#080b10')
            card=self.day_card(screen.get_size())
            # Entrada e saída da arte dentro do HOLD original de 1,6 s.
            progress=max(0,min(1,self.elapsed/.22,(self.HOLD-self.elapsed)/.24))
            progress=progress*progress*(3-2*progress)
            card.set_alpha(round(255*progress))
            screen.blit(card,(0,0))
        else:super().draw(screen)
