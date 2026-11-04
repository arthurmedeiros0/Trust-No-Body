"""Inventario e derrota, sem alterar objetos ou sprites do mundo."""
import pygame
from .survival import amount


class SurvivalUI:
    def __init__(self,session):
        self.session=session;self.active=False
        self.title=pygame.font.Font(None,48);self.font=pygame.font.Font(None,30)
        self.small=pygame.font.Font(None,24)
        self.restart=pygame.Rect(460,470,360,56)

    def line(self,screen,text,y,color='#e2dfd5'):
        image=self.font.render(text,True,color);screen.blit(image,image.get_rect(center=(640,y)))

    def draw(self,screen):
        survival=self.session.survival
        if not survival.alive or survival.won:
            screen.fill('#0a0d12')
            image=self.title.render('VOCÊ SOBREVIVEU' if survival.won else 'VOCÊ NÃO SOBREVIVEU',True,'#d5cfaa' if survival.won else '#cf8278')
            screen.blit(image,image.get_rect(center=(640,230)))
            message='A cura foi descoberta. Após vinte dias, há esperança além destas paredes.' if survival.won else survival.defeat_cause
            lines=[];line=''
            for word in message.split():
                trial=(line+' '+word).strip()
                if self.font.size(trial)[0]>1000:lines.append(line);line=word
                else:line=trial
            if line:lines.append(line)
            for index,line in enumerate(lines):self.line(screen,line,305+index*34)
            self.line(screen,f'Dia {survival.victory_day if survival.won else survival.defeat_day}',405)
            pygame.draw.rect(screen,'#303a42',self.restart)
            self.line(screen,'Nova partida [Enter / R]',498)
            image=self.small.render('ESC: sair',True,'#adb4bd');screen.blit(image,image.get_rect(center=(640,570)))
            return
        shade=pygame.Surface(screen.get_size(),pygame.SRCALPHA);shade.fill((0,0,0,210));screen.blit(shade,(0,0))
        panel=pygame.Rect(290,110,700,510)
        pygame.draw.rect(screen,'#15202a',panel);pygame.draw.rect(screen,'#978973',panel,2)
        title=self.title.render('SUPRIMENTOS DA CASA',True,'#eee3ce');screen.blit(title,title.get_rect(center=(640,163)))
        for y,text in ((290,f'Comida: {amount(survival.food)} latas'),
                       (355,f'Água: {amount(survival.water)} garrafas')):self.line(screen,text,y)
        image=self.small.render('I / ESC: fechar',True,'#aeb7bf');screen.blit(image,image.get_rect(center=(640,584)))
