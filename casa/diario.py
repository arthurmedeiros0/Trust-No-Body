"""Fichas e rascunhos pessoais, sem consultar condição ou sintomas reais."""
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
    examined_days: dict=field(default_factory=dict)
    accepted_day: int | None=None
    eliminated_day: int | None=None

class InvestigationJournal:
    def __init__(self):
        self.cases={}
        self.drafts={}
        self.encounters={}
        self.timeline=[]
        self.watched=set()

    def record(self,visitor_id):
        return self.cases.get(visitor_id) or self.drafts.get(visitor_id)

    def meet(self,visitor,day):
        """Chegar à porta cria apenas um rascunho, nunca uma ficha permanente."""
        if not visitor.arrived:return None
        d=visitor.definition
        name=d.get('name',visitor.id)
        if visitor.id not in self.encounters:
            self.encounters[visitor.id]=day
            self.timeline.append((day,name+' chegou à porta procurando abrigo.'))
        record=self.record(visitor.id)
        if record:return record
        if visitor.state=='rejeitado':return None
        record=Case(name,d.get('age','—'),d.get('profession','—'),self.encounters[visitor.id],visitor.state)
        if visitor.state=='aguardando':self.drafts[visitor.id]=record
        elif visitor.state in ('acolhido','eliminado'):self.cases[visitor.id]=record
        else:return None
        return record

    def decision(self,visitor,day,decision):
        name=visitor.definition.get('name',visitor.id)
        if decision=='rejeitado':
            self.drafts.pop(visitor.id,None)
        elif decision=='acolhido':
            record=self.drafts.pop(visitor.id,None) or self.cases.get(visitor.id) or self.meet(visitor,day)
            if record is not None:
                record.situation=decision;record.accepted_day=day
                self.cases[visitor.id]=record
        elif decision=='eliminado':
            record=self.cases.get(visitor.id) or self.meet(visitor,day)
            if record is not None:
                record.situation=decision;record.eliminated_day=day
        self.timeline.append((day,name+': '+decision+'.'))

    def conversation(self,visitor,day,question,answer):
        record=self.meet(visitor,day)
        if record is not None:record.conversations.append((day,question,answer))

    def examination(self,visitor,feature,day):
        """Registra o primeiro dia do exame, sem receber seu resultado."""
        if feature not in visitor.examined:return
        record=self.meet(visitor,day)
        if record is not None:record.examined_days.setdefault(feature,day)

    def watch(self,bulletin,day):
        if bulletin.id in self.watched:return
        self.watched.add(bulletin.id)
        self.timeline.append((day,f'Assistiu ao boletim do dia {bulletin.day}: {bulletin.headline}'))
        if bulletin.investigations:
            self.timeline.append((day,'Características investigáveis divulgadas ou recapituladas no boletim.'))
        if bulletin.id in PATTERNS:
            self.timeline.append((day,PATTERNS[bulletin.id][0]+' divulgado no boletim assistido.'))
