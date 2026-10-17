"""Tratamento conservador de fundo branco e de sua mistura nas bordas."""
from PIL import Image,ImageChops,ImageDraw,ImageOps,ImageFilter
import pygame

PROCESSING_VERSION='v7'
EXAM_SIZE=(900,460)
EXAM_BACKGROUND=(23,35,46,255)

def clean_external_specks(image):
    """Descarta ilhas pequenas e claras, separadas da silhueta principal."""
    image=image.convert('RGBA').copy()
    surface=pygame.image.frombytes(image.tobytes(),image.size,'RGBA')
    components=pygame.mask.from_surface(surface,0).get_bounding_rects()
    pixels=image.load()
    for rect in components:
        if rect.width*rect.height>64:continue
        points=[(x,y) for y in range(rect.top,rect.bottom) for x in range(rect.left,rect.right) if pixels[x,y][3]>0]
        if len(points)>32:continue
        if points and all(min(pixels[x,y][:3])>=185 and max(pixels[x,y][:3])-min(pixels[x,y][:3])<=45 for x,y in points):
            for x,y in points:pixels[x,y]=(*pixels[x,y][:3],0)
    return image

def clean_boundary_islands(image):
    """Pequenos grupos claros expostos ao exterior, mesmo ligados ao contorno."""
    r,g,b=image.convert('RGB').split()
    minimum=ImageChops.darker(ImageChops.darker(r,g),b)
    maximum=ImageChops.lighter(ImageChops.lighter(r,g),b)
    neutral=ImageChops.multiply(minimum.point(lambda v:255 if v>=150 else 0),
                               ImageChops.subtract(maximum,minimum).point(lambda v:255 if v<=45 else 0))
    candidate=Image.new('RGBA',image.size)
    candidate.putalpha(ImageChops.multiply(neutral,image.getchannel('A')))
    mask=pygame.mask.from_surface(pygame.image.frombytes(candidate.tobytes(),candidate.size,'RGBA'),0)
    alpha=image.getchannel('A');edge=ImageChops.subtract(alpha,alpha.filter(ImageFilter.MinFilter(3)))
    pixels=image.load()
    for rect in mask.get_bounding_rects():
        if rect.width*rect.height>256:continue
        points=[(x,y) for y in range(rect.top,rect.bottom) for x in range(rect.left,rect.right) if mask.get_at((x,y))]
        if len(points)>64 or not any(edge.getpixel(point)>0 for point in points):continue
        for x,y in points:pixels[x,y]=(*pixels[x,y][:3],0)
    return image

def remove_black(image):
    image=image.convert('RGBA')
    r,g,b=image.convert('RGB').split()
    maximum=ImageChops.lighter(ImageChops.lighter(r,g),b)
    dark=maximum.point(lambda value:255 if value<=8 else 0)
    mask=ImageOps.expand(dark,1,255)
    ImageDraw.floodfill(mask,(0,0),128)
    alpha=mask.crop((1,1,image.width+1,image.height+1)).point(lambda value:0 if value==128 else 255)
    image.putalpha(ImageChops.multiply(image.getchannel('A'),alpha))
    image=clean_external_specks(image)
    box=image.getbbox()
    if not box:raise ValueError('Sprite de caminhada vazio')
    return image.crop(box)

def remove_white(image):
    image=image.convert('RGBA')
    r,g,b=image.convert('RGB').split()
    minimum=ImageChops.darker(ImageChops.darker(r,g),b)
    white=minimum.point(lambda v:255 if v>=238 else 0)
    mask=ImageOps.expand(white,1,255)
    ImageDraw.floodfill(mask,(0,0),128)
    alpha=mask.crop((1,1,image.width+1,image.height+1)).point(lambda v:0 if v==128 else 255)
    alpha=ImageChops.multiply(image.getchannel('A'),alpha)
    image.putalpha(alpha)
    box=image.getbbox()
    if not box:raise ValueError('Recurso vazio')
    # Incluir o antialiasing cinza neutro do fundo e conexoes diagonais.
    # O recorte-base acima e mantido para nao mudar o enquadramento existente.
    maximum=ImageChops.lighter(ImageChops.lighter(r,g),b)
    neutral=ImageChops.multiply(minimum.point(lambda v:255 if v>=205 else 0),
                               ImageChops.subtract(maximum,minimum).point(lambda v:255 if v<=25 else 0))
    candidate=ImageOps.expand(ImageChops.lighter(white,neutral),1,255)
    rgba=Image.new('RGBA',candidate.size);rgba.putalpha(candidate)
    connected=pygame.mask.from_surface(pygame.image.frombytes(rgba.tobytes(),rgba.size,'RGBA'),0).connected_component((0,0))
    surface=pygame.Surface(candidate.size,pygame.SRCALPHA)
    connected.to_surface(surface,setcolor=(255,255,255,255),unsetcolor=(0,0,0,0))
    background=Image.frombytes('RGBA',candidate.size,pygame.image.tobytes(surface,'RGBA')).getchannel('A').crop((1,1,image.width+1,image.height+1))
    alpha=ImageChops.multiply(alpha,ImageOps.invert(background))
    image.putalpha(alpha)
    # Corrigir apenas os pixels junto ao fundo removido. Os detalhes internos
    # do jaleco nunca participam dessa operacao de descontaminacao.
    interior=alpha.filter(ImageFilter.MinFilter(7))
    edge=ImageChops.subtract(alpha,interior)
    pixels=image.load();inside=interior.load();edges=edge.load()
    search=[(dx,dy) for dy in range(-4,5) for dx in range(-4,5) if dx or dy]
    search.sort(key=lambda d:d[0]*d[0]+d[1]*d[1])
    area=edge.getbbox()
    if area:
        for y in range(area[1],area[3]):
            for x in range(area[0],area[2]):
                if not edges[x,y]:continue
                color=pixels[x,y]
                reference=None
                for dx,dy in search:
                    xx,yy=x+dx,y+dy
                    if 0<=xx<image.width and 0<=yy<image.height and inside[xx,yy]==255:
                        reference=pixels[xx,yy];break
                if reference is None:continue
                # Um pixel mais claro que o interior pode ser mistura com o branco.
                # C = alfa*F + (1-alfa)*255; inverter a mistura elimina o halo.
                denominator=255-min(reference[:3])
                if denominator<55 and min(color[:3])>=180 and max(color[:3])-min(color[:3])<=45:
                    # Uma ilha branca espessa junto a pele pode parecer interior.
                    # Buscar pele saturada proxima; branco interno do jaleco nao
                    # e removido por nao possuir esse contexto de borda.
                    alternatives=[]
                    for dy in range(-8,9):
                        for dx in range(-8,9):
                            xx,yy=x+dx,y+dy
                            if not (0<=xx<image.width and 0<=yy<image.height and inside[xx,yy]==255):continue
                            ref=pixels[xx,yy]
                            if max(ref[:3])-min(ref[:3])>=65:alternatives.append((dx*dx+dy*dy,ref))
                    if alternatives:
                        reference=min(alternatives,key=lambda item:item[0])[1]
                        denominator=255-min(reference[:3])
                if denominator<55:continue  # Interior claro: preservar o jaleco.
                coverage=max(0,min(1,(255-min(color[:3]))/denominator))
                if coverage>=.98 or coverage<=0:continue
                if coverage<.22 and min(color[:3])>=200 and max(color[:3])-min(color[:3])<=35:
                    pixels[x,y]=(*color[:3],0)
                    continue
                corrected=tuple(max(0,min(255,round((c-255*(1-coverage))/coverage))) for c in color[:3])
                pixels[x,y]=(*corrected,round(color[3]*coverage))
    image=clean_boundary_islands(clean_external_specks(image))
    image.paste((0,0,0,0),(0,0),image.getchannel('A').point(lambda v:255 if v==0 else 0))
    return image.crop(box)


def examination_panel(image,white_background=False):
    image=remove_white(image) if white_background else image.convert('RGBA')
    if white_background:image=refine_hand_wrists(image)
    scale=min(860/image.width,420/image.height)
    resized=image.resize((max(1,round(image.width*scale)),max(1,round(image.height*scale))),Image.Resampling.NEAREST)
    panel=Image.new('RGBA',EXAM_SIZE,EXAM_BACKGROUND)
    panel.alpha_composite(resized,((panel.width-resized.width)//2,(panel.height-resized.height)//2))
    return panel

def refine_hand_wrists(image):
    """Mascara externa dos punhos: proteger pele e parar ao chegar a manga."""
    image=image.copy();pixels=image.load()
    for left,right in ((0,image.width//2),(image.width//2,image.width)):
        for y in range(round(image.height*.48),round(image.height*.8)):
            row=[(x,pixels[x,y]) for x in range(left,right) if pixels[x,y][3]>0]
            # A manga azul marca o fim da regiao: nao tocar no jaleco claro.
            if sum(c[2]>c[0]*1.1 and c[1]>c[0]*1.05 and c[2]>45 and c[0]<130 for _,c in row)>=8:break
            skin=[x for x,c in row if c[0]-c[1]>=30 and c[1]-c[2]>=15 and c[0]>=90]
            if len(skin)<25:continue
            start,end=min(skin)-6,max(skin)+6
            for x,c in row:
                if not start<=x<=end and min(c[:3])>=145 and max(c[:3])-min(c[:3])<=55:
                    pixels[x,y]=(0,0,0,0)
    return image
