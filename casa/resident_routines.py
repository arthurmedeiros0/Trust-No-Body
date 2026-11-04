"""Pontos em coordenadas da arte e preferências de rotina, sem regras de infecção."""
from dataclasses import dataclass

CAPACITY={'sala':3,'cozinha':2,'corredor':2,'entrada':2,'banheiro':1}
# Locais de permanência revisados com as bases dos móveis. O gerenciador ainda
# valida colisão, conectividade e distância das interações em cada cenário.
ANCHORS={
    'sala':((860,575),(190,355),(610,285),(875,350),(210,540),(475,582)),
    'cozinha':((560,540),(1200,640),(500,785),(1180,790),(800,420),(1060,400)),
    'corredor':((420,232),(1000,234),(1320,232),(1050,250)),
    'entrada':((480,520),(480,650),(1060,580),(1080,755),(440,780)),
    'banheiro':((290,335),(420,355))}
OFFSETS=((0,0),(30,0),(-30,0),(0,24),(0,-24))

@dataclass(frozen=True)
class Profile:
    rooms: tuple
    speed: float=1.0
    wait: tuple=(3.0,6.0)
    social: str='neutro'

PROFILES={
    'ricardo':Profile(('sala','cozinha','entrada')),
    'laura':Profile(('corredor','sala','cozinha','banheiro'),wait=(2.5,5.0)),
    'antonio':Profile(('sala','cozinha','banheiro'),speed=.60,wait=(5.0,9.0)),
    'gabriel':Profile(('entrada','cozinha','corredor','sala'),wait=(2.5,5.5)),
    'helena':Profile(('sala','cozinha','corredor','banheiro'),speed=.85,wait=(4.0,7.0)),
    'daniel':Profile(('corredor','entrada','cozinha','banheiro'),social='reservado'),
    'marina':Profile(('cozinha','sala','corredor','banheiro'),social='proximo')}
