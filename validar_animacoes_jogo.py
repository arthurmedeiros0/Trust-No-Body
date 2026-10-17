"""Captura o render real do jogo em fases conhecidas, sem alterar a simulacao."""
import os
os.environ.setdefault('SDL_VIDEODRIVER','dummy')
import pygame
from PIL import Image,ImageDraw
from casa.game import House
from casa.config import ROOT,FRAME_TIME


def main():
    pygame.init();screen=pygame.display.set_mode((1280,720))
    game=House();game.handle_event(pygame.event.Event(pygame.KEYDOWN,key=pygame.K_RETURN))
    game.news.watch(game.news.current(1));game.change_room('sala')
    game.decide_visitor(game.visitor_session.visitors['ricardo'],'acolhido')
    actor=game.residents['ricardo'];player=game.player
    before=(player.feet.copy(),actor.feet.copy(),player.shadow,game.visitor_shadow)
    sheet=Image.new('RGB',(896,2150),'#243342');draw=ImageDraw.Draw(sheet)
    frames=[]
    for row,direction in enumerate(('frente','costas','esquerda','direita')):
        player.direction=actor.direction=direction
        player.moving=actor.moving=True;actor.walking=True
        for index in range(4):
            player.elapsed=index*FRAME_TIME+.001
            actor.animation_elapsed=index*actor.frame_seconds+.001
            game.draw(screen)
            screenshot=Image.frombytes('RGB',screen.get_size(),pygame.image.tobytes(screen,'RGB'))
            camera=game.scene.camera_for(player.feet)
            for who,feet in enumerate((player.feet,actor.feet)):
                x,y=map(round,feet-camera)
                crop=screenshot.crop((x-56,y-112,x+56,y+16)).resize((224,256),Image.Resampling.NEAREST)
                sheet.paste(crop,(index*224,30+(row*2+who)*264))
                draw.text((index*224+4,30+(row*2+who)*264),('protagonista' if who==0 else 'Ricardo')+' '+direction,fill='white')
            if row==3 and index==0:screenshot.save(ROOT/'docs/ajuste_lateral_sala.png')
        for index in range(16):
            player.elapsed=index*.06;actor.animation_elapsed=index*.06
            game.draw(screen)
            frames.append(Image.frombytes('RGB',screen.get_size(),pygame.image.tobytes(screen,'RGB')).resize((896,504),Image.Resampling.NEAREST))
    draw.text((8,8),'Render Pygame real: quatro fases, sombra e cenario; ampliacao 2x',fill='white')
    sheet.save(ROOT/'docs/ajuste_lateral_render.png')
    frames[0].save(ROOT/'docs/ajuste_lateral_jogo.gif',save_all=True,append_images=frames[1:],duration=60,loop=0,disposal=2)
    assert player.feet==before[0] and actor.feet==before[1]
    assert player.shadow is before[2] and game.visitor_shadow is before[3]
    resting=Image.new('RGB',(896,290),'#243342');labels=ImageDraw.Draw(resting)
    for column,(direction,vector) in enumerate((('frente',(0,34)),('costas',(0,-34)),('esquerda',(-34,0)),('direita',(34,0)))):
        actor.direction=direction;actor.walking=True;actor.moving=True
        actor.remaining=.1;actor.velocity.update(vector)
        actor.update(.1,game.scene.collisions)
        assert not actor.walking and not actor.moving
        assert actor.image(game.visitor_assets['ricardo']) is game.visitor_assets['ricardo'].sprites[direction]
        stopped=actor.feet.copy();actor.update(.02,game.scene.collisions)
        assert actor.feet==stopped
        game.draw(screen)
        screenshot=Image.frombytes('RGB',screen.get_size(),pygame.image.tobytes(screen,'RGB'))
        x,y=map(round,actor.feet-game.scene.camera_for(player.feet))
        resting.paste(screenshot.crop((x-56,y-112,x+56,y+16)).resize((224,256),Image.Resampling.NEAREST),(column*224,25))
        labels.text((column*224+5,5),'Parou de verdade: '+direction,fill='white')
    resting.save(ROOT/'docs/ricardo_reposo_real.png')
    pygame.quit()

if __name__=='__main__':main()
