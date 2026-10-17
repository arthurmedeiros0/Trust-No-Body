"""Escala apenas visual dos moradores, ancorada no mesmo ponto logico dos pes."""
from functools import lru_cache
import pygame

RICARDO_VISUAL_SCALE = 1.08


@lru_cache(maxsize=128)
def resident_frame(visitor_id, source):
    scale=RICARDO_VISUAL_SCALE if visitor_id=='ricardo' else 1.0
    width,height=source.get_size()
    size=(round(width*scale),round(height*scale))
    image=source if size==(width,height) else pygame.transform.scale(source,size)
    # Os PNGs tem canvas 64x96 e linha de apoio y=94. A escala efetiva
    # arredondada tambem precisa ser aplicada a essa ancora, nao a posicao.
    anchor=(image.get_width()//2,round(94*image.get_height()/height))
    return image,anchor
