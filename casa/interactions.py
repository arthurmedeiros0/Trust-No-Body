"""Objetos interativos reutilizaveis, selecionados pela proximidade."""
from dataclasses import dataclass
import pygame
from .config import INTERACTION_RADIUS
from .collisions import feet_rect

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
    region: pygame.Rect | None = None

    def distance(self, feet):
        if self.region is not None:
            body=feet_rect(feet)
            dx=max(self.region.left-body.right,body.left-self.region.right,0)
            dy=max(self.region.top-body.bottom,body.top-self.region.bottom,0)
            return (dx*dx+dy*dy)**.5
        return self.point.distance_to(feet)


def nearest(interactions, feet):
    candidates = [item for item in interactions if item.distance(feet) <= item.radius]
    return min(candidates, key=lambda item: item.distance(feet), default=None)
