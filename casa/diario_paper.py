"""Papel, fichário e marcações desenhados em memória para o diário."""
import pygame
from . import ui_theme as ui

INK='#3d342b'
MUTED='#73644f'
PAPER='#e1d0a8'
RULE='#cebb96'
BLUE='#334d60'
FADED='#8a7a69'


def background(screen,day):
    ui.shade(screen,228)
    pygame.draw.rect(screen,'#352a23',(38,34,1204,652),border_radius=12)
    pygame.draw.rect(screen,'#816747',(47,43,1186,632),2,border_radius=9)
    pygame.draw.rect(screen,'#c8b38b',(56,54,310,608))
    pygame.draw.rect(screen,PAPER,(382,54,842,608))
    for i in range(130):
        x=394+(i*97)%812;y=62+(i*43)%590
        pygame.draw.line(screen,'#dccaa2',(x,y),(min(1216,x+3+i%8),y))
    for y in range(207,628,30):pygame.draw.line(screen,RULE,(402,y),(1205,y))
    pygame.draw.line(screen,'#b98579',(408,170),(408,623))
    pygame.draw.line(screen,'#ab936b',(365,62),(365,652),2)
    for y in range(104,636,58):
        pygame.draw.ellipse(screen,'#352d26',(354,y,35,17),4)
        pygame.draw.arc(screen,'#b6afa0',(354,y-2,35,17),0,3.1,2)
    pygame.draw.polygon(screen,'#c5ae83',[(1200,54),(1224,78),(1200,78)])
    ui.text(screen,'Caderno de campo',pygame.Rect(78,77,278,38),ui.font(35),INK)
    ui.text(screen,f'ISOLAMENTO / DIA {day:02}',pygame.Rect(80,121,270,25),ui.font(22),MUTED,line_height=24)
    ui.text(screen,'Registros de investigação',pygame.Rect(414,72,620,38),ui.font(36),INK)
    ui.text(screen,'Roda do mouse: rolar  ·  ESC: voltar',pygame.Rect(414,635,650,24),ui.font(22),MUTED,line_height=24)


def tab(screen,rect,label,selected=False):
    rect=pygame.Rect(rect);hover=rect.collidepoint(pygame.mouse.get_pos())
    pygame.draw.polygon(screen,'#e9daba' if selected else '#bda37b' if hover else '#c6af87',
        [(rect.x,rect.bottom),(rect.x,rect.y+6),(rect.x+7,rect.y),(rect.right-7,rect.y),(rect.right,rect.y+6),(rect.right,rect.bottom)])
    if selected:pygame.draw.line(screen,BLUE,(rect.x+12,rect.bottom-4),(rect.right-12,rect.bottom-4),3)
    ui.text(screen,label,rect.inflate(-18,-10).move(0,1),ui.font(25),INK,line_height=26)


def rule(screen,x,y,width):pygame.draw.line(screen,RULE,(x,y),(x+width,y))


def strike(screen,text,font,position,color=FADED):
    image=font.render(text,True,color);screen.blit(image,position)
    rect=image.get_rect(topleft=position)
    pygame.draw.line(screen,color,(rect.left-1,rect.centery),(rect.right+2,rect.centery-1),2)
    return rect
