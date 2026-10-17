"""Limpeza conservadora da mascara, sem repintar cores da pixel art."""
from PIL import Image, ImageOps, ImageFilter
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
    # Esporoes finos de fundo junto ao chao; nao erode cabelo, maos ou sola clara.
    for y in range(76,image.height):
        for x in range(image.width):
            r,g,b,_=image.getpixel((x,y))
            if alpha.getpixel((x,y)) and not core.getpixel((x,y)) and max(r,g,b)<28 and max(r,g,b)-min(r,g,b)<=9:
                alpha.putpixel((x,y),0)
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
