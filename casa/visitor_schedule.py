"""Planejamento por partida e fila unica; sem inferencia sobre sintomas."""
from collections import deque
from dataclasses import dataclass


@dataclass(frozen=True)
class ArrivalRules:
    first_day: int=2
    last_day: int=20
    max_per_day: int=1
    priority_days: tuple=(2,3)
    minimum_encounters: int=1

    def __post_init__(self):
        if not 2<=self.first_day<=self.last_day<=20 or self.max_per_day<1 or self.minimum_encounters<0:
            raise ValueError('Parametros de chegada invalidos')


class VisitorManager:
    def __init__(self,visitors,rng,eligible,rules=None):
        self.visitors=visitors
        self.rules=rules or ArrivalRules()
        self.eligible=set(eligible)
        self.plan={}
        self.queue=deque()
        self.current=None
        self.seen=set()
        self.checked_days=set()
        self.opportunity_results={}
        self.opportunities={day:[] for day in self.rules.priority_days
                            if self.rules.first_day<=day<=self.rules.last_day}
        if 'ricardo' in self.eligible:self.plan['ricardo']=1
        candidates=[key for key in sorted(self.eligible) if key!='ricardo']
        rng.shuffle(candidates)
        slots=[day for day in range(self.rules.first_day,self.rules.last_day+1)
               for _ in range(self.rules.max_per_day)]
        priorities=[day for day in self.opportunities]
        rng.shuffle(priorities)
        # Reserva primeiro as oportunidades iniciais, sem inventar candidatos.
        required=min(len(candidates),max(1,self.rules.minimum_encounters),len(priorities))
        early=priorities[:required]
        for day in early:slots.remove(day)
        rng.shuffle(slots)
        for key,day in zip(candidates,early+slots):
            self.plan[key]=day
            if day in self.opportunities:self.opportunities[day].append(key)
        for key,day in self.plan.items():self.visitors[key].arrival_day=day

    @property
    def available(self):
        return [key for key in self.plan if key not in self.seen and self.visitors[key].state=='aguardando']

    @property
    def unscheduled(self):
        return sorted(self.eligible-set(self.plan))

    @property
    def accepted(self):return [key for key,v in self.visitors.items() if v.state=='acolhido']

    @property
    def rejected(self):return [key for key,v in self.visitors.items() if v.state=='rejeitado']

    @property
    def residents(self):return [key for key in self.accepted if self.visitors[key].alive]

    def activate(self,day,introduction_complete=False):
        if day==1 and not introduction_complete:return None
        if day>1 and 'ricardo' not in self.seen:return None
        if day not in self.checked_days:
            self.checked_days.add(day)
            if day in self.opportunities:
                self.opportunity_results[day]='planejado' if self.opportunities[day] else 'sem_candidatos'
            for key,arrival in self.plan.items():
                if arrival==day and key not in self.seen and key not in self.queue and self.visitors[key].state=='aguardando':
                    self.queue.append(key)
        return self.next()

    def next(self):
        if self.current and self.visitors[self.current].state=='aguardando':return None
        self.current=None
        while self.queue:
            key=self.queue.popleft()
            if key in self.seen or self.visitors[key].state!='aguardando':continue
            self.current=key;self.seen.add(key)
            self.visitors[key].arrived=True
            return self.visitors[key]
        return None
