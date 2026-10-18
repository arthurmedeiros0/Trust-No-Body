"""Capturas da Laura no jogo real e pre-visualizacao NEAREST dos ciclos."""
import os
os.environ.setdefault('SDL_VIDEODRIVER','dummy')
import pygame
from PIL import Image,ImageDraw
from casa.game import House
from casa.config import ROOT


def main():
    pygame.init();screen=pygame.display.set_mode((1280,720))
    game=House();game.dialog='';state=game.visitor_session
    game.news.watch(game.news.current(1));game.decide_visitor(state.visitors['ricardo'],'acolhido')
    while game.days.day<state.visitors['laura'].arrival_day:
        game.dialog='';game.change_room('quarto',game.scenes['quarto'].point((345,365)))
        game.handle_event(pygame.event.Event(pygame.KEYUP,key=pygame.K_e))
        game.interact();assert game.sleep_option
        game.confirm_sleep();game.update((0,0),3)
    game.dialog='';game.change_room('entrada',game.scenes['entrada'].point((768,402)))
    game.interact();game.update((0,0),1);game.update((0,0),1)
    assert game.observing and state.manager.current=='laura'
    def capture(name):game.draw(screen);pygame.image.save(screen,str(ROOT/'docs'/name))
    capture('laura_porta.png')
    ui=game.peephole.visitor_ui
    ui.page='talk';ui.response=ui.dialogue.intro();capture('laura_dialogo.png')
    assets=game.visitor_assets['laura']
    sheet=Image.new('RGB',(1200,4*310),'#d9d7ce');draw=ImageDraw.Draw(sheet)
    for row,direction in enumerate(('frente','costas','direita','esquerda')):
        for col,frame in enumerate([assets.sprites[direction],*assets.cycles[direction]]):
            image=Image.frombytes('RGBA',frame.get_size(),pygame.image.tobytes(frame,'RGBA')).resize((192,288),Image.Resampling.NEAREST)
            x=col*240+24;y=row*310
            draw.rectangle((x,y,x+192,y+288),fill='#14212a' if col%2 else '#dedbd3')
            sheet.paste(image,(x,y),image)
            draw.text((col*240+5,y+290),direction+(' idle' if col==0 else f' ciclo {col}'),fill='#111111')
    sheet.save(ROOT/'docs/laura_ciclos.png')
    exams=Image.new('RGB',(1200,6*200),'#101419');draw=ImageDraw.Draw(exams)
    for row,(key,variants) in enumerate(assets.investigation.items()):
        for col,(variant,frame) in enumerate(variants.items()):
            image=Image.frombytes('RGBA',frame.get_size(),pygame.image.tobytes(frame,'RGBA'))
            image.thumbnail((590,170),Image.Resampling.NEAREST)
            exams.paste(image,(col*600,row*200))
            draw.text((col*600,row*200+175),key+' '+variant,fill='white')
    exams.save(ROOT/'docs/laura_exames.png')
    game.decide_visitor(state.visitors['laura'],'acolhido');game.observing=False
    game.change_room('sala');game.dialog='';game.draw(screen)
    pygame.image.save(screen,str(ROOT/'docs/laura_moradores.png'))
    frames=[]
    for _ in range(32):
        game.update((0,0),.18);game.draw(screen)
        image=Image.frombytes('RGB',screen.get_size(),pygame.image.tobytes(screen,'RGB'))
        image=image.resize((768,432),Image.Resampling.NEAREST)
        frames.append(image)
    frames[0].save(ROOT/'docs/laura_moradores.gif',save_all=True,append_images=frames[1:],duration=180,loop=0)
    pygame.quit()


if __name__=='__main__':main()
