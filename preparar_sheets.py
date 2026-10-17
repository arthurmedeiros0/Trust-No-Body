"""Extracao reproduzivel das sheets aprovadas; nao gera arte nem altera exames."""
from pathlib import Path
import hashlib
import json
import shutil
from datetime import datetime
from PIL import Image, ImageDraw, ImageOps

ROOT = Path(__file__).resolve().parent
DIRECTIONS = ('frente', 'costas', 'esquerda', 'direita')

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def transparent(image, movement=False):
    """Somente fundo escuro neutro conectado as bordas; interiores preservados."""
    image = image.convert('RGBA')
    mask = Image.new('L', image.size)
    mask.putdata([255 if max(r,g,b)<=26 and (g>=r and g>=b if movement else max(r,g,b)-min(r,g,b)<=9) else 0
                  for r,g,b,a in image.getdata()])
    padded = ImageOps.expand(mask, border=1, fill=255)
    ImageDraw.floodfill(padded, (0,0), 128)
    alpha = padded.crop((1,1,image.width+1,image.height+1)).point(lambda v: 0 if v==128 else 255)
    # Restaura interiores escuros entre as bordas visiveis da silhueta.
    # Nas pernas mantemos os vãos; nos bustos a base aberta tambem e preenchida.
    spans=[]
    for y in range(image.height):
        xs=[x for x in range(image.width) if alpha.getpixel((x,y))]
        spans.append((min(xs),max(xs)) if xs else None)
    draw=ImageDraw.Draw(alpha)
    for y,span in enumerate(spans):
        if movement:continue
        if span is None:
            above=next((spans[k] for k in range(y-1,max(-1,y-13),-1) if spans[k]),None)
            below=next((spans[k] for k in range(y+1,min(image.height,y+13)) if spans[k]),None)
            if above and below:span=(max(above[0],below[0]),min(above[1],below[1]))
        if span:draw.line((span[0],y,span[1],y),fill=255)
    image.putalpha(alpha)
    # Descarta ilhas de ruido externas; contorno e interiores pertencem a silhueta.
    import pygame
    surface=pygame.image.frombytes(image.tobytes(),image.size,'RGBA')
    components=pygame.mask.from_surface(surface).connected_components()
    if components and movement:
        largest=max(components,key=lambda component:component.count())
        for component in components:
            if component.count()>=12:largest.draw(component,(0,0))
        alpha.putdata([255 if largest.get_at((x,y)) else 0 for y in range(image.height) for x in range(image.width)])
        image.putalpha(alpha)
    return image.crop(image.getbbox())

def sprite(image):
    scale=min(88/image.height,60/image.width)
    image=image.resize((round(image.width*scale),round(image.height*scale)),Image.Resampling.NEAREST)
    image=image.crop(image.getbbox())
    # O NEAREST pode descartar uma linha extrema: reafirma a altura corporal.
    if image.height!=88:
        image=image.resize((round(image.width*88/image.height),88),Image.Resampling.NEAREST)
    canvas=Image.new('RGBA',(64,96))
    canvas.alpha_composite(image,((64-image.width)//2,94-image.height))
    return canvas

def protected():
    base=ROOT/'personagens/visitantes/ricardo'
    return {str(p.relative_to(ROOT)):digest(p) for folder in ('retratos','investigacao','investigacao_processada','processados')
            for p in (base/folder).rglob('*.png')}

def backup():
    target=ROOT/'backups'/('sheets_'+datetime.now().strftime('%Y%m%d_%H%M%S_%f'))
    for name in ('personagens/protagonista/processados','personagens/visitantes/ricardo/sprites',
                 'personagens/visitantes/ricardo/andando'):
        if (ROOT/name).exists():shutil.copytree(ROOT/name,target/name)
    for name in ('dados/visitantes/ricardo.json','preparar_sprites.py'):
        (target/name).parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(ROOT/name,target/name)
    (target/'preservados.json').write_text(json.dumps(protected(),indent=2),encoding='utf-8')
    return target

def extract(character):
    base=ROOT/('personagens/protagonista' if character=='protagonista' else 'personagens/visitantes/ricardo')
    source=base/'referencias/novo_design.png'
    sheet=Image.open(source)
    assert sheet.size==(1536,1024), 'Sheet diferente: revise coordenadas antes de processar'
    out=base/'processados' if character=='protagonista' else base
    records=[];images=[]
    def save(name,box,movement=False):
        image=transparent(sheet.crop(box),movement)
        if movement:image=sprite(image)
        target=out/(name+'.png');target.parent.mkdir(parents=True,exist_ok=True);image.save(target)
        records.append(dict(destino=str(target.relative_to(ROOT)),recorte=box,sha256=digest(target)))
        images.append((name,image))
    idle=[(202,88,276,221),(309,89,384,225),(160,697,234,818),(530,89,606,225)]
    if character=='ricardo':idle=[(201,88,274,226),(307,89,384,227),(158,697,236,819),(535,88,610,226)]
    prefix='parado' if character=='protagonista' else 'sprites'
    for direction,box in zip(DIRECTIONS,idle):save(prefix+'/'+direction,box,True)
    # Os tres primeiros quadros de cada linha direcional, sem titulos/divisorias.
    for direction,(top,bottom) in zip(DIRECTIONS,[(410,532),(550,674),(697,819),(842,973)]):
        for index,x in enumerate((150,273,395),1):
            save(f'andando/{direction}/{index}',(x,top,x+83,bottom),True)
    portraits='retratos' if character=='protagonista' else 'dialogo'
    save(portraits+'/principal',(733,69,1117,535))
    for expression,box in zip(('normal','surpreso','preocupado','determinado'),
                             ((1164,82,1317,251),(1344,82,1499,251),(1164,301,1317,495),(1344,301,1499,495))):
        save(portraits+('/' if character=='protagonista' else '/expressoes/')+expression,box)
    if character=='ricardo':
        for detail,box in zip(('olhos','costas','mao','sapato'),((750,624,948,739),(978,615,1160,757),(760,791,935,946),(973,806,1152,946))):
            save('dialogo/detalhes/'+detail,box)
    report=dict(source=str(source.relative_to(ROOT)),source_sha256=digest(source),assets=records,
                observacao='Laterais extraidas independentemente; nao sao espelhamentos. Tres primeiros quadros por linha. Protagonista: idle esquerdo adaptado da linha esquerda; terceiro idle da sheet repete frente.')
    report_path=ROOT/'dados/sheets'/f'{character}.json';report_path.parent.mkdir(parents=True,exist_ok=True)
    report_path.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    preview=Image.new('RGB',(1000,1790),'#263645');draw=ImageDraw.Draw(preview)
    draw.text((15,8),character+' | nova sheet | pes: linha vermelha',fill='white')
    for i,(name,image) in enumerate(images):
        x=15+(i%4)*245;y=45+(i//4)*240
        tile=Image.new('RGBA',(225,208),'#b7bac4');d=ImageDraw.Draw(tile)
        for yy in range(0,208,12):
            for xx in range(0,225,12):
                if (xx//12+yy//12)%2:d.rectangle((xx,yy,xx+11,yy+11),fill='#e1ded5')
        scale=min(220/image.width,200/image.height)
        scaled=image.resize((round(image.width*scale),round(image.height*scale)),Image.Resampling.NEAREST)
        tile.alpha_composite(scaled,((225-scaled.width)//2,208-scaled.height))
        preview.paste(tile.convert('RGB'),(x,y));draw.text((x,y+211),name,fill='white')
        if i<16:draw.line((x,y+204,x+224,y+204),fill='red')
    if character=='ricardo':draw.text((15,1760),'Porta e todas as imagens de investigacao preservadas (SHA-256).',fill='white')
    preview.save(out/'conferencia_sheet.png')

def main():
    previous=protected();saved=backup()
    for character in ('protagonista','ricardo'):extract(character)
    assert previous==protected(), 'Assets protegidos foram alterados'
    print('Sheets extraidas. Backup:',saved.relative_to(ROOT))

if __name__=='__main__':main()
