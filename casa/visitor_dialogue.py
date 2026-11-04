"""Dialogos carregados separadamente dos estados e da apresentacao."""
import json
from dataclasses import dataclass,field
from .config import ROOT

@dataclass
class ConversationProgress:
    asked: set[int] = field(default_factory=set)
    stage: str = 'intro'
    question: int | None = None
    answer_text: str = ''
    text_page: int = 0

class Dialogue:
    def __init__(self,visitor,session=None,resident=False):
        self.visitor=visitor
        self.session=session
        self.data=json.loads((ROOT/f'dados/visitantes/{visitor.id}_dialogos.json').read_text(encoding='utf-8'))
        if resident:
            self.data={**self.data,'intro':self.data.get('resident_intro',['Como você está?']),
                       'questions':self.data.get('resident_questions',[])}
        self.progress=visitor.conversations.setdefault('resident' if resident else 'door',ConversationProgress())

    def pending(self):
        return [i for i in range(len(self.data['questions'])) if i not in self.progress.asked][:2]

    def ask(self,index):
        if index not in self.pending():return False
        self.progress.answer_text=self.answer(index)
        self.progress.question=index
        self.progress.asked.add(index)
        self.progress.stage='answer';self.progress.text_page=0
        return True

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
