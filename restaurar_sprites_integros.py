"""Restaura arte anterior as erosoes/composicoes, com retoques externos explicitos."""
import json
import shutil
from PIL import Image,ImageOps
from preparar_sheets import ROOT,backup,digest,protected
from casa.sprite_cleanup import reference_idle
import pygame

BASELINE=ROOT/'backups/sheets_20261017_152232_838869'
DIRECTIONS=('frente','costas','direita','esquerda')


def conservative_restore(image):
    """So descarta ilhas externas; nenhum pixel do componente corporal e apagado."""
    image=image.convert('RGBA')
    parts=pygame.mask.from_surface(pygame.image.frombytes(image.tobytes(),image.size,'RGBA')).connected_components()
    principal=max(parts,key=lambda part:part.count());bounds=principal.get_bounding_rects()[0]
    for part in parts:
        if bounds.contains(part.get_bounding_rects()[0]):continue
        for y in range(96):
            for x in range(64):
                if part.get_at((x,y)):image.putpixel((x,y),(0,0,0,0))
    # Compensa apenas eventual ultima linha formada por ruido. Nao redimensiona.
    dy=94-image.getbbox()[3]
    canvas=Image.new('RGBA',(64,96));canvas.alpha_composite(image,(0,dy))
    return canvas,dy


def main():
    previous=protected();saved=backup()
    pointer=ROOT/'dados/sheets/backup_restauracao.txt'
    if not pointer.exists():pointer.write_text(str(saved.relative_to(ROOT)),encoding='utf-8')
    for character,relative,prefix in (('protagonista','personagens/protagonista/processados','parado'),
                                      ('ricardo','personagens/visitantes/ricardo','sprites')):
        if character=='ricardo' and json.loads((ROOT/'dados/visitantes/ricardo.json').read_text(encoding='utf-8')).get('internal_sprite_manifest'):
            continue # Nunca recoloca a sheet antiga sobre os PNGs individuais ativos.
        base=ROOT/relative
        for direction in DIRECTIONS:
            paths=[f'{prefix}/{direction}.png']+[f'andando/{direction}/{n}.png' for n in (1,2,3)]
            for path in paths:
                with Image.open(BASELINE/relative/path) as original:
                    image,dy=conservative_restore(original);image.save(base/path)
        if character=='protagonista':
            image=reference_idle(ROOT/'personagens/protagonista/referencias/protagonista_parado_lado.png')
            image.save(base/'parado/direita.png');ImageOps.mirror(image).save(base/'parado/esquerda.png')
            # Apenas ganchos externos efetivamente conferidos. Nao erode o corpo.
            for path,right in (('parado/frente.png',17),('andando/frente/2.png',20)):
                image=Image.open(base/path).convert('RGBA')
                image.paste((0,0,0,0),(0,86,right,94));image.save(base/path)
        else:
            # A sheet tem dois idles olhando para a direita. O esquerdo passa a
            # ser um idle autentico espelhado, em vez do primeiro passo esquerdo.
            with Image.open(base/'sprites/direita.png') as image:
                ImageOps.mirror(image).save(base/'sprites/esquerda.png')
        manifest_path=ROOT/f'dados/sheets/{character}.json'
        manifest=json.loads(manifest_path.read_text(encoding='utf-8'))
        for row in manifest['assets']:
            path=ROOT/row['destino']
            normalized=row['destino'].replace('\\','/')
            if '/andando/' in normalized or f'/{prefix}/' in normalized:
                row['sha256']=digest(path)
                row['edicao']='Arte restaurada do backup anterior a erosao; sem composicao de tronco/pernas.'
                row['restaurado_de']=str((BASELINE/path.relative_to(ROOT)).relative_to(ROOT))
                if character=='protagonista' and normalized.endswith(('parado/direita.png','parado/esquerda.png')):
                    row.pop('restaurado_de',None)
                    row['edicao']='Referencia lateral oficial intacta; esquerda espelhada.'
                    row['recorte']=[420,205,825,1033]
                if character=='ricardo' and normalized.endswith('sprites/esquerda.png'):
                    row['edicao']='Parado direito autentico espelhado; nao usa quadro de caminhada.'
                    row['espelhado_de']='sprites/direita.png'
        manifest['observacao']='Movimento restaurado integralmente; idle lateral protagonista da referencia oficial; idle esquerdo Ricardo espelhado do parado direito. Somente dois retoques externos na sola do protagonista.'
        manifest_path.write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
        overview=Image.new('RGB',(800,1320),'#243342')
        from PIL import ImageDraw
        draw=ImageDraw.Draw(overview)
        for row,direction in enumerate(DIRECTIONS):
            for col,path in enumerate([f'{prefix}/{direction}.png']+[f'andando/{direction}/{n}.png' for n in (1,2,3)]):
                x,y=col*200,row*330
                for yy in range(0,288,12):
                    for xx in range(0,192,12):
                        draw.rectangle((x+xx,y+yy,x+xx+11,y+yy+11),fill='#eee9df' if (xx//12+yy//12)%2 else '#a5aab9')
                image=Image.open(base/path).convert('RGBA').resize((192,288),Image.Resampling.NEAREST)
                overview.paste(image,(x,y),image);draw.text((x,y+295),path,fill='white')
        overview.save(base/'conferencia_sheet.png')
    assert protected()==previous
    print('Arte restaurada sem erosao. Backup anterior:',saved.relative_to(ROOT))

if __name__=='__main__':main()
