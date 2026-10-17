"""Fade de sono nao bloqueante, com cartela de novo dia e retorno ao quarto."""
import pygame
from .transitions import Fade


class SleepTransition(Fade):
    DURATION=.45
    HOLD=1.6

    def __init__(self,days):
        super().__init__();self.days=days
        self.title=pygame.font.Font(None,76)
        self.subtitle=pygame.font.Font(None,28)

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
            title=self.title.render(f'DIA {self.days.day}',True,'#e9dfcb')
            text=self.subtitle.render('Mais um dia começa. A situação lá fora continua incerta.',True,'#a8adb4')
            screen.blit(title,title.get_rect(center=(640,315)))
            screen.blit(text,text.get_rect(center=(640,395)))
        else:super().draw(screen)
