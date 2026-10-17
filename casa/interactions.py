"""Objetos interativos reutilizaveis, selecionados pela proximidade."""
from dataclasses import dataclass
import pygame
from .config import INTERACTION_RADIUS

@dataclass
class Interaction:
    label: str
    point: pygame.Vector2
    action: str
    target: str = ''
    text: str = ''
    arrival: tuple | None = None
    direction: str = 'frente'
    prompt: str = ''
    radius: float = INTERACTION_RADIUS

    def distance(self, feet):
        return self.point.distance_to(feet)


def nearest(interactions, feet):
    candidates = [item for item in interactions if item.distance(feet) <= item.radius]
    return min(candidates, key=lambda item: item.distance(feet), default=None)
