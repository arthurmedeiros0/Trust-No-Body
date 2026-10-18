"""Interface reutilizavel: dialogo, exame visual e confirmacao de decisoes."""
import pygame
from .visitor_assets import fit
from .visitor_dialogue import Dialogue
from .medical_knowledge import MedicalKnowledge

class VisitorUI:
    def __init__(self,visitor,assets,on_decision,knowledge=None,resident=False):
        self.visitor=visitor;self.assets=assets;self.on_decision=on_decision
        self.dialogue=Dialogue(visitor)
        self.knowledge=knowledge if knowledge is not None else MedicalKnowledge()
        self.resident=resident
        if resident:
            self.dialogue.data={**self.dialogue.data,
                'intro':self.dialogue.data.get('resident_intro',['Como você está?']),
                'questions':self.dialogue.data.get('resident_questions',[])}
        self.page='root';self.feature=None;self.decision=None
        self.response='';self.buttons={}
        self.font=pygame.font.Font(None,25);self.small=pygame.font.Font(None,22)

    def reset(self):
        self.page='root';self.feature=None;self.response=''

    def layout(self):
        if self.page=='image' and self.feature not in self.knowledge.known:self.page='root';self.feature=None
        if self.page=='confirm' and self.resident:self.page='root'
        if self.page=='root':
            labels=[('talk','Conversar')]
            if self.knowledge.known:labels.append(('investigate','Investigar'))
            if not self.resident:labels.extend([('accept','Aceitar'),('reject','Rejeitar')])
            labels.append(('back','Voltar'))
            return {key:(pygame.Rect(165+i*192,655,180,44),label) for i,(key,label) in enumerate(labels)}
        if self.page=='investigate':
            labels=[(key,item['label']+(' [visto]' if key in self.visitor.examined else '')) for key,item in self.visitor.definition['investigation'].items() if key in self.knowledge.known]
            return {**{key:(pygame.Rect(410,195+i*57,460,46),label) for i,(key,label) in enumerate(labels)},'back':(pygame.Rect(540,600,200,42),'Voltar')}
        if self.page=='talk':
            count=len(self.dialogue.data['questions'])
            step=min(48,280//max(1,count))
            return {**{str(i):(pygame.Rect(210,335+i*step,860,step-4),item['question']) for i,item in enumerate(self.dialogue.data['questions'])},'back':(pygame.Rect(540,635,200,42),'Voltar')}
        if self.page=='confirm':
            return {'confirm':(pygame.Rect(420,410,200,48),'Confirmar'),'back':(pygame.Rect(660,410,200,48),'Cancelar')}
        return {'back':(pygame.Rect(540,645,200,44),'Voltar')}

    def back(self):
        if self.page=='root':return 'back'
        self.page='investigate' if self.page=='image' else 'root'
        return None

    def handle_event(self,event):
        if event.type==pygame.KEYDOWN and event.key==pygame.K_ESCAPE:return self.back()
        if event.type!=pygame.MOUSEBUTTONDOWN or event.button!=1:return None
        key=next((key for key,(rect,_) in self.layout().items() if rect.collidepoint(event.pos)),None)
        if key is None:return None
        if key=='back':return self.back()
        if self.page=='root':
            if key=='talk':
                self.visitor.talked=True;self.response=self.dialogue.intro();self.page='talk'
            elif key=='investigate':self.page='investigate'
            elif key in ('accept','reject'):
                if not (self.visitor.talked or self.visitor.examined):
                    self.response='Converse ou examine uma característica antes de decidir.'
                else:self.decision='acolhido' if key=='accept' else 'rejeitado';self.page='confirm'
        elif self.page=='investigate':
            if key not in self.knowledge.known:return None
            self.feature=key;self.knowledge.observe(self.visitor,key);self.page='image'
        elif self.page=='talk':self.response=self.dialogue.answer(int(key))
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

    def text(self,screen,text,rect):
        y=rect.y
        for paragraph in text.split('\n'):
            line=''
            for word in paragraph.split():
                trial=(line+' '+word).strip()
                if self.font.size(trial)[0]>rect.width:
                    screen.blit(self.font.render(line,True,'#eee6d4'),(rect.x,y));y+=26;line=word
                else:line=trial
            if line:screen.blit(self.font.render(line,True,'#eee6d4'),(rect.x,y));y+=26
            y+=5

    def draw(self,screen):
        self.layout() # Sanitiza paginas/atalhos bloqueados antes de acessar imagens.
        if self.resident:
            shade=pygame.Surface(screen.get_size(),pygame.SRCALPHA);shade.fill((0,0,0,180));screen.blit(shade,(0,0))
        if self.page!='root':
            shade=pygame.Surface(screen.get_size(),pygame.SRCALPHA);shade.fill((0,0,0,200));screen.blit(shade,(0,0))
            pygame.draw.rect(screen,'#17232e',(170,105,940,535),border_radius=8)
        title=f"{self.visitor.definition['name']} | {self.visitor.definition['age']} anos | {self.visitor.definition['profession']}"
        if self.page=='root':
            pygame.draw.rect(screen,'#172027',(0,640,1280,80))
            screen.blit(self.small.render(title,True,'#eeddb8'),(170,624))
            if self.response:
                pygame.draw.rect(screen,'#17232e',(205,570,870,44))
                self.text(screen,self.response,pygame.Rect(220,580,840,30))
        elif self.page=='talk':
            self.text(screen,title,pygame.Rect(205,125,870,40))
            self.text(screen,self.response,pygame.Rect(210,177,860,195))
        elif self.page=='investigate':
            self.text(screen,'Investigação visual - selecione uma característica',pygame.Rect(230,135,820,40))
        elif self.page=='image':
            item=self.visitor.definition['investigation'][self.feature]
            image=self.examination_image()
            image=fit(image,(860,440));screen.blit(image,image.get_rect(center=(640,370)))
            self.text(screen,item['label'],pygame.Rect(220,125,840,35))
        elif self.page=='confirm':
            choice='acolher' if self.decision=='acolhido' else 'rejeitar'
            before=self.dialogue.data.get('before_decision',[])
            if before:self.text(screen,'\n'.join(before),pygame.Rect(250,165,780,100))
            self.text(screen,f'Deseja {choice} {self.visitor.definition["name"]}?',pygame.Rect(315,285,650,80))
        for rect,label in self.layout().values():
            pygame.draw.rect(screen,'#344b49',rect,border_radius=5)
            text=self.small.render(label,True,'#f3e6ca');screen.blit(text,text.get_rect(center=rect.center))
