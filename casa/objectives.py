"""Orientação de exploração derivada do estado da partida, sem alterar suas regras."""
from dataclasses import dataclass


@dataclass(frozen=True)
class Objective:
    action: str
    hint: str = ''


class ObjectiveGuide:
    def __init__(self, session):
        self.session = session

    def current(self):
        session = self.session
        day = session.day
        intro = session.intro
        if day == 1 and not intro.fridge_checked:
            return Objective('Verifique a geladeira na cozinha.')

        bulletin = session.news.current(day)
        if not bulletin.read:
            if day == 4:
                return Objective('Assista ao noticiário na sala.', 'Novas características podem ser reveladas.')
            if day == 7:
                return Objective('Assista ao noticiário na sala.', 'Novas informações sobre a infecção podem ajudar.')
            return Objective('Assista ao noticiário na sala.')

        visitor = session.visitors.get(session.manager.current)
        if visitor and visitor.arrived and visitor.state == 'aguardando':
            if day == 1 and not intro.door_checked:
                return Objective('Investigue quem está na porta da entrada.')
            return Objective('Investigue o visitante na entrada e decida.', self._discovery_hint(bulletin))

        if day == 1 and not intro.door_checked:
            return Objective('Investigue quem está na porta da entrada.')
        return Objective('Volte ao quarto e durma para avançar.', self._discovery_hint(bulletin) or
                         ('Opcional: revise suas observações no diário.' if day == 5 else ''))

    def _discovery_hint(self, bulletin):
        if not bulletin.read:
            return ''
        medical = self.session.medical
        if not set(bulletin.investigations).issubset(medical.known):
            return ''
        if bulletin.id == 'boletim_04':
            return 'Opcional: investigue manchas nas mãos e dentes deteriorados.'
        if bulletin.id in ('boletim_07', 'boletim_14', 'boletim_17') and bulletin.id in self.session.knowledge.published:
            return 'Opcional: consulte o diário e compare os sintomas com o padrão divulgado.'
        new = [key for key in bulletin.investigations if key not in {
            feature for previous in self.session.news.bulletins if previous.day < bulletin.day and previous.read
            for feature in previous.investigations}]
        if new:
            return 'Opcional: investigue as novas características em visitantes e moradores.'
        return ''

    def opening(self):
        objective = self.current()
        return objective.action + (' ' + objective.hint if objective.hint else '')
