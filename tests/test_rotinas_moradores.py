"""Distribuição, segurança, rotinas diárias e integração das três etapas."""
import os
os.environ.setdefault('SDL_VIDEODRIVER','dummy');os.environ.setdefault('SDL_AUDIODRIVER','dummy')
import copy
import random
import unittest
from collections import deque
from unittest.mock import patch,Mock
import pygame
from casa.game import House
from casa.days import DayEvent
from casa.resident import Resident,ActorCollisions,clear_segment
from casa.resident_manager import ResidentManager
from casa.resident_routines import CAPACITY
from casa.collisions import feet_rect

ORDER=('ricardo','laura','antonio','gabriel','helena','daniel','marina')

class RoutineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):pygame.init();pygame.display.set_mode((1280,720))

    def setUp(self):
        self.g=House();self.g.dialog='';self.g.resident_manager.rng=random.Random(13)
        self.s=self.g.visitor_session;self.m=self.g.resident_manager

    def accept(self,key):
        v=self.s.visitors[key];v.arrived=True;self.s.manager.seen.add(key)
        self.s._arrive(v);self.s.manager.current=key
        self.assertTrue(self.g.decide_visitor(v,'acolhido'));return self.g.residents[key]

    def all(self):
        for key in ORDER:self.accept(key)

    def snapshot(self):return {key:(a.room,tuple(a.feet)) for key,a in self.g.residents.items()}

    def assert_safe(self):
        for key,a in self.g.residents.items():
            self.assertIn(a.room,CAPACITY);self.assertNotEqual(a.room,'quarto')
            self.assertTrue(self.g.scenes[a.room].collisions.allows(a.feet))
            self.assertTrue(self.m.reachable(self.g.scenes[a.room],a.feet))
            for door in self.m.reserved[a.room]:self.assertGreaterEqual(a.feet.distance_to(door),self.m.CLEARANCE-.001)
            self.assertIs(self.g.resident_positions[key],a.feet)
        for room,capacity in CAPACITY.items():
            actors=[a for a in self.g.residents.values() if a.room==room]
            self.assertLessEqual(len(actors),capacity)
            for i,a in enumerate(actors):
                for b in actors[i+1:]:self.assertFalse(feet_rect(a.feet).colliderect(feet_rect(b.feet)))

    def approach(self,actor):
        self.g.change_room(actor.room);self.g.dialog='';self.s.medical.discoveries.clear()
        for offset in ((35,0),(-35,0),(0,28),(0,-28),(45,20),(-45,20)):
            point=actor.feet+pygame.Vector2(offset)
            if not self.g.scene.collisions.allows(point):continue
            if feet_rect(point).colliderect(feet_rect(actor.feet)):continue
            self.g.player.feet=point
            item=self.g.nearest_interaction()
            if item and item.action=='resident' and item.target==actor.visitor_id:return
        self.fail('Sem acesso ao morador '+actor.visitor_id)

    def test_seven_coexist_in_different_safe_rooms_without_bedroom_or_street(self):
        self.all();self.assertEqual(len(self.g.residents),7)
        self.assertGreaterEqual(len(set(a.room for a in self.g.residents.values())),3)
        self.assert_safe();self.assertEqual(set(self.s.journal.cases),set(ORDER))
        self.assertFalse(self.g.peephole.visitor_ui.visitor.state=='aguardando')
        self.assertEqual(self.m.locations,{key:a.room for key,a in self.g.residents.items()})

    def test_every_allowed_room_has_reachable_valid_points_and_safe_routes(self):
        self.assertEqual(set(self.m.nodes),set(CAPACITY))
        for room,nodes in self.m.nodes.items():
            self.assertTrue(nodes,room)
            for node in nodes:
                self.assertTrue(self.m.static_safe(room,node.feet))
                for point in node.waypoints:
                    self.assertTrue(self.m.static_safe(room,point))
                    self.assertTrue(clear_segment(node.feet,point,self.g.scenes[room].collisions.allows))

    def test_state_is_stable_when_player_leaves_returns_and_renders(self):
        self.all();before=self.snapshot();objects=dict(self.g.residents)
        for room in self.g.scenes:
            self.g.change_room(room);self.g.draw(pygame.display.get_surface())
        self.assertEqual(before,self.snapshot())
        for key,a in objects.items():self.assertIs(self.g.residents[key],a)

    def test_real_new_day_changes_routines_once_but_f6_does_not(self):
        self.all();self.s.survival.add_supplies(100,100);self.s.intro.broadcast_seen=True
        before=self.snapshot();runs=self.m.planning_runs
        self.assertTrue(self.s.days.advance());self.assertEqual(self.m.last_day,2)
        self.assertEqual(self.m.planning_runs,runs+1);self.assertNotEqual(before,self.snapshot());self.assert_safe()
        after=self.snapshot();self.m.start_day(DayEvent(2,1,2));self.assertEqual(after,self.snapshot())
        for _ in range(4):self.g.handle_event(pygame.event.Event(pygame.KEYDOWN,key=pygame.K_F6))
        self.assertEqual(after,self.snapshot());self.assertEqual(self.m.planning_runs,runs+1)

    def test_daily_changes_never_teleport_visible_people_or_spawn_into_view(self):
        self.all();self.g.change_room('sala')
        visible={key:tuple(a.feet) for key,a in self.g.residents.items() if a.room=='sala'}
        hidden={key for key,a in self.g.residents.items() if a.room!='sala'}
        self.m.start_day(DayEvent(3,2,3))
        for key,feet in visible.items():self.assertEqual((self.g.residents[key].room,tuple(self.g.residents[key].feet)),('sala',feet))
        for key in hidden:self.assertNotEqual(self.g.residents[key].room,'sala')
        self.assert_safe()

    def test_many_daily_plans_remain_safe_and_reuse_actor_instances(self):
        self.all();objects=dict(self.g.residents);layouts=set()
        for day in range(2,21):
            self.m.start_day(DayEvent(day,day-1,day));self.assert_safe()
            layouts.add(tuple((key,a.room) for key,a in self.g.residents.items()))
            for key,a in objects.items():self.assertIs(self.g.residents[key],a)
        self.assertGreater(len(layouts),3)

    def test_profiles_give_retired_resident_slower_steps_and_longer_pauses(self):
        doctor=self.accept('ricardo');retired=self.accept('antonio')
        self.assertLess(retired.speed,doctor.speed)
        self.assertGreater(retired.wait_range[0],doctor.wait_range[0])
        self.assertIsNotNone(retired.waypoints)

    def test_no_per_frame_planning_no_image_reload_and_offscreen_actors_frozen(self):
        self.all();self.g.change_room('sala');runs=self.m.planning_runs;builds=self.m.geometry_builds
        offscreen={key:(tuple(a.feet),a.remaining) for key,a in self.g.residents.items() if a.room!='sala'}
        with patch.object(self.m,'_place',side_effect=AssertionError('Planejamento por frame')),patch.object(self.m,'refresh_geometry',side_effect=AssertionError('Geometria por frame')),patch('pygame.image.load',side_effect=AssertionError('Imagem recarregada')):
            for _ in range(120):self.g.update((0,0),1/60);self.g.draw(pygame.display.get_surface())
        self.assertEqual(runs,self.m.planning_runs);self.assertEqual(builds,self.m.geometry_builds)
        for key,state in offscreen.items():self.assertEqual(state,(tuple(self.g.residents[key].feet),self.g.residents[key].remaining))

    def test_walks_never_cross_furniture_player_or_other_npcs(self):
        self.all();moved=set()
        for room in CAPACITY:
            self.g.change_room(room)
            for _ in range(720):
                before={key:a.feet.copy() for key,a in self.g.residents.items()}
                self.g.update((0,0),1/30)
                self.assert_safe()
                for key,a in self.g.residents.items():
                    if a.feet!=before[key]:moved.add(key)
                    self.assertLessEqual(a.feet.distance_to(before[key]),a.speed/30+.001)
                    if a.room==room:self.assertFalse(feet_rect(a.feet).colliderect(feet_rect(self.g.player.feet)))
        self.assertEqual(moved,set(ORDER))

    def test_waypoint_direction_animation_stop_and_blocked_movement_recovery(self):
        a=self.accept('ricardo');self.g.change_room(a.room)
        a.remaining=0;self.g.update((0,0),.05)
        self.assertTrue(a.walking);self.assertEqual(a.animation_state,'walk')
        expected='direita' if a.velocity.x>0 else 'esquerda' if a.velocity.x<0 else 'frente' if a.velocity.y>0 else 'costas'
        self.assertEqual(a.direction,expected)
        assets=self.g.visitor_assets[a.visitor_id];self.assertIn(a.image(assets),assets.cycles[a.direction])
        before=a.feet.copy()
        blocked=ActorCollisions(self.g.scene.collisions,[feet_rect(a.feet).inflate(60,60)])
        a.update(.2,blocked);self.assertEqual(a.feet,before);self.assertEqual(a.animation_state,'idle')
        a.remaining=0;a.update(.1,ActorCollisions(self.g.scene.collisions));self.assertNotEqual(a.feet,before)
        a.rest();direction=a.direction;self.assertIs(a.image(assets),assets.sprites[direction])

    def test_large_steps_do_not_tunnel_and_player_cannot_cross_resident(self):
        a=self.accept('ricardo');self.g.change_room(a.room)
        a.remaining=0
        for _ in range(30):
            self.g.update((0,0),2.0)
            self.assertTrue(self.g.scene.collisions.allows(a.feet))
            for door in a.reserved:self.assertGreaterEqual(a.feet.distance_to(door),self.m.CLEARANCE-.001)
        a.remaining=100;a.rest();a.remaining=100
        self.g.player.feet=a.feet-pygame.Vector2(45,0)
        for _ in range(90):
            self.g.update((1,0),1/60)
            self.assertFalse(feet_rect(a.feet).colliderect(feet_rect(self.g.player.feet)))

    def test_all_allowed_room_interactions_and_journal_preserve_progress(self):
        a=self.accept('ricardo');v=self.s.visitors['ricardo'];self.s.medical.learn(v.symptoms);self.s.medical.discoveries.clear()
        for room in CAPACITY:
            node=self.m.nodes[room][0]
            a.room=room;a.feet.update(node.feet);a.origin.update(node.feet);a.waypoints=[pygame.Vector2(p) for p in node.waypoints];a.reserved=self.m.reserved[room]
            self.approach(a);a.remaining=0;self.m.update(room,.05)
            self.approach(a);before=a.feet.copy();self.g.interact();view=self.g.resident_ui
            self.assertIsNotNone(view);self.assertEqual(a.animation_state,'idle')
            self.assertTrue({'talk','investigate','eliminate','back'}<=set(view.layout()))
            self.g.update((1,1),1);self.assertEqual(a.feet,before)
            view.dialogue.ask(view.dialogue.pending()[0]) if view.dialogue.pending() else None
            asked=set(view.dialogue.progress.asked)
            view.page='investigate';feature='manchas_maos'
            view.handle_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN,button=1,pos=view.layout()[feature][0].center))
            self.g.handle_event(pygame.event.Event(pygame.KEYDOWN,key=pygame.K_j));self.assertTrue(self.g.journal_ui.active)
            self.g.handle_event(pygame.event.Event(pygame.KEYDOWN,key=pygame.K_ESCAPE))
            self.assertIs(self.g.resident_ui,view);self.assertEqual(view.page,'image');self.assertEqual(view.feature,feature)
            self.assertEqual(asked,view.dialogue.progress.asked)
            self.assertEqual(self.s.journal.cases[v.id].marks[feature],'Não verificado')
            self.g.resident_ui=None

    def test_interaction_cannot_cross_solid_armrest_or_room_boundary(self):
        a=self.accept('ricardo');self.g.change_room('sala')
        a.feet.update(self.g.scene.point((326,420)));self.g.player.feet=self.g.scene.point((269,420))
        self.assertTrue(self.g.scene.collisions.allows(a.feet));self.assertTrue(self.g.scene.collisions.allows(self.g.player.feet))
        self.assertLess(a.feet.distance_to(self.g.player.feet),58)
        self.assertFalse(self.m.can_interact(a));self.g.interact();self.assertIsNone(self.g.resident_ui)
        a.room='corredor';self.assertFalse(self.m.can_interact(a))
        self.assertFalse(self.g.nearest_interaction() and self.g.nearest_interaction().action=='resident')

    def test_dynamic_room_controls_draw_not_static_definition(self):
        a=self.accept('ricardo');original=self.s.visitors['ricardo'].definition['room']
        node=self.m.nodes['entrada'][0];a.room='entrada';a.feet.update(node.feet)
        self.assertEqual(original,'sala')
        with patch.object(a,'image',wraps=a.image) as image:
            self.g.change_room('sala');self.g.draw(pygame.display.get_surface());image.assert_not_called()
            self.g.change_room('entrada');self.g.draw(pygame.display.get_surface());self.assertTrue(image.called)

    def test_elimination_any_room_removes_motion_and_preserves_diary_sanity(self):
        self.all();a=self.g.residents['marina'];v=self.s.visitors['marina'];record=self.s.journal.cases[v.id]
        record.notes='Registro preservado';self.g.change_room(a.room)
        old_sanity=self.s.survival.sanity;self.assertTrue(self.g.eliminate_resident(v,'eliminado'))
        self.assertNotIn(v.id,self.g.residents);self.assertNotIn(v.id,self.g.resident_positions)
        self.assertEqual(a.animation_state,'idle');self.assertFalse(a.walking)
        self.assertEqual(record.notes,'Registro preservado');self.assertEqual(record.situation,'eliminado')
        self.assertEqual(self.s.survival.sanity,old_sanity-(2 if v.diagnosis=='infectado' else 3))
        self.m.start_day(DayEvent(2,1,2));self.assertNotIn(v.id,self.g.residents)
        self.g.journal_ui.open(v.id);self.g.journal_ui.draw(pygame.display.get_surface())
        self.assertTrue(any(key==v.id for _,key,_ in self.g.journal_ui.struck_names))

    def test_external_elimination_is_cleaned_and_stops_occupying_space(self):
        a=self.accept('ricardo');self.assertTrue(self.s.eliminate('ricardo'))
        self.g.update((0,0),.01)
        self.assertNotIn('ricardo',self.m.actors);self.assertFalse(a.walking)

    def test_failed_placement_is_atomic_and_safe_alternative_is_used(self):
        v=self.s.visitors['ricardo'];v.arrived=True;self.s.manager.current=v.id
        before=(v.state,self.s.survival.food,self.s.survival.water,len(self.s.decisions))
        with patch.object(self.m,'_place',return_value=None):self.assertFalse(self.g.decide_visitor(v,'acolhido'))
        self.assertEqual(before,(v.state,self.s.survival.food,self.s.survival.water,len(self.s.decisions)))
        self.assertNotIn(v.id,self.m.actors)
        # Uma posição preferida ocupada pelo jogador leva a outro ponto seguro.
        node=self.m.nodes['sala'][0];self.g.change_room('sala',node.feet)
        self.assertTrue(self.g.decide_visitor(v,'acolhido'));a=self.m.actors[v.id]
        self.assertFalse(a.room=='sala' and tuple(a.feet)==node.feet);self.assert_safe()

    def test_all_routines_leave_conditions_supplies_and_survival_unchanged(self):
        self.all()
        visitors={key:copy.deepcopy(vars(v)) for key,v in self.s.visitors.items()}
        survival=copy.deepcopy(vars(self.s.survival));news=[(b.id,b.read,b.available) for b in self.s.news.bulletins]
        for day in range(2,9):self.m.start_day(DayEvent(day,day-1,day))
        for room in CAPACITY:
            self.g.change_room(room)
            for _ in range(60):self.g.update((0,0),1/60)
        self.assertEqual(visitors,{key:vars(v) for key,v in self.s.visitors.items()})
        self.assertEqual(survival,vars(self.s.survival));self.assertEqual(news,[(b.id,b.read,b.available) for b in self.s.news.bulletins])

    def test_existing_test_mode_still_accepts_and_distributes(self):
        v=self.s.start_test('antonio','saudavel',rng=random.Random(9))
        self.assertTrue(self.g.decide_visitor(v,'acolhido'));self.assert_safe()
        self.assertEqual(v.diagnosis,'saudavel');self.assertTrue(self.s.test_mode)

    def test_passages_and_progression_objects_remain_reachable_with_seven(self):
        self.all()
        for room,scene in self.g.scenes.items():
            self.g.change_room(room);actors=self.m.visible(room)
            collision=ActorCollisions(scene.collisions,[feet_rect(a.feet) for a in actors])
            origin=scene.spawn;queue=deque([(0,0)]);seen={(0,0)};points=[]
            while queue:
                x,y=queue.popleft();point=origin+pygame.Vector2(x*8,y*8);points.append(point)
                for nx,ny in ((x-1,y),(x+1,y),(x,y-1),(x,y+1)):
                    if (nx,ny) not in seen and collision.allows(origin+pygame.Vector2(nx*8,ny*8)):
                        seen.add((nx,ny));queue.append((nx,ny))
            for target in scene.interactions:
                accessible=False
                for point in points:
                    if target.distance(point)>target.radius:continue
                    self.g.player.feet=point
                    if self.g.nearest_interaction() is target:accessible=True;break
                self.assertTrue(accessible,(room,target.action))

    def test_safe_recovery_uses_existing_free_spawn_when_curated_slots_are_unavailable(self):
        with patch.object(self.m,'nodes',{room:() for room in CAPACITY}):
            placement=self.m._place('ricardo',{},1)
        self.assertIsNotNone(placement)
        self.assertTrue(self.m.static_safe(placement.room,placement.feet))
        self.assertTrue(placement.waypoints)

    def test_daily_failure_keeps_the_whole_old_plan(self):
        self.all();before=self.snapshot()
        with patch.object(self.m,'_place',return_value=None):self.m.start_day(DayEvent(2,1,2))
        self.assertEqual(before,self.snapshot());self.assert_safe()

    def test_managed_movement_is_consistent_across_frame_rates(self):
        source=self.accept('ricardo');scene=self.g.scenes[source.room];states=[]
        for fps in (30,60,120):
            a=Resident('ricardo',source.room,source.origin,settings={'wait_seconds':(1,1)},rng=random.Random(12),reserved=source.reserved,waypoints=source.waypoints)
            for _ in range(12*fps):a.update(1/fps,ActorCollisions(scene.collisions))
            states.append(a.feet.copy());self.assertTrue(scene.collisions.allows(a.feet))
        self.assertLess(states[0].distance_to(states[-1]),1.5)

    def test_interaction_pause_does_not_reset_timers_or_plan_every_frame(self):
        a=self.accept('ricardo');self.approach(a);self.g.interact()
        state=(a.remaining,tuple(a.feet),a.room);runs=self.m.planning_runs
        for _ in range(120):self.g.update((0,0),1/60)
        self.assertEqual(state,(a.remaining,tuple(a.feet),a.room));self.assertEqual(runs,self.m.planning_runs)
        self.assertEqual(a.animation_state,'idle')

if __name__=='__main__':unittest.main()
