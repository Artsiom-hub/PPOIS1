from __future__ import annotations

import pygame


class HUD:
    """
    Простой HUD для отображения игрового состояния.
    Не управляет логикой, только рисует информацию.
    """

    def __init__(self, game, player, score_system, wave_system) -> None:
        self.game = game
        self.player = player
        self.score_system = score_system
        self.wave_system = wave_system

        self.font = pygame.font.Font(None, 30)
        self.small_font = pygame.font.Font(None, 24)

    def draw(self, screen: pygame.Surface) -> None:
        self._draw_top_bar(screen)
        self._draw_player_status(screen)

    def _draw_top_bar(self, screen: pygame.Surface) -> None:
        bar_rect = pygame.Rect(0, 0, self.game.width, 100)
        pygame.draw.rect(screen, (10, 14, 26), bar_rect)
        pygame.draw.line(screen, (60, 80, 120), (0, 100), (self.game.width, 100), 2)

        score_text = self.font.render(
            f"SCORE: {self.score_system.score}",
            True,
            (255, 255, 255),
        )
        high_score_text = self.small_font.render(
            f"HIGH: {self.score_system.high_score}",
            True,
            (180, 180, 220),
        )
        wave_text = self.font.render(
            f"WAVE: {self.wave_system.current_wave_number}",
            True,
            (255, 255, 255),
        )

        screen.blit(score_text, (20, 16))
        screen.blit(high_score_text, (20, 50))
        screen.blit(wave_text, (self.game.width // 2 - 50, 16))

    def _draw_player_status(self, screen: pygame.Surface) -> None:
        lives_text = self.font.render(
            f"LIVES: {self.player.lives}",
            True,
            (255, 255, 255),
        )
        hp_text = self.font.render(
            f"HP: {self.player.hp}/{self.player.max_hp}",
            True,
            (255, 255, 255),
        )
        weapon_text = self.small_font.render(
            f"WEAPON: {self.player.current_weapon}",
            True,
            (255, 240, 140),
        )

        screen.blit(lives_text, (self.game.width - 180, 16))
        screen.blit(hp_text, (self.game.width - 180, 46))
        screen.blit(weapon_text, (self.game.width - 260, 76))