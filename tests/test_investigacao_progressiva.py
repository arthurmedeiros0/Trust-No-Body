"""Conhecimento aprendido, acesso protegido e interacao real com moradores."""
import copy
import unittest
from unittest.mock import patch
import pygame
from casa.game import House
from casa.medical_knowledge import LABELS,MedicalKnowledge
from casa.visitor_ui import VisitorUI
from casa.collisions import feet_rect


class ProgressiveInvestigationTests(unittest.TestCase):
    def test_missed_day_four_recovered_at_day_five_once_for_door_and_residents(self):
        game=self.game;session=self.session
        self.accept('ricardo');session.survival.add_supplies(30,30) # Somente fixture.
        while game.days.day<5:
            if session.manager.current:
                self.assertTrue(game.decide_visitor(session.visitors[session.manager.current],'acolhido'))
            game.dialog='';game.change_room('quarto',game.scenes['quarto'].point((345,365)))
            game.handle_event(pygame.event.Event(pygame.KEYUP,key=pygame.K_e))
            game.interact();self.assertTrue(game.sleep_option)
            game.confirm_sleep();game.update((0,0),3)
        self.assertFalse(session.medical.known)
        snapshot={key:copy.deepcopy(v.symptoms) for key,v in session.visitors.items()}
        arrivals=set(session.manager.seen)
        game.dialog='';tv=game.television;tv.open();tv.choose('history')
        self.assertEqual([b.day for b in game.news.history],[4,3,2,1])
        label=next(label for key,_,label in tv.layout() if key=='news:boletim_04')
        self.assertIn('[NÃO ASSISTIDA]',label)
        calls=[];game.news.on_watch.append(lambda b:calls.append(b.id))
        tv.choose('news:boletim_04')
        self.assertTrue(tv.bulletin.read);self.assertEqual(tv.bulletin.day,4)
        self.assertEqual(session.medical.known,{'manchas_maos','dentes_deteriorados'})
        self.assertFalse(game.dialog)
        tv.choose('back');self.assertIn('[ASSISTIDA]',next(label for key,_,label in tv.layout() if key=='news:boletim_04'))
        tv.choose('news:boletim_04');self.assertEqual(calls,['boletim_04'])
        for _ in range(3):game.handle_event(pygame.event.Event(pygame.KEYDOWN,key=pygame.K_ESCAPE))
        self.assertIn('NOVAS INVESTIGAÇÕES',game.dialog)
        game.dialog=''
        tv.open();tv.choose('history');tv.choose('news:boletim_04')
        tv.choose('back');tv.choose('news:boletim_01');tv.choose('close');game.update((0,0),0)
        self.assertFalse(game.dialog);self.assertEqual(calls,['boletim_04'])
        self.assertEqual(session.manager.seen,arrivals)
        for key in ('ricardo','laura'):
            door=VisitorUI(session.visitors[key],game.visitor_assets[key],lambda *args:False,knowledge=session.medical)
            door.page='investigate';self.assertEqual(set(door.layout()),{'manchas_maos','dentes_deteriorados','back'})
            resident=self.approach(key);self.click(resident,'investigate')
            self.assertEqual(set(resident.layout()),{'manchas_maos','dentes_deteriorados','back'})
            game.resident_ui=None
        self.assertEqual({key:v.symptoms for key,v in session.visitors.items()},snapshot)

    def test_future_and_current_cannot_be_opened_as_old_news_and_recap_still_works(self):
        game=self.game;game.days.day=5;game.news.unlock(5)
        ui=game.television;ui.open();ui.choose('history')
        for day in range(5,21):
            ui.choose(f'news:boletim_{day:02}')
            self.assertEqual(ui.page,'history')
            self.assertFalse(game.news.bulletins[day-1].read)
        self.assertFalse(self.session.medical.known)
        game.days.day=7;game.news.unlock(7);ui.choose('current')
        self.assertEqual(self.session.medical.known,set(list(LABELS)[:3]))
        ui.choose('history')
        self.assertIn('news:boletim_04',[key for key,_,_ in ui.layout()])

    def test_twenty_day_archive_pages_include_every_unread_previous_bulletin(self):
        game=self.game;game.days.day=20;game.news.unlock(20)
        ui=game.television;ui.open();ui.choose('history')
        seen=[]
        for _ in range(3):
            seen.extend(key for key,_,_ in ui.layout() if key.startswith('news:'))
            ui.choose('next')
        self.assertEqual(seen,[f'news:boletim_{day:02}' for day in range(19,0,-1)])
        self.assertEqual(len(set(seen)),19)
        self.assertFalse(game.news.bulletins[18].read)
        ui.choose('prev');self.assertEqual(ui.offset,8)
        ui.choose('prev');self.assertEqual(ui.offset,0)
        game.handle_event(pygame.event.Event(pygame.KEYDOWN,key=pygame.K_RETURN))
        self.assertEqual(ui.bulletin.day,19);self.assertTrue(ui.bulletin.read)
        game.handle_event(pygame.event.Event(pygame.KEYDOWN,key=pygame.K_ESCAPE))
        self.assertEqual(ui.page,'history')
        game.draw(pygame.display.get_surface())

    def setUp(self):
        self.game=House();self.game.dialog=''
        self.session=self.game.visitor_session
        self.session.news.watch(self.session.news.current(1))

    def watch(self,day):
        self.session.days.day=day;self.session.news.unlock(day)
        self.session.news.watch(self.session.news.current(day))

    def click(self,ui,key):
        ui.handle_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN,button=1,pos=ui.layout()[key][0].center))

    def accept(self,key):
        if key=='laura':
            day=self.session.visitors[key].arrival_day
            self.session.days.day=day
            self.session._arrive(self.session.manager.activate(day,True))
        self.assertTrue(self.game.decide_visitor(self.session.visitors[key],'acolhido'))

    def approach(self,key):
        game=self.game;actor=game.residents[key]
        game.change_room(actor.room)
        for offset in ((30,0),(-30,0),(0,30),(0,-30)):
            point=actor.feet+pygame.Vector2(offset)
            if game.scene.collisions.allows(point):
                game.player.feet=point
                if game.nearest_interaction().target==key:break
        self.assertEqual(game.nearest_interaction().target,key)
        game.dialog='';game.interact()
        self.assertIsNotNone(game.resident_ui)
        return game.resident_ui

    def test_initial_locked_but_talk_accept_reject_work(self):
        ui=self.game.peephole.visitor_ui
        self.assertEqual(self.session.medical.known,set())
        self.assertNotIn('investigate',ui.layout())
        self.assertTrue({'talk','accept','reject','back'}.issubset(ui.layout()))
        self.click(ui,'talk');self.click(ui,'back');self.click(ui,'accept')
        self.assertEqual(ui.page,'confirm')
        self.click(ui,'confirm')
        self.assertEqual(self.session.visitors['ricardo'].state,'acolhido')

    def test_days_alone_do_not_unlock_and_watch_progression_is_idempotent(self):
        snapshot={key:copy.deepcopy(v.symptoms) for key,v in self.session.visitors.items()}
        expected={4:2,7:3,10:5,14:6,17:6}
        for day,count in expected.items():
            before=set(self.session.medical.known)
            self.session.days.day=day;self.session.news.unlock(day)
            self.assertEqual(self.session.medical.known,before)
            self.session.news.watch(self.session.news.current(day))
            self.assertEqual(self.session.medical.known,set(list(LABELS)[:count]))
            pending=list(self.session.medical.discoveries)
            self.session.news.watch(self.session.news.current(day))
            self.assertEqual(self.session.medical.discoveries,pending)
        self.assertEqual({key:v.symptoms for key,v in self.session.visitors.items()},snapshot)

    def test_later_recap_unlocks_only_mentioned_features(self):
        for day,count in ((7,3),(10,5),(14,6),(17,6)):
            game=House();game.days.day=day;game.news.unlock(day)
            game.news.watch(game.news.current(day))
            self.assertEqual(game.visitor_session.medical.known,set(list(LABELS)[:count]))
        for day in (1,2,3,5,6,8,9,11,12,13,15,16,18,19,20):
            game=House();game.days.day=day;game.news.unlock(day)
            game.news.watch(game.news.current(day))
            self.assertFalse(game.visitor_session.medical.known)

    def test_discovery_notice_only_after_closing_tv_and_not_repeated(self):
        game=self.game;game.days.day=4;game.news.unlock(4)
        game.television.open();game.television.choose('current')
        self.assertFalse(game.dialog)
        game.handle_event(pygame.event.Event(pygame.KEYDOWN,key=pygame.K_ESCAPE))
        self.assertFalse(game.dialog)
        game.handle_event(pygame.event.Event(pygame.KEYDOWN,key=pygame.K_ESCAPE))
        self.assertIn('NOVAS INVESTIGAÇÕES',game.dialog)
        self.assertIn('Manchas',game.dialog);self.assertNotIn('olhos',game.dialog)
        game.dialog='';game.news.watch(game.news.current(4));game.update((0,0),0)
        self.assertFalse(game.dialog)

    def test_door_filters_and_denies_direct_locked_image_access(self):
        ui=self.game.peephole.visitor_ui
        ui.feature='olhos_alterados'
        with self.assertRaises(PermissionError):ui.examination_image()
        ui.page='image';ui.draw(pygame.display.get_surface());self.assertEqual(ui.page,'root')
        self.watch(4);self.session.medical.discoveries.clear()
        self.click(ui,'investigate')
        self.assertEqual(set(ui.layout()),{'manchas_maos','dentes_deteriorados','back'})
        for feature in ('manchas_maos','dentes_deteriorados'):
            self.click(ui,feature)
            self.assertIs(ui.examination_image(),ui.assets.investigation[feature]['alterado' if ui.visitor.symptoms[feature] else 'normal'])
            self.click(ui,'back')
        ui.feature='tremores_involuntarios'
        with self.assertRaises(PermissionError):ui.examination_image()

    def test_both_residents_share_knowledge_but_keep_images_and_observations(self):
        self.accept('ricardo');self.accept('laura')
        self.watch(4);self.session.medical.discoveries.clear()
        for key in ('ricardo','laura'):
            ui=self.approach(key)
            self.assertEqual(set(ui.layout()),{'talk','investigate','back'})
            self.assertTrue(ui.resident)
            self.click(ui,'talk');self.assertTrue(ui.response)
            self.assertEqual(len(ui.dialogue.data['questions']),2)
            self.click(ui,'back');self.click(ui,'investigate');self.click(ui,'manchas_maos')
            actual=self.session.visitors[key].symptoms['manchas_maos']
            self.assertIs(ui.examination_image(),self.game.visitor_assets[key].investigation['manchas_maos']['alterado' if actual else 'normal'])
            self.assertEqual(self.session.medical.status(key,'manchas_maos'),'presente' if actual else 'ausente')
            self.assertEqual(self.session.medical.status(key,'dentes_deteriorados'),'nao_observado')
            self.assertEqual(self.session.medical.status(key,'olhos_alterados'),'desconhecido')
            self.game.resident_ui=None
        self.assertIsNot(self.game.visitor_assets['ricardo'],self.game.visitor_assets['laura'])

    def test_resident_initially_locked_pauses_and_resumes_no_remote_interaction(self):
        self.accept('ricardo');ui=self.approach('ricardo')
        self.assertEqual(set(ui.layout()),{'talk','back'})
        actor=self.game.residents['ricardo'];position=actor.feet.copy()
        self.assertIs(actor.image(self.game.visitor_assets['ricardo']),self.game.visitor_assets['ricardo'].sprites[actor.direction])
        self.game.update((1,0),10);self.assertEqual(actor.feet,position)
        self.game.handle_event(pygame.event.Event(pygame.KEYDOWN,key=pygame.K_ESCAPE))
        self.assertIsNone(self.game.resident_ui)
        for _ in range(400):self.game.update((0,0),.025)
        self.assertNotEqual(actor.feet,position)
        self.game.change_room('corredor');self.game.interact()
        self.assertIsNone(self.game.resident_ui)

    def test_nearest_object_wins_and_never_opens_two_interfaces(self):
        self.accept('ricardo');game=self.game;actor=game.residents['ricardo']
        game.change_room('quarto',game.scenes['quarto'].point((635,250)))
        game.change_room('cozinha',game.scenes['cozinha'].point((635,250)))
        actor.room='cozinha';actor.feet=game.player.feet+pygame.Vector2(0,56)
        self.assertEqual(game.nearest_interaction().action,'fridge')
        game.interact();self.assertIsNone(game.resident_ui);self.assertTrue(game.inventory.active)
        game.handle_event(pygame.event.Event(pygame.KEYDOWN,key=pygame.K_ESCAPE))
        game.dialog='';game.player.feet=actor.feet+pygame.Vector2(0,-20)
        self.assertEqual(game.nearest_interaction().action,'resident')
        game.interact();self.assertIsNotNone(game.resident_ui)
        self.assertFalse(game.inventory.active);self.assertFalse(game.television.active)

    def test_new_game_resets_all_medical_data(self):
        self.watch(17)
        visitor=self.session.visitors['ricardo']
        self.session.medical.observe(visitor,'manchas_maos')
        state=self.session.survival;state.alive=False
        self.game.handle_event(pygame.event.Event(pygame.KEYDOWN,key=pygame.K_RETURN))
        self.assertFalse(self.game.visitor_session.medical.known)
        self.assertFalse(self.game.visitor_session.medical.observations)

    def test_sleep_and_room_changes_preserve_knowledge_observations_and_real_symptoms(self):
        self.accept('ricardo');self.accept('laura');self.watch(4)
        self.session.medical.discoveries.clear()
        visitor=self.session.visitors['ricardo']
        self.session.medical.observe(visitor,'dentes_deteriorados')
        known=set(self.session.medical.known)
        observed=copy.deepcopy(self.session.medical.observations)
        symptoms={key:copy.deepcopy(v.symptoms) for key,v in self.session.visitors.items()}
        self.session.survival.add_supplies(20,20) # Exclusivo da fixture.
        for room in self.game.scenes:self.game.change_room(room)
        self.game.change_room('quarto',self.game.scenes['quarto'].point((345,365)))
        self.game.interact();self.assertTrue(self.game.sleep_option)
        with patch('casa.visitors.random.getrandbits',side_effect=AssertionError('novo sorteio')):
            self.game.confirm_sleep();self.game.update((0,0),3)
        self.assertEqual(self.game.days.day,5)
        self.assertEqual(self.session.medical.known,known)
        self.assertEqual(self.session.medical.observations,observed)
        self.assertEqual({key:v.symptoms for key,v in self.session.visitors.items()},symptoms)
