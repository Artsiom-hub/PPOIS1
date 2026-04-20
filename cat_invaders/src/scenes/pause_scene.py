from __future__ import annotations

import pygame

from src.core.scene_manager import BaseScene


class PauseScene(BaseScene):
    """
    Пауза.
    ESC — продолжить игру
    ENTER — выйти в меню
    """

    def on_enter(self, **kwargs) -> None:
        self.title_font = pygame.font.Font(None, 72)
        self.info_font = pygame.font.Font(None, 36)

    def handle_event(self, event) -> None:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.request_pop = True
            elif event.key == pygame.K_RETURN:
                self.is_finished = True
                self.next_scene_name = "menu"

    def render(self, screen) -> None:
        overlay = pygame.Surface((self.game.width, self.game.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        screen.blit(overlay, (0, 0))

        title = self.title_font.render("PAUSED", True, (255, 255, 0))
        line1 = self.info_font.render("ESC - CONTINUE", True, (255, 255, 255))
        line2 = self.info_font.render("ENTER - MENU", True, (255, 255, 255))

        screen.blit(title, title.get_rect(center=(self.game.width // 2, 260)))
        screen.blit(line1, line1.get_rect(center=(self.game.width // 2, 360)))
        screen.blit(line2, line2.get_rect(center=(self.game.width // 2, 410)))