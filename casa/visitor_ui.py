"""Interface reutilizavel: dialogo, exame visual e confirmacao de decisoes."""
import pygame
from .visitor_assets import fit
from .visitor_dialogue import Dialogue
from .medical_knowledge import MedicalKnowledge

class VisitorUI:
    def __init__(self,visitor,assets,on_decision,knowledge=None,resident=False,session=None):
        self.visitor=visitor;self.assets=assets;self.on_decision=on_decision
        self.dialogue=Dialogue(visitor,session,resident)
        self.knowledge=knowledge if knowledge is not None else MedicalKnowledge()
        self.resident=resident
        self.page='root';self.feature=None;self.decision=None
        self.response='';self.buttons={}
        self.font=pygame.font.Font(None,25);self.small=pygame.font.Font(None,22)
        self.session = session

    def reset(self):
        self.page='root';self.feature=None;self.response=''

    @property
    def response(self):return self._response

    @response.setter
    def response(self,value):
        self._response=value
        self.text_page=0

    def speech_rect(self):
        if self.page=='intro':return pygame.Rect(210,459,860,130)
        if self.page=='answer':return pygame.Rect(210,519,860,78)
        if self.page=='confirm':return pygame.Rect(250,165,780,208)
        return pygame.Rect(220,465,840,104)

    def speech(self):
        if self.page!='confirm':return self.response
        choice={'acolhido':'acolher','rejeitado':'rejeitar','eliminado':'eliminar'}[self.decision]
        before=(['Esta decisão é irreversível e afetará sua sanidade.'] if self.decision=='eliminado'
                else self.dialogue.data.get('before_decision',[]))
        return '\n\n'.join([*before,f'Deseja {choice} {self.visitor.definition["name"]}?'])

    def pagination(self):
        if self.page not in ('root','intro','answer','confirm'):return {}
        pages=self.text_pages(self.speech(),self.speech_rect())
        self.text_page=max(0,min(self.text_page,len(pages)-1))
        if len(pages)==1:return {}
        y={'root':578,'intro':610,'answer':610,'confirm':386}[self.page]
        controls={}
        if self.text_page>0:controls['text_prev']=(pygame.Rect(220,y,150,28),'Anterior')
        if self.text_page<len(pages)-1:controls['text_next']=(pygame.Rect(910,y,150,28),'Próxima')
        return controls

    def remember_conversation(self):
        if self.page in ('intro','answer','talk'):
            self.dialogue.progress.stage=self.page
            self.dialogue.progress.text_page=self.text_page

    def open_conversation(self):
        progress=self.dialogue.progress
        self.page=progress.stage
        self.response=(progress.answer_text if self.page=='answer' else
                       self.dialogue.intro() if self.page=='intro' else '')
        self.text_page=progress.text_page

    def continue_conversation(self):
        pages=self.text_pages(self.speech(),self.speech_rect())
        if self.text_page<len(pages)-1:self.text_page+=1
        else:self.page='talk';self.response=''
        self.remember_conversation()

    def diagnosis_indicator(self):
        if self.session is None or self.page not in ('investigate','image'):return None
        if not any(key in self.knowledge.known for key in self.visitor.definition['investigation']):return None
        result=self.session.diagnosticar_visitante(self.visitor.id)
        return {'infectado':'PADRÃO DE INFECÇÃO IDENTIFICADO','saudavel':'Diagnóstico: saudável'}.get(result,'Diagnóstico inconclusivo')

    def layout(self):
        if self.page=='image' and self.feature not in self.knowledge.known:self.page='root';self.feature=None
        if self.page=='confirm' and self.resident and self.decision!='eliminado':self.page='root'
        if self.page=='root':
            labels=[('talk','Conversar')]
            if self.knowledge.known:labels.append(('investigate','Investigar'))
            if not self.resident:labels.extend([('accept','Aceitar'),('reject','Rejeitar')])
            elif self.session is not None and self.visitor.alive and self.visitor.state=='acolhido':labels.append(('eliminate','Eliminar'))
            labels.append(('back','Voltar'))
            return {**{key:(pygame.Rect(165+i*192,655,180,44),label) for i,(key,label) in enumerate(labels)},**self.pagination()}
        if self.page=='investigate':
            labels=[(key,item['label']+(' [visto]' if key in self.visitor.examined else '')) for key,item in self.visitor.definition['investigation'].items() if key in self.knowledge.known]
            return {**{key:(pygame.Rect(410,195+i*57,460,46),label) for i,(key,label) in enumerate(labels)},'back':(pygame.Rect(540,600,200,42),'Voltar')}
        if self.page=='talk':
            return {**{str(i):(pygame.Rect(210,518+position*56,860,44),self.dialogue.data['questions'][i]['question'])
                       for position,i in enumerate(self.dialogue.pending())},
                    'back':(pygame.Rect(540,655,200,42),'Voltar')}
        if self.page in ('intro','answer'):
            return {'continue':(pygame.Rect(420,655,220,42),'Continuar'),
                    'back':(pygame.Rect(660,655,200,42),'Voltar'),**self.pagination()}
        if self.page=='confirm':
            return {'confirm':(pygame.Rect(420,440,200,48),'Confirmar'),'back':(pygame.Rect(660,440,200,48),'Cancelar'),**self.pagination()}
        return {'back':(pygame.Rect(540,645,200,44),'Voltar')}

    def back(self):
        if self.page=='root':return 'back'
        self.remember_conversation()
        if self.page in ('intro','answer','talk'):self.response=''
        self.page='investigate' if self.page=='image' else 'root'
        self.text_page=0
        return None

    def handle_event(self,event):
        if event.type==pygame.KEYDOWN and event.key==pygame.K_ESCAPE:return self.back()
        if event.type==pygame.KEYDOWN and event.key in (pygame.K_RETURN,pygame.K_SPACE) and self.page in ('intro','answer'):
            self.continue_conversation();return None
        if event.type==pygame.KEYDOWN and event.key in (pygame.K_LEFT,pygame.K_RIGHT,pygame.K_PAGEUP,pygame.K_PAGEDOWN):
            controls=self.pagination()
            key='text_prev' if event.key in (pygame.K_LEFT,pygame.K_PAGEUP) else 'text_next'
            if key in controls:self.text_page+=-1 if key=='text_prev' else 1
            self.remember_conversation()
            return None
        if event.type!=pygame.MOUSEBUTTONDOWN or event.button!=1:return None
        key=next((key for key,(rect,_) in self.layout().items() if rect.collidepoint(event.pos)),None)
        if key is None:return None
        if key in ('text_prev','text_next'):
            self.text_page+=-1 if key=='text_prev' else 1
            self.remember_conversation()
            return None
        if key=='back':return self.back()
        if key=='continue' and self.page in ('intro','answer'):
            self.continue_conversation();return None
        if self.page=='root':
            if key=='talk':
                self.visitor.talked=True;self.open_conversation()
            elif key=='investigate':self.page='investigate'
            elif key=='eliminate' and self.resident:
                self.decision='eliminado';self.page='confirm';self.text_page=0
            elif key in ('accept','reject'):
                if not (self.visitor.talked or self.visitor.examined):
                    self.response='Converse ou examine uma característica antes de decidir.'
                else:self.decision='acolhido' if key=='accept' else 'rejeitado';self.page='confirm';self.text_page=0
        elif self.page=='investigate':
            if key not in self.knowledge.known:return None
            self.feature=key;self.knowledge.observe(self.visitor,key);self.page='image'
        elif self.page=='talk':
            if self.dialogue.ask(int(key)):
                self.response=self.dialogue.progress.answer_text;self.page='answer'
        elif self.page=='confirm' and key=='confirm':
            if self.on_decision(self.visitor,self.decision):self.reset()
            else:self.response='Não foi possível concluir a decisão.';self.page='root'
        return None

    def draw_portrait(self,screen):
        if self.visitor.state=='aguardando':
            image=self.assets.portrait
            screen.blit(image,image.get_rect(midbottom=self.visitor.definition['portrait_anchor']))

    def examination_image(self):
        if self.feature not in self.knowledge.known:raise PermissionError('Investigacao ainda desconhecida')
        variant='alterado' if self.visitor.symptoms[self.feature] else 'normal'
        return self.assets.investigation[self.feature][variant]

    def wrapped_lines(self,text,width,font=None):
        font=font or self.font
        lines=[]
        for paragraph in text.split('\n'):
            line=''
            for word in paragraph.split():
                if line and font.size(line+' '+word)[0]>width:
                    lines.append(line);line=''
                while font.size(word)[0]>width and len(word)>1:
                    end=1
                    while end<len(word) and font.size(word[:end+1])[0]<=width:end+=1
                    lines.append(word[:end]);word=word[end:]
                line=(line+' '+word).strip()
            lines.append(line)
        return lines

    def text_pages(self,text,rect,font=None):
        font=font or self.font
        lines=self.wrapped_lines(text,rect.width,font)
        capacity=max(1,rect.height//max(26,font.get_linesize()))
        return [lines[i:i+capacity] for i in range(0,len(lines),capacity)] or [[]]

    def text(self,screen,text,rect,page=0,font=None,color='#eee6d4'):
        font=font or self.font
        pages=self.text_pages(text,rect,font)
        lines=pages[max(0,min(page,len(pages)-1))]
        previous=screen.get_clip()
        screen.set_clip(previous.clip(rect))
        try:
            for index,line in enumerate(lines):
                screen.blit(font.render(line,True,color),(rect.x,rect.y+index*max(26,font.get_linesize())))
        finally:screen.set_clip(previous)
        return len(pages)

    def draw_speech(self,screen):
        rect=self.speech_rect()
        pygame.draw.rect(screen,'#101b24',rect.inflate(24,16))
        pygame.draw.rect(screen,'#56645b',rect.inflate(24,16),1)
        pages=self.text(screen,self.speech(),rect,self.text_page)
        if pages>1:
            y={'root':592,'intro':624,'answer':624,'confirm':400}[self.page]
            label=self.small.render(f'{self.text_page+1} / {pages}',True,'#b4b8aa')
            screen.blit(label,label.get_rect(center=(640,y)))

    def draw(self,screen):
        self.layout() # Sanitiza paginas/atalhos bloqueados antes de acessar imagens.
        if self.resident:
            shade=pygame.Surface(screen.get_size(),pygame.SRCALPHA);shade.fill((0,0,0,180));screen.blit(shade,(0,0))
            if self.assets is not None and self.page in ('intro','talk','answer'):
                portrait=self.assets.portrait
                screen.blit(portrait,portrait.get_rect(midbottom=self.visitor.definition['portrait_anchor']))
        if self.page in ('intro','talk','answer'):
            # Painel baixo: mantém o rosto e o tronco do visitante em destaque.
            pygame.draw.rect(screen,'#17232e',(170,405,940,235))
            pygame.draw.rect(screen,'#56645b',(170,405,940,235),1)
        elif self.page!='root':
            shade=pygame.Surface(screen.get_size(),pygame.SRCALPHA);shade.fill((0,0,0,200));screen.blit(shade,(0,0))
            pygame.draw.rect(screen,'#17232e',(170,105,940,535),border_radius=8)
        definition=self.visitor.definition
        details=[definition['name']]
        if definition.get('age') is not None:details.append(f"{definition['age']} anos")
        if definition.get('profession'):details.append(definition['profession'])
        title=' | '.join(details)
        if self.page=='root':
            pygame.draw.rect(screen,'#172027',(0,640,1280,80))
            self.text(screen,title,pygame.Rect(170,620,940,28),font=self.small,color='#eeddb8')
            if self.response:
                self.draw_speech(screen)
        elif self.page=='talk':
            self.text(screen,title,pygame.Rect(205,420,870,28))
            prompt='O que deseja perguntar?' if self.dialogue.pending() else 'Conversa concluída. Todas as perguntas foram realizadas.'
            self.text(screen,prompt,pygame.Rect(210,470,860,30))
        elif self.page in ('intro','answer'):
            self.text(screen,title,pygame.Rect(205,420,870,28))
            if self.page=='answer':
                question=self.dialogue.data['questions'][self.dialogue.progress.question]['question']
                self.text(screen,'Você: '+question,pygame.Rect(210,459,860,52),color='#d5bf86')
            self.draw_speech(screen)
        elif self.page=='investigate':
            self.text(screen,'Investigação visual - selecione uma característica',pygame.Rect(230,135,820,40))
        elif self.page=='image':
            item=self.visitor.definition['investigation'][self.feature]
            image=self.examination_image()
            image=fit(image,(860,440));screen.blit(image,image.get_rect(center=(640,370)))
            self.text(screen,item['label'],pygame.Rect(220,125,840,35))
        elif self.page=='confirm':
            self.draw_speech(screen)
        indicator=self.diagnosis_indicator()
        if indicator:
            # Faixa abaixo da imagem (que termina em y=590) e acima de Voltar.
            area=pygame.Rect(350,552 if self.page=='investigate' else 593,580,25)
            pygame.draw.rect(screen,'#172027',area)
            color='#d9ab80' if indicator=='PADRÃO DE INFECÇÃO IDENTIFICADO' else '#b4b8aa'
            text=self.small.render(indicator,True,color)
            screen.blit(text,text.get_rect(center=area.center))
        for rect,label in self.layout().values():
            pygame.draw.rect(screen,'#344b49',rect,border_radius=5)
            # Perguntas também respeitam a caixa; os textos originais cabem nela.
            previous=screen.get_clip();screen.set_clip(previous.clip(rect.inflate(-8,-2)))
            try:
                text=self.small.render(label,True,'#f3e6ca');screen.blit(text,text.get_rect(center=rect.center))
            finally:screen.set_clip(previous)
