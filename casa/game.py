"""Controle da exploracao e interface das interacoes basicas."""
import pygame
from .config import ROOMS, DOOR_X, CORRIDOR_RETURN_Y
from .collisions import feet_rect
from .sprites import load_sprites
from .scenes import Scene
from .player import Player
from .interactions import nearest
from .transitions import Fade
from .collision_editor import CollisionEditor
from .peephole import Peephole
from .visitors import VisitorSession
from .visitor_assets import load_assets
from .visitor_ui import VisitorUI
from .shadow import Shadow
from .resident import Resident,ActorCollisions,free_spawn

class House:
    def __init__(self, development=False):
        self.scenes={name:Scene(name) for name in ROOMS}
        self.room='corredor'
        self.period='dia'
        self.debug=False
        self.dialog=''
        self.sleep_option=False
        self.fade=Fade()
        self.player=Player(*load_sprites(),self.scene.spawn)
        self.font=pygame.font.Font(None,25)
        self.small=pygame.font.Font(None,22)
        self.editor=CollisionEditor(self) if development else None
        self.peephole=Peephole()
        self.observing=False
        self.visitor_session=VisitorSession()
        self.visitor_assets={key:load_assets(v.definition) for key,v in self.visitor_session.visitors.items()}
        self.visitor_shadow=Shadow()
        self.present_visitor('ricardo')
        self.resident_positions={}
        self.residents={}

    def present_visitor(self,visitor_id):
        visitor=self.visitor_session.visitors[visitor_id]
        self.peephole.visitor_ui=VisitorUI(visitor,self.visitor_assets[visitor.id],self.decide_visitor)

    def decide_visitor(self,visitor,decision):
        if visitor.state!='aguardando':return False
        if decision=='acolhido':
            scene=self.scenes[visitor.definition['room']]
            desired=scene.point(visitor.definition['room_position'])
            occupied=[feet_rect(actor.feet) for actor in self.residents.values() if actor.room==scene.name]
            if self.room==scene.name:occupied.append(feet_rect(self.player.feet))
            reserved=[scene.spawn]+[scene.point(item.arrival) for other in self.scenes.values()
                for item in other.interactions if item.target==scene.name and item.arrival]
            feet=free_spawn(scene,desired,occupied,reserved)
            if feet is None:return False
            actor=Resident(visitor.id,scene.name,feet,visitor.definition['room_direction'],visitor.definition.get('resident'),reserved=reserved)
            self.residents[visitor.id]=actor
            self.resident_positions[visitor.id]=actor.feet
        return self.visitor_session.decide(visitor,decision)

    def draw_residents(self,screen,camera,foreground=False):
        for key,visitor in self.visitor_session.visitors.items():
            if visitor.state!='acolhido' or visitor.definition['room']!=self.room:continue
            feet=self.resident_positions[key]
            if (feet.y>self.player.feet.y)!=foreground:continue
            image=self.residents[key].image(self.visitor_assets[key])
            point=feet-camera;self.visitor_shadow.draw(screen,feet,camera)
            screen.blit(image,(round(point.x)-32,round(point.y)-94))
            if self.debug:
                pygame.draw.rect(screen,'#ffac66',feet_rect(feet).move(-round(camera.x),-round(camera.y)),1)

    @property
    def scene(self):
        return self.scenes[self.room]

    def change_room(self, name, feet=None, direction='frente'):
        self.room=name
        self.player.feet=pygame.Vector2(feet if feet is not None else self.scene.spawn)
        self.player.direction=direction
        self.player.stop()

    def interact(self):
        if self.fade.active or self.dialog or self.observing: return
        item=nearest(self.scene.interactions,self.player.feet)
        if item is None: return
        self.player.stop()
        if item.action=='door':
            self.fade.start(lambda:self.change_room(item.target,direction=item.direction))
        elif item.action=='exit':
            room=self.room
            feet=self.scenes['corredor'].point((DOOR_X[room],CORRIDOR_RETURN_Y))
            self.fade.start(lambda:self.change_room('corredor',feet,item.direction))
        elif item.action=='passage':
            feet=self.scenes[item.target].point(item.arrival) if item.arrival else None
            self.fade.start(lambda:self.change_room(item.target,feet,item.direction))
        elif item.action=='peephole':
            self.fade.start(lambda:setattr(self,'observing',True))
        elif item.action=='sleep':
            self.dialog='Deseja dormir? [S] Sim    [N] Cancelar'
            self.sleep_option=True
        else:
            self.dialog=item.text

    @property
    def captures_escape(self):
        return self.observing or self.fade.active or bool(self.editor and self.editor.active)

    def close_peephole(self):
        if not self.fade.active:
            self.fade.start(lambda:setattr(self,'observing',False))

    def handle_event(self, event):
        if self.observing:
            if event.type==pygame.KEYDOWN and event.key==pygame.K_F6:
                self.period='noite' if self.period=='dia' else 'dia'
            elif self.peephole.handle_event(event)=='back':self.close_peephole()
            return
        if self.fade.active and not (event.type==pygame.KEYDOWN and event.key in (pygame.K_F3,pygame.K_F6)):return
        if self.editor and self.editor.handle_event(event): return
        if event.type!=pygame.KEYDOWN: return
        if event.key==pygame.K_F6:
            self.period='noite' if self.period=='dia' else 'dia'
        elif event.key==pygame.K_F3:
            self.debug=not self.debug
        elif self.dialog:
            if self.sleep_option and event.key==pygame.K_s:
                self.dialog='Descanso selecionado. O sistema de sono sera implementado depois.'
                self.sleep_option=False
            elif event.key in (pygame.K_n,pygame.K_RETURN,pygame.K_SPACE):
                self.dialog='';self.sleep_option=False
        elif event.key==pygame.K_e:
            self.interact()

    def update(self, movement, dt):
        if self.editor and self.editor.active:
            self.player.stop()
        elif self.fade.active:
            self.player.stop();self.fade.update(dt)
        elif self.observing:
            self.player.stop()
        elif self.dialog:
            self.player.stop()
        else:
            actors=[actor for actor in self.residents.values() if actor.room==self.room]
            self.player.update(movement,dt,ActorCollisions(self.scene.collisions,[feet_rect(actor.feet) for actor in actors]))
            for actor in actors:
                blocked=[feet_rect(self.player.feet)]+[feet_rect(other.feet) for other in actors if other is not actor]
                actor.update(dt,ActorCollisions(self.scene.collisions,blocked))

    def draw(self, screen):
        if self.observing:
            self.peephole.draw(screen,self.period)
            self.fade.draw(screen)
            return
        screen.fill('#101419')
        camera=self.editor.camera() if self.editor and self.editor.active else self.scene.camera_for(self.player.feet)
        previous_clip=screen.get_clip()
        screen.set_clip(self.scene.viewport)
        self.scene.draw(screen,self.period,self.debug or bool(self.editor and self.editor.active),camera)
        self.draw_residents(screen,camera)
        self.player.draw(screen,camera)
        self.draw_residents(screen,camera,foreground=True)
        if self.debug:
            body=feet_rect(self.player.feet).move(-round(camera.x),-round(camera.y))
            pygame.draw.rect(screen,'cyan',body,1)
            shadow_rect=self.player.shadow.rect(self.player.feet,camera)
            pygame.draw.ellipse(screen,'#d68bfa',shadow_rect,1)
        screen.set_clip(previous_clip)
        title=f'Trust No Body | {self.room.capitalize()} | {self.period.capitalize()}'
        screen.blit(self.font.render(title,True,'#f1e6c8'),(20,18))
        controls='WASD / Setas: mover   E: interagir   F6: dia/noite   F3: colisoes   ESC: sair'
        screen.blit(self.small.render(controls,True,'#bbbfc4'),(20,690))
        if self.debug:
            source=self.scene.source_point(self.player.feet)
            info=(f'{self.room} | escala {self.scene.scale:.4f} | '
                  f'pes na arte: ({source.x:.1f}, {source.y:.1f}) | '
                  f'camera: ({camera.x:.0f}, {camera.y:.0f})')
            screen.blit(self.small.render(info,True,'#8de5df'),(20,43))
        item=nearest(self.scene.interactions,self.player.feet)
        if item and not self.dialog and not self.fade.active:
            label=self.font.render(item.prompt or '[E] Interagir - '+item.label,True,'#fff1b8')
            box=label.get_rect(midbottom=(640,665)).inflate(24,12)
            pygame.draw.rect(screen,'#172027',box,border_radius=6)
            screen.blit(label,label.get_rect(center=box.center))
        if self.dialog:
            box=pygame.Rect(130,540,1020,130)
            pygame.draw.rect(screen,'#18222e',box,border_radius=8)
            pygame.draw.rect(screen,'#d5bf86',box,2,border_radius=8)
            words=self.dialog.split();lines=[];line=''
            for word in words:
                trial=(line+' '+word).strip()
                if self.font.size(trial)[0]>970:
                    lines.append(line);line=word
                else: line=trial
            lines.append(line)
            for i,line in enumerate(lines):
                screen.blit(self.font.render(line,True,'#f5e9cf'),(150,558+i*27))
            if not self.sleep_option:
                screen.blit(self.small.render('Enter / Espaco: fechar',True,'#bbc6d0'),(150,638))
        self.fade.draw(screen)
        if self.editor:self.editor.draw(screen)
