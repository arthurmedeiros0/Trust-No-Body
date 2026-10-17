"""Fade nao bloqueante: troca de comodo somente na tela totalmente escura."""
import pygame
from .config import WINDOW

class Fade:
    DURATION=.22

    def __init__(self):
        self.pending=None
        self.phase=''
        self.elapsed=0.
        self.overlay=pygame.Surface(WINDOW)
        self.overlay.fill('black')

    @property
    def active(self):
        return bool(self.phase)

    def start(self, callback):
        if self.active: return
        self.pending=callback
        self.phase='out';self.elapsed=0.

    def update(self, dt):
        if not self.active: return
        self.elapsed+=dt
        if self.elapsed>=self.DURATION:
            self.elapsed-=self.DURATION
            if self.phase=='out':
                callback=self.pending;self.pending=None
                callback();self.phase='in'
            else:
                self.phase='';self.elapsed=0.

    def draw(self, screen):
        if self.active:
            progress=min(1,self.elapsed/self.DURATION)
            self.overlay.set_alpha(round(255*(progress if self.phase=='out' else 1-progress)))
            screen.blit(self.overlay,(0,0))
