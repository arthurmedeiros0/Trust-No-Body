"""Sobrevivencia por racoes inteiras de meia unidade; sem logica de infeccao."""
from dataclasses import dataclass


def amount(value):
    return f'{value:g}'.replace('.',',')


def protagonist_first(ids):
    return ['protagonista']+sorted(person for person in ids if person!='protagonista')


@dataclass
class Needs:
    hunger: int=0
    thirst: int=0


@dataclass(frozen=True)
class DailyReport:
    day: int
    food: float
    water: float
    residents: int
    sanity: int
    hungry: bool
    thirsty: bool
    cause: str=''

    def text(self):
        text=(f'Resumo do dia anterior — Dia {self.day}. Comida consumida: {amount(self.food)} lata(s). '
              f'Água consumida: {amount(self.water)} garrafa(s). Moradores: {self.residents}. Sanidade: {self.sanity}/8.')
        if self.hungry:text+=' Você não recebeu sua ração de comida.'
        if self.thirsty:text+=' Você não recebeu sua ração de água.'
        return text


class Survival:
    MAX_SANITY=8

    def __init__(self):
        self._food=0;self._water=0;self.sanity=8
        self.people={'protagonista':Needs()}
        self.loneliness=0;self.alive=True;self.defeat_day=None;self.defeat_cause=''
        self.reports={};self.ration_policy=protagonist_first

    @property
    def food(self):return self._food/2

    @property
    def water(self):return self._water/2

    def add_supplies(self,food,water):
        if min(food,water)<0 or food*2!=int(food*2) or water*2!=int(water*2):
            raise ValueError('Suprimentos devem ser nao negativos, em incrementos de 0,5')
        self._food+=int(food*2);self._water+=int(water*2)

    def change_sanity(self,delta):
        self.sanity=max(0,min(self.MAX_SANITY,self.sanity+delta))

    def predicted_needs(self,day,living_ids):
        """Previsao para a HUD, sem consumir ou modificar dias completos."""
        needs=self.people['protagonista']
        if day==1:return Needs()
        if day in self.reports:return Needs(needs.hunger,needs.thirst)
        ids=list(dict.fromkeys(living_ids))
        order=self.ration_policy(ids)
        if len(order)!=len(ids) or set(order)!=set(ids) or 'protagonista' not in ids:
            raise ValueError('Politica de racoes deve ordenar exatamente os moradores vivos')
        position=order.index('protagonista')
        return Needs(0 if self._food>position else min(needs.hunger+1,3),
                     0 if self._water>position else min(needs.thirst+1,2))

    def close_day(self,day,living_ids,company_seen=False):
        if day in self.reports:return self.reports[day]
        if not self.alive:raise ValueError('Partida encerrada')
        ids=list(dict.fromkeys(living_ids))
        order=self.ration_policy(ids)
        if len(order)!=len(ids) or set(order)!=set(ids) or 'protagonista' not in ids:
            raise ValueError('Politica de racoes deve ordenar exatamente os moradores vivos')
        before_food=self._food;before_water=self._water
        tolerance=day==1
        for person in order:
            needs=self.people.setdefault(person,Needs())
            if tolerance:continue
            fed=self._food>0;hydrated=self._water>0
            if fed:self._food-=1
            if hydrated:self._water-=1
            needs.hunger=0 if fed else needs.hunger+1
            needs.thirst=0 if hydrated else needs.thirst+1
        companion=company_seen or len(ids)>1
        self.loneliness=0 if companion else self.loneliness+1
        self.change_sanity(1 if companion else -1)
        needs=self.people['protagonista']
        cause=('A falta de água tornou impossível continuar.' if not tolerance and needs.thirst>=2 else
               'A falta de comida tornou impossível continuar.' if not tolerance and needs.hunger>=3 else
               'Cinco dias de solidão tornaram impossível continuar.' if self.loneliness>=5 else '')
        # Os dias completos sao registrados apenas aqui, depois da distribuicao.
        needs.thirst=min(needs.thirst,2)
        needs.hunger=min(needs.hunger,3)
        if cause:self.alive=False;self.defeat_day=day;self.defeat_cause=cause
        report=DailyReport(day,(before_food-self._food)/2,(before_water-self._water)/2,
                           len(ids),self.sanity,needs.hunger>0,needs.thirst>0,cause)
        self.reports[day]=report
        return report
