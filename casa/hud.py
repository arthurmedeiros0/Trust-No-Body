"""Cabeçalho de exploração: apenas leitura e apresentação do estado atual."""
import pygame
from . import ui_theme as ui


def fitted_text(screen, value, rect, size, color=ui.TEXT):
    """Mantém textos extensos dentro da coluna sem invadir os vizinhos."""
    rect=pygame.Rect(rect)
    face=ui.font(size)
    while face.size(value)[0]>rect.width and size>14:
        size-=1;face=ui.font(size)
    lines=ui.wrapped_lines(value,rect.width,face)
    height=max(face.get_linesize(),rect.height//max(1,len(lines)))
    ui.text(screen,value,rect,face,color,line_height=height)


def layout(width, journal_rect):
    """Reserva o alvo real do diário e distribui o espaço restante."""
    right=min(width-20,journal_rect.left-12)
    left_width=min(400,round(right*.35))
    location=pygame.Rect(20,9,left_width,44)
    start=location.right+12
    status=pygame.Rect(start,9,right-start,44)
    weights=(1.15,1.0,1.0,1.0)
    edges=[status.x]
    for weight in weights:
        edges.append(edges[-1]+status.width*weight/sum(weights))
    cells=[pygame.Rect(round(edges[i]),9,round(edges[i+1])-round(edges[i]),44) for i in range(4)]
    return location,status,cells


def status_values(house):
    state=house.visitor_session.survival
    needs=state.predicted_needs(house.days.day,house.visitor_session.living_ids)
    return (("DIA",f'{house.days.day:02} / {house.days.LIMIT}'),
            ("SANIDADE",f'{state.sanity} / 8'),
            ("FOME",f'{needs.hunger} / 3 dias'),
            ("SEDE",f'{needs.thirst} / 2 dias'))


def draw(screen,house):
    location,status,cells=layout(screen.get_width(),house.journal_ui.access_rect)
    ui.panel(screen,location,alpha=248,accent=ui.PAPER)
    ui.panel(screen,status,alpha=248)
    period=house.period.capitalize()
    fitted_text(screen,f'{house.room.capitalize()}  /  {period}',
                 (location.x+14,13,location.width-28,20),24,ui.PAPER)
    objective=house.visitor_session.intro.objective
    detail='Objetivo: '+objective if objective else 'TRUST NO BODY'
    fitted_text(screen,detail,(location.x+14,35,location.width-28,16),18,ui.MUTED)
    for i,(cell,(label,value)) in enumerate(zip(cells,status_values(house))):
        if i:pygame.draw.line(screen,ui.BORDER,(cell.x,19),(cell.x,43))
        fitted_text(screen,label,(cell.x+14,13,cell.width-28,14),16,ui.MUTED)
        fitted_text(screen,value,(cell.x+14,29,cell.width-28,23),27 if i==0 else 23,ui.PAPER if i==0 else ui.TEXT)
