"""Telejornal modal com tela CRT e arquivo; estado de leitura pertence ao NewsArchive."""
import pygame
from . import ui_theme as ui

class Television:
    SCREEN=pygame.Rect(108,80,1028,556)
    BODY=pygame.Rect(148,284,948,274)
    def __init__(self,news,days):
        self.news=news;self.days=days;self.active=False;self.page='root'
        self.bulletin=None;self.return_page='root';self.offset=0;self.cursor=0
        self.font=ui.font(27);self.small=ui.font(23);self.headline=ui.font(34)
        self.report_page=0;self.pressed_key=None;self.pressed_until=0

    def open(self):
        self.active=True;self.page='root';self.offset=0;self.cursor=0;self.report_page=0

    def body_rect(self):
        lines=len(ui.wrapped_lines(self.bulletin.headline,948,self.headline)) if self.bulletin else 1
        top=189+max(1,lines)*34+26
        return pygame.Rect(148,top,948,558-top)

    def report_pages(self):
        return ui.text_pages('\n\n'.join(self.bulletin.paragraphs) if self.bulletin else '',self.body_rect(),self.font,28)

    def disabled(self,key):
        return ((key=='prev' and self.offset==0) or
                (key=='next' and self.offset+8>=len(self.news.history)) or
                (key=='report_prev' and self.report_page==0) or
                (key=='report_next' and self.report_page>=len(self.report_pages())-1))

    def layout(self):
        if self.page=='root':
            return [('current',pygame.Rect(148,330,536,112),'Assistir ao noticiário atual'),
                    ('history',pygame.Rect(708,330,388,112),'Arquivo de transmissões'),
                    ('close',pygame.Rect(896,584,200,36),'Desligar / Voltar')]
        if self.page=='history':
            entries=[('news:'+b.id,pygame.Rect(148,184+i*48,948,42),f'Dia {b.day} — {b.headline} ['+('ASSISTIDA' if b.read else 'NÃO ASSISTIDA')+']')
                     for i,b in enumerate(self.news.history[self.offset:self.offset+8])]
            return entries+[('prev',pygame.Rect(656,584,208,36),'Anteriores'),
                            ('next',pygame.Rect(880,584,216,36),'Próximas'),
                            ('back',pygame.Rect(148,584,200,36),'Voltar')]
        return [('back',pygame.Rect(148,584,200,36),'Voltar'),
                ('report_prev',pygame.Rect(656,584,208,36),'Página anterior'),
                ('report_next',pygame.Rect(880,584,216,36),'Próxima página')]

    def choose(self,key):
        if self.disabled(key):return
        self.cursor=0
        self.pressed_key=key;self.pressed_until=pygame.time.get_ticks()+140
        if key=='close':self.active=False
        elif key=='back':self.page=self.return_page if self.page=='report' else 'root'
        elif key=='history':self.page='history';self.offset=0
        elif key=='prev':self.offset=max(0,self.offset-8)
        elif key=='next':self.offset=min(max(0,((len(self.news.history)-1)//8)*8),self.offset+8)
        elif key=='report_prev':self.report_page=max(0,self.report_page-1)
        elif key=='report_next':self.report_page=min(len(self.report_pages())-1,self.report_page+1)
        elif key=='current':
            self.bulletin=self.news.current(self.days.day)
            self.news.watch(self.bulletin);self.return_page='root';self.page='report';self.report_page=0
        elif key.startswith('news:'):
            bulletin=next((b for b in self.news.history if b.id==key[5:]),None)
            if bulletin and self.news.watch(bulletin):
                self.bulletin=bulletin;self.return_page='history';self.page='report';self.report_page=0

    def handle_event(self,event):
        if event.type==pygame.KEYDOWN:
            if event.key==pygame.K_ESCAPE:
                self.choose('close' if self.page=='root' else 'back');return
            if self.page=='report' and event.key in (pygame.K_LEFT,pygame.K_RIGHT,pygame.K_PAGEUP,pygame.K_PAGEDOWN):
                self.choose('report_prev' if event.key in (pygame.K_LEFT,pygame.K_PAGEUP) else 'report_next');return
            entries=self.layout()
            if event.key in (pygame.K_UP,pygame.K_DOWN):
                step=1 if event.key==pygame.K_DOWN else -1
                for _ in entries:
                    self.cursor=(self.cursor+step)%len(entries)
                    if not self.disabled(entries[self.cursor][0]):break
            elif event.key in (pygame.K_RETURN,pygame.K_SPACE):self.choose(entries[self.cursor%len(entries)][0])
        elif event.type==pygame.MOUSEBUTTONDOWN and event.button==1:
            key=next((key for key,rect,label in self.layout() if rect.collidepoint(event.pos)),None)
            if key:self.choose(key)
        elif event.type==pygame.MOUSEWHEEL and self.page=='report':
            self.choose('report_prev' if event.y>0 else 'report_next')

    def text(self,screen,text,font,rect,color,line_height):
        ui.text(screen,text,rect,font,color,line_height=line_height)
        return rect.y+len(ui.wrapped_lines(text,rect.width,font))*line_height

    def frame(self,screen):
        screen.fill(ui.INK,(0,686,1280,34))
        ui.shade(screen,224)
        pygame.draw.rect(screen,'#080c10',(70,42,1140,638),border_radius=24)
        pygame.draw.rect(screen,'#42454a',(78,50,1124,622),2,border_radius=20)
        pygame.draw.rect(screen,'#282b2e',(94,66,1056,584),border_radius=14)
        pygame.draw.rect(screen,'#111e27',self.SCREEN,border_radius=8)
        pygame.draw.rect(screen,'#52616a',self.SCREEN,1,border_radius=8)
        for y in range(310,510,8):pygame.draw.line(screen,'#3c4145',(1164,y),(1186,y),2)
        for y in (180,246):
            pygame.draw.circle(screen,'#252c31',(1175,y),17)
            pygame.draw.circle(screen,'#656a68',(1175,y),17,1)
            pygame.draw.line(screen,'#92958c',(1175,y-10),(1175,y-2),2)
        pygame.draw.circle(screen,'#ac4b4c',(1175,586),4)
        ui.text(screen,'TNB · RECEPTOR DE EMERGÊNCIA',pygame.Rect(466,651,400,20),ui.font(18),ui.MUTED,line_height=18)
        # Textura de transmissão sob os textos, sem animação ou cintilação.
        for y in range(84,632,5):pygame.draw.line(screen,'#13222c',(113,y),(1130,y))
        pygame.draw.rect(screen,'#633039',(132,100,6,43))
        ui.text(screen,'REDE DE EMERGÊNCIA',pygame.Rect(148,99,640,34),ui.font(34),ui.TEXT)
        pygame.draw.circle(screen,'#c3938b',(151,149),3)
        ui.text(screen,'SINAL ATIVO / BOLETIM OFICIAL',pygame.Rect(162,138,650,24),ui.font(20),'#c3938b',line_height=22)
        ui.text(screen,f'DIA {self.bulletin.day if self.page=="report" and self.bulletin else self.days.day:02} / 20',pygame.Rect(930,108,166,28),self.font,ui.PAPER)
        pygame.draw.line(screen,'#40515c',(148,169),(1096,169))

    def draw(self,screen):
        self.frame(screen)
        if self.page=='report':
            b=self.bulletin
            ui.text(screen,b.headline,pygame.Rect(148,189,948,78),self.headline,ui.PAPER,line_height=34)
            ui.text(screen,'\n\n'.join(b.paragraphs),self.body_rect(),self.font,ui.TEXT,self.report_page,28)
            ui.text(screen,f'TRANSMISSÃO {b.day:02}   /   {self.report_page+1:02} de {len(self.report_pages()):02}',pygame.Rect(372,592,268,24),ui.font(20),ui.MUTED,line_height=22)
        elif self.page=='history':
            if not self.news.history:ui.text(screen,'Nenhuma transmissão anterior publicada.',pygame.Rect(148,232,948,40),self.font,ui.MUTED)
        else:
            ui.text(screen,'INFORMAÇÃO DURANTE O ISOLAMENTO',pygame.Rect(148,210,948,36),ui.font(32),ui.PAPER)
            ui.text(screen,'Acompanhe o boletim do dia ou consulte as transmissões arquivadas.',pygame.Rect(148,264,948,52),self.font,ui.MUTED)
            ui.text(screen,'TRANSMISSÃO ATUAL',pygame.Rect(172,460,500,24),ui.font(20),ui.PAPER,line_height=22)
            ui.text(screen,'Reprodução de boletins publicados',pygame.Rect(732,460,364,26),ui.font(20),ui.MUTED,line_height=22)
        for i,(key,rect,label) in enumerate(self.layout()):
            selected=i==self.cursor
            if key.startswith('news:'):
                b=next(b for b in self.news.history if b.id==key[5:])
                ui.button(screen,rect,'',selected=selected,pressed=key==self.pressed_key and pygame.time.get_ticks()<self.pressed_until)
                ui.text(screen,f'{b.day:02}',pygame.Rect(rect.x+12,rect.y+9,36,26),self.font,ui.PAPER)
                # Duas linhas conservam manchetes inteiras; situação em coluna própria.
                row_lines=len(ui.wrapped_lines(b.headline,704,ui.font(22)))
                row_y=rect.y+(rect.height-row_lines*20)//2
                ui.text(screen,b.headline,pygame.Rect(rect.x+62,row_y,704,40),ui.font(22),ui.TEXT,line_height=20)
                ui.text(screen,'ASSISTIDA' if b.read else 'NÃO ASSISTIDA',pygame.Rect(rect.right-155,rect.y+13,146,24),ui.font(19),ui.MUTED if b.read else ui.PAPER,line_height=20)
            else:ui.button(screen,rect,label,selected=selected,disabled=self.disabled(key),pressed=key==self.pressed_key and pygame.time.get_ticks()<self.pressed_until,typeface=self.small)
