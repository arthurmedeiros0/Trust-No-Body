"""Distribuição diária e circulação curta, usando a física existente de Resident."""
from collections import deque
from dataclasses import dataclass
import json
import random
from types import SimpleNamespace
import pygame
from .config import DOOR_X,CORRIDOR_RETURN_Y
from .collisions import feet_rect
from .resident import Resident,ActorCollisions,free_spawn,clear_segment
from .resident_routines import ANCHORS,OFFSETS,CAPACITY,PROFILES,Profile

@dataclass(frozen=True)
class Placement:
    room: str
    feet: tuple
    waypoints: tuple

class ResidentManager:
    CLEARANCE=72
    SEPARATION=96
    WALK_SEPARATION=68
    GRID=8
    _geometry_cache={}

    def __init__(self,house,rng=None):
        self.house=house;self.rng=rng or random.Random()
        self.actors={};self.positions={};self.nodes={};self.reserved={};self.components={}
        self.last_day=None;self.planning_runs=0;self.geometry_builds=0
        self.refresh_geometry()

    @property
    def locations(self):return {key:actor.room for key,actor in self.actors.items()}

    def _reserved(self,scene):
        points=[scene.spawn.copy()]+[item.point.copy() for item in scene.interactions]
        for other in self.house.scenes.values():
            points += [scene.point(item.arrival) for item in other.interactions if item.target==scene.name and item.arrival]
        if scene.name=='corredor':points += [scene.point((x,CORRIDOR_RETURN_Y)) for x in DOOR_X.values()]
        return points

    def _component(self,scene):
        origin=scene.spawn.copy();seen=set();queue=deque()
        if scene.collisions.allows(origin):seen.add((0,0));queue.append((0,0))
        while queue:
            x,y=queue.popleft()
            for nx,ny in ((x-1,y),(x+1,y),(x,y-1),(x,y+1)):
                if (nx,ny) in seen:continue
                point=origin+pygame.Vector2(nx*self.GRID,ny*self.GRID)
                if scene.collisions.allows(point):
                    seen.add((nx,ny));queue.append((nx,ny))
        return frozenset(seen)

    def reachable(self,scene,point):
        delta=(pygame.Vector2(point)-scene.spawn)/self.GRID
        x,y=round(delta.x),round(delta.y)
        for dx in (-1,0,1):
            for dy in (-1,0,1):
                index=(x+dx,y+dy)
                if index in self.components[scene.name]:
                    grid=scene.spawn+pygame.Vector2(index)*self.GRID
                    if clear_segment(grid,point,scene.collisions.allows):return True
        return False

    def static_safe(self,room,point):
        scene=self.house.scenes[room];point=pygame.Vector2(point)
        return (scene.collisions.allows(point) and
                all(pygame.Vector2(point).distance_to(p)>=self.CLEARANCE for p in self.reserved[room]) and
                self.reachable(scene,point))

    def refresh_geometry(self):
        for room in CAPACITY:
            scene=self.house.scenes[room];self.reserved[room]=self._reserved(scene)
            key=(room,scene.scale,tuple(scene.rect),json.dumps(scene.collision_data,sort_keys=True),tuple(tuple(p) for p in self.reserved[room]))
            cached=self._geometry_cache.get(key)
            if cached:
                self.components[room],self.nodes[room]=cached;continue
            self.components[room]=self._component(scene);self.geometry_builds+=1
            nodes=[]
            for source in ANCHORS[room]:
                anchor=scene.point(source)
                if not self.static_safe(room,anchor):continue
                points=[]
                for dx,dy in OFFSETS:
                    point=scene.point((source[0]+dx,source[1]+dy))
                    if self.static_safe(room,point) and clear_segment(anchor,point,scene.collisions.allows):points.append(tuple(point))
                nodes.append(Placement(room,tuple(anchor),tuple(points)))
            self.nodes[room]=tuple(nodes)
            self._geometry_cache[key]=(self.components[room],self.nodes[room])

    def profile(self,visitor_id):return PROFILES.get(visitor_id,Profile(tuple(CAPACITY)))

    def _safe(self,room,point,placed,visitor_id):
        if not self.static_safe(room,point):return False
        others=[pygame.Vector2(p.feet) for key,p in placed.items() if key!=visitor_id and p.room==room]
        separation=116 if self.profile(visitor_id).social=='reservado' else self.SEPARATION
        if any(pygame.Vector2(point).distance_to(other)<separation for other in others):return False
        if room==self.house.room:
            if pygame.Vector2(point).distance_to(self.house.player.feet)<self.SEPARATION:return False
        return True

    def _place(self,visitor_id,placed,day,visible=None,daily=False):
        profile=self.profile(visitor_id);preferences=list(profile.rooms)
        shift=(day-1)%len(preferences) if daily else 0
        preferences=preferences[shift:]+preferences[:shift]
        # Todos os ambientes seguros continuam disponíveis como recuperação.
        rooms=preferences+[room for room in CAPACITY if room not in preferences]
        counts={room:sum(p.room==room for p in placed.values()) for room in CAPACITY}
        ranked=sorted((room for room in rooms if room!=visible and counts[room]<CAPACITY[room]),
                      key=lambda room:counts[room]/CAPACITY[room]*.8+rooms.index(room)*.18+self.rng.random()*.025)
        for room in ranked:
            candidates=[]
            for i,node in enumerate(self.nodes[room]):
                if not self._safe(room,node.feet,placed,visitor_id):continue
                others=[pygame.Vector2(p.feet) for p in placed.values() if p.room==room]
                social=0
                if others:
                    distance=min(pygame.Vector2(node.feet).distance_to(p) for p in others)
                    social=distance*.001*(-1 if profile.social=='reservado' else 1 if profile.social=='proximo' else 0)
                score=(self.rng.random() if daily else i*.06+self.rng.random()*.02)+social
                candidates.append((score,node))
            if candidates:return min(candidates,key=lambda pair:pair[0])[1]
        # Busca determinística em torno de pontos de rotina já revisados. Não
        # acolhe nem consome recursos se todos os ambientes estiverem bloqueados.
        for room in ranked:
            scene=self.house.scenes[room]
            safe_map=SimpleNamespace(allows=lambda p:self._safe(room,p,placed,visitor_id))
            proxy=SimpleNamespace(collisions=safe_map)
            for source in ANCHORS[room]:
                feet=free_spawn(proxy,scene.point(source))
                if feet is not None:
                    points=[tuple(feet)]
                    for dx,dy in OFFSETS[1:]:
                        candidate=feet+pygame.Vector2(dx*scene.scale,dy*scene.scale)
                        if safe_map.allows(candidate) and clear_segment(feet,candidate,safe_map.allows):points.append(tuple(candidate))
                    return Placement(room,tuple(feet),tuple(points))
        return None

    def prepare(self,visitor):
        self.cleanup();self.refresh_geometry();self.planning_runs+=1
        placed={key:Placement(a.room,tuple(a.feet),()) for key,a in self.actors.items()}
        return self._place(visitor.id,placed,self.house.days.day)

    def add(self,visitor,placement):
        profile=self.profile(visitor.id)
        settings=dict(visitor.definition.get('resident') or {})
        settings.update(speed=settings.get('speed',34)*profile.speed,wait_seconds=profile.wait,interaction_clearance=self.CLEARANCE)
        actor=Resident(visitor.id,placement.room,placement.feet,visitor.definition.get('room_direction','frente'),settings,
                       rng=random.Random(self.rng.getrandbits(64)),reserved=self.reserved[placement.room],waypoints=placement.waypoints)
        actor.routine_day=self.house.days.day
        self.actors[visitor.id]=actor;self.positions[visitor.id]=actor.feet
        return actor

    def remove(self,visitor_id):
        actor=self.actors.pop(visitor_id,None)
        if actor is not None:actor.pause();actor.walking=False;actor.velocity.update(0,0)
        self.positions.pop(visitor_id,None)

    def cleanup(self):
        visitors=self.house.visitor_session.visitors
        for key in list(self.actors):
            visitor=visitors.get(key)
            if visitor is None or not visitor.alive or visitor.state!='acolhido':self.remove(key)

    def start_day(self,event):
        if event.day==self.last_day:return
        self.last_day=event.day;self.cleanup();self.refresh_geometry();self.planning_runs+=1
        visible=None if self.house.observing else self.house.room
        fixed={key:Placement(a.room,tuple(a.feet),()) for key,a in self.actors.items() if a.room==visible}
        planned=dict(fixed);keys=[key for key in self.actors if key not in fixed];self.rng.shuffle(keys)
        for key in keys:
            placement=self._place(key,planned,event.day,visible=visible,daily=True)
            if placement is None:return # Transação: mantém todos os locais anteriores.
            planned[key]=placement
        for key in keys:
            actor=self.actors[key];placement=planned[key]
            actor.room=placement.room;actor.feet.update(placement.feet);actor.origin.update(placement.feet)
            actor.reserved=[pygame.Vector2(p) for p in self.reserved[placement.room]]
            actor.waypoints=[pygame.Vector2(p) for p in placement.waypoints]
            actor.routine_day=event.day;actor.rest()

    def visible(self,room):
        return [a for key,a in self.actors.items() if a.room==room and
                self.house.visitor_session.visitors[key].alive and self.house.visitor_session.visitors[key].state=='acolhido']

    def pause(self,room):
        for actor in self.visible(room):actor.pause()

    def update(self,room,dt):
        self.cleanup();actors=self.visible(room);scene=self.house.scenes[room]
        for actor in actors:
            others=[other for other in actors if other is not actor]
            base=ActorCollisions(scene.collisions,[feet_rect(self.house.player.feet)]+[feet_rect(other.feet) for other in others])
            collisions=SimpleNamespace(allows=lambda p,base=base,others=others:base.allows(p) and all(pygame.Vector2(p).distance_to(a.feet)>=self.WALK_SEPARATION for a in others))
            actor.update(dt,collisions)

    def can_interact(self,actor):
        if actor.room!=self.house.room:return False
        return clear_segment(self.house.player.feet,actor.feet,self.house.scene.collisions.allows)
