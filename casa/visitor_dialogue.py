"""Dialogos carregados separadamente dos estados e da apresentacao."""
import json
from .config import ROOT

class Dialogue:
    def __init__(self,visitor,session=None):
        self.visitor=visitor
        self.session=session
        self.data=json.loads((ROOT/f'dados/visitantes/{visitor.id}_dialogos.json').read_text(encoding='utf-8'))

    def intro(self):return '\n\n'.join(self.data['intro'])

    def answer(self,index):
        question=self.data['questions'][index]
        answer=question['answer']
        if question.get('ricardo_states') and self.session:
            ricardo=self.session.visitors.get('ricardo')
            state=('nao_encontrado' if ricardo is None or not ricardo.arrived else
                   'presente' if ricardo.state=='acolhido' and ricardo.alive else
                   'recusado' if ricardo.state=='rejeitado' else 'conhecido')
            answer=question['ricardo_states'].get(state,answer)
        if question.get('news_context') and self.session:
            published=self.session.knowledge.published.values()
            if published:
                day=max(item['day'] for item in published)
                answer+=' O noticiário que você acompanhou chegou ao dia {day}, mas nenhuma notícia isolada confirma um diagnóstico.'
                return answer.format(food=self.visitor.food,water=self.visitor.water,day=day)
        return answer.format(food=self.visitor.food,water=self.visitor.water)
