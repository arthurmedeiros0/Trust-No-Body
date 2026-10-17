"""Ciclos compartilhados pela exploracao e pelo teste de movimentacao."""
from .config import LATERAL_CYCLE

def animation_cycles(idle, walk):
    return {direction: tuple(idle[direction] if index is None else walk[direction][index]
                             for index in LATERAL_CYCLE[direction])
            if direction in ('direita','esquerda') else tuple(frames)
            for direction,frames in walk.items()}
