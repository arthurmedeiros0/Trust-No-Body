"""Retratos faciais normais: recortes em memória, independentes dos sintomas."""
from functools import lru_cache
import pygame
from .config import ROOT
from .visitor_assets import fit
from . import ui_theme as ui

# Frações da imagem ORIGINAL de palidez normal, após revisão dos sete arquivos.
FACE_CROPS={
    'ricardo':(.08,.02,.84,.84), 'laura':(.30,.02,.38,.76),
    'antonio':(.10,.02,.80,.82), 'daniel':(.04,.02,.92,.71),
    'gabriel':(.12,.03,.76,.78), 'helena':(.10,.13,.80,.61),
    'marina':(.12,.01,.76,.83)}

@lru_cache(maxsize=32)
def _load(path,crop):
    image=pygame.image.load(path).convert_alpha()
    x,y,w,h=crop
    rect=pygame.Rect(round(x*image.get_width()),round(y*image.get_height()),round(w*image.get_width()),round(h*image.get_height())).clip(image.get_rect())
    return image.subsurface(rect).copy() if rect.width and rect.height else None

def face(definition):
    item=definition.get('investigation',{}).get('palidez_anormal',{})
    normal=item.get('normal')
    if not normal:return None
    path=ROOT/definition.get('asset_root','')/normal
    try:return _load(str(path),FACE_CROPS.get(definition['id'],(0,0,1,1)))
    except (OSError,pygame.error,ValueError):return None

def draw(screen,definition,rect):
    rect=pygame.Rect(rect);ui.panel(screen,rect,alpha=255)
    image=face(definition)
    if image is not None:
        image=fit(image,rect.inflate(-8,-8).size)
        screen.blit(image,image.get_rect(center=rect.center))
    else:
        pygame.draw.circle(screen,'#53616a',(rect.centerx,rect.y+rect.height//3),18)
        pygame.draw.ellipse(screen,'#53616a',(rect.centerx-30,rect.y+rect.height//2,60,46))
        ui.text(screen,definition.get('name','?')[:1],pygame.Rect(rect.x+8,rect.bottom-26,rect.width-16,22),ui.font(22))
