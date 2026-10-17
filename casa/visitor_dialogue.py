"""Dialogos carregados separadamente dos estados e da apresentacao."""
import json
from .config import ROOT

class Dialogue:
    def __init__(self,visitor):
        self.visitor=visitor
        self.data=json.loads((ROOT/f'dados/visitantes/{visitor.id}_dialogos.json').read_text(encoding='utf-8'))

    def intro(self):return '\n\n'.join(self.data['intro'])

    def answer(self,index):
        return self.data['questions'][index]['answer'].format(food=self.visitor.food,water=self.visitor.water)
