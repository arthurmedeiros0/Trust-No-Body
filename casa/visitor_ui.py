"""Interface reutilizavel: dialogo, exame visual e confirmacao de decisoes."""
import pygame
from .visitor_dialogue import Dialogue
from .medical_knowledge import MedicalKnowledge
from . import ui_theme as theme
from . import visitor_presentation as presentation

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
        self.pressed_key=None;self.pressed_until=0

    def reset(self):
        self.page='root';self.feature=None;self.response=''

    @property
    def response(self):return self._response

    @response.setter
    def response(self,value):
        self._response=value
        self.text_page=0

    def speech_rect(self):
        return presentation.speech_rect(self)

    def speech(self):
        if self.page!='confirm':return self.response
        choice={'acolhido':'acolher','rejeitado':'rejeitar','eliminado':'eliminar'}[self.decision]
        before=(['Esta decisão é irreversível e afetará sua sanidade.'] if self.decision=='eliminado'
                else self.dialogue.data.get('before_decision',[]))
        return '\n\n'.join([*before,f'Deseja {choice} {self.visitor.definition["name"]}?'])

    def pagination(self):
        return presentation.pagination(self)

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
        """A interface deixa a interpretacao das pistas a cargo do jogador."""
        return None

    def layout(self):
        return presentation.layout(self)

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
        self.pressed_key=key;self.pressed_until=pygame.time.get_ticks()+140
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
            if self.session is not None:self.session.journal.examination(self.visitor,key,self.session.day)
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
        return theme.wrapped_lines(text,width,font or self.font)

    def text_pages(self,text,rect,font=None):
        return theme.text_pages(text,rect,font or self.font)

    def text(self,screen,text,rect,page=0,font=None,color='#eee6d4'):
        return theme.text(screen,text,rect,font or self.font,color,page)

    def draw_speech(self,screen):
        presentation.draw_speech(self,screen)

    def draw(self,screen):
        presentation.draw(self,screen)
