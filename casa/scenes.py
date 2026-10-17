"""Escala calibrada, coordenadas da arte e camera desacoplada das colisoes."""
import pygame
from .config import ROOT, ROOMS, VIEWPORT, SCENE_SCALE, INTERACTION_RADIUS
from .collisions import CollisionMap
from .collision_data import load
from .interactions import Interaction

class Scene:
    def __init__(self, name):
        self.name=name
        self.config=ROOMS[name]
        originals={period:pygame.image.load(str(ROOT/'cenarios'/name/file)).convert()
                   for period,file in self.config['images'].items()}
        self.source_size=self.config['source_size']
        if any(image.get_size()!=self.source_size for image in originals.values()):
            raise ValueError('Dimensoes do cenario diferentes da configuracao: '+name)
        self.viewport=pygame.Rect(VIEWPORT)
        self.scale=SCENE_SCALE*self.config['art_scale']
        scaled=(round(self.source_size[0]*self.scale),round(self.source_size[1]*self.scale))
        self.rect=pygame.Rect((0,0),scaled)
        self.rect.center=self.viewport.center
        self.images={period:pygame.transform.scale(image,scaled) for period,image in originals.items()}
        self.collision_data=load(name,self.source_size)
        self.rebuild_collisions()
        self.interactions=[Interaction(**{**item,'point':self.point(item['point']),
                                          'radius':INTERACTION_RADIUS})
                           for item in self.config['interactions']]
        self.spawn=self.point(self.config['spawn'])

    def rebuild_collisions(self):
        data=self.collision_data
        polygon=[self.point(p) for p in data.get('floor_polygon') or []] or None
        self.collisions=CollisionMap(self.transform_rect(data['floor']),
            [self.transform_rect(obj['rect']) for obj in data['obstacles']],polygon)

    def point(self, point):
        return pygame.Vector2(self.rect.x+point[0]*self.scale,self.rect.y+point[1]*self.scale)

    def source_point(self, world):
        return (pygame.Vector2(world)-pygame.Vector2(self.rect.topleft))/self.scale

    def transform_rect(self, rect):
        x,y,w,h=rect
        # Transformar as duas extremidades evita deslocamentos entre bordas adjacentes.
        left,top=round(self.rect.x+x*self.scale),round(self.rect.y+y*self.scale)
        right,bottom=round(self.rect.x+(x+w)*self.scale),round(self.rect.y+(y+h)*self.scale)
        return (left,top,right-left,bottom-top)

    def camera_for(self, feet):
        offset=pygame.Vector2()
        for axis in (0,1):
            if self.rect.size[axis]>self.viewport.size[axis]:
                low=self.rect.topleft[axis]-self.viewport.topleft[axis]
                high=self.rect.bottomright[axis]-self.viewport.bottomright[axis]
                offset[axis]=round(max(low,min(high,feet[axis]-self.viewport.center[axis])))
        return offset

    def draw(self, screen, period, debug=False, camera=(0,0)):
        camera=pygame.Vector2(camera)
        screen.blit(self.images[period],pygame.Vector2(self.rect.topleft)-camera)
        if debug:
            self.collisions.draw(screen,camera)
            for item in self.interactions:
                point=item.point-camera
                pygame.draw.circle(screen,'#edcf65',point,round(item.radius),1)
                pygame.draw.circle(screen,'#edcf65',point,4)
