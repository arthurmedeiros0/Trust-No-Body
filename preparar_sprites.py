"""Prepare originais sem altera-los. Execute: python preparar_sprites.py."""
from pathlib import Path
import hashlib
import json
from PIL import Image, ImageDraw, ImageChops, ImageOps

ROOT = Path(__file__).resolve().parent
BASE = ROOT / 'personagens' / 'protagonista'
SOURCE = BASE / 'originais'
OUTPUT = BASE / 'processados'
# Classificacao visual; indices referem-se a lista alfabetica dos 13 originais.
POSES = [(6,'parado/frente'),(8,'parado/costas'),(9,'parado/direita'),
         (12,'parado/esquerda'),(4,'andando/frente/1'),(7,'andando/frente/2'),
         (10,'andando/frente/3'),(1,'andando/costas/1'),(5,'andando/costas/2'),
         (11,'andando/costas/3'),(0,'andando/direita/1'),(2,'andando/direita/2'),
         (3,'andando/direita/3')]


def remove_background(path):
    im = Image.open(path).convert('RGBA')
    # Pad permite uma unica inundacao atingir todas as bordas.
    rgb = im.convert('RGB')
    channels = rgb.split()
    maximum = ImageChops.lighter(ImageChops.lighter(channels[0], channels[1]), channels[2])
    dark = maximum.point(lambda v: 255 if v <= 3 else 0)
    mask = ImageOps.expand(dark, border=1, fill=255)
    ImageDraw.floodfill(mask, (0, 0), 128, thresh=0)
    background = mask.crop((1,1,im.width+1,im.height+1)).point(lambda v: 0 if v == 128 else 255)
    im.putalpha(ImageChops.multiply(im.getchannel('A'), background))
    box = im.getbbox()
    if box is None:
        raise ValueError(f'Imagem vazia: {path}')
    return im.crop(box), box


def main():
    files = sorted(SOURCE.glob('*.png'))
    if len(files) != 13:
        raise ValueError('Esperados os 13 originais; confira o mapeamento antes de continuar.')
    prepared = []
    for index, destination in POSES:
        im, box = remove_background(files[index])
        # Regua visual comum: 88 px do topo do cabelo ao apoio do pe.
        # Os originais foram gerados em escalas distintas; a referencia e a
        # mesma altura corporal para todo o conjunto, sem deformar a largura.
        scale = 88 / im.height
        prepared.append((files[index], destination, im, box, scale))
    # Um unico fator de ajuste para o conjunto inteiro, mantendo a altura corporal comum.
    fit = min(1, min(min(60/(im.width*s),90/(im.height*s)) for _,_,im,_,s in prepared))
    report = []
    sprites = []
    for source, destination, im, box, scale in prepared:
        size = (max(1,round(im.width*scale*fit)), max(1,round(im.height*scale*fit)))
        resized = im.resize(size, Image.Resampling.NEAREST)
        canvas = Image.new('RGBA',(64,96))
        canvas.alpha_composite(resized, ((64-size[0])//2,94-size[1]))
        target = OUTPUT / (destination+'.png')
        target.parent.mkdir(parents=True, exist_ok=True)
        canvas.save(target)
        sprites.append((destination,canvas))
        report.append(dict(original=source.name,sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
                           destino=str(target.relative_to(ROOT)),recorte=box,tamanho_visual=size,escala=scale*fit))
    for n in range(1,4):
        canvas = ImageOps.mirror(Image.open(OUTPUT/f'andando/direita/{n}.png'))
        target=OUTPUT/f'andando/esquerda/{n}.png';target.parent.mkdir(parents=True,exist_ok=True);canvas.save(target)
        sprites.append((f'andando/esquerda/{n}',canvas))
    sheet=Image.new('RGB',(4*230,4*330),'#262b35'); draw=ImageDraw.Draw(sheet)
    lookup=dict(sprites)
    for row,direction in enumerate(('frente','costas','direita','esquerda')):
        for col,pose in enumerate((f'parado/{direction}',*[f'andando/{direction}/{n}' for n in range(1,4)])):
            x,y=col*230+19,row*330+20
            for yy in range(0,288,12):
                for xx in range(0,192,12):
                    draw.rectangle((x+xx,y+yy,x+xx+11,y+yy+11),fill='#aaaabb' if (xx//12+yy//12)%2 else '#dddde5')
            tile=lookup[pose].resize((192,288),Image.Resampling.NEAREST)
            sheet.paste(tile,(x,y),tile)
            draw.line((x,y+282,x+192,y+282),fill='#ee4455',width=1)
            draw.text((x,y+293),pose,fill='white')
    sheet.save(OUTPUT/'comparacao.png')
    (OUTPUT/'manifesto.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print('16 sprites 64x96, comparacao e manifesto gerados.')

if __name__ == '__main__':
    main()

