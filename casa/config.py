"""Coordenadas em pixels das imagens originais; nunca da janela.
Retangulos: (x, y, largura, altura). Pontos: (x, y).
Colisoes: arquivos colisoes/*.json. Backup inicial: backups/colisoes_antes_editor/.
"""
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
WINDOW = (1280, 720)
VIEWPORT = (20, 65, 1240, 610)
FPS = 60
SPEED = 220
FRAME_TIME = .14
PLAYER_ASSET_ROOT = ROOT/'personagens/protagonista/classicos'
PLAYER_LATERAL_CYCLE = (0, None, 1, None, 2, None)
# Escala de exibicao comum; art_scale normaliza unidades da arte, nao o jogador.
SCENE_SCALE = 1.0
PLAYER_SIZE = (64, 96)
PLAYER_FOOT_Y = 94
PLAYER_HITBOX = (20, 10)
SHADOW_SIZE = (34, 12)
SHADOW_OPACITY = 65
SHADOW_OFFSET_Y = 2
INTERACTION_RADIUS = 58
LATERAL_CYCLE = {'direita': (None, 0, None, 2),
                 'esquerda': (None, 1, None, 2)}
CORRIDOR_RETURN_Y = 235
DOOR_X = {'sala': 294, 'quarto': 569, 'cozinha': 1160, 'banheiro': 1431}
ROOMS = {
 'corredor': {
  'images': {'dia':'corredor_dia.png','noite':'corredor_noite.png'},
  'source_size': (1727,311), 'art_scale': .90,
  'spawn': (650,246),
  'interactions': [dict(label=name.capitalize(),point=(x,193),action='door',target=name,
                        direction='costas')
                   for name,x in DOOR_X.items()],
 },
 'quarto': {
  'images': {'dia':'quarto_dia.png','noite':'quarto_noite.png'},
  'source_size': (747,561), 'art_scale': .88,
  'spawn': (403,452),
  'interactions': [dict(label='Voltar ao corredor',point=(403,482),action='exit',direction='frente'),
    dict(label='Televisao',point=(110,267),action='television'),
    dict(label='Cama',point=(299,339),region=(232,125,131,215),action='sleep')],
 },
 'cozinha': {
  'images': {'dia':'cozinha_dia.png','noite':'cozinha_noite.png'},
  'source_size': (747,561), 'art_scale': .90,
  'spawn': (379,488),
  'interactions': [dict(label='Voltar ao corredor',point=(379,519),action='exit',direction='frente'),
    dict(label='Geladeira',point=(668,237),action='fridge')],
 },
 'banheiro': {
  'images': {'dia':'banheiro_dia.png','noite':'banheiro_noite.png'},
  'source_size': (747,561), 'art_scale': .92,
  # Bases individuais: as lacunas entre os moveis continuam transitaveis.
  'spawn': (374,478),
  'interactions': [dict(label='Voltar ao corredor',point=(374,516),action='exit',direction='frente')],
 },
 'sala': {
  'images': {'dia':'trust_no_body_sala_dia_corrigida.png',
             'noite':'trust_no_body_sala_noite_corrigida.png'},
  'source_size': (1053,724),
  # Calibracao pela altura visual dos moveis; jogador permanece 64 x 96.
  'art_scale': .68,
  'spawn': (343,636),
  'upper_door': (826,244),
  'interactions': [dict(label='Voltar ao corredor',point=(343,663),action='exit',direction='frente'),
    dict(label='Entrar na Entrada',point=(826,244),action='passage',target='entrada',direction='costas')],
 },
 'entrada': {
  'images': {'dia':'dia.png','noite':'noite.png'},
  'source_size': (1536,1024), 'art_scale': .50,
  'spawn': (768,870),
  'interactions': [dict(label='Voltar a sala',point=(768,925),action='passage',target='sala',arrival=(826,274),direction='frente'),
    dict(label='Olhar pelo olho mágico',point=(768,402),action='peephole',prompt='[E] Olhar pelo olho mágico')],
 },
}
# Cena frontal independente. Visitante vazio por enquanto; coordenadas da tela.
PEEPHOLE_IMAGES = {'dia':'dia.png','noite':'noite.png'}
PEEPHOLE_VIEWPORT = (20,65,1240,570)
FUTURE_VISITOR_POSITION = (640,620)
FUTURE_VISITOR_SCALE = 1.0
