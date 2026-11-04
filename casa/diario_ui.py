"""Fichário modal: moradores, rascunho da visita e observações exclusivamente manuais."""
import pygame
from .diario import MARKS,CONCLUSIONS,PATTERNS
from .medical_knowledge import LABELS
from . import ui_theme as ui,face_portraits,diario_paper as paper
from .diario_editor import NoteEditor

class JournalUI:
    TABS=('Personagens','Noticiários','Anotações','Linha do Tempo')
    def __init__(self,session,assets=None):
        self.session=session;self.data=session.journal;self.assets=assets or {}
        self.active=False;self.tab=self.TABS[0];self.selected=None;self.draft_id=None
        self.scroll=0;self.max_scroll=0;self.cursor=0;self.editing=False
        self.buttons={};self.note_positions=[];self.struck_names=[]
        self.font=ui.font(26);self.title=ui.font(36);self.small=ui.font(23);self.caption=ui.font(22)
        self.body=pygame.Rect(426,184,760,432)
        self.notes_area=pygame.Rect(440,280,728,316)
        self.access_rect=pygame.Rect(1198,9,56,44)
        self.editor=NoteEditor(self.font)
        self.editor_states={};self.page_scrolls={}

    def available_records(self):
        records=dict(self.data.cases)
        if self.draft_id in self.data.drafts:records[self.draft_id]=self.data.drafts[self.draft_id]
        return records

    def current_case(self):return self.available_records().get(self.selected)

    def open(self,visitor_id=None):
        if self.active:return
        self.active=True;self.draft_id=visitor_id if visitor_id in self.data.drafts else None
        if visitor_id in self.available_records():self.selected=visitor_id
        elif self.selected not in self.available_records():self.selected=next(iter(self.available_records()),None)
        self.focus(False);self.restore_position()

    def close(self):
        self.save_position();self.focus(False);self.active=False

    def focus(self,enabled):
        self.editing=bool(enabled)
        if enabled:
            pygame.key.start_text_input();pygame.key.set_text_input_rect(self.notes_area)
        else:pygame.key.stop_text_input()

    def save_position(self):
        self.page_scrolls[(self.tab,self.selected)]=self.scroll
        if self.tab=='Anotações' and self.selected:self.editor_states[self.selected]=(self.cursor,self.scroll)

    def restore_position(self):
        case=self.current_case()
        self.scroll=self.page_scrolls.get((self.tab,self.selected),0)
        if self.tab=='Anotações':self.cursor,self.scroll=self.editor_states.get(self.selected,(len(case.notes) if case else 0,self.scroll))
        self.cursor=min(self.cursor,len(case.notes)) if case else 0
        self.editor.preferred_x=None;self.buttons={}
        self.measure()

    def select(self,key):
        self.save_position();self.focus(False);self.selected=key;self.restore_position()

    def change_tab(self,tab):
        self.save_position();self.focus(False);self.tab=tab;self.restore_position()

    def wrap(self,text,width):return ui.wrapped_lines(text,width,self.font)

    def note_layout(self,text):return self.editor.positions(text,self.notes_area)

    def ensure_cursor(self):
        case=self.current_case()
        if not case:return
        _,_,y=self.note_layout(case.notes)[min(self.cursor,len(case.notes))]
        bottom=self.notes_area.bottom-28
        if y-self.scroll>bottom:self.scroll=y-bottom
        elif y-self.scroll<self.notes_area.top:self.scroll=max(0,y-self.notes_area.top)
        self.measure()

    def handle_event(self,event):
        if event.type==pygame.KEYDOWN:
            if event.key==pygame.K_ESCAPE or (event.key==pygame.K_j and not self.editing):self.close();return
        case=self.current_case()
        if event.type==pygame.MOUSEWHEEL:
            self.scroll=max(0,min(self.max_scroll,self.scroll-event.y*60));return
        if event.type==pygame.MOUSEBUTTONDOWN and event.button==1:
            # Reconstrói a geometria para não usar controles de uma página/rolagem anterior.
            self.build_buttons()
            hit=next((key for key,rect in self.buttons.items() if rect.collidepoint(event.pos)),None)
            if hit:
                kind,value=hit
                if kind=='close':self.close()
                elif kind=='tab':self.change_tab(value)
                elif kind in ('case','draft'):self.select(value)
                elif kind=='mark' and case:
                    feature,mark=value
                    if feature in self.session.medical.known:case.marks[feature]=mark
                elif kind=='conclusion' and case:case.conclusion=value
                return
            self.focus(self.tab=='Anotações' and case is not None and self.notes_area.collidepoint(event.pos))
            if self.editing:
                positions=self.note_layout(case.notes)
                point=(event.pos[0],event.pos[1]+self.scroll)
                self.cursor=min(positions,key=lambda p:(p[2]-point[1])**2+(p[1]-point[0])**2)[0]
                self.editor.preferred_x=None
            return
        if not self.editing or case is None:return
        if event.type==pygame.TEXTINPUT:
            case.notes=case.notes[:self.cursor]+event.text+case.notes[self.cursor:]
            self.cursor+=len(event.text);self.editor.preferred_x=None
        elif event.type==pygame.KEYDOWN:
            case.notes,self.cursor=self.editor.key(case.notes,self.cursor,event.key,self.notes_area)
        self.ensure_cursor()

    def draw_access(self,screen):
        rect=self.access_rect;hover=rect.collidepoint(pygame.mouse.get_pos())
        ui.panel(screen,rect,color='#423b31' if hover else ui.PANEL,alpha=248,accent=ui.PAPER)
        book=pygame.Rect(rect.x+11,rect.y+8,23,28)
        pygame.draw.rect(screen,'#b59b71',book,border_radius=2)
        pygame.draw.line(screen,'#473c2e',(book.x+5,book.y+2),(book.x+5,book.bottom-2),2)
        for y in (book.y+8,book.y+14,book.y+20):pygame.draw.line(screen,'#574935',(book.x+9,y),(book.right-3,y))
        ui.text(screen,'J',pygame.Rect(rect.right-17,rect.y+14,14,24),ui.font(21),ui.PAPER,line_height=22)
        if hover:
            ui.panel(screen,(1082,57,172,32),alpha=255)
            ui.text(screen,'Diário [J]',pygame.Rect(1094,64,150,24),ui.font(23),ui.PAPER,line_height=24)

    def register(self,kind,value,rect,clip=None):
        if getattr(self,"measuring",False):return
        rect=pygame.Rect(rect)
        if clip is not None:rect=rect.clip(clip)
        if rect.width and rect.height:self.buttons[(kind,value)]=rect

    def controls(self,screen=None):
        self.register('close','',pygame.Rect(1076,68,120,34))
        if screen:paper.tab(screen,(1076,68,120,34),'Voltar',False)
        for i,tab in enumerate(self.TABS):
            rect=pygame.Rect(414+i*194,124,186,38)
            self.register('tab',tab,rect)
            if screen:paper.tab(screen,rect,tab,self.tab==tab)
        y=190
        if self.draft_id in self.data.drafts:
            rect=pygame.Rect(78,174,268,76);self.register('draft',self.draft_id,rect)
            if screen:
                pygame.draw.rect(screen,'#decaa2' if self.selected==self.draft_id else '#c0a77d',rect,border_radius=4)
                ui.text(screen,'Rascunho da visita',pygame.Rect(90,182,244,26),ui.font(25),paper.BLUE)
                ui.text(screen,self.data.drafts[self.draft_id].name,pygame.Rect(90,213,244,30),ui.font(29),paper.INK)
            y=288
        if screen:
            ui.text(screen,'MORADORES / '+str(len(self.data.cases)),pygame.Rect(80,y-30,268,26),self.caption,paper.MUTED)
        for key,case in self.data.cases.items():
            rect=pygame.Rect(78,y,268,54);self.register('case',key,rect)
            if screen:
                selected=key==self.selected;hover=rect.collidepoint(pygame.mouse.get_pos())
                if selected or hover:pygame.draw.rect(screen,'#d9c29a' if selected else '#cfb68d',rect,border_radius=3)
                if selected:pygame.draw.line(screen,paper.BLUE,(rect.x,rect.y+4),(rect.x,rect.bottom-4),3)
                pos=(92,y+3)
                if case.situation=='eliminado':
                    struck=paper.strike(screen,case.name,ui.font(29),pos);self.struck_names.append(('sidebar',key,struck))
                else:ui.text(screen,case.name,pygame.Rect(*pos,244,29),ui.font(29),paper.INK)
                status='Eliminado · dia '+str(case.eliminated_day) if case.situation=='eliminado' else 'Acolhido · dia '+str(case.accepted_day or case.arrival)
                ui.text(screen,status,pygame.Rect(92,y+31,244,23),self.caption,paper.FADED if case.situation=='eliminado' else paper.MUTED,line_height=24)
            y+=58
        if screen and not self.data.cases:
            ui.text(screen,'As fichas permanentes são criadas ao acolher alguém.',pygame.Rect(82,y+8,260,100),self.font,paper.MUTED,line_height=28)

    def ink_choice(self,screen,kind,value,label,rect,selected,mark=None):
        self.register(kind,value,rect,self.body)
        if screen is None:return
        rect=pygame.Rect(rect)
        if selected:pygame.draw.rect(screen,'#d0c4a7',rect,border_radius=3)
        elif rect.collidepoint(pygame.mouse.get_pos()):pygame.draw.rect(screen,'#d9c79e',rect,border_radius=3)
        circle=(rect.x+13,rect.centery)
        pygame.draw.circle(screen,paper.BLUE if selected else paper.MUTED,circle,5,1)
        if selected:
            if mark=='Ausente':pygame.draw.line(screen,paper.BLUE,(circle[0]-3,circle[1]),(circle[0]+3,circle[1]),2)
            elif mark=='Não verificado':pygame.draw.circle(screen,paper.BLUE,circle,2)
            else:pygame.draw.lines(screen,paper.BLUE,False,[(circle[0]-3,circle[1]),(circle[0],circle[1]+3),(circle[0]+5,circle[1]-4)],2)
        ui.text(screen,label,pygame.Rect(rect.x+26,rect.y+8,rect.width-30,26),self.small,paper.BLUE if selected else paper.MUTED,line_height=26)

    def content(self,screen=None):
        x=self.body.x;width=self.body.width;y=self.body.y-self.scroll
        case=self.current_case()
        def paragraph(value,font=None,color=paper.INK,left=None,available=None,gap=12):
            nonlocal y
            font=font or self.font;left=x if left is None else left;available=width if available is None else available
            lines=ui.wrapped_lines(value,available,font);line=max(28,font.get_linesize()+3)
            if screen:
                ui.text(screen,value,pygame.Rect(left,y,available,len(lines)*line),font,color,line_height=line)
            y+=len(lines)*line+gap
        def heading(value):
            nonlocal y
            paragraph(value,self.title,gap=10)
            if screen:paper.rule(screen,x,y-5,width)
            y+=10
        if self.tab=='Personagens' and case:
            header_y=y
            if screen:
                portrait=pygame.Rect(x+width-152,y+5,146,164)
                face_portraits.draw(screen,self.session.visitors[self.selected].definition,portrait)
                pygame.draw.rect(screen,'#c9b181',(portrait.x-5,portrait.y-5,44,10))
                if case.situation=='eliminado':
                    tint=pygame.Surface(portrait.size,pygame.SRCALPHA);tint.fill((216,205,181,100));screen.blit(tint,portrait)
                    r=paper.strike(screen,case.name,ui.font(40),(x,y));self.struck_names.append(('sheet',self.selected,r))
                else:ui.text(screen,case.name,pygame.Rect(x,y,width-174,42),ui.font(40),paper.INK)
            y+=52
            paragraph(f'{case.age} anos · {case.profession}',available=width-174,gap=6)
            paragraph(f'Chegada à porta: dia {case.arrival}',self.small,paper.MUTED,available=width-174,gap=4)
            status=('Eliminado · dia '+str(case.eliminated_day) if case.situation=='eliminado' else
                    'Acolhido · dia '+str(case.accepted_day) if case.accepted_day else 'Rascunho da visita · decisão pendente')
            paragraph(status,self.small,paper.FADED if case.situation=='eliminado' else paper.BLUE,available=width-174)
            y=max(y,header_y+190)
            heading('Características observáveis')
            known=[key for key in LABELS if key in self.session.medical.known]
            if not known:
                paragraph('Nenhuma característica física foi divulgada oficialmente. Acompanhe os noticiários para conhecer os primeiros sinais da epidemia.',color=paper.MUTED)
            visitor=self.session.visitors[self.selected]
            for feature in known:
                if screen:
                    ui.text(screen,LABELS[feature],pygame.Rect(x,y,354,30),self.font,paper.INK)
                    day=case.examined_days.get(feature)
                    examined=feature in visitor.examined
                    status=f'Exame realizado · dia {day}' if day is not None else 'Exame realizado' if examined else 'Disponível · ainda não examinado'
                    ui.text(screen,status,pygame.Rect(x,y+29,354,26),self.caption,paper.MUTED,line_height=26)
                for i,(mark,w) in enumerate(zip(MARKS,(158,112,106))):
                    left=x+width-388+(0 if i==0 else 164 if i==1 else 282)
                    self.ink_choice(screen,'mark',(feature,mark),mark,(left,y+5,w,40),case.marks[feature]==mark,mark)
                if screen:paper.rule(screen,x,y+66,width)
                y+=80
            y+=8;heading('Minha conclusão')
            for conclusion in CONCLUSIONS:
                self.ink_choice(screen,'conclusion',conclusion,conclusion,(x,y,width,40),case.conclusion==conclusion)
                y+=46
            y+=20;heading('Conversas registradas')
            if not case.conversations:paragraph('Nenhuma pergunta realizada.',color=paper.MUTED)
            for day,question,answer in case.conversations:
                paragraph(f'Dia {day} — Você: {question}',color=paper.BLUE,gap=6)
                paragraph(answer);y+=12
        elif self.tab=='Noticiários':
            watched=sorted((b for b in self.session.news.bulletins if b.read),key=lambda b:b.day)
            if not watched:heading('Arquivo de notícias');paragraph('Nenhum noticiário assistido.',color=paper.MUTED)
            for b in watched:
                parts=[(f'BOLETIM / DIA {b.day:02}',self.caption,paper.MUTED),(b.headline,self.title,paper.INK)]
                parts += [(text,self.font,paper.INK) for text in b.paragraphs]
                if b.id in PATTERNS:
                    title,text=PATTERNS[b.id];parts += [('PADRÃO DIVULGADO · '+title,self.font,paper.BLUE),(text,self.font,paper.BLUE)]
                card_height=36+sum(len(ui.wrapped_lines(text,width-40,font))*max(28,font.get_linesize()+3)+12 for text,font,_ in parts)
                if screen:
                    pygame.draw.rect(screen,'#e9debf',(x,y,width,card_height))
                    pygame.draw.line(screen,'#9e8e70',(x,y+card_height),(x+width,y+card_height))
                    pygame.draw.rect(screen,'#c2ad82',(x+20,y-4,68,10))
                y+=20
                for text,font,color in parts:paragraph(text,font,color,left=x+20,available=width-40)
                y+=40
        elif self.tab=='Linha do Tempo':
            heading('O que aconteceu até aqui')
            if not self.data.timeline:paragraph('Nenhum acontecimento registrado.',color=paper.MUTED)
            ordered=sorted(enumerate(self.data.timeline),key=lambda entry:(entry[1][0],entry[0]))
            for _,(day,value) in ordered:
                top=y
                if screen:
                    pygame.draw.line(screen,'#a18d6b',(x+15,y),(x+15,y+48),2)
                    pygame.draw.circle(screen,paper.BLUE,(x+15,y+12),4)
                    ui.text(screen,f'DIA {day:02}',pygame.Rect(x+32,y,76,28),self.caption,paper.MUTED)
                paragraph(value,left=x+122,available=width-122,gap=22)
                if screen:pygame.draw.line(screen,'#a18d6b',(x+15,top+12),(x+15,y),1)
        elif self.tab=='Anotações' and case:
            # O título e a borda do editor ficam fixos; somente o texto é rolado.
            if screen:
                ui.text(screen,'Anotações / '+case.name,pygame.Rect(x,self.body.y,width,38),self.title,paper.INK)
                ui.text(screen,'Clique no papel para escrever. Suas hipóteses ficam registradas aqui.',pygame.Rect(x,self.body.y+46,width,56),self.small,paper.MUTED)
                pygame.draw.rect(screen,'#d2bd92',self.notes_area.inflate(20,18),1,border_radius=3)
                old=screen.get_clip();screen.set_clip(old.clip(self.notes_area))
                for line in range(self.notes_area.y+26,self.notes_area.bottom,30):paper.rule(screen,self.notes_area.x,line,self.notes_area.width)
                positions=self.note_layout(case.notes)
                self.note_positions=[(i,px,py-self.scroll) for i,px,py in positions]
                for i,px,py in positions[:-1]:
                    if self.notes_area.top-30<=py-self.scroll<=self.notes_area.bottom and case.notes[i]!='\n':
                        screen.blit(self.font.render(case.notes[i],True,paper.BLUE),(px,py-self.scroll))
                if not case.notes and not self.editing:ui.text(screen,'Observações, suspeitas, contradições…',self.notes_area,self.font,paper.FADED)
                if self.editing:
                    _,px,py=positions[min(self.cursor,len(case.notes))]
                    pygame.draw.line(screen,paper.BLUE,(px,py-self.scroll),(px,py-self.scroll+24),2)
                screen.set_clip(old)
            return max(0,self.note_layout(case.notes)[-1][2]-self.notes_area.bottom+32)
        else:
            heading('Um registro para cada história')
            paragraph('As fichas são abertas quando você acolhe alguém. Selecione um morador à esquerda para consultar suas observações.',color=paper.MUTED)
        return max(0,y+self.scroll-self.body.bottom+12)

    def measure(self):
        self.measuring=True
        try:self.max_scroll=self.content(None)
        finally:self.measuring=False
        self.scroll=max(0,min(self.scroll,self.max_scroll))

    def build_buttons(self):
        self.buttons={};self.controls();self.measure();self.content()

    def draw(self,screen):
        self.struck_names=[];paper.background(screen,self.session.day)
        self.buttons={};self.controls(screen);self.measure()
        old=screen.get_clip();screen.set_clip(old.clip(self.body))
        self.content(screen);screen.set_clip(old)
        if self.max_scroll:
            area=self.notes_area if self.tab=='Anotações' else self.body
            track=pygame.Rect(1203,area.y,4,area.height)
            pygame.draw.rect(screen,'#c0aa80',track)
            height=max(32,round(area.height*area.height/(area.height+self.max_scroll)))
            thumb=pygame.Rect(track.x,track.y+round((track.height-height)*self.scroll/self.max_scroll),4,height)
            pygame.draw.rect(screen,paper.MUTED,thumb)
