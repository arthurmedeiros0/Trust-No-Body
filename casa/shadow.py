"""Sombra visual compartilhada; dimensoes em pixels da tela, sem colisao."""
import pygame
from .config import SHADOW_SIZE,SHADOW_OPACITY,SHADOW_OFFSET_Y

class Shadow:
    def __init__(self, size=SHADOW_SIZE, opacity=SHADOW_OPACITY, offset_y=SHADOW_OFFSET_Y):
        self.offset_y=offset_y
        self.surface=pygame.Surface(size,pygame.SRCALPHA)
        # Aneis externos mais leves para suavizar a elipse sem filtros no sprite.
        layers=max(1,min(4,size[1]//2))
        for inset in range(layers):
            rect=self.surface.get_rect().inflate(-2*inset,-2*inset)
            pygame.draw.ellipse(self.surface,(0,0,0,round(opacity*(inset+1)/layers)),rect)

    def rect(self, feet, camera=(0,0)):
        point=pygame.Vector2(feet)-pygame.Vector2(camera)
        return self.surface.get_rect(center=(round(point.x),round(point.y+self.offset_y)))

    def draw(self, screen, feet, camera=(0,0)):
        screen.blit(self.surface,self.rect(feet,camera))
