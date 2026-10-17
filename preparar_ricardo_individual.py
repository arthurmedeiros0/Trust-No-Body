"""Prepara somente os novos PNGs do Ricardo; preserva RGB/alpha da arte original."""
from datetime import datetime
import hashlib
import json
from pathlib import Path
import shutil
from PIL import Image,ImageOps,ImageDraw

ROOT=Path(__file__).resolve().parent
BASE=ROOT/'personagens/visitantes/ricardo'
MANIFEST=ROOT/'dados/animacoes/ricardo_individual.json'
SOURCES={'frente':('frente.png','andandofrente1.png','andandofrente2.png'),
         'costas':('costas.png','andandocostas1.png','andandocostas2.png'),
         'direita':('lado.png','andandolado1.png','andandolado2.png')}


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def protected():
    folders=['personagens/protagonista','cenarios','colisoes','dados/visitantes']
    folders += [str((BASE/name).relative_to(ROOT)) for name in
                ('referencias','retratos','investigacao','investigacao_processada','processados','dialogo','sprites_movimento')]
    result={str(p.relative_to(ROOT)):sha(p) for name in folders for p in (ROOT/name).rglob('*')
            if p.is_file() and p!=ROOT/'dados/visitantes/ricardo.json'}
    for name in ('logica_infeccao.py','casa/player.py','casa/config.py','casa/sprites.py','casa/scenes.py','casa/game.py'):
        result[name]=sha(ROOT/name)
    return result


def external_white(image):
    """Respeita alpha existente. Em imagens opacas, inunda so branco ligado a borda."""
    image=image.convert('RGBA')
    if image.getchannel('A').getextrema()[0]<255:return image
    candidate=Image.new('L',image.size)
    candidate.putdata([255 if min(r,g,b)>=250 and max(r,g,b)-min(r,g,b)<=3 else 0
                       for r,g,b,a in image.get_flattened_data()])
    padded=ImageOps.expand(candidate,border=1,fill=255)
    ImageDraw.floodfill(padded,(0,0),128)
    image.putalpha(padded.crop((1,1,image.width+1,image.height+1)).point(lambda v:0 if v==128 else 255))
    return image


def prepare():
    originals={name:external_white(Image.open(BASE/'referencias'/name)) for group in SOURCES.values() for name in group}
    # Mesmo fator para todos: nao normaliza tamanho de cabeca individualmente.
    boxes={name:image.getbbox() for name,image in originals.items()}
    scale=min(88/max(box[3]-box[1] for box in boxes.values()),
              60/max(box[2]-box[0] for box in boxes.values()))
    outputs={};records=[]
    for direction,names in SOURCES.items():
        for index,name in enumerate(names):
            crop=originals[name].crop(boxes[name])
            size=(round(crop.width*scale),round(crop.height*scale))
            resized=crop.resize(size,Image.Resampling.NEAREST)
            # Recorta so linhas vazias apos NEAREST; nunca estica novamente.
            resized=resized.crop(resized.getbbox())
            canvas=Image.new('RGBA',(64,96))
            offset=((64-resized.width)//2,94-resized.height)
            canvas.alpha_composite(resized,offset)
            path=f'sprites/{direction}.png' if index==0 else f'andando/{direction}/{index}.png'
            outputs[path]=canvas
            records.append(dict(destino=path,original=name,sha256_original=sha(BASE/'referencias'/name),
                                recorte=boxes[name],escala=scale,resize=size,offset=offset,visual=resized.size))
    for path,image in list(outputs.items()):
        if '/direita' in path:
            target=path.replace('/direita','/esquerda');outputs[target]=ImageOps.mirror(image)
            records.append(dict(destino=target,espelhado_de=path))
    return outputs,records,scale


def main():
    outputs,records,scale=prepare()
    previous_walk_count=len(list((BASE/'andando').glob('*/*.png')))
    saved=ROOT/'backups'/('ricardo_individual_'+datetime.now().strftime('%Y%m%d_%H%M%S_%f'))
    for name in ('sprites','andando'):
        shutil.copytree(BASE/name,saved/name)
    saved.mkdir(parents=True,exist_ok=True)
    shutil.copy2(ROOT/'dados/visitantes/ricardo.json',saved/'ricardo.json')
    if MANIFEST.exists():shutil.copy2(MANIFEST,saved/'ricardo_individual.json')
    for name in ('casa/animation.py','casa/visitor_walk_assets.py','casa/resident.py'):
        shutil.copy2(ROOT/name,saved/Path(name).name)
    snapshot=protected();(saved/'preservados.json').write_text(json.dumps(snapshot,ensure_ascii=False,indent=2),encoding='utf-8')
    for relative,image in outputs.items():
        target=BASE/relative;target.parent.mkdir(parents=True,exist_ok=True);image.save(target)
    # Terceiros quadros antigos ficam no backup e nao entre os novos ativos.
    for direction in ('frente','costas','direita','esquerda'):
        old=BASE/f'andando/{direction}/3.png'
        if old.exists():old.unlink()
    for record in records:record['sha256']=sha(BASE/record['destino'])
    data=dict(version=1,backup=str(saved.relative_to(ROOT)),previous_walk_count=previous_walk_count,canvas=[64,96],foot_line=94,common_scale=scale,
              frames={d:[f'andando/{d}/1.png',f'andando/{d}/2.png'] for d in ('frente','costas','direita','esquerda')},
              assets=records,notes='Fontes RGBA ja transparentes: alpha preservado. Dois laterais direitos similares; esquerda espelhada por ausencia de fonte esquerda.')
    MANIFEST.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
    registry=ROOT/'dados/visitantes/ricardo.json';definition=json.loads(registry.read_text(encoding='utf-8'))
    definition['internal_sprite_manifest']=str(MANIFEST.relative_to(ROOT)).replace('\\','/')
    registry.write_text(json.dumps(definition,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    assert snapshot==protected()
    print('12 sprites RGBA preparados sem erosao. Backup:',saved.relative_to(ROOT))

if __name__=='__main__':main()
