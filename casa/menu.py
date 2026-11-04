"""Menu e seleção de visitantes, mantendo a partida em House."""
import pygame

from .config import WINDOW

ORDER=('ricardo','laura','antonio','gabriel','helena','daniel','marina')
NAMES=('Ricardo','Laura','Antônio','Gabriel','Helena','Daniel','Marina')
CONDITIONS=('Aleatória','Saudável','Infectado','Infectado — padrão 1','Infectado — padrão 2','Infectado — padrão 3')
CONDITION_VALUES=('aleatoria','saudavel','infectado','padrao_1','padrao_2','padrao_3')

class GameMenu:
    def __init__(self,available):
        self.available=set(available)
        self.page='main'
        self.mode=None
        self.selected=0
        self.condition=0
        self.hover=None
        self.title=pygame.font.Font(None,76)
        self.font=pygame.font.Font(None,32)
        self.small=pygame.font.Font(None,23)

    def entries(self):
        if self.page=='main':
            return [('normal','JOGAR — MODO NORMAL'),('test','TESTAR PERSONAGENS — MODO TESTE'),('quit','SAIR')]
        if self.page=='select':
            return [(key,name+('' if key in self.available else '  •  indisponível'))
                    for key,name in zip(ORDER,NAMES)]+[('back','VOLTAR')]
        if self.page=='setup':
            options=[('condition','CONDIÇÃO: '+CONDITIONS[self.condition])]
            return options+[('start','INICIAR TESTE'),('back','VOLTAR')]
        if self.mode=='test':
            return [('resume','CONTINUAR'),('restart','REINICIAR TESTE'),('select','SELECIONAR PERSONAGEM'),('main','MENU PRINCIPAL')]
        return [('resume','CONTINUAR'),('main','MENU PRINCIPAL')]

    def rectangles(self):
        entries=self.entries()
        top=285 if self.page=='main' else 155 if self.page=='select' else 310
        spacing=56 if self.page=='select' else 74
        return {key:pygame.Rect(365,top+i*spacing,550,49) for i,(key,_) in enumerate(entries)}

    def handle_event(self,event):
        if event.type==pygame.MOUSEMOTION:
            self.hover=next((key for key,rect in self.rectangles().items() if rect.collidepoint(event.pos)),None)
        if event.type==pygame.MOUSEBUTTONDOWN and event.button==1:
            key=next((key for key,rect in self.rectangles().items() if rect.collidepoint(event.pos)),None)
            return self.choose(key)
        if event.type==pygame.KEYDOWN:
            if event.key==pygame.K_ESCAPE:
                if self.page=='setup':self.page='select'
                elif self.page=='select':self.page='main'
                elif self.page=='pause':return self.choose('resume')
                return None
            keys=list(self.rectangles())
            if event.key in (pygame.K_DOWN,pygame.K_s):self.selected=(self.selected+1)%len(keys)
            elif event.key in (pygame.K_UP,pygame.K_w):self.selected=(self.selected-1)%len(keys)
            elif event.key in (pygame.K_RETURN,pygame.K_SPACE):return self.choose(keys[self.selected])
            elif event.key in (pygame.K_LEFT,pygame.K_RIGHT) and self.page=='setup':
                self.condition=(self.condition+(1 if event.key==pygame.K_RIGHT else -1))%len(CONDITIONS)
        return None

    def choose(self,key):
        if key is None:return None
        if key=='normal':return ('normal',None,None)
        if key=='test':self.page='select';self.selected=0
        elif key in ORDER and key in self.available:self.character=key;self.page='setup';self.selected=0
        elif key=='condition':self.condition=(self.condition+1)%len(CONDITIONS)
        elif key=='start':return ('test',self.character,CONDITION_VALUES[self.condition])
        elif key=='back':self.page='select' if self.page=='setup' else 'main';self.selected=0
        elif key=='resume':return ('resume',None,None)
        elif key=='restart':return ('restart',None,None)
        elif key=='select':self.page='select';self.selected=0
        elif key=='main':self.page='main';self.selected=0;return ('main',None,None)
        elif key=='quit':return ('quit',None,None)
        return None

    def draw(self,screen):
        screen.fill('#0c1117')
        # Moldura em blocos para combinar com a arte pixelada da casa.
        for inset,color in ((28,'#28302f'),(34,'#111c22'),(42,'#657062'),(46,'#111820')):
            pygame.draw.rect(screen,color,(inset,inset,WINDOW[0]-2*inset,WINDOW[1]-2*inset),4)
        for x in range(75,1200,32):
            pygame.draw.rect(screen,'#1d292c',(x,98,12,5))
            pygame.draw.rect(screen,'#1d292c',(x,607,12,5))
        if self.page=='main':title='TRUST NO BODY'
        elif self.page=='select':title='TESTAR PERSONAGENS'
        elif self.page=='setup':title=self.character.upper()
        else:title='PAUSA'
        heading=self.title.render(title,True,'#d7c9a4')
        screen.blit(heading,heading.get_rect(center=(640,170 if self.page=='main' else 115)))
        if self.page=='main':
            sub=self.small.render('Every body tells a story. Not every story is true.',True,'#9ca7a2')
            screen.blit(sub,sub.get_rect(center=(640,228)))
        if self.page=='setup':
            message='Clique na condição ou use as setas para testar cada padrão.'
            hint=self.small.render(message,True,'#9ca7a2')
            screen.blit(hint,hint.get_rect(center=(640,240)))
        for i,(key,label) in enumerate(self.entries()):
            rect=self.rectangles()[key]
            disabled=self.page=='select' and key in ORDER and key not in self.available
            active=not disabled and (key==self.hover or i==self.selected)
            pygame.draw.rect(screen,'#374b48' if active else '#1d2a2d',rect)
            pygame.draw.rect(screen,'#b6a884' if active else '#52605c',rect,2)
            rendered=self.font.render(label,True,'#6c7777' if disabled else '#f0e4c9' if active else '#bbc5bd')
            screen.blit(rendered,rendered.get_rect(center=rect.center))
        footer=self.small.render('W/S ou setas / ENTER   •   mouse   •   ESC voltar   •   F1 pausar no jogo',True,'#89938c')
        screen.blit(footer,footer.get_rect(center=(640,654)))
