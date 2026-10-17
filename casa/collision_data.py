"""Persistencia validada de colisoes em coordenadas originais."""
import copy
import json
import math
import shutil
from datetime import datetime
from pathlib import Path
from .config import ROOT

DATA_DIR=ROOT/'colisoes'

def validate(data, room, source_size):
    if data.get('version')!=1 or data.get('room')!=room or tuple(data.get('source_size',()))!=tuple(source_size):
        raise ValueError('Cabecalho de colisoes invalido: '+room)
    def numbers(values,n):
        return isinstance(values,(list,tuple)) and len(values)==n and all(isinstance(v,(int,float)) and not isinstance(v,bool) and math.isfinite(v) for v in values)
    def rect(values):
        return numbers(values,4) and values[0]>=0 and values[1]>=0 and values[2]>0 and values[3]>0 and values[0]+values[2]<=source_size[0] and values[1]+values[3]<=source_size[1]
    if not rect(data.get('floor')):raise ValueError('Piso invalido')
    polygon=data.get('floor_polygon')
    if polygon is not None and (len(polygon)<3 or not all(numbers(p,2) and 0<=p[0]<=source_size[0] and 0<=p[1]<=source_size[1] for p in polygon)):
        raise ValueError('Poligono invalido')
    ids=set()
    for obj in data['obstacles']:
        if not isinstance(obj.get('id'),str) or not obj['id'] or obj['id'] in ids or not rect(obj.get('rect')):
            raise ValueError('Obstaculo invalido ou duplicado')
        ids.add(obj['id'])
    return copy.deepcopy(data)

def load(room,source_size,directory=DATA_DIR):
    path=Path(directory)/(room+'.json')
    try:return validate(json.loads(path.read_text(encoding='utf-8')),room,source_size)
    except (OSError,ValueError,KeyError,TypeError) as error:
        raise ValueError(f'Falha ao carregar {path}: {error}') from error

def save(data,directory=DATA_DIR):
    data=validate(data,data['room'],data['source_size'])
    folder=Path(directory);folder.mkdir(parents=True,exist_ok=True)
    target=folder/(data['room']+'.json')
    if target.exists():
        backups=folder/'backups';backups.mkdir(exist_ok=True)
        shutil.copy2(target,backups/(data['room']+'_'+datetime.now().strftime('%Y%m%d_%H%M%S_%f')+'.json'))
    temporary=target.with_suffix('.json.tmp')
    try:
        temporary.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        temporary.replace(target)
    finally:
        if temporary.exists():temporary.unlink()
