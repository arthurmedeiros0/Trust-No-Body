"""Editor de desenvolvimento: coordenadas da arte, nunca da janela."""
import copy
import uuid
import pygame
from .collision_data import save

class CollisionEditor:
    def __init__(self,game):
        self.game=game
        self.active=False
        self.selected=None
        self.operation=None
        self.before=None
        self.dirty=set()
        self.message=''
        self.pan=pygame.Vector2()
        self.floor_mode=False

    @property
    def scene(self):return self.game.scene

    def camera(self):
        scene=self.scene;camera=scene.camera_for(self.game.player.feet)+self.pan
        for axis in (0,1):
            if scene.rect.size[axis]>scene.viewport.size[axis]:
                camera[axis]=max(scene.rect.topleft[axis]-scene.viewport.topleft[axis],min(scene.rect.bottomright[axis]-scene.viewport.bottomright[axis],camera[axis]))
            else:camera[axis]=0
        return pygame.Vector2(round(camera.x),round(camera.y))

    def source(self,pos):
        point=self.scene.source_point(pygame.Vector2(pos)+self.camera())
        return pygame.Vector2(max(0,min(self.scene.source_size[0],round(point.x))),max(0,min(self.scene.source_size[1],round(point.y))))

    def screen_point(self,pos):return self.scene.point(pos)-self.camera()

    def handles(self,rect):
        x,y,w,h=rect
        return [(x,y),(x+w/2,y),(x+w,y),(x+w,y+h/2),(x+w,y+h),(x+w/2,y+h),(x,y+h),(x,y+h/2)]

    def current_rect(self):
        if self.floor_mode:return self.scene.collision_data['floor']
        if self.selected is not None and self.selected<len(self.scene.collision_data['obstacles']):
            return self.scene.collision_data['obstacles'][self.selected]['rect']

    def begin(self,op,pos):
        self.before=copy.deepcopy(self.scene.collision_data)
        self.start=self.source(pos);self.operation=op

    def cancel(self):
        if self.operation:
            self.scene.collision_data=self.before
            self.scene.rebuild_collisions()
            self.operation=None
            self.selected=None
            self.message='Operacao cancelada'
            return True
        return False

    def handle_event(self,event):
        if event.type==pygame.KEYDOWN and event.key==pygame.K_F4:
            self.cancel();self.active=not self.active;self.pan.update(0,0)
            self.game.player.stop();self.message='Edicao ativa' if self.active else 'Edicao encerrada (Ctrl+S para persistir)'
            return True
        if not self.active:return False
        if event.type==pygame.KEYDOWN and event.key in (pygame.K_F3,pygame.K_F6):return False
        if event.type==pygame.KEYDOWN:
            if event.key==pygame.K_ESCAPE:
                if not self.cancel():self.active=False
            elif event.key==pygame.K_s and getattr(event,'mod',pygame.key.get_mods())&pygame.KMOD_CTRL:
                self.cancel()
                try:
                    save(self.scene.collision_data)
                    self.dirty.discard(self.scene.name);self.message='Salvo: colisoes/'+self.scene.name+'.json (backup criado)'
                except (OSError,ValueError) as error:self.message='Erro ao salvar: '+str(error)
            elif event.key==pygame.K_DELETE and not self.floor_mode and self.selected is not None and not self.operation:
                del self.scene.collision_data['obstacles'][self.selected]
                self.selected=None;self.scene.rebuild_collisions();self.dirty.add(self.scene.name)
            elif event.key==pygame.K_p:
                self.cancel();self.floor_mode=not self.floor_mode;self.selected=None
            elif event.key==pygame.K_TAB:
                self.cancel();names=list(self.game.scenes);index=names.index(self.scene.name)
                self.game.change_room(names[(index+1)%len(names)])
                self.selected=None;self.pan.update(0,0)
            elif event.key in (pygame.K_LEFT,pygame.K_RIGHT,pygame.K_UP,pygame.K_DOWN):
                self.pan+=pygame.Vector2(80*(int(event.key==pygame.K_RIGHT)-int(event.key==pygame.K_LEFT)),80*(int(event.key==pygame.K_DOWN)-int(event.key==pygame.K_UP)))
            return True
        if event.type==pygame.MOUSEBUTTONDOWN and event.button==1:
            if not self.scene.viewport.collidepoint(event.pos) or pygame.Rect(15,70,1250,67).collidepoint(event.pos):return True
            polygon=self.scene.collision_data.get('floor_polygon') if self.floor_mode else None
            if polygon:
                for index,p in enumerate(polygon):
                    if self.screen_point(p).distance_to(event.pos)<=9:
                        self.begin(('vertex',index),event.pos);return True
                return True
            rect=self.current_rect()
            if rect:
                for index,point in enumerate(self.handles(rect)):
                    if self.screen_point(point).distance_to(event.pos)<=8:
                        self.begin(('resize',index),event.pos);return True
            source=self.source(event.pos)
            if self.floor_mode:
                if pygame.Rect(self.scene.collision_data['floor']).collidepoint(source):self.begin(('move',0),event.pos)
                return True
            for index in range(len(self.scene.collision_data['obstacles'])-1,-1,-1):
                if pygame.Rect(self.scene.collision_data['obstacles'][index]['rect']).collidepoint(source):
                    self.selected=index;self.begin(('move',0),event.pos);return True
            self.selected=len(self.scene.collision_data['obstacles'])
            self.begin(('create',0),event.pos)
            self.scene.collision_data['obstacles'].append(dict(id='novo_'+uuid.uuid4().hex[:10],rect=[int(source.x),int(source.y),1,1]))
            return True
        if event.type==pygame.MOUSEMOTION and self.operation:
            point=self.source(event.pos);kind,index=self.operation;data=self.scene.collision_data
            if kind=='vertex':
                data['floor_polygon'][index]=[point.x,point.y]
                polygon=data['floor_polygon'];xs=[p[0] for p in polygon];ys=[p[1] for p in polygon]
                data['floor']=[min(xs),min(ys),max(1,max(xs)-min(xs)),max(1,max(ys)-min(ys))]
            else:
                original=self.before['floor'] if self.floor_mode else (self.before['obstacles'][self.selected]['rect'] if kind!='create' else None)
                if kind=='create':
                    left,top=min(self.start.x,point.x),min(self.start.y,point.y)
                    rect=[left,top,max(1,abs(point.x-self.start.x)),max(1,abs(point.y-self.start.y))]
                elif kind=='move':
                    x,y,w,h=original;delta=point-self.start
                    rect=[max(0,min(self.scene.source_size[0]-w,x+delta.x)),max(0,min(self.scene.source_size[1]-h,y+delta.y)),w,h]
                else:
                    x,y,w,h=original;right,bottom=x+w,y+h
                    if index in (0,6,7):x=min(point.x,right-1)
                    if index in (2,3,4):right=max(point.x,x+1)
                    if index in (0,1,2):y=min(point.y,bottom-1)
                    if index in (4,5,6):bottom=max(point.y,y+1)
                    rect=[x,y,right-x,bottom-y]
                if self.floor_mode:data['floor']=rect
                else:data['obstacles'][self.selected]['rect']=rect
            self.scene.rebuild_collisions()
            return True
        if event.type==pygame.MOUSEBUTTONUP and event.button==1 and self.operation:
            if self.scene.collision_data!=self.before:self.dirty.add(self.scene.name)
            self.operation=None;return True
        return True

    def draw(self,screen):
        if not self.active:return
        camera=self.camera()
        previous=screen.get_clip();screen.set_clip(self.scene.viewport)
        self.scene.collisions.draw(screen,camera)
        polygon=self.scene.collision_data.get('floor_polygon') if self.floor_mode else None
        points=polygon or (self.handles(self.current_rect()) if self.current_rect() else [])
        if self.current_rect() and not polygon:
            pygame.draw.rect(screen,'white',pygame.Rect(self.scene.transform_rect(self.current_rect())).move(-camera.x,-camera.y),2)
        for point in points:
            p=self.screen_point(point)
            pygame.draw.rect(screen,'white',pygame.Rect(round(p.x)-4,round(p.y)-4,8,8))
        screen.set_clip(previous)
        box=pygame.Rect(15,70,1250,67);pygame.draw.rect(screen,'#17232e',box)
        status=f'EDITOR {self.scene.name} {"*" if self.scene.name in self.dirty else ""} | '+('PISO: arraste vertices/alcas' if self.floor_mode else 'OBSTACULOS: criar / mover / redimensionar')
        screen.blit(self.game.small.render(status,True,'white'),(25,75))
        controls='Ctrl+S salvar | Delete excluir | ESC cancelar/sair | F4 sair | Tab comodo | Setas camera | P piso'
        screen.blit(self.game.small.render(controls,True,'#f0d899'),(25,96))
        screen.blit(self.game.small.render(self.message,True,'#8de5bc'),(25,116))
