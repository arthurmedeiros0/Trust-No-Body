"""Validacao somente de leitura: cadastros incompletos nao entram na agenda."""
import json
from PIL import Image
from .config import ROOT,ROOMS

DIRECTIONS=('frente','costas','direita','esquerda')
FEATURES=('manchas_maos','dentes_deteriorados','olhos_alterados',
          'veias_escurecidas','palidez_anormal','tremores_involuntarios')


def readiness(definition):
    try:
        for field in ('id','name','age','profession','history','portrait_height','portrait_anchor',
                      'room_position','room_direction'):
            if field not in definition:raise ValueError('Campo ausente: '+field)
        if definition['room'] not in ROOMS:raise ValueError('Comodo desconhecido')
        base=ROOT/definition['asset_root']
        images=[base/definition['portrait']]
        images.extend(base/definition['sprites'][direction] for direction in DIRECTIONS)
        for feature in FEATURES:
            images.extend(base/definition['investigation'][feature][variant] for variant in ('normal','alterado'))
        dialogue=json.loads((ROOT/f"dados/visitantes/{definition['id']}_dialogos.json").read_text(encoding='utf-8'))
        if not dialogue['intro'] or not dialogue['questions']:raise ValueError('Dialogos incompletos')
        for question in dialogue['questions']:
            question['question'];question['answer'].format(food=2,water=2)
        if definition.get('internal_sprite_manifest'):
            manifest=json.loads((ROOT/definition['internal_sprite_manifest']).read_text(encoding='utf-8'))
            for direction in DIRECTIONS:
                frames=manifest['frames'][direction]
                if not frames:raise ValueError('Caminhada incompleta')
                images.extend(base/path for path in frames)
        elif definition.get('sheet_sprites'):
            images.extend(base/f'andando/{direction}/{number}.png' for direction in DIRECTIONS for number in range(1,4))
        else:
            manifest=json.loads((ROOT/definition['walk_manifest']).read_text(encoding='utf-8'))
            for direction in ('frente','costas','direita'):
                frames=manifest['frames'][direction]
                if not frames:raise ValueError('Caminhada incompleta')
                images.extend(base/'sprites_movimento'/frame['original'] for frame in frames)
        for path in images:
            with Image.open(path) as image:image.verify()
        return ''
    except (OSError,ValueError,KeyError,TypeError,IndexError) as error:
        return str(error)
