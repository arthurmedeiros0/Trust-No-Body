"""Piso poligonal e bases dos moveis, no mesmo espaco do jogador."""
import pygame
from .config import PLAYER_HITBOX


def feet_rect(feet):
    body=pygame.Rect((0,0),PLAYER_HITBOX)
    body.midbottom=(round(feet.x),round(feet.y))
    return body


class CollisionMap:
    def __init__(self, floor, blocks, polygon=None):
        self.floor=pygame.Rect(floor)
        self.blocks=[pygame.Rect(rect) for rect in blocks]
        self.polygon=polygon
        self.floor_mask=None
        self.body_mask=pygame.mask.Mask(PLAYER_HITBOX,fill=True)
        if polygon:
            surface=pygame.Surface(self.floor.size,pygame.SRCALPHA)
            points=[(round(x-self.floor.x),round(y-self.floor.y)) for x,y in polygon]
            pygame.draw.polygon(surface,'white',points)
            self.floor_mask=pygame.mask.from_surface(surface)

    def allows(self, feet):
        body=feet_rect(feet)
        if not self.floor.contains(body): return False
        if self.floor_mask is not None:
            offset=(body.x-self.floor.x,body.y-self.floor.y)
            if self.floor_mask.overlap_area(self.body_mask,offset)!=body.width*body.height:
                return False
        return not any(body.colliderect(block) for block in self.blocks)

    def draw(self, screen, camera=(0,0)):
        offset=pygame.Vector2(camera)
        if self.polygon:
            pygame.draw.polygon(screen,'#49df9c',[pygame.Vector2(p)-offset for p in self.polygon],2)
        else:
            pygame.draw.rect(screen,'#49df9c',self.floor.move(-round(offset.x),-round(offset.y)),2)
        for block in self.blocks:
            pygame.draw.rect(screen,'#f36a6a',block.move(-round(offset.x),-round(offset.y)),2)
