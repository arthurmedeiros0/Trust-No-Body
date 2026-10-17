"""Morador simples: pausas, passos curtos e colisoes pelos pes."""
import math
import random
import pygame
from .collisions import feet_rect

class ActorCollisions:
    def __init__(self,scenario,blocked=()):
        self.scenario=scenario
        self.blocked=list(blocked)

    def allows(self,feet):
        return self.scenario.allows(feet) and not any(feet_rect(feet).colliderect(rect) for rect in self.blocked)


def free_spawn(scene,preferred,blocked=(),reserved=()):
    collisions=ActorCollisions(scene.collisions,[rect.inflate(24,24) for rect in blocked])
    preferred=pygame.Vector2(preferred)
    candidates=[pygame.Vector2(preferred)]
    for radius in range(20,401,20):
        for offset in range(-radius,radius+1,20):
            candidates.extend(preferred+pygame.Vector2(x,y) for x,y in ((offset,-radius),(offset,radius),(-radius,offset),(radius,offset)))
    return next((p for p in candidates if collisions.allows(p) and all(p.distance_to(door)>=48 for door in reserved)),None)

class Resident:
    def __init__(self,visitor_id,room,feet,direction='frente',settings=None,rng=None,reserved=()):
        settings=settings or {}
        self.visitor_id=visitor_id;self.room=room
        self.feet=pygame.Vector2(feet);self.origin=self.feet.copy()
        self.reserved=[pygame.Vector2(point) for point in reserved]
        self.direction=direction
        self.speed=settings.get('speed',34)
        self.radius=settings.get('radius',72)
        self.wait_range=tuple(settings.get('wait_seconds',(2,4)))
        self.walk_range=tuple(settings.get('walk_seconds',(.7,1.4)))
        self.rng=rng if rng is not None else random.Random()
        self.velocity=pygame.Vector2()
        self.walking=False
        self.moving=False
        self.animation_elapsed=0.
        self.frame_seconds=settings.get('frame_seconds',.18)
        self.remaining=self.rng.uniform(*self.wait_range)

    def rest(self):
        self.walking=False;self.velocity.update(0,0)
        self.moving=False;self.animation_elapsed=0.
        self.remaining=self.rng.uniform(*self.wait_range)

    def _allowed(self,point,collisions):
        return (point.distance_to(self.origin)<=self.radius and collisions.allows(point)
                and all(point.distance_to(door)>=40 for door in self.reserved))

    def _choose(self,collisions):
        options=[('frente',(0,1)),('costas',(0,-1)),('direita',(1,0)),('esquerda',(-1,0))]
        self.rng.shuffle(options)
        for direction,vector in options:
            velocity=pygame.Vector2(vector)*self.speed
            if self._allowed(self.feet+velocity*.2,collisions):
                self.direction=direction;self.velocity=velocity
                self.animation_elapsed=0.
                self.walking=True;self.remaining=self.rng.uniform(*self.walk_range)
                return
        self.rest()

    def update(self,dt,collisions):
        if dt<=0:return
        self.moving=False
        if not collisions.allows(self.feet):
            # Nao force deslocamento se o editor tiver ocupado a posicao do NPC.
            self.rest();return
        remaining=dt
        while remaining>1e-8:
            if self.remaining<=1e-8:
                if self.walking:self.rest()
                else:self._choose(collisions)
            chunk=min(remaining,self.remaining)
            if self.walking:
                delta=self.velocity*chunk
                steps=max(1,math.ceil(delta.length()/3))
                for _ in range(steps):
                    point=self.feet+delta/steps
                    if not self._allowed(point,collisions):
                        self.rest();break
                    self.feet.update(point)
                    self.moving=True
                    self.animation_elapsed+=chunk/steps
            self.remaining-=chunk;remaining-=chunk

    def image(self,assets):
        frames=assets.cycles.get(self.direction,())
        if self.moving and frames:
            return frames[int(self.animation_elapsed/self.frame_seconds)%len(frames)]
        return assets.sprites[self.direction]
