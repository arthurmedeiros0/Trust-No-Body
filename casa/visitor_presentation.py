"""Geometria e desenho das interfaces de visitantes, separados do fluxo de jogo."""
import pygame
from . import ui_theme as ui
from . import face_portraits
from .visitor_assets import fit

GAP=ui.SPACE
TEXT_WIDTH=908
MAX_SPEECH_HEIGHT=156

def conversation_geometry(view):
    width=TEXT_WIDTH
    question_height=0
    if view.page=='answer':
        question=view.dialogue.data['questions'][view.dialogue.progress.question]['question']
        question_height=len(ui.wrapped_lines('Você: '+question,width,view.font))*26+16
    if view.page=='talk':
        content=sum(max(48,len(ui.wrapped_lines(view.dialogue.data['questions'][i]['question'],834,view.small))*view.small.get_linesize()+16)+16 for i in view.dialogue.pending())+34
    else:content=min(MAX_SPEECH_HEIGHT,max(26,len(ui.wrapped_lines(view.speech(),width,view.font))*26))+question_height
    height=max(262,104+content+80)
    box=pygame.Rect(80,704-height,1120,height)
    return box,pygame.Rect(260,box.y+104+question_height,width,max(26,content-question_height))

def speech_rect(view):
    if view.page in ('intro','answer'):return conversation_geometry(view)[1]
    if view.page=='confirm':return pygame.Rect(350,292,580,104)
    lines=len(ui.wrapped_lines(view.speech(),1064,view.font))
    height=min(MAX_SPEECH_HEIGHT,max(26,lines*26))
    return pygame.Rect(104,570-height,1064,height)

def pagination(view):
    if view.page not in ('root','intro','answer','confirm'):return {}
    pages=view.text_pages(view.speech(),view.speech_rect())
    view.text_page=max(0,min(view.text_page,len(pages)-1))
    if len(pages)==1:return {}
    x,y=(350,414) if view.page=='confirm' else (680,584) if view.page=='root' else (260,650)
    result={}
    if view.text_page>0:result['text_prev']=(pygame.Rect(x,y,110,30),'Anterior')
    if view.text_page<len(pages)-1:result['text_next']=(pygame.Rect(x+126,y,110,30),'Próxima')
    return result

def layout(view):
    if view.page=='image' and view.feature not in view.knowledge.known:view.page='root';view.feature=None
    if view.page=='confirm' and view.resident and view.decision!='eliminado':view.page='root'
    if view.page=='root':
        result={'talk':(pygame.Rect(104,652,172,40),'Conversar')}
        if view.knowledge.known:result['investigate']=(pygame.Rect(292,652,172,40),'Investigar')
        if not view.resident:
            result['accept']=(pygame.Rect(650,652,160,40),'Aceitar')
            result['reject']=(pygame.Rect(826,652,160,40),'Rejeitar')
        elif view.session is not None and view.visitor.alive and view.visitor.state=='acolhido':
            result['eliminate']=(pygame.Rect(826,652,160,40),'Eliminar')
        result['back']=(pygame.Rect(1002,652,174,40),'Voltar')
        return {**result,**pagination(view)}
    if view.page=='investigate':
        features=[(key,item) for key,item in view.visitor.definition['investigation'].items() if key in view.knowledge.known]
        top=inspection_rect(view).top+112
        return {**{key:(pygame.Rect(354,top+i*48,572,40),item['label']+(' [visto]' if key in view.visitor.examined else '')) for i,(key,item) in enumerate(features)},
                'back':(pygame.Rect(726,top+len(features)*48+12,200,38),'Voltar')}
    if view.page=='talk':
        box,_=conversation_geometry(view);top=box.y+138;result={}
        for i in view.dialogue.pending():
            label=view.dialogue.data['questions'][i]['question']
            height=max(48,len(ui.wrapped_lines(label,834,view.small))*view.small.get_linesize()+16)
            result[str(i)]=(pygame.Rect(290,top,878,height),label);top+=height+16
        result['back']=(pygame.Rect(992,650,176,38),'Voltar')
        return result
    if view.page in ('intro','answer'):
        return {'continue':(pygame.Rect(766,650,208,38),'Continuar'),
                'back':(pygame.Rect(992,650,176,38),'Voltar'),**pagination(view)}
    if view.page=='confirm':
        return {'confirm':(pygame.Rect(350,458,286,42),'Confirmar eliminação' if view.decision=='eliminado' else 'Confirmar'),
                'back':(pygame.Rect(652,458,278,42),'Cancelar'),**pagination(view)}
    return {'back':(pygame.Rect(974,638,202,42),'Voltar')}

def inspection_rect(view):
    count=sum(key in view.knowledge.known for key in view.visitor.definition['investigation'])
    height=190+count*48
    return pygame.Rect(322,(720-height)//2,636,height)

def identity(view,screen,x,y):
    d=view.visitor.definition
    ui.text(screen,d['name'],pygame.Rect(x,y,650,30),ui.font(32),ui.PAPER)
    detail=' · '.join(str(v) for v in (str(d['age'])+' anos' if d.get('age') is not None else '',d.get('profession','')) if v)
    ui.text(screen,detail,pygame.Rect(x,y+31,800,24),view.small,ui.MUTED,line_height=22)

def draw_speech(view,screen):
    rect=view.speech_rect()
    if view.page=='root':ui.panel(screen,rect.inflate(24,16))
    pages=view.text(screen,view.speech(),rect,view.text_page)
    if pages>1:
        if view.page=='confirm':point=(900,423)
        elif view.page=='root':point=(1040,586)
        else:point=(555,659)
        ui.text(screen,f'{view.text_page+1:02} / {pages:02}',pygame.Rect(*point,100,24),view.small,ui.MUTED,line_height=22)

def draw(view,screen):
    buttons=layout(view)
    # Oculta a legenda de movimento sob a interface modal.
    screen.fill(ui.INK,(0,686,1280,34))
    if view.resident and view.assets is not None and view.page in ('intro','talk','answer'):
        portrait=view.assets.portrait
        screen.blit(portrait,portrait.get_rect(midbottom=view.visitor.definition['portrait_anchor']))
    if view.page in ('root','intro','talk','answer'):
        # Moradores permanecem no cenário; a porta já desenha o visitante em Peephole.
        if view.page=='root':
            ui.panel(screen,(80,582,1120,122),alpha=228)
            identity(view,screen,104,590)
            if view.response:draw_speech(view,screen)
        else:
            box,body=conversation_geometry(view)
            ui.panel(screen,box,alpha=232,accent=ui.PAPER)
            face_portraits.draw(screen,view.visitor.definition,pygame.Rect(104,box.y+24,124,146))
            identity(view,screen,260,box.y+20)
            if view.page=='talk':
                prompt='O que deseja perguntar?' if view.dialogue.pending() else 'Conversa concluída. Todas as perguntas foram realizadas.'
                ui.text(screen,prompt,pygame.Rect(290,box.y+100,878,26),view.small,ui.MUTED,line_height=22)
            else:
                if view.page=='answer':
                    question=view.dialogue.data['questions'][view.dialogue.progress.question]['question']
                    ui.text(screen,'Você: '+question,pygame.Rect(260,box.y+104,908,body.y-box.y-120),view.font,ui.PAPER)
                draw_speech(view,screen)
    elif view.page=='investigate':
        ui.shade(screen,160);box=inspection_rect(view);ui.panel(screen,box,accent=ui.PAPER)
        ui.text(screen,'INSPEÇÃO — '+view.visitor.definition['name'].upper(),pygame.Rect(box.x+32,box.y+23,572,34),ui.font(32),ui.PAPER)
        ui.text(screen,'Escolha uma característica para examinar.',pygame.Rect(box.x+32,box.y+67,572,26),view.font,ui.MUTED)
    elif view.page=='image':
        ui.shade(screen,220);ui.panel(screen,(80,60,1120,640),alpha=255)
        item=view.visitor.definition['investigation'][view.feature]
        ui.text(screen,'INSPEÇÃO / '+view.visitor.definition['name'].upper(),pygame.Rect(104,78,1060,28),view.small,ui.MUTED)
        ui.text(screen,item['label'],pygame.Rect(104,112,1060,36),ui.font(32),ui.PAPER)
        area=pygame.Rect(104,164,1072,444)
        pygame.draw.rect(screen,'#0a1118',area)
        image=fit(view.examination_image(),area.inflate(-16,-16).size)
        screen.blit(image,image.get_rect(center=area.center))
        for x,y,dx,dy in ((area.left,area.top,1,1),(area.right,area.top,-1,1),(area.left,area.bottom,1,-1),(area.right,area.bottom,-1,-1)):
            pygame.draw.lines(screen,ui.MUTED,False,[(x,y+dy*17),(x,y),(x+dx*17,y)],2)
        status='Exame visual realizado. Interprete o que observou.'
        ui.text(screen,status,pygame.Rect(104,646,820,28),view.small,ui.MUTED)
    elif view.page=='confirm':
        ui.shade(screen,210)
        danger=view.decision=='eliminado'
        ui.panel(screen,(310,214,660,310),accent=ui.RED_HOVER if danger else ui.PAPER)
        ui.text(screen,'DECISÃO IRREVERSÍVEL' if danger else 'CONFIRMAR DECISÃO',pygame.Rect(350,240,580,34),ui.font(32),'#e3a5a2' if danger else ui.PAPER)
        draw_speech(view,screen)
    for key,(rect,label) in buttons.items():
        danger=key=='eliminate' or (key=='confirm' and view.decision=='eliminado')
        choice=view.page=='talk' and key.isdigit()
        if view.page=='investigate' and key!='back':
            seen=key in view.visitor.examined
            ui.button(screen,rect,'',selected=seen,pressed=key==view.pressed_key and pygame.time.get_ticks()<view.pressed_until)
            pygame.draw.circle(screen,ui.PAPER if seen else ui.MUTED,(rect.x+18,rect.centery),4,0 if seen else 1)
            ui.text(screen,view.visitor.definition['investigation'][key]['label'],pygame.Rect(rect.x+36,rect.y+9,370,28),view.font)
            ui.text(screen,'OBSERVADO' if seen else 'PENDENTE',pygame.Rect(rect.right-124,rect.y+13,112,22),ui.font(18),ui.PAPER if seen else ui.MUTED,line_height=20)
        else:
            ui.button(screen,rect,label,danger=danger,choice=choice,pressed=key==view.pressed_key and pygame.time.get_ticks()<view.pressed_until,typeface=view.small)
