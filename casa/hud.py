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


def objective_size(width, objective):
    """Altura suficiente para o texto real, sem aumentar a barra de status."""
    text_width=width-28
    action_line=max(17,ui.font(17).get_linesize())
    hint_line=max(15,ui.font(14).get_linesize())
    action_height=len(ui.wrapped_lines(objective.action,text_width,ui.font(17)))*action_line
    hint_y=34+action_height+4
    hint_height=(len(ui.wrapped_lines(objective.hint,text_width,ui.font(14)))*hint_line
                 if objective.hint else 0)
    height=(hint_y+hint_height+10) if objective.hint else (34+action_height+10)
    return height,action_height,hint_y,hint_height


def layout(width, journal_rect, objective=None):
    """Reserva o alvo real do diário e distribui o espaço restante."""
    right=min(width-20,journal_rect.left-12)
    left_width=min(400,round(right*.35))
    height=objective_size(left_width,objective)[0] if objective else 64
    location=pygame.Rect(20,9,left_width,height)
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
    objective=house.objectives.current()
    location,status,cells=layout(screen.get_width(),house.journal_ui.access_rect,objective)
    _,action_height,hint_y,hint_height=objective_size(location.width,objective)
    ui.panel(screen,location,alpha=248,accent=ui.PAPER)
    ui.panel(screen,status,alpha=248)
    period=house.period.capitalize()
    fitted_text(screen,f'{house.room.capitalize()}  /  {period}',
                 (location.x+14,13,location.width-124,20),24,ui.PAPER)
    fitted_text(screen,'OBJETIVO',(location.right-108,15,96,18),16,ui.MUTED)
    ui.text(screen,objective.action,(location.x+14,34,location.width-28,action_height),ui.font(17),ui.TEXT,line_height=max(17,ui.font(17).get_linesize()))
    if objective.hint:
        ui.text(screen,objective.hint,(location.x+14,hint_y,location.width-28,hint_height),ui.font(14),ui.MUTED,line_height=max(15,ui.font(14).get_linesize()))
    for i,(cell,(label,value)) in enumerate(zip(cells,status_values(house))):
        if i:pygame.draw.line(screen,ui.BORDER,(cell.x,19),(cell.x,43))
        fitted_text(screen,label,(cell.x+14,13,cell.width-28,14),16,ui.MUTED)
        fitted_text(screen,value,(cell.x+14,29,cell.width-28,23),27 if i==0 else 23,ui.PAPER if i==0 else ui.TEXT)
