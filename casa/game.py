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
from .resident_render import resident_frame
from .sleep import SleepTransition
from .television import Television
from .survival_ui import SurvivalUI

class House:
    def __init__(self, development=False):
        self.development=development
        self.scenes={name:Scene(name) for name in ROOMS}
        self.room='quarto'
        self.period='dia'
        self.debug=False
        self.dialog='Você acorda com uma sensação de fome. Não se lembra da última vez que fez uma refeição de verdade.'
        self.sleep_option=False
        self.fade=Fade()
        self.player=Player(*load_sprites(),free_spawn(self.scene,self.scene.point((345,365))) or self.scene.spawn)
        self.font=pygame.font.Font(None,25)
        self.small=pygame.font.Font(None,22)
        self.editor=CollisionEditor(self) if development else None
        self.peephole=Peephole()
        self.observing=False
        self.visitor_session=VisitorSession()
        self.days=self.visitor_session.days
        self.news=self.visitor_session.news
        self.sleep_transition=SleepTransition(self.days)
        self.television=Television(self.news,self.days)
        self.inventory=SurvivalUI(self.visitor_session)
        self.news.on_watch.append(self.news_seen)
        self.summary_pending=False
        self.sleep_held=False
        self.visitor_assets={key:load_assets(v.definition) for key,v in self.visitor_session.visitors.items()
                             if key not in self.visitor_session.unavailable}
        self.visitor_session.on_arrival.append(lambda visitor:self.present_visitor(visitor.id))
        self.visitor_shadow=Shadow()
        self.resident_positions={}
        self.residents={}

    def news_seen(self,bulletin):
        visitor=self.visitor_session.visitors.get('ricardo')
        if bulletin.day==1 and visitor and visitor.arrived and visitor.state=='aguardando' and self.peephole.visitor_ui is None:
            self.present_visitor('ricardo')

    def present_visitor(self,visitor_id):
        visitor=self.visitor_session.visitors[visitor_id]
        if not visitor.arrived or visitor_id not in self.visitor_assets:return False
        current=self.peephole.visitor_ui
        if current and current.visitor.state=='aguardando' and current.visitor.id!=visitor_id:return False
        self.peephole.visitor_ui=VisitorUI(visitor,self.visitor_assets[visitor.id],self.decide_visitor)
        return True

    def decide_visitor(self,visitor,decision):
        if not visitor.arrived or visitor.state!='aguardando' or not self.visitor_session.survival.alive:return False
        if self.visitor_session.manager.current and self.visitor_session.manager.current!=visitor.id:return False
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
            if visitor.state!='acolhido' or not visitor.alive or visitor.definition['room']!=self.room:continue
            feet=self.resident_positions[key]
            if (feet.y>self.player.feet.y)!=foreground:continue
            image=self.residents[key].image(self.visitor_assets[key])
            image,anchor=resident_frame(key,image)
            point=feet-camera;self.visitor_shadow.draw(screen,feet,camera)
            screen.blit(image,(round(point.x)-anchor[0],round(point.y)-anchor[1]))
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
        if not self.visitor_session.survival.alive or self.inventory.active or self.fade.active or self.sleep_transition.active or self.dialog or self.observing or self.television.active or bool(self.editor and self.editor.active): return
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
            if self.peephole.visitor_ui and self.peephole.visitor_ui.visitor.arrived:
                self.visitor_session.intro.door_checked=True
            self.fade.start(lambda:setattr(self,'observing',True))
        elif item.action=='sleep':
            if self.sleep_held:return
            self.sleep_held=True
            reason=self.sleep_block_reason()
            self.dialog=reason or 'Deseja dormir e avançar para o próximo dia?'
            self.sleep_option=not bool(reason)
        elif item.action=='television':
            self.television.open()
        elif item.action=='fridge':
            survival=self.visitor_session.survival
            first=not self.visitor_session.intro.fridge_checked
            self.visitor_session.intro.fridge_checked=True
            if first and survival.food==0 and survival.water==0:
                self.dialog='A geladeira está vazia. Não há nada para comer. A última garrafa de água também acabou.'
            else:
                self.inventory.active=True
        else:
            self.dialog=item.text

    @property
    def captures_escape(self):
        return self.observing or self.fade.active or self.sleep_transition.active or self.television.active or self.inventory.active or bool(self.dialog) or bool(self.editor and self.editor.active)

    def sleep_block_reason(self):
        if not self.visitor_session.intro.broadcast_seen:return 'Assista ao noticiário do primeiro dia antes de encerrar o dia.'
        if self.days.day>=self.days.LIMIT:return 'O dia 20 foi alcançado. A partida continua disponível; novos avanços estão suspensos.'
        if any(v.arrived and v.state=='aguardando' for v in self.visitor_session.visitors.values()):
            return 'Resolva a situação do visitante aguardando na porta antes de dormir.'
        return ''

    def confirm_sleep(self):
        if not self.sleep_option or self.room!='quarto' or self.sleep_transition.active or self.fade.active or self.observing or self.television.active:return
        reason=self.sleep_block_reason()
        if reason:self.dialog=reason;self.sleep_option=False;return
        bedroom=self.scenes['quarto']
        occupied=[feet_rect(a.feet) for a in self.residents.values() if a.room=='quarto']
        arrival=free_spawn(bedroom,bedroom.point((345,365)),occupied)
        self.sleep_option=False
        if arrival is None:self.dialog='Não há espaço livre ao lado da cama. Confira as colisões antes de dormir.';return
        self.dialog='';self.player.stop()
        if not self.days.close_day():return
        def wake():
            if self.days.advance():
                self.change_room('quarto',arrival,'frente')
                self.period='dia'
                self.summary_pending=True
        self.sleep_transition.start(wake)

    def close_peephole(self):
        if not self.fade.active:
            self.fade.start(lambda:setattr(self,'observing',False))

    def handle_event(self, event):
        if event.type==pygame.KEYUP and event.key==pygame.K_e:self.sleep_held=False
        if not self.visitor_session.survival.alive:
            if (event.type==pygame.KEYDOWN and event.key in (pygame.K_RETURN,pygame.K_r)) or (event.type==pygame.MOUSEBUTTONDOWN and event.button==1 and self.inventory.restart.collidepoint(event.pos)):
                self.__init__(self.development)
            return
        if self.inventory.active:
            if event.type==pygame.KEYDOWN and event.key in (pygame.K_i,pygame.K_ESCAPE):self.inventory.active=False
            return
        if self.observing:
            if event.type==pygame.KEYDOWN and event.key==pygame.K_F6:
                self.period='noite' if self.period=='dia' else 'dia'
            elif self.peephole.handle_event(event)=='back':self.close_peephole()
            return
        if self.sleep_transition.active:
            if event.type==pygame.KEYDOWN and event.key==pygame.K_F3:self.debug=not self.debug
            elif event.type==pygame.KEYDOWN and event.key==pygame.K_F6:self.period='noite' if self.period=='dia' else 'dia'
            return
        if self.television.active:
            if event.type==pygame.KEYDOWN and event.key==pygame.K_F6:self.period='noite' if self.period=='dia' else 'dia'
            elif event.type==pygame.KEYDOWN and event.key==pygame.K_F3:self.debug=not self.debug
            else:self.television.handle_event(event)
            return
        if self.fade.active and not (event.type==pygame.KEYDOWN and event.key in (pygame.K_F3,pygame.K_F6)):return
        if self.sleep_option and event.type==pygame.MOUSEBUTTONDOWN and event.button==1:
            if pygame.Rect(340,615,240,42).collidepoint(event.pos):self.confirm_sleep()
            elif pygame.Rect(700,615,240,42).collidepoint(event.pos):self.dialog='';self.sleep_option=False
            return
        if self.dialog and event.type==pygame.KEYDOWN and event.key==pygame.K_ESCAPE:
            self.dialog='';self.sleep_option=False;return
        if self.dialog and event.type==pygame.KEYDOWN and event.key not in (pygame.K_F3,pygame.K_F6):
            if self.sleep_option and event.key in (pygame.K_s,pygame.K_RETURN):self.confirm_sleep()
            elif event.key in (pygame.K_n,pygame.K_RETURN,pygame.K_SPACE):self.dialog='';self.sleep_option=False
            return
        if self.editor and self.editor.handle_event(event): return
        if event.type!=pygame.KEYDOWN: return
        if event.key==pygame.K_F6:
            self.period='noite' if self.period=='dia' else 'dia'
        elif event.key==pygame.K_F3:
            self.debug=not self.debug
        elif event.key==pygame.K_e:
            if not getattr(event,'repeat',False):self.interact()
        elif event.key==pygame.K_i:
            self.inventory.active=True;self.player.stop()

    def update(self, movement, dt):
        if not self.visitor_session.survival.alive or self.inventory.active:
            self.player.stop()
        elif self.sleep_transition.active:
            self.player.stop();self.sleep_transition.update(dt)
            if not self.sleep_transition.active and self.summary_pending:
                self.summary_pending=False
                self.dialog=self.visitor_session.last_report.text()
        elif self.television.active:
            self.player.stop()
        elif self.editor and self.editor.active:
            self.player.stop()
        elif self.fade.active:
            self.player.stop();self.fade.update(dt)
        elif self.observing:
            self.player.stop()
        elif self.dialog:
            self.player.stop()
        else:
            actors=[actor for actor in self.residents.values() if actor.room==self.room and self.visitor_session.visitors[actor.visitor_id].alive]
            self.player.update(movement,dt,ActorCollisions(self.scene.collisions,[feet_rect(actor.feet) for actor in actors]))
            for actor in actors:
                blocked=[feet_rect(self.player.feet)]+[feet_rect(other.feet) for other in actors if other is not actor]
                actor.update(dt,ActorCollisions(self.scene.collisions,blocked))

    def draw(self, screen):
        if not self.visitor_session.survival.alive:
            self.inventory.draw(screen);return
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
        screen.blit(self.small.render(self.survival_hud(),True,'#f1e6c8'),(490,18))
        objective=self.visitor_session.intro.objective
        if objective and not self.debug:
            screen.blit(self.small.render('Objetivo: '+objective,True,'#d5c59f'),(20,43))
        controls='WASD / Setas: mover   E: interagir   I: suprimentos   F6: dia/noite   F3: colisoes   ESC: sair'
        screen.blit(self.small.render(controls,True,'#bbbfc4'),(20,690))
        if self.debug:
            source=self.scene.source_point(self.player.feet)
            info=(f'{self.room} | escala {self.scene.scale:.4f} | '
                  f'pes na arte: ({source.x:.1f}, {source.y:.1f}) | '
                  f'camera: ({camera.x:.0f}, {camera.y:.0f})')
            screen.blit(self.small.render(info,True,'#8de5df'),(20,43))
        item=nearest(self.scene.interactions,self.player.feet)
        if item and not self.dialog and not self.fade.active and not self.sleep_transition.active and not self.television.active:
            label=self.font.render(item.prompt or '[E] Interagir - '+item.label,True,'#fff1b8')
            box=label.get_rect(midbottom=(640,665)).inflate(24,12)
            pygame.draw.rect(screen,'#172027',box,border_radius=6)
            screen.blit(label,label.get_rect(center=box.center))
        if self.dialog:
            words=self.dialog.split();lines=[];line=''
            for word in words:
                trial=(line+' '+word).strip()
                if self.font.size(trial)[0]>970:
                    lines.append(line);line=word
                else: line=trial
            lines.append(line)
            height=max(130,len(lines)*27+65)
            box=pygame.Rect(130,670-height,1020,height)
            pygame.draw.rect(screen,'#18222e',box,border_radius=8)
            pygame.draw.rect(screen,'#d5bf86',box,2,border_radius=8)
            for i,line in enumerate(lines):
                screen.blit(self.font.render(line,True,'#f5e9cf'),(150,box.y+18+i*27))
            if not self.sleep_option:
                screen.blit(self.small.render('Enter / Espaco: fechar',True,'#bbc6d0'),(150,638))
            else:
                for rect,label in ((pygame.Rect(340,615,240,42),'Dormir [S / Enter]'),(pygame.Rect(700,615,240,42),'Cancelar [N / ESC]')):
                    pygame.draw.rect(screen,'#34424c',rect)
                    text=self.font.render(label,True,'#f5e9cf');screen.blit(text,text.get_rect(center=rect.center))
        self.fade.draw(screen)
        if self.editor:self.editor.draw(screen)
        if self.television.active:self.television.draw(screen)
        if self.inventory.active:self.inventory.draw(screen)
        self.sleep_transition.draw(screen)

    def survival_hud(self):
        state=self.visitor_session.survival
        needs=state.predicted_needs(self.days.day,self.visitor_session.living_ids)
        return (f'Dia {self.days.day}/{self.days.LIMIT} | Sanidade: {state.sanity}/8 | '
                f'Fome: {needs.hunger}/3 dias | Sede: {needs.thirst}/2 dias')
