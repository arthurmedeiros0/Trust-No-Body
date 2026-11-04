"""Registros pessoais da sessão, sem acesso à condição ou aos sintomas reais."""
from dataclasses import dataclass, field
from .medical_knowledge import LABELS

MARKS=('Não verificado','Presente','Ausente')
CONCLUSIONS=('Ainda não sei','Suspeito que esteja infectado','Acredito que esteja saudável')
PATTERNS={
    'boletim_07': ('Primeiro padrão de infecção', 'Manchas nas mãos: presentes. Dentes deteriorados: presentes. Olhos alterados: ausentes.'),
    'boletim_14': ('Segundo padrão de infecção', 'Veias escurecidas: presentes. Palidez anormal: presente. Tremores involuntários: ausentes.'),
    'boletim_17': ('Terceiro padrão de infecção', 'Olhos alterados: presentes. Tremores involuntários: presentes. Manchas nas mãos: ausentes.')}

@dataclass
class Case:
    name: str
    age: object
    profession: str
    arrival: int
    situation: str='aguardando'
    marks: dict=field(default_factory=lambda:dict.fromkeys(LABELS,MARKS[0]))
    conclusion: str=CONCLUSIONS[0]
    notes: str=''
    conversations: list=field(default_factory=list)

class InvestigationJournal:
    def __init__(self):
        self.cases={}
        self.timeline=[]
        self.watched=set()

    def meet(self,visitor,day):
        if visitor.id in self.cases:return
        d=visitor.definition
        self.cases[visitor.id]=Case(d.get('name',visitor.id),d.get('age','—'),d.get('profession','—'),day,visitor.state)
        self.timeline.append((day,self.cases[visitor.id].name+' chegou à porta procurando abrigo.'))

    def decision(self,visitor,day,decision):
        self.meet(visitor,day)
        self.cases[visitor.id].situation=decision
        self.timeline.append((day,self.cases[visitor.id].name+': '+decision+'.'))

    def conversation(self,visitor,day,question,answer):
        self.meet(visitor,day)
        self.cases[visitor.id].conversations.append((day,question,answer))

    def watch(self,bulletin,day):
        if bulletin.id in self.watched:return
        self.watched.add(bulletin.id)
        self.timeline.append((day,f'Assistiu ao boletim do dia {bulletin.day}: {bulletin.headline}'))
        if bulletin.investigations:
            self.timeline.append((day,'Novas características investigáveis divulgadas no boletim.'))
        if bulletin.id in PATTERNS:
            self.timeline.append((day,PATTERNS[bulletin.id][0]+' divulgado no boletim assistido.'))
