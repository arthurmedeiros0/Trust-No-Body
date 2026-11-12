"""Tela narrativa breve exibida antes de cada nova partida."""
import pygame
from . import ui_theme as ui


HEADER = 'TRANSMISSÃO INTERROMPIDA'
TITLE = 'O INÍCIO DO FIM'
PARAGRAPHS = (
    'Um vírus desconhecido se espalhou rapidamente. O governo decretou um lockdown imediato.',
    'Você está sozinho, sem suprimentos. Para sobreviver, talvez precise abrir a porta para desconhecidos.',
)
QUESTION = 'Mas em quem você pode confiar?'
CONTINUE = 'ENTER — CONTINUAR'


class IntroUI:
    def __init__(self):
        self.active = True
        self.elapsed = 0.0
        self.panel = pygame.Rect(190, 86, 900, 548)
        self.button = pygame.Rect(476, 550, 328, 52)

    def handle_event(self, event):
        if not self.active:
            return False
        keyboard = event.type == pygame.KEYDOWN and event.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_ESCAPE)
        mouse = event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.button.collidepoint(event.pos)
        if keyboard or mouse:
            self.active = False
            return True
        return False

    def update(self, dt):
        self.elapsed += max(0, dt)

    @staticmethod
    def centered_lines(screen, value, top, width, size, color, spacing):
        font = ui.font(size)
        lines = ui.wrapped_lines(value, width, font)
        for index, line in enumerate(lines):
            image = font.render(line, True, color)
            screen.blit(image, image.get_rect(center=(screen.get_width()//2, top + index*spacing)))
        return top + len(lines)*spacing

    def draw(self, screen):
        screen.fill('#080d13')
        for y in range(0, screen.get_height(), 8):
            pygame.draw.line(screen, '#0c141c', (0, y), (screen.get_width(), y))
        ui.panel(screen, self.panel, color=ui.INK, alpha=246, accent=ui.PAPER)
        pygame.draw.circle(screen, ui.PAPER, (342, 135), 4)
        pygame.draw.arc(screen, ui.MUTED, (328, 121, 28, 28), -0.9, 0.9, 1)
        pygame.draw.arc(screen, ui.MUTED, (322, 115, 40, 40), -0.9, 0.9, 1)
        self.centered_lines(screen, HEADER, 135, 710, 22, ui.MUTED, 26)
        pygame.draw.line(screen, ui.BORDER, (252, 176), (1028, 176))
        self.centered_lines(screen, TITLE, 234, 780, 56, ui.PAPER, 56)
        self.centered_lines(screen, PARAGRAPHS[0], 320, 760, 27, ui.TEXT, 32)
        self.centered_lines(screen, PARAGRAPHS[1], 400, 760, 27, ui.TEXT, 32)
        self.centered_lines(screen, QUESTION, 495, 760, 30, ui.PAPER, 36)
        ui.button(screen, self.button, CONTINUE, typeface=ui.font(24))
        # A tela pode ser ignorada imediatamente; o fade apenas suaviza a entrada.
        alpha=round(100*max(0,1-self.elapsed/.18))
        if alpha:
            shade=pygame.Surface(screen.get_size(),pygame.SRCALPHA)
            shade.fill((0,0,0,alpha))
            screen.blit(shade,(0,0))
