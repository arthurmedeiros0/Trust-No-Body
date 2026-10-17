"""Boletins narrativos e estados da partida; sem inferencias ou diagnosticos."""
from dataclasses import dataclass
import json
from .config import ROOT


@dataclass
class Bulletin:
    id: str
    day: int
    headline: str
    paragraphs: list[str]
    available: bool=False
    read: bool=False


class NewsArchive:
    def __init__(self,knowledge):
        self.knowledge=knowledge
        self.on_watch=[]
        self.bulletins=[Bulletin(**row) for row in json.loads((ROOT/'dados/noticiarios.json').read_text(encoding='utf-8'))]
        if sorted(b.day for b in self.bulletins)!=list(range(1,21)) or len({b.id for b in self.bulletins})!=20:
            raise ValueError('Necessario um boletim unico por dia, de 1 a 20')
        self.unlock(1)

    def unlock(self,day):
        for bulletin in self.bulletins:bulletin.available=bulletin.day<=day

    def current(self,day):
        return next(b for b in self.bulletins if b.day==day and b.available)

    def watch(self,bulletin):
        if bulletin not in self.bulletins or not bulletin.available:return False
        first=not bulletin.read
        bulletin.read=True
        self.knowledge.published[bulletin.id]=dict(id=bulletin.id,day=bulletin.day,headline=bulletin.headline)
        if first:
            for callback in tuple(self.on_watch):callback(bulletin)
        return True

    @property
    def history(self):return [b for b in self.bulletins if b.read and b.available]
