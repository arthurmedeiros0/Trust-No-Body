"""Editor por eventos reais do Pygame; persistencia isolada em temporarios."""
import copy
import json
import runpy
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import pygame
from support import exploration_house as House
from casa.config import ROOT,ROOMS
from casa.collision_data import load,save,validate
from casa.collisions import feet_rect

class EditorTests(unittest.TestCase):
    def setUp(self):
        self.game=House(development=True)
        self.game.change_room('sala');self.editor=self.game.editor
        self.key(pygame.K_F4)

    def key(self,key,mod=0):
        self.game.handle_event(pygame.event.Event(pygame.KEYDOWN,key=key,mod=mod))

    def mouse(self,kind,source):
        p=self.editor.screen_point(source);pos=(round(p.x),round(p.y))
        self.game.handle_event(pygame.event.Event(kind,pos=pos,button=1,buttons=(1,0,0),rel=(0,0)))

    def drag(self,start,end):
        self.mouse(pygame.MOUSEBUTTONDOWN,start)
        self.mouse(pygame.MOUSEMOTION,end)
        self.mouse(pygame.MOUSEBUTTONUP,end)

    def test_create_move_resize_cancel_and_delete(self):
        scene=self.game.scene;initial=len(scene.collision_data['obstacles'])
        interactions=copy.deepcopy(scene.config['interactions'])
        self.drag((480,580),(530,610))
        self.assertEqual(len(scene.collision_data['obstacles']),initial+1)
        rect=scene.collision_data['obstacles'][-1]['rect']
        self.assertAlmostEqual(rect[2],50,delta=2)
        self.drag((505,595),(535,585))
        moved=copy.deepcopy(scene.collision_data['obstacles'][-1]['rect'])
        self.assertAlmostEqual(moved[0],510,delta=2)
        self.assertAlmostEqual(moved[1],570,delta=2)
        x,y,w,h=moved
        self.drag((x+w,y+h),(x+w+15,y+h+8))
        resized=copy.deepcopy(scene.collision_data['obstacles'][-1]['rect'])
        self.assertGreater(resized[2],moved[2]);self.assertGreater(resized[3],moved[3])
        x,y,w,h=resized
        self.mouse(pygame.MOUSEBUTTONDOWN,(x+w/2,y+h/2))
        self.mouse(pygame.MOUSEMOTION,(x+w/2+15,y+h/2))
        self.key(pygame.K_ESCAPE)
        self.assertTrue(self.editor.active)
        self.assertEqual(scene.collision_data['obstacles'][-1]['rect'],resized)
        self.mouse(pygame.MOUSEBUTTONDOWN,(x+w/2,y+h/2))
        self.mouse(pygame.MOUSEBUTTONUP,(x+w/2,y+h/2))
        self.key(pygame.K_DELETE)
        self.assertEqual(len(scene.collision_data['obstacles']),initial)
        self.assertEqual(scene.config['interactions'],interactions)
        self.key(pygame.K_ESCAPE);self.assertFalse(self.editor.active)

    def test_save_reload_backup_and_invalid_data(self):
        with tempfile.TemporaryDirectory() as tmp:
            data=self.game.scene.collision_data
            save(data,tmp);original=Path(tmp,'sala.json').read_bytes()
            self.drag((480,580),(530,610))
            with patch('casa.collision_editor.save',side_effect=lambda data:save(data,tmp)):
                self.key(pygame.K_s,pygame.KMOD_CTRL)
            loaded=load('sala',self.game.scene.source_size,tmp)
            self.assertEqual(loaded,self.game.scene.collision_data)
            backups=list(Path(tmp,'backups').glob('sala_*.json'))
            self.assertEqual(len(backups),1);self.assertEqual(backups[0].read_bytes(),original)
            self.assertIn('Salvo:',self.editor.message)
            self.assertNotIn('sala',self.editor.dirty)
            invalid=copy.deepcopy(loaded);invalid['obstacles'][0]['rect'][2]=-1
            before=Path(tmp,'sala.json').read_bytes()
            with self.assertRaises(ValueError):save(invalid,tmp)
            self.assertEqual(Path(tmp,'sala.json').read_bytes(),before)

    def test_editor_camera_all_rooms_and_floor(self):
        for name in ROOMS:
            self.game.change_room(name);self.editor.pan.update(0,0)
            point=pygame.Vector2(ROOMS[name]['spawn'])
            self.assertLess(self.editor.source(self.editor.screen_point(point)).distance_to(point),2)
            self.game.draw(pygame.display.get_surface())
        self.game.change_room('corredor')
        before=self.editor.camera().x
        self.key(pygame.K_RIGHT)
        self.assertNotEqual(before,self.editor.camera().x)
        p=(1100,245)
        self.assertLess(self.editor.source(self.editor.screen_point(p)).distance_to(p),2)
        self.game.change_room('banheiro');self.editor.pan.update(0,0)
        self.key(pygame.K_p)
        original=copy.deepcopy(self.game.scene.collision_data)
        vertex=original['floor_polygon'][0]
        self.drag(vertex,(vertex[0]+5,vertex[1]))
        self.assertNotEqual(self.game.scene.collision_data['floor_polygon'],original['floor_polygon'])
        self.assertEqual(self.game.scene.collision_data['obstacles'],original['obstacles'])
        self.key(pygame.K_F3);self.assertTrue(self.game.debug)
        period=self.game.period;self.key(pygame.K_F6);self.assertNotEqual(period,self.game.period)

    def test_development_only_and_import_preservation(self):
        production=House()
        production.handle_event(pygame.event.Event(pygame.KEYDOWN,key=pygame.K_F4))
        self.assertIsNone(production.editor)
        before=runpy.run_path(str(ROOT/'backups/colisoes_antes_editor/config.py'))
        for name,cfg in ROOMS.items():
            if name=='entrada':continue  # Novo ambiente, ausente no backup historico.
            legacy=before['ROOMS'][name]
            for key in ('art_scale','source_size','spawn','interactions'):
                actual=cfg[key][:1] if name=='sala' and key=='interactions' else cfg[key]
                if key=='interactions':
                    # Apenas a orientacao de chegada mudou nesta etapa.
                    actual=[{k:v for k,v in item.items() if k!='direction'} for item in actual]
                expected=copy.deepcopy(legacy[key])
                if name=='quarto' and key=='interactions':
                    # A TV ganhou interface; pontos, portas e cama nao mudaram.
                    tv=next(item for item in expected if item['label']=='Televisao')
                    tv['action']='television';tv.pop('text',None)
                    next(item for item in expected if item['label']=='Cama')['region']=(232,125,131,215)
                if name=='cozinha' and key=='interactions':
                    fridge=next(item for item in expected if item['label']=='Geladeira')
                    fridge['action']='fridge';fridge.pop('text',None)
                self.assertEqual(actual,expected)
            original=json.loads((ROOT/f'backups/colisoes_antes_editor/{name}.json').read_text(encoding='utf-8'))
            current=load(name,cfg['source_size'])
            if name not in ('banheiro','sala'):self.assertEqual(current,original)
            else:self.assertTrue({obj['id'] for obj in original['obstacles']}.issubset({obj['id'] for obj in current['obstacles']}))

    def test_sofa_and_table_stop_feet_and_passage_is_free(self):
        game=self.game;scene=game.scene;self.editor.active=False
        for start,vector in [((480,580),(0,-1)),((480,425),(0,1))]:
            game.player.feet=scene.point(start)
            game.update(vector,1)
            self.assertTrue(scene.collisions.allows(game.player.feet))
            rect=feet_rect(game.player.feet)
            sofa=pygame.Rect(scene.transform_rect(next(o['rect'] for o in scene.collision_data['obstacles'] if o['id']=='sofa')))
            self.assertFalse(rect.colliderect(sofa))
        # A antiga posicao sobre o sofa agora e bloqueada.
        self.assertFalse(scene.collisions.allows(scene.point((480,450))))
        self.assertTrue(scene.collisions.allows(scene.point((480,425))))
