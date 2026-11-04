"""Revisão reproduzível: 1, 3 e 7 moradores, cômodos e custo por frame."""
import os
os.environ.setdefault('SDL_VIDEODRIVER','dummy');os.environ.setdefault('SDL_AUDIODRIVER','dummy')
import json
import random
from pathlib import Path
from time import perf_counter
import pygame
from casa.game import House
from casa.config import FPS
from casa.resident_routines import CAPACITY

ORDER=('ricardo','laura','antonio','gabriel','helena','daniel','marina')

def main():
    pygame.init();screen=pygame.display.set_mode((1280,720))
    out=Path('docs/rotinas_etapa3');out.mkdir(parents=True,exist_ok=True)
    g=House();g.dialog='';g.resident_manager.rng=random.Random(13)
    s=g.visitor_session;s.news.watch(s.news.current(1));s.survival.add_supplies(100,100)
    def accept(key):
        v=s.visitors[key];v.arrived=True;s.manager.seen.add(key);s._arrive(v);s.manager.current=key
        assert g.decide_visitor(v,'acolhido')
    def capture(name,room):
        g.change_room(room);g.dialog='';g.draw(screen);pygame.image.save(screen,str(out/name))
    accept('ricardo');capture('01_um_morador_sala.png','sala')
    for key in ORDER[1:3]:accept(key)
    capture('02_tres_moradores_sala.png','sala');capture('03_tres_moradores_corredor.png','corredor')
    for key in ORDER[3:]:accept(key)
    initial={key:{'room':a.room,'source_feet':list(g.scenes[a.room].source_point(a.feet))} for key,a in g.residents.items()}
    for i,room in enumerate(CAPACITY,4):capture(f'{i:02}_sete_{room}.png',room)
    capture('09_quarto_reservado.png','quarto')
    # Avança pelo calendário real, sob o contexto seguro do quarto.
    days=[]
    for day in range(2,5):
        g.change_room('quarto');assert s.days.advance()
        days.append({'day':day,'locations':g.resident_manager.locations})
        if any(a.room=='banheiro' for a in g.residents.values()):
            capture('10_rotina_banheiro.png','banheiro');break
    for i,room in enumerate(('sala','cozinha','corredor','entrada'),11):capture(f'{i:02}_novo_dia_{room}.png',room)
    # Estado de ação e integração: conversa e diário no cômodo atual do médico.
    actor=g.residents['ricardo'];g.change_room(actor.room)
    for delta in ((35,0),(-35,0),(0,28),(0,-28)):
        feet=actor.feet+pygame.Vector2(delta)
        if not g.scene.collisions.allows(feet):continue
        g.player.feet=feet
        item=g.nearest_interaction()
        if item and item.action=='resident' and item.target==actor.visitor_id:break
    g.interact();assert g.resident_ui
    g.resident_ui.open_conversation();g.draw(screen);pygame.image.save(screen,str(out/'15_conversa_no_comodo.png'))
    g.open_journal();g.draw(screen);pygame.image.save(screen,str(out/'16_diario_preservado.png'))
    g.journal_ui.close();g.resident_ui=None
    # Eliminação no cômodo atual: a ficha permanece, o ator sai imediatamente.
    v=s.visitors['ricardo'];assert g.eliminate_resident(v,'eliminado')
    assert 'ricardo' not in g.residents
    g.update((0,0),.23);g.update((0,0),.23);g.dialog=''
    g.open_journal();g.draw(screen);pygame.image.save(screen,str(out/'17_eliminado_preservado.png'));g.journal_ui.close()
    # Medida separada com sete vivos, em outra sessão de demonstração.
    bench=House();bench.dialog='';bench.resident_manager.rng=random.Random(13)
    for key in ORDER:
        v=bench.visitor_session.visitors[key];v.arrived=True;bench.visitor_session.manager.seen.add(key);bench.visitor_session.manager.current=key
        assert bench.decide_visitor(v,'acolhido')
    measured={};runs=bench.resident_manager.planning_runs;geometry=bench.resident_manager.geometry_builds
    for room in CAPACITY:
        bench.change_room(room);samples=[]
        for _ in range(30):bench.update((0,0),1/FPS);bench.draw(screen)
        for _ in range(240):
            start=perf_counter();bench.update((0,0),1/FPS);bench.draw(screen);samples.append((perf_counter()-start)*1000)
        values=sorted(samples)
        measured[room]={'mean_ms':sum(samples)/len(samples),'p95_ms':values[int(len(values)*.95)],'frames':len(samples)}
    assert bench.resident_manager.planning_runs==runs
    assert bench.resident_manager.geometry_builds==geometry
    report={'resolution':[1280,720],'configured_fps':FPS,'driver':pygame.display.get_driver(),'initial':initial,'new_days':days,'performance':measured,'planning_runs_during_frames':0,'geometry_builds_during_frames':0}
    (out/'validacao_visual_desempenho.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(measured,indent=2));pygame.quit()

if __name__=='__main__':main()
