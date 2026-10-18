"""Sinais aprendidos e observados; nenhuma classificacao de infeccao."""
LABELS={
    'manchas_maos':'Manchas nas mãos',
    'dentes_deteriorados':'Deterioração dos dentes',
    'olhos_alterados':'Alterações nos olhos',
    'veias_escurecidas':'Veias escurecidas no pescoço',
    'palidez_anormal':'Palidez anormal',
    'tremores_involuntarios':'Tremores involuntários'}


class MedicalKnowledge:
    def __init__(self):
        self.known=set()
        self.observations={}
        self.discoveries=[]

    def learn(self,features):
        new=[key for key in LABELS if key in features and key not in self.known]
        self.known.update(new)
        self.discoveries.extend(new)
        return new

    def observe(self,visitor,feature):
        if feature not in self.known:raise PermissionError('Investigacao ainda desconhecida')
        self.observations.setdefault(visitor.id,{})[feature]=visitor.symptoms[feature]
        visitor.examined.add(feature)

    def status(self,visitor_id,feature):
        if feature not in self.known:return 'desconhecido'
        observed=self.observations.get(visitor_id,{})
        if feature not in observed:return 'nao_observado'
        return 'presente' if observed[feature] else 'ausente'

    def take_notice(self):
        if not self.discoveries:return ''
        names=[LABELS[key] for key in dict.fromkeys(self.discoveries)]
        self.discoveries.clear()
        return ('NOVAS INVESTIGAÇÕES DISPONÍVEIS. Você aprendeu a observar: '+
                '; '.join(names)+'. Essas características agora podem ser investigadas em visitantes e moradores.')
