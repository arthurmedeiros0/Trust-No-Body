"""Calendario manual e pontos de extensao; nenhuma consequencia de sobrevivencia."""
from dataclasses import dataclass


@dataclass(frozen=True)
class DayEvent:
    day: int
    previous_day: int
    next_day: int


class DayCycle:
    LIMIT=20

    def __init__(self):
        self.day=1
        self.listeners={'day_end':[], 'day_start':[]}
        self._advancing=False
        self._closed_day=None
        self._can_advance=True
        self._closing=False

    def close_day(self):
        if self._closing:return False
        if self.day>=self.LIMIT:return False
        if self._closed_day==self.day:return self._can_advance
        self._closed_day=self.day;self._can_advance=True
        event=DayEvent(self.day,self.day,self.day+1)
        self._closing=True
        try:
            for callback in tuple(self.listeners['day_end']):
                if callback(event) is False:self._can_advance=False
        finally:self._closing=False
        return self._can_advance

    def subscribe(self,event,callback):
        self.listeners[event].append(callback)

    def advance(self):
        if self.day>=self.LIMIT or self._advancing or self._closing:return False
        self._advancing=True
        try:
            old=self.day;new=old+1
            if not self.close_day():return False
            self.day=new
            for callback in tuple(self.listeners['day_start']):callback(DayEvent(new,old,new))
            return True
        finally:self._advancing=False
