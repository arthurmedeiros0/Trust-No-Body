"""Carregamento explicito dos 16 sprites organizados."""
import pygame
from .config import PLAYER_ASSET_ROOT, PLAYER_SIZE

def load_sprites():
    base = PLAYER_ASSET_ROOT
    idle, walk = {}, {}
    for direction in ('frente','costas','direita','esquerda'):
        idle[direction] = pygame.image.load(str(base/f'parado/{direction}.png')).convert_alpha()
        walk[direction] = [pygame.image.load(str(base/f'andando/{direction}/{n}.png')).convert_alpha() for n in range(1,4)]
        for image in [idle[direction],*walk[direction]]:
            if image.get_size() != PLAYER_SIZE:
                raise ValueError('Sprite fora do padrao 64 x 96: '+direction)
    return idle, walk
