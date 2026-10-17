"""Copias transparentes e carregamento dos recursos cadastrados."""
import hashlib
import json
from functools import lru_cache
from pathlib import Path
from PIL import Image
from .visitor_image_processing import remove_white,examination_panel,PROCESSING_VERSION
import pygame
from .config import ROOT
from .visitor_walk_assets import prepare_walks,comparison
from .animation import resident_animation_cycles


def remove_border_white(image):
    return remove_white(image)


def processed(source):
    digest=hashlib.sha256(source.read_bytes()).hexdigest()[:16]
    target=source.parents[1]/'processados'/(source.stem+'_'+PROCESSING_VERSION+'_'+digest+'.png')
    if not target.exists():
        target.parent.mkdir(parents=True,exist_ok=True)
        with Image.open(source) as original:remove_border_white(original).save(target)
    return target


def fit(image,size):
    scale=min(size[0]/image.get_width(),size[1]/image.get_height())
    return pygame.transform.scale(image,(max(1,round(image.get_width()*scale)),max(1,round(image.get_height()*scale))))

class VisitorAssets:
    def __init__(self,definition):
        base=ROOT/definition['asset_root']
        self.portrait=pygame.image.load(str(processed(base/definition['portrait']))).convert_alpha()
        self.portrait=fit(self.portrait,(650,definition['portrait_height']))
        self.sprites={}
        for direction,path in definition['sprites'].items():
            if definition.get('sheet_sprites'):
                self.sprites[direction]=pygame.image.load(str(base/path)).convert_alpha()
                continue
            original=pygame.image.load(str(processed(base/path))).convert_alpha()
            character=fit(original,(60,88))
            canvas=pygame.Surface((64,96),pygame.SRCALPHA)
            canvas.blit(character,((64-character.get_width())//2,94-character.get_height()))
            self.sprites[direction]=canvas
        paths=prepare_walks(definition)
        self.walk={direction:[pygame.image.load(str(path)).convert_alpha() for path in frames]
                   for direction,frames in paths.items()}
        self.cycles=resident_animation_cycles(self.sprites,self.walk)
        if self.walk:comparison(self.sprites,self.walk,base/'andando/comparacao.png')
        self.investigation={}
        for key,item in definition['investigation'].items():
            self.investigation[key]={}
            for variant in ('normal','alterado'):
                source=base/item[variant]
                digest=hashlib.sha256(source.read_bytes()).hexdigest()[:16]
                target=base/'investigacao_processada'/key/(variant+'_'+PROCESSING_VERSION+'_'+digest+'.png')
                if not target.exists():
                    target.parent.mkdir(parents=True,exist_ok=True)
                    with Image.open(source) as original:
                        examination_panel(original,white_background=(key=='manchas_maos')).save(target)
                self.investigation[key][variant]=pygame.image.load(str(target)).convert_alpha()


def load_assets(definition):
    return _cached_assets(json.dumps(definition,sort_keys=True))

@lru_cache(maxsize=16)
def _cached_assets(serialized):
    return VisitorAssets(json.loads(serialized))
