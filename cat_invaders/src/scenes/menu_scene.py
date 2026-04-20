from __future__ import annotations

import pygame

from src.core.scene_manager import BaseScene


class MenuScene(BaseScene):
    def on_enter(self, **kwargs) -> None:
        self.options = [
            ("НАЧАТЬ ИГРУ", "gameplay"),
            ("ТАБЛИЦА РЕКОРДОВ", "scores"),
            ("СПРАВКА", "help"),
            ("ВЫХОД", "exit"),
        ]

        self.selected_index = 0

        self.title_font = pygame.font.Font(None, 72)
        self.menu_font = pygame.font.Font(None, 42)

        # музыка меню
        audio_cfg = self.game.game_config.get("audio", {})
        music_path = audio_cfg.get("music_menu")
        if music_path:
            try:
                self.game.resource_manager.play_music(music_path, loops=-1)
            except:
                pass

    def handle_event(self, event) -> None:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.selected_index = (self.selected_index - 1) % len(self.options)

            elif event.key == pygame.K_DOWN:
                self.selected_index = (self.selected_index + 1) % len(self.options)

            elif event.key == pygame.K_RETURN:
                _, action = self.options[self.selected_index]

                if action == "exit":
                    self.game.stop()
                else:
                    self.is_finished = True
                    self.next_scene_name = action

    def render(self, screen) -> None:
        screen.fill((10, 10, 30))

        title = self.title_font.render("CAT INVADERS", True, (255, 255, 255))
        screen.blit(title, title.get_rect(center=(self.game.width // 2, 150)))

        for i, (text, _) in enumerate(self.options):
            color = (255, 255, 0) if i == self.selected_index else (200, 200, 200)

            label = self.menu_font.render(text, True, color)
            screen.blit(label, label.get_rect(center=(self.game.width // 2, 300 + i * 60)))