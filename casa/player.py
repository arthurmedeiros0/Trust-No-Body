"""Jogador com colisao nos pes, animacao e movimento por eixo."""
import math
import pygame
from .config import SPEED, FRAME_TIME, PLAYER_FOOT_Y
from .animation import animation_cycles
from .shadow import Shadow

class Player:
    def __init__(self, idle, walk, feet):
        self.idle,self.walk = idle,walk
        self.cycles = animation_cycles(idle,walk)
        self.shadow = Shadow()
        self.feet = pygame.Vector2(feet)
        self.direction = 'frente'
        self.elapsed = 0.
        self.moving = False

    def stop(self):
        self.elapsed = 0.
        self.moving = False

    def update(self, movement, dt, collisions):
        vector = pygame.Vector2(movement)
        if not vector.length_squared():
            self.stop()
            return
        direction = ('direita' if vector.x>0 else 'esquerda') if vector.x else ('frente' if vector.y>0 else 'costas')
        if direction != self.direction or not self.moving:
            self.elapsed=0.
        self.direction=direction
        delta=vector.normalize()*SPEED*dt
        # Subpassos evitam atravessar obstaculos mesmo em atualizacoes longas.
        steps=max(1,math.ceil(max(abs(delta.x),abs(delta.y))/4))
        before=self.feet.copy()
        for _ in range(steps):
            for axis in (0,1):
                candidate=self.feet.copy();candidate[axis]+=delta[axis]/steps
                if collisions.allows(candidate):
                    self.feet=candidate
        self.moving=self.feet.distance_squared_to(before)>0.000001
        if self.moving: self.elapsed+=dt
        else: self.elapsed=0.

    @property
    def image(self):
        return self.cycles[self.direction][int(self.elapsed/FRAME_TIME)%len(self.cycles[self.direction])] if self.moving else self.idle[self.direction]

    def draw(self, screen, camera=(0,0)):
        # O ultimo pixel visivel dos sprites fica em y=93.
        self.shadow.draw(screen,self.feet,camera)
        point=self.feet-pygame.Vector2(camera)
        screen.blit(self.image,(round(point.x)-self.image.get_width()//2,round(point.y)-PLAYER_FOOT_Y))
