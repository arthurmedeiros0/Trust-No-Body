"""Sprites de caminhada: mapeamento visual explicito e escala comum aos parados."""
import hashlib
import json
from pathlib import Path
from PIL import Image,ImageOps,ImageDraw
from .config import ROOT
from .visitor_image_processing import remove_black,PROCESSING_VERSION


def prepare_walks(definition):
    if definition.get('sheet_sprites'):
        base=ROOT/definition['asset_root']
        return {direction:[base/f'andando/{direction}/{n}.png' for n in range(1,4)]
                for direction in definition['sprites']}
    if not definition.get('walk_manifest'):return {}
    base=ROOT/definition['asset_root']
    manifest_path=ROOT/definition['walk_manifest']
    manifest=json.loads(manifest_path.read_text(encoding='utf-8'))
    fingerprint=hashlib.sha256(manifest_path.read_bytes()+PROCESSING_VERSION.encode())
    sources=[]
    for direction,frames in manifest['frames'].items():
        for number,frame in enumerate(frames,1):
            source=base/'sprites_movimento'/frame['original']
            digest=hashlib.sha256(source.read_bytes()).hexdigest()
            if digest!=frame['sha256']:raise ValueError('Original de caminhada mudou; revise o manifesto: '+str(source))
            fingerprint.update(digest.encode());sources.append((direction,number,source))
    output=base/'andando';stamp=output/'processamento.json'
    paths={direction:[output/direction/f'{n}.png' for n in range(1,4)] for direction in ('frente','costas','direita','esquerda')}
    signature=fingerprint.hexdigest()
    if stamp.exists() and json.loads(stamp.read_text(encoding='utf-8')).get('signature')==signature and all(p.exists() for frames in paths.values() for p in frames):return paths
    crops=[(direction,number,source,remove_black(Image.open(source))) for direction,number,source in sources]
    # Mesma regua visual dos sprites parados: 88 px; ajuste global de encaixe.
    target_height=manifest['visual_height']
    common_fit=min(1,min(60/(im.width*target_height/im.height) for _,_,_,im in crops))
    report=[]
    for direction,number,source,im in crops:
        scale=target_height/im.height*common_fit
        size=(round(im.width*scale),round(im.height*scale))
        canvas=Image.new('RGBA',tuple(manifest['canvas']))
        canvas.alpha_composite(im.resize(size,Image.Resampling.NEAREST),((64-size[0])//2,manifest['foot_line']-size[1]))
        path=paths[direction][number-1];path.parent.mkdir(parents=True,exist_ok=True);canvas.save(path)
        report.append(dict(original=source.name,direction=direction,frame=number,size=size,scale=scale))
    for number,path in enumerate(paths['esquerda']):
        path.parent.mkdir(parents=True,exist_ok=True)
        ImageOps.mirror(Image.open(paths['direita'][number])).save(path)
    stamp.write_text(json.dumps(dict(signature=signature,version=PROCESSING_VERSION,reference_height=target_height,feet=manifest['foot_line'],frames=report),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    return paths


def comparison(idle,walk,output):
    # Surfaces ja carregadas pelo jogo; ampliacao NEAREST sobre quadriculado.
    import pygame
    sheet=Image.new('RGB',(920,1320),'#17232e');draw=ImageDraw.Draw(sheet)
    for row,direction in enumerate(('frente','costas','direita','esquerda')):
        for col,surface in enumerate([idle[direction],*walk[direction]]):
            x,y=col*230+19,row*330+10
            for yy in range(0,288,12):
                for xx in range(0,192,12):
                    draw.rectangle((x+xx,y+yy,x+xx+11,y+yy+11),fill='#aab0bb' if (xx//12+yy//12)%2 else '#e0e3e8')
            im=Image.frombytes('RGBA',surface.get_size(),pygame.image.tobytes(surface,'RGBA')).resize((192,288),Image.Resampling.NEAREST)
            sheet.paste(im,(x,y),im)
            draw.line((x,y+282,x+192,y+282),fill='#ee4455')
            draw.text((x,y+296),direction+(' parado' if col==0 else f' passo {col}'),fill='white')
    sheet.save(output)
