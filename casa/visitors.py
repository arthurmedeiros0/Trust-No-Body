"""Cadastro, sorteio por partida e decisoes; sem inferencias de infeccao."""
from dataclasses import dataclass,field
from pathlib import Path
import json
import random
import inspect
import importlib
from itertools import product
from functools import lru_cache
from .days import DayCycle
from .news import NewsArchive
from .config import ROOT
from .survival import Survival,Needs
from .visitor_schedule import VisitorManager,ArrivalRules
from .visitor_registry import readiness
from .medical_knowledge import MedicalKnowledge,LABELS

# O módulo reservado pode ainda não fornecer a função do grupo.
try:
    infection_logic=importlib.import_module('logica_infeccao')
except ModuleNotFoundError as error:
    if error.name!='logica_infeccao':raise
    infection_logic=None

PROTOCOL_NEWS=frozenset(('boletim_07','boletim_14','boletim_17'))


@lru_cache(maxsize=32)
def consistent_candidates(diagnose,features,condition):
    """Enumera dados completos; somente a função do grupo classifica padrões.

    'Inconclusivo' só exclui os padrões oficiais nesta validação interna com
    TODOS os exames e notícias. Nunca prova saúde a partir de dados parciais.
    """
    candidates=[]
    for values in product((False,True),repeat=len(features)):
        result=diagnose(dict(zip(features,values)),set(PROTOCOL_NEWS))
        if (condition=='infectado' and result=='infectado' or
            condition=='saudavel' and result in ('inconclusivo','saudavel')):
            candidates.append(values)
    return tuple(candidates)

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
    arrival_day: int | None = None

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
    def __init__(self, rng=None, definitions=None, arrival_rules=None, asset_check=readiness):
        rng=rng if rng is not None else random
        self.days=DayCycle()
        self.survival=Survival()
        self.intro=Introduction()
        self.company_seen_today=False
        self.last_report=None
        self.knowledge=JournalKnowledge()
        self.medical=MedicalKnowledge()
        self.news=NewsArchive(self.knowledge)
        self.days.subscribe('day_start',lambda event:self.news.unlock(event.day))
        self.days.subscribe('day_end',self._end_day)
        self.days.subscribe('day_start',self._start_day)
        self.news.on_watch.append(self._news_seen)
        self.decisions=[]
        self.test_mode=False
        self.on_arrival=[]
        self.visitors={}
        self.unavailable={}
        directory=ROOT/'dados/visitantes'
        if definitions is None:
            definitions=[json.loads(path.read_text(encoding='utf-8')) for path in sorted(directory.glob('*.json'))
                         if not path.stem.endswith('_dialogos')]
        for definition in definitions:
            if definition['id'] in self.visitors:raise ValueError('Identificador de visitante duplicado: '+definition['id'])
            supplies=definition.get('initial_supplies',{})
            visitor=Visitor(definition,{},
                            rng.randint(*supplies.get('food',(0,3))),rng.randint(*supplies.get('water',(0,3))))
            self.set_condition(visitor,rng)
            self.visitors[visitor.id]=visitor
            reason=asset_check(definition)
            if reason:self.unavailable[visitor.id]=reason
        if arrival_rules is None:
            arrival_rules=ArrivalRules(**json.loads((ROOT/'dados/agendamento_visitantes.json').read_text(encoding='utf-8')))
        self.manager=VisitorManager(self.visitors,rng,set(self.visitors)-set(self.unavailable),arrival_rules)

    def diagnosticar_visitante(self,visitante_id):
        """Encaminha somente evidências observadas, sem inferências locais.

        Sintomas desconhecidos são omitidos; False significa ausência examinada.
        A condição real do visitante nunca é alterada por esta consulta.
        """
        if visitante_id not in self.visitors:raise KeyError(visitante_id)
        sintomas=dict(self.medical.observations.get(visitante_id,{}))
        noticias=set(self.knowledge.published)
        if self.test_mode:
            noticias.update(b.id for b in self.news.bulletins if b.day in (7,14,17))
        diagnosticar=getattr(infection_logic,'diagnosticar',None)
        if not callable(diagnosticar):return 'inconclusivo'
        try:
            inspect.signature(diagnosticar).bind(sintomas,noticias)
        except (TypeError,ValueError):
            return 'inconclusivo'
        resultado=diagnosticar(sintomas,noticias)
        return resultado if resultado in ('infectado','inconclusivo','saudavel') else 'inconclusivo'

    @staticmethod
    def set_condition(visitor,rng,condition='aleatoria'):
        if condition=='aleatoria':condition='infectado' if rng.random()<.5 else 'saudavel'
        if condition not in ('saudavel','infectado'):raise ValueError('Condição de teste inválida')
        features=tuple(LABELS)
        diagnose=getattr(infection_logic,'diagnosticar',None)
        if not callable(diagnose):raise RuntimeError('A geração coerente requer diagnosticar(sintomas, noticias_lidas).')
        candidates=consistent_candidates(diagnose,features,condition)
        probabilities={key:.5 for key in features}
        if visitor.id in ('gabriel','antonio'):
            # Mantém sinais benignos de trabalho e doenças anteriores.
            probabilities.update(manchas_maos=.65,dentes_deteriorados=.25)
            if condition=='saudavel':probabilities.update(olhos_alterados=0,veias_escurecidas=0)
        weights=[]
        for values in candidates:
            weight=1
            for key,present in zip(features,values):
                probability=probabilities[key]
                weight*=probability if present else 1-probability
            weights.append(weight)
        if not candidates or not any(weights):
            raise RuntimeError('A lógica do grupo não fornece sintomas compatíveis com a condição: '+condition)
        values=rng.choices(candidates,weights=weights,k=1)[0]
        visitor.diagnosis=condition
        visitor.symptoms=dict(zip(features,values))

    @staticmethod
    def set_antonio_condition(visitor,rng,condition='aleatoria'):
        VisitorSession.set_condition(visitor,rng,condition)

    set_gabriel_condition=set_condition

    def start_test(self,visitor_id,condition='aleatoria',rng=None):
        """Ativa um visitante na sessão real, sem avançar dias ou disparar a agenda."""
        if visitor_id in self.unavailable or visitor_id not in self.visitors:
            raise ValueError('Visitante indisponível: '+visitor_id)
        visitor=self.visitors[visitor_id]
        self.test_mode=True
        if visitor_id=='gabriel':self.set_gabriel_condition(visitor,rng or random,condition)
        elif visitor_id=='antonio':self.set_antonio_condition(visitor,rng or random,condition)
        elif condition!='aleatoria':raise ValueError('Condição de teste indisponível para este visitante')
        self.medical.observations.pop(visitor_id,None)
        visitor.examined.clear()
        self.medical.known.update(visitor.definition['investigation'])
        self.manager.queue.clear()
        self.manager.current=visitor_id
        self.manager.seen.add(visitor_id)
        visitor.arrived=True
        self._arrive(visitor)
        return visitor

    @property
    def day(self):return self.days.day

    @property
    def living_ids(self):
        return (['protagonista'] if self.survival.alive else [])+[v.id for v in self.visitors.values() if v.state=='acolhido' and v.alive]

    def _news_seen(self,bulletin):
        self.medical.learn(bulletin.investigations)
        if bulletin.day==1:
            self.intro.broadcast_seen=True
            if self.day==1 and not self.test_mode:self._arrive(self.manager.activate(1,True))

    def _arrive(self,visitor):
        if visitor:
            for callback in tuple(self.on_arrival):callback(visitor)

    def _end_day(self,event):
        # Publicação rege o mundo; leitura e exames regem só a investigação.
        published={b.id for b in self.news.bulletins if b.day<=event.day}
        diagnose=getattr(infection_logic,'diagnosticar',None)
        infected=callable(diagnose) and any(
            v.state=='acolhido' and v.alive and v.diagnosis=='infectado' and
            diagnose(dict(v.symptoms),set(published))=='infectado'
            for v in self.visitors.values())
        self.last_report=self.survival.close_day(event.day,self.living_ids,self.company_seen_today,infected)
        return self.survival.alive and not self.survival.won

    def _start_day(self,event):
        self.company_seen_today=len(self.living_ids)>1
        if not self.test_mode:self._arrive(self.manager.activate(event.day,self.intro.broadcast_seen))

    def decide(self,visitor,decision):
        if not self.survival.alive or self.survival.won:return False
        if self.visitors.get(visitor.id) is not visitor:return False
        if self.manager.current and self.manager.current!=visitor.id:return False
        if not visitor.decide(decision):return False
        if decision=='acolhido' and not visitor.supplies_transferred:
            self.survival.add_supplies(visitor.food,visitor.water)
            visitor.supplies_transferred=True
            self.survival.people.setdefault(visitor.id,Needs())
            self.company_seen_today=True
        self.decisions.append(dict(day=self.day,visitor=visitor.id,decision=decision))
        self._arrive(self.manager.next())
        return True

    def eliminate(self,visitor_id):
        visitor=self.visitors.get(visitor_id)
        if (not self.survival.alive or self.survival.won or visitor is None or
            not visitor.alive or visitor.state!='acolhido'):return False
        visitor.alive=False;visitor.state='eliminado'
        self.survival.people.pop(visitor_id,None)
        self.survival.change_sanity(-2 if visitor.diagnosis=='infectado' else -3)
        self.company_seen_today=len(self.living_ids)>1
        self.decisions.append(dict(day=self.day,visitor=visitor_id,decision='eliminado'))
        return True
