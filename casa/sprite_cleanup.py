"""Limpeza conservadora da mascara, sem repintar cores da pixel art."""
from PIL import Image, ImageOps, ImageFilter, ImageDraw
import pygame


def clean_sprite(image):
    image=image.convert('RGBA')
    mask=pygame.mask.from_surface(pygame.image.frombytes(image.tobytes(),image.size,'RGBA'))
    components=mask.connected_components()
    if not components:raise ValueError('Sprite vazio')
    principal=max(components,key=lambda part:part.count())
    # Ilhas separadas nao fazem parte da silhueta. Pixels internos sao intocados.
    alpha=Image.new('L',image.size)
    alpha.putdata([255 if principal.get_at((x,y)) else 0
                   for y in range(image.height) for x in range(image.width)])
    core=alpha.filter(ImageFilter.MinFilter(3)).filter(ImageFilter.MaxFilter(3))
    working=principal.copy()
    # Esporoes finos de fundo junto ao chao; nao erode cabelo, maos ou sola clara.
    for y in range(30,image.height):
        for x in range(image.width):
            r,g,b,_=image.getpixel((x,y))
            if alpha.getpixel((x,y)) and not core.getpixel((x,y)) and max(r,g,b)<28 and max(r,g,b)-min(r,g,b)<=9:
                neighbors=sum(working.get_at((nx,ny)) for ny in range(max(0,y-1),min(image.height,y+2))
                              for nx in range(max(0,x-1),min(image.width,x+2)))-1
                if neighbors<=3:
                    working.set_at((x,y),0)
                    # Um pixel de ligacao do pescoco, mao ou bolsa nao e residuo.
                    parts=working.connected_components()
                    if len(parts)==1:alpha.putpixel((x,y),0)
                    elif sum(p.count() for p in parts)-max(p.count() for p in parts)<=4:
                        working=max(parts,key=lambda part:part.count())
                        alpha.putdata([255 if working.get_at((px,py)) else 0
                                       for py in range(image.height) for px in range(image.width)])
                    else:working.set_at((x,y),1)
    image.putalpha(alpha)
    mask=pygame.mask.from_surface(pygame.image.frombytes(image.tobytes(),image.size,'RGBA'))
    principal=max(mask.connected_components(),key=lambda part:part.count())
    image.putalpha(Image.frombytes('L',image.size,bytes(255 if principal.get_at((x,y)) else 0
                        for y in range(image.height) for x in range(image.width))))
    # Preserva a regua e a proporcao, realinhando apenas se saiu ruido extremo.
    box=image.getbbox();body=image.crop(box)
    scale=88/body.height
    body=body.resize((round(body.width*scale),88),Image.Resampling.NEAREST)
    body=body.crop(body.getbbox())
    canvas=Image.new('RGBA',(64,96))
    canvas.alpha_composite(body,((64-body.width)//2,94-body.height))
    return canvas


def reference_idle(source):
    """Extrai a referencia lateral oficial, sem compor pernas de outros quadros."""
    image=Image.open(source).convert('RGBA').crop((420,205,825,1033))
    background=Image.new('L',image.size)
    background.putdata([255 if max(r,g,b)<=26 and max(r,g,b)-min(r,g,b)<=9 else 0
                        for r,g,b,a in image.get_flattened_data()])
    padded=ImageOps.expand(background,border=1,fill=255)
    ImageDraw.floodfill(padded,(0,0),128)
    alpha=padded.crop((1,1,image.width+1,image.height+1)).point(lambda v:0 if v==128 else 255)
    alpha=alpha.filter(ImageFilter.MaxFilter(21)).filter(ImageFilter.MinFilter(21))
    holes=ImageOps.expand(alpha,border=1,fill=0)
    ImageDraw.floodfill(holes,(0,0),128)
    alpha=holes.crop((1,1,image.width+1,image.height+1)).point(lambda v:0 if v==128 else 255)
    # A mochila externa e quase preta e aberta ao fundo: mascara geometrica
    # especifica da referencia, preservando suas cores originais sem repintar.
    ImageDraw.Draw(alpha).polygon([(x-420,y-205) for x,y in
        ((474,542),(513,557),(508,604),(502,645),(507,729),(529,766),
         (486,765),(443,743),(430,698),(431,606),(448,573))],fill=255)
    # Recupera contornos pretos proximos, mantendo a sombra de chao fora do recorte.
    expanded=alpha.filter(ImageFilter.MaxFilter(7))
    alpha.putdata([255 if a or (n and max(pixel[:3])<=7) else 0
                   for a,n,pixel in zip(alpha.get_flattened_data(),expanded.get_flattened_data(),image.get_flattened_data())])
    image.putalpha(alpha)
    body=image.crop(image.getbbox());scale=88/body.height
    body=body.resize((round(body.width*scale),88),Image.Resampling.NEAREST)
    canvas=Image.new('RGBA',(64,96));canvas.alpha_composite(body,((64-body.width)//2,6))
    # Nao erode nem filtra o corpo da referencia lateral oficial.
    body=canvas.crop(canvas.getbbox())
    if body.height!=88:body=body.resize((round(body.width*88/body.height),88),Image.Resampling.NEAREST)
    canvas=Image.new('RGBA',(64,96));canvas.alpha_composite(body,((64-body.width)//2,94-body.height))
    return canvas


def stable_walk(idle,step):
    """Preserva rosto, tronco e bolsa; troca somente a parte inferior da pose."""
    image=Image.new('RGBA',(64,96))
    image.paste(idle.crop((0,0,64,67)),(0,0))
    image.paste(step.crop((0,67,64,96)),(0,67))
    # Nao recentraliza o quadro composto: isso faria o rosto oscilar um pixel.
    return image


def lateral_idle(base):
    """Torso lateral existente; pernas verticais e pe apoiado, sem pose de passada."""
    # O quadro mais fechado da linha esquerda e a base. Nenhum desenho novo de rosto.
    right=ImageOps.mirror(base)
    # Reconstroi as pernas abaixo da barra usando a perna de apoio desse quadro.
    # Pixels de calca e sapato sao copiados sem interpolacao ou recoloracao.
    upper=right.crop((0,0,64,68))
    result=Image.new('RGBA',(64,96));result.paste(upper,(0,0))
    leg=right.crop((28,68,39,94))
    result.alpha_composite(leg,(27,68))
    result.alpha_composite(leg,(31,68))
    return clean_sprite(result)
