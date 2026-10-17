"""Conferencia de todos os novos assets, ciclos e repouso no render real."""
import os
os.environ.setdefault('SDL_VIDEODRIVER','dummy')
from PIL import Image,ImageDraw
import pygame
import json
from casa.config import ROOT
from casa.game import House


def main():
    pygame.init();screen=pygame.display.set_mode((1280,720))
    game=House();game.handle_event(pygame.event.Event(pygame.KEYDOWN,key=pygame.K_RETURN))
    game.news.watch(game.news.current(1));game.change_room('sala')
    game.decide_visitor(game.visitor_session.visitors['ricardo'],'acolhido')
    assets=game.visitor_assets['ricardo'];actor=game.residents['ricardo']
    sheet=Image.new('RGB',(800,1340),'#243342');draw=ImageDraw.Draw(sheet)
    snapshots=Image.new('RGB',(896,1080),'#243342');sd=ImageDraw.Draw(snapshots)
    rest=Image.new('RGB',(896,290),'#243342');rd=ImageDraw.Draw(rest)
    def tile(surface):
        original=Image.frombytes('RGBA',(64,96),pygame.image.tobytes(surface,'RGBA'))
        bg=Image.new('RGB',(192,288));d=ImageDraw.Draw(bg)
        for y in range(0,288,12):
            for x in range(0,192,12):d.rectangle((x,y,x+11,y+11),fill='#eee9df' if (x//12+y//12)%2 else '#a5aab9')
        scaled=original.resize((192,288),Image.Resampling.NEAREST);bg.paste(scaled,(0,0),scaled)
        ImageDraw.Draw(bg).line((0,282,191,282),fill='red')
        return bg
    gif=[]
    for row,(direction,vector) in enumerate((('frente',(0,34)),('costas',(0,-34)),('direita',(34,0)),('esquerda',(-34,0)))):
        actor.direction=direction;actor.walking=actor.moving=True
        for index,frame in enumerate(assets.cycles[direction]):
            sheet.paste(tile(frame),(index*200,row*330+20))
            draw.text((index*200+5,row*330+315),direction+' '+('idle' if index%2==0 else f'passo {index//2+1}'),fill='white')
            actor.animation_elapsed=index*actor.frame_seconds+.001
            game.draw(screen)
            shot=Image.frombytes('RGB',(1280,720),pygame.image.tobytes(screen,'RGB'))
            x,y=map(round,actor.feet-game.scene.camera_for(game.player.feet))
            snapshots.paste(shot.crop((x-56,y-112,x+56,y+16)).resize((224,256),Image.Resampling.NEAREST),(index*224,row*270+12))
            sd.text((index*224+4,row*270+12),direction+f' fase {index}',fill='white')
        for i in range(24):
            actor.animation_elapsed=i*.06
            game.draw(screen)
            gif.append(Image.frombytes('RGB',(1280,720),pygame.image.tobytes(screen,'RGB')).resize((896,504),Image.Resampling.NEAREST))
        actor.velocity.update(vector);actor.remaining=.07
        actor.update(.07,game.scene.collisions)
        assert actor.animation_state=='idle' and actor.image(assets) is assets.sprites[direction]
        stopped=actor.feet.copy();actor.update(.02,game.scene.collisions)
        assert actor.feet==stopped
        game.draw(screen);shot=Image.frombytes('RGB',(1280,720),pygame.image.tobytes(screen,'RGB'))
        x,y=map(round,actor.feet-game.scene.camera_for(game.player.feet))
        rest.paste(shot.crop((x-56,y-112,x+56,y+16)).resize((224,256),Image.Resampling.NEAREST),(row*224,25))
        rd.text((row*224+5,5),'Repouso real: '+direction,fill='white')
    sheet.save(ROOT/'docs/ricardo_individual_ciclos.png')
    snapshots.save(ROOT/'docs/ricardo_individual_render.png')
    rest.save(ROOT/'docs/ricardo_individual_reposo.png')
    gif[0].save(ROOT/'docs/ricardo_individual_jogo.gif',save_all=True,append_images=gif[1:],duration=60,loop=0,disposal=2)
    # Agora usa a escolha automatica e House.update, sem impor direcao ou fase.
    actor.rng.seed(7);actor.rest();actor.remaining=.02
    automatic=[];trace=[];previous=None
    contact=Image.new('RGB',(896,580),'#243342');cd=ImageDraw.Draw(contact)
    for tick in range(720):
        game.update((0,0),1/60)
        if actor.animation_state=='idle':assert actor.image(assets) is assets.sprites[actor.direction]
        assert game.scene.collisions.allows(actor.feet)
        if tick%6==0:
            game.draw(screen)
            shot=Image.frombytes('RGB',(1280,720),pygame.image.tobytes(screen,'RGB'))
            automatic.append(shot.resize((640,360),Image.Resampling.NEAREST))
            state=(actor.animation_state,actor.direction)
            if state!=previous:
                record=dict(t=round(tick/60,2),state=state[0],direction=state[1],feet=list(actor.feet))
                trace.append(record);previous=state
                if len(trace)<=8:
                    x,y=map(round,actor.feet-game.scene.camera_for(game.player.feet))
                    col=(len(trace)-1)%4;row=(len(trace)-1)//4
                    contact.paste(shot.crop((x-56,y-112,x+56,y+16)).resize((224,256),Image.Resampling.NEAREST),(col*224,row*290+25))
                    cd.text((col*224+4,row*290+5),f'{record["t"]}s {state[0]} {state[1]}',fill='white')
    assert {'idle','walk'}<={r['state'] for r in trace}
    automatic[0].save(ROOT/'docs/ricardo_individual_automatico.gif',save_all=True,append_images=automatic[1:],duration=100,loop=0,disposal=2)
    contact.save(ROOT/'docs/ricardo_individual_automatico.png')
    (ROOT/'docs/ricardo_individual_automatico.json').write_text(json.dumps(trace,indent=2),encoding='utf-8')
    pygame.quit()

if __name__=='__main__':main()
