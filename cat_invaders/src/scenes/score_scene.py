from __future__ import annotations

import pygame

from src.core.scene_manager import BaseScene


class ScoreScene(BaseScene):
    def on_enter(self, **kwargs) -> None:
        self.title_font = pygame.font.Font(None, 64)
        self.font = pygame.font.Font(None, 34)
        self.small_font = pygame.font.Font(None, 28)

        self.scores = self.game.high_score_manager.get_scores()

    def handle_event(self, event) -> None:
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.is_finished = True
            self.next_scene_name = "menu"

    def render(self, screen) -> None:
        screen.fill((10, 10, 20))

        title = self.title_font.render("ТАБЛИЦА РЕКОРДОВ", True, (255, 255, 255))
        screen.blit(title, title.get_rect(center=(self.game.width // 2, 100)))

        if not self.scores:
            empty = self.font.render("Рекордов пока нет", True, (180, 180, 180))
            screen.blit(empty, empty.get_rect(center=(self.game.width // 2, 260)))
        else:
            header = self.small_font.render("МЕСТО      ИМЯ      ОЧКИ      ВОЛНА", True, (255, 255, 120))
            screen.blit(header, (180, 170))

            for i, entry in enumerate(self.scores, start=1):
                line = self.font.render(
                    f"{i:<2}        {entry['name']:<8} {entry['score']:<8} {entry['wave']}",
                    True,
                    (220, 220, 220),
                )
                screen.blit(line, (180, 210 + (i - 1) * 36))

        hint = self.small_font.render("ESC - назад", True, (150, 150, 150))
        screen.blit(hint, (self.game.width // 2 - 60, 620))