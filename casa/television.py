"""Telejornal modal: dados separados, historico apenas do que foi assistido."""
import pygame


class Television:
    def __init__(self,news,days):
        self.news=news;self.days=days;self.active=False;self.page='root'
        self.bulletin=None;self.return_page='root';self.offset=0;self.cursor=0
        self.font=pygame.font.Font(None,27);self.small=pygame.font.Font(None,23)
        self.headline=pygame.font.Font(None,35)

    def open(self):
        self.active=True;self.page='root';self.offset=0;self.cursor=0

    def layout(self):
        if self.page=='root':
            return [(key,pygame.Rect(360,245+i*78,560,55),label) for i,(key,label) in enumerate(
                (('current','Noticiário atual'),('history','Notícias anteriores'),('close','Voltar'))) ]
        if self.page=='history':
            entries=[('news:'+b.id,pygame.Rect(130,185+i*49,1020,44),f'Dia {b.day} — {b.headline}')
                     for i,b in enumerate(self.news.history[self.offset:self.offset+8])]
            return entries+[('prev',pygame.Rect(350,615,200,40),'Anteriores'),
                            ('next',pygame.Rect(575,615,200,40),'Próximas'),
                            ('back',pygame.Rect(130,615,180,40),'Voltar')]
        return [('back',pygame.Rect(130,615,180,40),'Voltar')]

    def choose(self,key):
        self.cursor=0
        if key=='close':self.active=False
        elif key=='back':self.page=self.return_page if self.page=='report' else 'root'
        elif key=='history':self.page='history';self.offset=0
        elif key=='prev':self.offset=max(0,self.offset-8)
        elif key=='next':self.offset=min(max(0,((len(self.news.history)-1)//8)*8),self.offset+8)
        elif key=='current':
            self.bulletin=self.news.current(self.days.day)
            self.news.watch(self.bulletin);self.return_page='root';self.page='report'
        elif key.startswith('news:'):
            bulletin=next((b for b in self.news.history if b.id==key[5:]),None)
            if bulletin:self.bulletin=bulletin;self.return_page='history';self.page='report'

    def handle_event(self,event):
        if event.type==pygame.KEYDOWN:
            if event.key==pygame.K_ESCAPE:
                self.choose('close' if self.page=='root' else 'back');return
            entries=self.layout()
            if event.key in (pygame.K_UP,pygame.K_DOWN):
                self.cursor=(self.cursor+(1 if event.key==pygame.K_DOWN else -1))%len(entries)
            elif event.key in (pygame.K_RETURN,pygame.K_SPACE):self.choose(entries[self.cursor%len(entries)][0])
        elif event.type==pygame.MOUSEBUTTONDOWN and event.button==1:
            key=next((key for key,rect,label in self.layout() if rect.collidepoint(event.pos)),None)
            if key:self.choose(key)

    def text(self,screen,text,font,rect,color,line_height):
        y=rect.y
        for paragraph in text.split('\n'):
            line=''
            for word in paragraph.split():
                trial=(line+' '+word).strip()
                if line and font.size(trial)[0]>rect.width:
                    screen.blit(font.render(line,True,color),(rect.x,y));y+=line_height;line=word
                else:line=trial
            if line:screen.blit(font.render(line,True,color),(rect.x,y));y+=line_height
            y+=8
        return y

    def draw(self,screen):
        shade=pygame.Surface(screen.get_size(),pygame.SRCALPHA);shade.fill((0,0,0,220));screen.blit(shade,(0,0))
        box=pygame.Rect(90,75,1100,610)
        pygame.draw.rect(screen,'#101820',box);pygame.draw.rect(screen,'#76756a',box,2)
        pygame.draw.rect(screen,'#a43436',(110,94,7,54))
        screen.blit(self.headline.render('NOTICIÁRIO',True,'#f0e7d7'),(132,96))
        screen.blit(self.small.render('TRANSMISSÃO DE EMERGÊNCIA',True,'#d8887b'),(132,133))
        screen.blit(self.font.render(f'Dia {self.days.day} / 20',True,'#dad6cc'),(1010,107))
        if self.page=='report':
            b=self.bulletin
            self.text(screen,f'DIA {b.day} — {b.headline}',self.headline,pygame.Rect(130,180,1020,90),'#f6e9cc',34)
            self.text(screen,'\n'.join(b.paragraphs),self.font,pygame.Rect(130,290,1020,305),'#d8dce0',28)
        elif self.page=='history':
            if not self.news.history:screen.blit(self.font.render('Nenhuma transmissão assistida.',True,'#bdc1c5'),(130,195))
        else:
            self.text(screen,'Boletim do dia e arquivo das transmissões assistidas.',self.font,pygame.Rect(160,180,960,50),'#bdc1c5',28)
        for i,(key,rect,label) in enumerate(self.layout()):
            pygame.draw.rect(screen,'#28323b',rect)
            pygame.draw.rect(screen,'#af8670' if i==self.cursor else '#555b60',rect,1)
            font=self.small if key.startswith('news:') else self.font
            while font.size(label)[0]>rect.width-20:label=label[:-2]+'…' if not label.endswith('…') else label[:-2]+'…'
            image=font.render(label,True,'#f0e5d2');screen.blit(image,image.get_rect(midleft=(rect.x+10,rect.centery)))
        pygame.draw.rect(screen,'#792e32',(110,665,1060,16))
        screen.blit(self.small.render('EPIDEMIA — NOVAS INFORMAÇÕES',True,'#f6dddd'),(420,662))
