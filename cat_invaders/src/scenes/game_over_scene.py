from __future__ import annotations

import pygame

from src.core.scene_manager import BaseScene


class GameOverScene(BaseScene):
    def on_enter(self, **kwargs) -> None:
        self.score = int(kwargs.get("score", 0))
        self.wave = int(kwargs.get("wave", 0))

        self.title_font = pygame.font.Font(None, 72)
        self.info_font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 28)

        # 🔥 проверка на топ-1
        self.is_new_record = self.game.high_score_manager.is_top_score(self.score)

        # ввод имени
        self.entering_name = self.is_new_record
        self.player_name = ""
        self.max_name_length = 10

        audio_cfg = self.game.game_config.get("audio", {})
        music_path = audio_cfg.get("music_game_over")

        if music_path:
            try:
                self.game.resource_manager.stop_music()
                self.game.resource_manager.play_music(music_path, loops=0)
            except:
                pass

    def handle_event(self, event) -> None:
        if self.entering_name:
            self._handle_name_input(event)
            return

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                self.is_finished = True
                self.next_scene_name = "gameplay"
            elif event.key == pygame.K_ESCAPE:
                self.is_finished = True
                self.next_scene_name = "menu"

    def _handle_name_input(self, event) -> None:
        if event.type != pygame.KEYDOWN:
            return

        if event.key == pygame.K_RETURN:
            name = self.player_name.strip() or "PLAYER"

            self.game.high_score_manager.add_score(
                score=self.score,
                wave=self.wave,
                name=name,
            )

            self.entering_name = False
            return

        elif event.key == pygame.K_BACKSPACE:
            self.player_name = self.player_name[:-1]

        else:
            if len(self.player_name) < self.max_name_length:
                char = event.unicode
                if char.isprintable():
                    self.player_name += char.upper()

    def render(self, screen) -> None:
        screen.fill((35, 0, 0))

        title = self.title_font.render("GAME OVER", True, (255, 255, 255))
        screen.blit(title, title.get_rect(center=(self.game.width // 2, 180)))

        score_text = self.info_font.render(f"SCORE: {self.score}", True, (255, 220, 120))
        screen.blit(score_text, score_text.get_rect(center=(self.game.width // 2, 280)))

        wave_text = self.info_font.render(f"WAVE: {self.wave}", True, (200, 200, 255))
        screen.blit(wave_text, wave_text.get_rect(center=(self.game.width // 2, 330)))

        # 🔥 режим нового рекорда
        if self.entering_name:
            congrats = self.info_font.render("НОВЫЙ РЕКОРД!", True, (255, 255, 0))
            screen.blit(congrats, congrats.get_rect(center=(self.game.width // 2, 400)))

            prompt = self.small_font.render("Введите имя:", True, (220, 220, 220))
            screen.blit(prompt, prompt.get_rect(center=(self.game.width // 2, 450)))

            name_display = self.info_font.render(self.player_name + "_", True, (255, 255, 255))
            screen.blit(name_display, name_display.get_rect(center=(self.game.width // 2, 500)))

            hint = self.small_font.render("ENTER - сохранить", True, (180, 180, 180))
            screen.blit(hint, hint.get_rect(center=(self.game.width // 2, 560)))

        else:
            controls = self.small_font.render(
                "ENTER - RESTART    ESC - MENU",
                True,
                (220, 220, 220),
            )
            screen.blit(controls, controls.get_rect(center=(self.game.width // 2, 520)))