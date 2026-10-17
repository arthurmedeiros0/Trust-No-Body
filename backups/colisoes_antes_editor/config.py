"""Coordenadas em pixels das imagens originais; nunca da janela.
Retangulos: (x, y, largura, altura). Pontos: (x, y).
Colisoes aproximadas da base dos moveis; F3 permite revisar sobre a arte.
"""
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
WINDOW = (1280, 720)
VIEWPORT = (20, 65, 1240, 610)
FPS = 60
SPEED = 220
FRAME_TIME = .14
# Escala de exibicao comum; art_scale normaliza unidades da arte, nao o jogador.
SCENE_SCALE = 1.0
PLAYER_SIZE = (64, 96)
PLAYER_FOOT_Y = 94
PLAYER_HITBOX = (20, 10)
SHADOW_SIZE = (34, 12)
SHADOW_OPACITY = 65
SHADOW_OFFSET_Y = 2
INTERACTION_RADIUS = 58
LATERAL_CYCLE = (0, None, 1, None, 2, None)
CORRIDOR_RETURN_Y = 235
DOOR_X = {'sala': 294, 'quarto': 569, 'cozinha': 1160, 'banheiro': 1431}
ROOMS = {
 'corredor': {
  'images': {'dia':'corredor_dia.png','noite':'corredor_noite.png'},
  'source_size': (1727,311), 'art_scale': .90,
  'floor': (125,174,1480,105),
  'floor_polygon': [(125,174),(1605,174),(1605,250),(1545,250),
                    (1545,274),(183,274),(183,250),(125,250)],
  'blocks': [(135,174,65,35),(754,174,198,37),(1527,174,61,36)],
  'spawn': (650,246),
  'interactions': [dict(label=name.capitalize(),point=(x,193),action='door',target=name) for name,x in DOOR_X.items()],
 },
 'quarto': {
  'images': {'dia':'quarto_dia.png','noite':'quarto_noite.png'},
  'source_size': (747,561), 'art_scale': .88,
  'floor': (62,190,622,309),
  'blocks': [(62,435,271,64),(473,435,211,64), (232,190,131,150),
             (183,190,57,26),(367,190,42,7),(434,190,205,16),
             (62,202,51,106),(103,374,79,62),(614,294,60,136),(619,197,44,68)],
  'named_blocks': {'cadeira': (582,343,34,67),
                   'cabideiro': (68,337,33,37)},
  'spawn': (403,452),
  'interactions': [dict(label='Voltar ao corredor',point=(403,482),action='exit'),
    dict(label='Televisao',point=(110,267),action='message',text='Noticiario: a cidade segue em silencio. Novas noticias em breve.'),
    dict(label='Cama',point=(299,339),action='sleep')],
 },
 'cozinha': {
  'images': {'dia':'cozinha_dia.png','noite':'cozinha_noite.png'},
  'source_size': (747,561), 'art_scale': .90,
  'floor': (42,221,660,316),
  'blocks': [(42,469,277,68),(439,469,263,68),(48,221,106,36),
    (205,221,433,12),(638,221,67,15),(235,277,153,148),
    (46,302,48,113),(665,305,37,139),(63,417,34,42)],
  'spawn': (379,488),
  'interactions': [dict(label='Voltar ao corredor',point=(379,519),action='exit'),
    dict(label='Geladeira',point=(668,237),action='message',text='Estoque: verificacao de alimentos ainda nao implementada.')],
 },
 'banheiro': {
  'images': {'dia':'banheiro_dia.png','noite':'banheiro_noite.png'},
  'source_size': (747,561), 'art_scale': .92,
  'floor': (178,190,393,345),
  'floor_polygon': [(178,190),(571,190),(571,433),(471,433),
                    (471,475),(410,475),(410,535),(334,535),
                    (334,475),(275,475),(275,433),(178,433)],
  'blocks': [],
  # Bases individuais: as lacunas entre os moveis continuam transitaveis.
  'named_blocks': {'pia_armario': (220,190,123,54),
                   'vaso': (374,202,53,48),
                   'lixeira': (433,228,28,22),
                   'box': (474,151,92,211),
                   'planta_estante': (179,246,42,39),
                   'estante': (179,286,43,79),
                   'cesto_esquerdo': (181,370,52,63),
                   'cesto_direito': (508,357,55,75)},
  'spawn': (374,478),
  'interactions': [dict(label='Voltar ao corredor',point=(374,516),action='exit')],
 },
 'sala': {
  'images': {'dia':'trust_no_body_sala_dia_corrigida.png',
             'noite':'trust_no_body_sala_noite_corrigida.png'},
  'source_size': (1053,724),
  # Calibracao pela altura visual dos moveis; jogador permanece 64 x 96.
  'art_scale': .68,
  'floor': (80,245,925,435),
  'blocks': [(80,617,191,63),(414,617,591,63),
             (94,245,35,19),(137,245,136,15),(302,245,36,13),
             (934,365,68,105),(936,480,69,137),
             (80,444,40,124)],
  'named_blocks': {'sofa': (285,477,382,74),
                   'mesa_centro': (370,372,220,36),
                   'poltrona': (697,379,139,64),
                   'mesinha_lateral': (685,477,94,49)},
  'spawn': (343,636),
  'reserved_door': (826,244),
  'interactions': [dict(label='Voltar ao corredor',point=(343,663),action='exit')],
 },
}
