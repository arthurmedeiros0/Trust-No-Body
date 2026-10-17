"""Cadastro, sorteio por partida e decisoes; sem inferencias de infeccao."""
from dataclasses import dataclass,field
from pathlib import Path
import json
import random
from .days import DayCycle
from .news import NewsArchive
from .config import ROOT
from .survival import Survival,Needs

@dataclass
class Visitor:
    definition: dict
    symptoms: dict[str,bool]
    food: int
    water: int
    state: str = 'aguardando'
    diagnosis: str = 'diagnostico_pendente'
    examined: set[str] = field(default_factory=set)
    talked: bool = False
    arrived: bool = False
    alive: bool = True
    supplies_transferred: bool = False

    @property
    def id(self):return self.definition['id']

    def decide(self,decision):
        if not self.arrived or self.state!='aguardando' or decision not in ('acolhido','rejeitado'):return False
        self.state=decision
        return True

    @property
    def available_food(self):return 0 if self.supplies_transferred else self.food

    @property
    def available_water(self):return 0 if self.supplies_transferred else self.water


@dataclass
class Introduction:
    fridge_checked: bool=False
    broadcast_seen: bool=False
    door_checked: bool=False

    @property
    def objective(self):
        if not self.fridge_checked:return 'Verificar a geladeira.'
        if not self.broadcast_seen:return 'Assistir ao noticiário.'
        if not self.door_checked:return 'Investigar quem está na porta.'
        return ''

@dataclass
class JournalKnowledge:
    # Armazenamento apenas: nenhum significado logico e calculado aqui.
    published: dict[str,dict] = field(default_factory=dict)

class VisitorSession:
    def __init__(self, rng=None):
        rng=rng if rng is not None else random
        self.days=DayCycle()
        self.survival=Survival()
        self.intro=Introduction()
        self.company_seen_today=False
        self.last_report=None
        self.knowledge=JournalKnowledge()
        self.news=NewsArchive(self.knowledge)
        self.days.subscribe('day_start',lambda event:self.news.unlock(event.day))
        self.days.subscribe('day_end',self._end_day)
        self.days.subscribe('day_start',self._start_day)
        self.news.on_watch.append(self._news_seen)
        self.decisions=[]
        self.visitors={}
        directory=ROOT/'dados/visitantes'
        for path in sorted(directory.glob('*.json')):
            if path.stem.endswith('_dialogos'):continue
            definition=json.loads(path.read_text(encoding='utf-8'))
            supplies=definition.get('initial_supplies',{})
            visitor=Visitor(definition,{key:bool(rng.getrandbits(1)) for key in definition['investigation']},
                            rng.randint(*supplies.get('food',(0,3))),rng.randint(*supplies.get('water',(0,3))))
            self.visitors[visitor.id]=visitor

    @property
    def day(self):return self.days.day

    @property
    def living_ids(self):
        return (['protagonista'] if self.survival.alive else [])+[v.id for v in self.visitors.values() if v.state=='acolhido' and v.alive]

    def _news_seen(self,bulletin):
        if bulletin.day==1:
            self.intro.broadcast_seen=True
            visitor=self.visitors.get('ricardo')
            if visitor and visitor.state=='aguardando':visitor.arrived=True

    def _end_day(self,event):
        self.last_report=self.survival.close_day(event.day,self.living_ids,self.company_seen_today)
        return self.survival.alive

    def _start_day(self,event):
        self.company_seen_today=len(self.living_ids)>1

    def decide(self,visitor,decision):
        if not visitor.decide(decision):return False
        if decision=='acolhido' and not visitor.supplies_transferred:
            self.survival.add_supplies(visitor.food,visitor.water)
            visitor.supplies_transferred=True
            self.survival.people.setdefault(visitor.id,Needs())
            self.company_seen_today=True
        self.decisions.append(dict(day=self.day,visitor=visitor.id,decision=decision))
        return True
