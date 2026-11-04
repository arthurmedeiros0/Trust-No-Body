"""Caderno modal desenhado com Pygame; entradas manuais independentes dos exames."""
import pygame
from .diario import MARKS, CONCLUSIONS, PATTERNS
from .medical_knowledge import LABELS

class JournalUI:
    TABS=('Personagens','Noticiários','Anotações','Linha do Tempo')
    def __init__(self,session,assets=None):
        self.session=session
        self.data=session.journal
        self.assets=assets or {}
        self.active=False
        self.tab=self.TABS[0]
        self.selected=None
        self.scroll=0
        self.cursor=0
        self.editing=False
        self.buttons={}
        self.font=pygame.font.Font(None,25)
        self.title=pygame.font.Font(None,36)
        self.small=pygame.font.Font(None,22)
        self.caption=pygame.font.Font(None,17)
        self.body=pygame.Rect(405,173,765,450)
        self.max_scroll=0
        self.note_positions=[]

    def open(self):
        self.active=True
        self.scroll=0
        if self.selected not in self.data.cases:self.selected=next(iter(self.data.cases),None)

    def focus(self,enabled):
        self.editing=enabled
        if enabled:pygame.key.start_text_input()
        else:pygame.key.stop_text_input()

    def wrap(self,text,width):
        # Quebra também palavras compridas e conserva linhas vazias.
        lines=[]
        for paragraph in text.split('\n'):
            line=''
            for char in paragraph:
                if self.font.size(line+char)[0]>width:
                    split=line.rfind(' ')
                    if split>0:
                        lines.append(line[:split]);line=line[split+1:]
                    else:lines.append(line);line=''
                line+=char
            lines.append(line)
        return lines

    def handle_event(self,event):
        if event.type==pygame.KEYDOWN and event.key==pygame.K_ESCAPE:
            self.active=False;self.focus(False);return
        case=self.data.cases.get(self.selected)
        if event.type==pygame.MOUSEWHEEL:
            self.scroll=max(0,min(self.max_scroll,self.scroll-event.y*54));return
        if event.type==pygame.MOUSEBUTTONDOWN and event.button==1:
            for key,rect in self.buttons.items():
                if not rect.collidepoint(event.pos):continue
                kind,value=key
                if kind=='close':self.active=False;self.focus(False)
                elif kind=='tab':self.tab=value;self.scroll=0;self.focus(False)
                elif kind=='case':
                    self.selected=value;self.scroll=0;self.focus(False)
                    self.cursor=len(self.data.cases[value].notes)
                elif kind=='mark':
                    case.marks[value]=MARKS[(MARKS.index(case.marks[value])+1)%len(MARKS)]
                elif kind=='conclusion':case.conclusion=CONCLUSIONS[(CONCLUSIONS.index(case.conclusion)+1)%len(CONCLUSIONS)]
                return
            self.focus(self.tab=='Anotações' and case is not None and self.body.collidepoint(event.pos))
            if self.editing:
                self.cursor=min(self.cursor,len(case.notes))
                if self.note_positions:
                    self.cursor=min(self.note_positions,key=lambda p:(p[2]-event.pos[1])**2+(p[1]-event.pos[0])**2)[0]
            return
        if not self.editing or not case:return
        text=case.notes
        if event.type==pygame.TEXTINPUT:
            case.notes=text[:self.cursor]+event.text+text[self.cursor:];self.cursor+=len(event.text)
        elif event.type==pygame.KEYDOWN:
            if event.key==pygame.K_BACKSPACE and self.cursor:
                case.notes=text[:self.cursor-1]+text[self.cursor:];self.cursor-=1
            elif event.key==pygame.K_DELETE:case.notes=text[:self.cursor]+text[self.cursor+1:]
            elif event.key==pygame.K_LEFT:self.cursor=max(0,self.cursor-1)
            elif event.key==pygame.K_RIGHT:self.cursor=min(len(text),self.cursor+1)
            elif event.key==pygame.K_HOME:self.cursor=text.rfind('\n',0,self.cursor)+1
            elif event.key==pygame.K_END:
                end=text.find('\n',self.cursor);self.cursor=len(text) if end<0 else end
            elif event.key==pygame.K_RETURN:
                case.notes=text[:self.cursor]+'\n'+text[self.cursor:];self.cursor+=1
        # Ao digitar, mantém o cursor visível, inclusive em textos extensos.
        prefix=case.notes[:self.cursor]
        row=self.note_layout(prefix)[-1][2]-self.body.y
        if row-self.scroll>self.body.height-30:self.scroll=row-self.body.height+30
        elif row<self.scroll:self.scroll=max(0,row)

    def note_layout(self,text):
        positions=[];x=self.body.x;y=self.body.y
        for i,char in enumerate(text):
            width=self.font.size(char)[0]
            if char!='\n' and x+width>self.body.right-16:x=self.body.x;y+=28
            positions.append((i,x,y))
            if char=='\n':x=self.body.x;y+=28
            else:x+=width
        positions.append((len(text),x,y))
        return positions

    def draw(self,screen):
        shade=pygame.Surface(screen.get_size(),pygame.SRCALPHA);shade.fill((6,5,4,220));screen.blit(shade,(0,0))
        pygame.draw.rect(screen,'#38271f',(64,43,1154,635),border_radius=12)
        pygame.draw.rect(screen,'#c5ac7c',(77,54,1128,610),border_radius=5)
        pygame.draw.rect(screen,'#ddcba2',(88,63,1098,588))
        for y in range(186,633,28):pygame.draw.line(screen,'#cbb991',(400,y),(1175,y))
        pygame.draw.line(screen,'#907957',(380,74),(380,639),3)
        pygame.draw.line(screen,'#b09a73',(388,74),(388,639),2)
        screen.blit(self.title.render('Diário de investigação',True,'#3c3026'),(107,77))
        self.buttons={}
        def button(kind,value,label,rect,selected=False):
            rect=pygame.Rect(rect);self.buttons[(kind,value)]=rect
            pygame.draw.rect(screen,'#bda477' if selected else '#cfba90',rect,border_radius=3)
            pygame.draw.line(screen,'#796246',rect.bottomleft,rect.bottomright)
            old=screen.get_clip();screen.set_clip(old.clip(rect.inflate(-8,0)))
            screen.blit(self.small.render(label,True,'#342b23'),(rect.x+8,rect.y+8));screen.set_clip(old)
        button('close','', 'Voltar [ESC]',(1050,76,126,32))
        for i,tab in enumerate(self.TABS):button('tab',tab,tab,(405+i*192,125,184,34),self.tab==tab)
        for i,(key,case) in enumerate(self.data.cases.items()):
            y=150+i*69
            button('case',key,case.name,(105,y,255,25),key==self.selected)
            details=(f'{case.age} anos · {case.profession}',
                     f'Dia {case.arrival} · {case.situation}',case.conclusion)
            for n,text in enumerate(details):
                clip=screen.get_clip();screen.set_clip(pygame.Rect(105,y+25,255,44))
                screen.blit(self.caption.render(text,True,'#5c4935'),(113,y+25+n*14));screen.set_clip(clip)
        if not self.data.cases:screen.blit(self.small.render('Nenhum visitante encontrado.',True,'#4a3a2b'),(105,160))
        screen.blit(self.small.render('Roda do mouse: rolar a página',True,'#594631'),(409,630))
        old=screen.get_clip();screen.set_clip(old.clip(self.body))
        y=self.body.y-self.scroll
        def paragraph(text,title=False):
            nonlocal y
            font=self.title if title else self.font
            for line in self.wrap(text,self.body.width-20):
                screen.blit(font.render(line,True,'#3c3026'),(self.body.x,y));y+=32 if title else 28
            y+=12
        case=self.data.cases.get(self.selected)
        if self.tab=='Personagens' and case:
            paragraph(case.name,True)
            paragraph(f'{case.age} anos | {case.profession}\nChegada: dia {case.arrival} | Situação: {case.situation}')
            asset=self.assets.get(self.selected)
            if asset:
                portrait=pygame.transform.smoothscale(asset.portrait,(50,65))
                screen.blit(portrait,(1110,y-110))
            paragraph('Sintomas — clique na marcação para alterar')
            for feature,label in LABELS.items():
                screen.blit(self.font.render(label,True,'#3c3026'),(self.body.x,y+7))
                rect=pygame.Rect(925,y,235,32)
                if self.body.contains(rect):button('mark',feature,case.marks[feature],rect)
                y+=40
            y+=12;paragraph('Minha conclusão')
            rect=pygame.Rect(self.body.x,y,745,34)
            if self.body.contains(rect):button('conclusion','',case.conclusion,rect)
            y+=55;paragraph('Conversas registradas',True)
            if not case.conversations:paragraph('Nenhuma pergunta registrada.')
            for day,question,answer in case.conversations:
                paragraph(f'Dia {day} — Você: {question}');paragraph(answer)
        elif self.tab=='Noticiários':
            watched=[b for b in self.session.news.bulletins if b.read]
            if not watched:paragraph('Nenhum noticiário assistido.')
            for bulletin in sorted(watched,key=lambda b:b.day):
                paragraph(f'Dia {bulletin.day} — {bulletin.headline}')
                for text in bulletin.paragraphs:paragraph(text)
                if bulletin.id in PATTERNS:
                    title,text=PATTERNS[bulletin.id];paragraph(title);paragraph(text)
                y+=20
        elif self.tab=='Linha do Tempo':
            if not self.data.timeline:paragraph('Nenhum acontecimento registrado.')
            for day,text in self.data.timeline:paragraph(f'Dia {day} — {text}')
        elif self.tab=='Anotações' and case:
            positions=self.note_layout(case.notes)
            self.note_positions=[(i,x,py-self.scroll) for i,x,py in positions]
            for i,x,py in positions[:-1]:
                char=case.notes[i]
                if char!='\n':screen.blit(self.font.render(char,True,'#28354a'),(x,py-self.scroll))
            if not case.notes and not self.editing:paragraph('Clique nesta página para escrever sobre '+case.name+'.')
            if self.editing:
                _,x,py=positions[min(self.cursor,len(case.notes))]
                pygame.draw.line(screen,'#28354a',(x,py-self.scroll),(x,py-self.scroll+23),2)
            y=positions[-1][2]-self.scroll+32
        else:paragraph('Selecione um visitante na página à esquerda.')
        self.max_scroll=max(0,y+self.scroll-self.body.bottom+12)
        self.scroll=min(self.scroll,self.max_scroll)
        screen.set_clip(old)
        if self.max_scroll:
            track=pygame.Rect(1180,173,4,450);pygame.draw.rect(screen,'#b19b74',track)
            thumb=pygame.Rect(1180,173+int(410*self.scroll/self.max_scroll),4,40);pygame.draw.rect(screen,'#665039',thumb)
