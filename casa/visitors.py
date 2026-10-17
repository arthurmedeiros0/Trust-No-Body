"""Cadastro, sorteio por partida e decisoes; sem inferencias de infeccao."""
from dataclasses import dataclass,field
from pathlib import Path
import json
import random
from .config import ROOT

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

    @property
    def id(self):return self.definition['id']

    def decide(self,decision):
        if self.state!='aguardando' or decision not in ('acolhido','rejeitado'):return False
        self.state=decision
        return True

@dataclass
class JournalKnowledge:
    # Armazenamento apenas: nenhum significado logico e calculado aqui.
    published: dict[str,dict] = field(default_factory=dict)

class VisitorSession:
    def __init__(self, rng=None):
        rng=rng if rng is not None else random
        self.day=1
        self.knowledge=JournalKnowledge()
        self.decisions=[]
        self.visitors={}
        directory=ROOT/'dados/visitantes'
        for path in sorted(directory.glob('*.json')):
            if path.stem.endswith('_dialogos'):continue
            definition=json.loads(path.read_text(encoding='utf-8'))
            visitor=Visitor(definition,{key:bool(rng.getrandbits(1)) for key in definition['investigation']},rng.randint(0,3),rng.randint(0,3))
            self.visitors[visitor.id]=visitor

    def decide(self,visitor,decision):
        if not visitor.decide(decision):return False
        self.decisions.append(dict(day=self.day,visitor=visitor.id,decision=decision))
        return True
