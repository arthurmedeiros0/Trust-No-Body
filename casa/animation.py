"""Ciclos compartilhados pela exploracao e pelo teste de movimentacao."""
from .config import LATERAL_CYCLE, PLAYER_LATERAL_CYCLE

def animation_cycles(idle, walk, lateral_cycle=None):
    patterns=lateral_cycle if lateral_cycle is not None else {d:PLAYER_LATERAL_CYCLE for d in ('direita','esquerda')}
    return {direction: tuple(idle[direction] if index is None else walk[direction][index]
                             for index in patterns[direction])
            if direction in ('direita','esquerda') else tuple(frames)
            for direction,frames in walk.items()}


def resident_animation_cycles(idle,walk,step_first=False):
    # Cada passo disponivel e precedido pelo proprio idle, inclusive com um
    # unico quadro. Nao usa indices fixos nem imagens de outra direcao.
    return {direction:tuple(image for frame in frames for image in ((frame,idle[direction]) if step_first else (idle[direction],frame)))
            for direction,frames in walk.items()}
