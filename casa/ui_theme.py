"""Componentes de apresentação compartilhados; não consultam o estado clínico."""
from functools import lru_cache
import pygame

INK='#101923'
PANEL='#14212d'
BORDER='#425361'
TEXT='#ebe6da'
MUTED='#a3b1b9'
PAPER='#d8c49c'
RED='#73333a'
RED_HOVER='#94434c'
BLUE='#293d4a'
SPACE=16

@lru_cache(maxsize=16)
def font(size=25):return pygame.font.Font(None,size)

def panel(screen,rect,color=PANEL,alpha=238,accent=None):
    rect=pygame.Rect(rect)
    layer=pygame.Surface(rect.size,pygame.SRCALPHA)
    layer.fill((*pygame.Color(color)[:3],alpha));screen.blit(layer,rect)
    pygame.draw.rect(screen,BORDER,rect,1)
    if accent:pygame.draw.line(screen,accent,(rect.left,rect.top),(rect.left,rect.bottom),3)

def shade(screen,alpha=180):
    layer=pygame.Surface(screen.get_size(),pygame.SRCALPHA);layer.fill((3,7,12,alpha));screen.blit(layer,(0,0))

def wrapped_lines(text,width,typeface):
    lines=[]
    for paragraph in text.split('\n'):
        line=''
        for word in paragraph.split():
            if line and typeface.size(line+' '+word)[0]>width:lines.append(line);line=''
            while typeface.size(word)[0]>width and len(word)>1:
                end=1
                while end<len(word) and typeface.size(word[:end+1])[0]<=width:end+=1
                lines.append(word[:end]);word=word[end:]
            line=(line+' '+word).strip()
        lines.append(line)
    return lines

def text_pages(text,rect,typeface,line_height=26):
    lines=wrapped_lines(text,rect.width,typeface)
    capacity=max(1,rect.height//max(line_height,typeface.get_linesize()))
    return [lines[i:i+capacity] for i in range(0,len(lines),capacity)] or [[]]

def text(screen,value,rect,typeface=None,color=TEXT,page=0,line_height=26):
    typeface=typeface or font();rect=pygame.Rect(rect)
    pages=text_pages(value,rect,typeface,line_height)
    clip=screen.get_clip();screen.set_clip(clip.clip(rect))
    for i,line in enumerate(pages[max(0,min(page,len(pages)-1))]):
        screen.blit(typeface.render(line,True,color),(rect.x,rect.y+i*max(line_height,typeface.get_linesize())))
    screen.set_clip(clip)
    return len(pages)

def button(screen,rect,label,*,danger=False,selected=False,disabled=False,choice=False,pressed=False,typeface=None):
    rect=pygame.Rect(rect);typeface=typeface or font(23)
    hover=rect.collidepoint(pygame.mouse.get_pos()) and not disabled
    down=pressed or (hover and pygame.mouse.get_pressed()[0])
    base=RED if danger else BLUE
    color=('#472b31' if danger else '#17232c') if disabled else (RED_HOVER if danger else '#354f5e') if hover or selected else base
    if down:color='#542b33' if danger else '#1c303e'
    pygame.draw.rect(screen,color,rect,border_radius=3)
    pygame.draw.rect(screen,'#b87477' if danger and hover else PAPER if hover or selected else BORDER,rect,1,border_radius=3)
    if choice:
        pygame.draw.polygon(screen,PAPER if hover else MUTED,[(rect.x+13,rect.centery-4),(rect.x+18,rect.centery),(rect.x+13,rect.centery+4)])
    lines=wrapped_lines(label,rect.width-(44 if choice else 24),typeface)
    # Conteúdo de ação deve caber integralmente; reduz apenas se necessário.
    while (len(lines)*typeface.get_linesize()>rect.height-8) and typeface.get_height()>13:
        typeface=font(typeface.get_height()-1);lines=wrapped_lines(label,rect.width-(44 if choice else 24),typeface)
    height=len(lines)*typeface.get_linesize()
    for i,line in enumerate(lines):
        image=typeface.render(line,True,'#697780' if disabled else TEXT)
        pos=(rect.x+30,rect.centery-height//2+i*typeface.get_linesize()) if choice else image.get_rect(center=(rect.centerx,rect.centery-height//2+i*typeface.get_linesize()+typeface.get_linesize()//2))
        screen.blit(image,pos)
