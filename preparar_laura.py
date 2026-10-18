"""Deriva assets da Laura com Pillow; nunca sobrescreve os 21 originais."""
import hashlib
import json
from pathlib import Path
from PIL import Image,ImageOps,ImageDraw,ImageChops

ROOT=Path(__file__).resolve().parent
BASE=ROOT/'personagens/visitantes/laura'
OUT=BASE/'processados'
GROUPS={
    'frente':('parado/parado_frente.png','andando/andando_frente_um.png','andando/andando_frente_dois.png'),
    'costas':('parado/parado_tras.png','andando/andando_tras_um.png','andando/andando_tras_dois.png'),
    'direita':('parado/parado_lado.png','andando/andando_lado_um.png','andando/andando_lado_dois.png')}


def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def transparent(image):
    image=image.convert('RGBA')
    # As fontes atuais ja possuem alpha: preservar todos os pixels literalmente.
    if image.getchannel('A').getextrema()[0]<255:return image
    r,g,b=image.convert('RGB').split()
    maximum=ImageChops.lighter(ImageChops.lighter(r,g),b)
    mask=ImageOps.expand(maximum.point(lambda v:255 if v<=8 else 0),1,255)
    ImageDraw.floodfill(mask,(0,0),128)
    image.putalpha(mask.crop((1,1,image.width+1,image.height+1)).point(lambda v:0 if v==128 else 255))
    return image


def prepare():
    sources=[BASE/path for group in GROUPS.values() for path in group]
    sources += [BASE/'porta/porta.png',*sorted((BASE/'investigacao').glob('*.png'))]
    original_hashes={p.relative_to(BASE).as_posix():digest(p) for p in sources}
    outputs={};records=[]
    for direction,paths in GROUPS.items():
        for index,path in enumerate(paths):
            with Image.open(BASE/path) as source:image=transparent(source)
            box=image.getbbox();crop=image.crop(box)
            scale=min(86/crop.height,60/crop.width)
            size=(round(crop.width*scale),round(crop.height*scale))
            resized=crop.resize(size,Image.Resampling.NEAREST)
            resized=resized.crop(resized.getbbox())
            canvas=Image.new('RGBA',(64,96))
            offset=((64-resized.width)//2,94-resized.height)
            canvas.alpha_composite(resized,offset)
            target=f'sprites/{direction}.png' if index==0 else f'andando/{direction}/{index}.png'
            outputs[target]=canvas
            records.append(dict(output='processados/'+target,source=path,crop=box,scale=scale,size=size,offset=offset))
    for path,image in list(outputs.items()):
        if '/direita' in path:outputs[path.replace('/direita','/esquerda')]=ImageOps.mirror(image)
    with Image.open(BASE/'porta/porta.png') as source:portrait=transparent(source)
    outputs['porta.png']=portrait.crop(portrait.getbbox())
    for path in sorted((BASE/'investigacao').glob('*.png')):
        with Image.open(path) as source:image=transparent(source)
        # Um unico painel derivado por arquivo fonte, inclusive rosto_normal.
        image=image.crop(image.getbbox())
        scale=min(860/image.width,420/image.height)
        image=image.resize((round(image.width*scale),round(image.height*scale)),Image.Resampling.NEAREST)
        panel=Image.new('RGBA',(900,460),(23,35,46,255))
        panel.alpha_composite(image,((900-image.width)//2,(460-image.height)//2))
        outputs['investigacao/'+path.name]=panel
    for path,image in outputs.items():
        target=OUT/path;target.parent.mkdir(parents=True,exist_ok=True);image.save(target)
    manifest=dict(version=1,canvas=[64,96],foot_line=94,visual_height=86,
        frames={d:[f'processados/andando/{d}/{i}.png' for i in (1,2)] for d in ('frente','costas','direita','esquerda')},
        source_hashes=original_hashes,records=records,
        output_hashes={f'processados/{p}':digest(OUT/p) for p in outputs},
        notes='Alpha original preservado; escala proporcional NEAREST, pes y=94; esquerda espelhada da direita.')
    target=ROOT/'dados/animacoes/laura.json';target.parent.mkdir(parents=True,exist_ok=True)
    target.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    assert all(digest(BASE/path)==value for path,value in original_hashes.items())
    print(f'{len(outputs)} imagens derivadas; {len(sources)} originais intactos.')


if __name__=='__main__':prepare()
