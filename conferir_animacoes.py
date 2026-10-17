"""Conferencias ampliadas e GIFs com a ordem real dos quadros usados pelo jogo."""
from PIL import Image, ImageDraw
from preparar_sheets import ROOT
from casa.animation import animation_cycles, resident_animation_cycles


def main():
    backup=ROOT/(ROOT/'dados/sheets/backup_restauracao.txt').read_text(encoding='utf-8')
    for character in ('protagonista','ricardo'):
        base=ROOT/('personagens/protagonista/processados' if character=='protagonista' else 'personagens/visitantes/ricardo')
        prefix='parado' if character=='protagonista' else 'sprites'
        directions=('frente','costas','esquerda','direita')
        idle={d:Image.open(base/f'{prefix}/{d}.png').convert('RGBA') for d in directions}
        walk={d:[Image.open(base/f'andando/{d}/{n}.png').convert('RGBA') for n in (1,2,3)] for d in directions}
        cycles=(animation_cycles if character=='protagonista' else resident_animation_cycles)(idle,walk)
        sheet=Image.new('RGB',(1200,1370),'#243342');draw=ImageDraw.Draw(sheet)
        draw.text((12,8),character+' | antes / idle atual / ciclo real | ampliacao 3x NEAREST',fill='white')
        def tile(canvas,im,x,y,label):
            checker=Image.new('RGBA',(192,288));p=ImageDraw.Draw(checker)
            for yy in range(0,288,12):
                for xx in range(0,192,12):
                    p.rectangle((xx,yy,xx+11,yy+11),fill='#eee9df' if (xx//12+yy//12)%2 else '#a5aab9')
            checker.alpha_composite(im.resize((192,288),Image.Resampling.NEAREST))
            canvas.paste(checker.convert('RGB'),(x,y))
            p=ImageDraw.Draw(canvas);p.line((x,y+282,x+191,y+282),fill='#e94040')
            p.text((x,y+294),label,fill='white')
        for row,direction in enumerate(directions):
            y=40+row*330
            previous=Image.open(backup/base.relative_to(ROOT)/f'{prefix}/{direction}.png').convert('RGBA')
            tile(sheet,previous,4,y,direction+' antes')
            tile(sheet,idle[direction],204,y,'idle atual')
            for index,frame in enumerate(cycles[direction]):
                tile(sheet,frame,404+index*200,y,'idle' if frame is idle[direction] else 'passo '+str(walk[direction].index(frame)+1))
        sheet.save(ROOT/f'docs/animacoes_{character}.png')
        frames=[]
        for index in range(12):
            canvas=Image.new('RGB',(800,340),'#243342')
            for column,direction in enumerate(directions):
                tile(canvas,cycles[direction][index%len(cycles[direction])],column*200,8,direction)
            frames.append(canvas)
        frames[0].save(ROOT/f'docs/animacoes_{character}.gif',save_all=True,append_images=frames[1:],
                       duration=140 if character=='protagonista' else 180,loop=0,disposal=2)

if __name__=='__main__':main()
