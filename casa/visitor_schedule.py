"""Planejamento por partida e fila unica; sem inferencia sobre sintomas."""
from collections import deque
from dataclasses import dataclass,field


@dataclass(frozen=True)
class ArrivalRules:
    fixed_visitors: dict=field(default_factory=lambda:{'ricardo':1,'laura':2})
    arrival_days: tuple=(4,6,9,13,17)

    def __post_init__(self):
        days=list(self.fixed_visitors.values())+list(self.arrival_days)
        if (any(type(day) is not int or not 1<=day<=20 for day in days)
            or list(self.arrival_days)!=sorted(self.arrival_days)
            or self.fixed_visitors.get('ricardo')!=1):
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
        self.opportunities={day:[] for day in sorted(set(self.rules.fixed_visitors.values())|set(self.rules.arrival_days)) if day>1}
        self.plan.update({key:day for key,day in self.rules.fixed_visitors.items() if key in self.eligible})
        candidates=[key for key in sorted(self.eligible) if key not in self.rules.fixed_visitors]
        rng.shuffle(candidates)
        for key,day in zip(candidates,self.rules.arrival_days):
            self.plan[key]=day
        for key,day in self.plan.items():
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
                if arrival<=day and key not in self.seen and key not in self.queue and self.visitors[key].state=='aguardando':
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
