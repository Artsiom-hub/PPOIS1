from __future__ import annotations

from typing import TYPE_CHECKING, Any

import pygame

from src.entities.enemy import Enemy

if TYPE_CHECKING:
    from src.core.game import Game


class Boss(Enemy):
    """
    Босс.
    Пока это Enemy с фазами.
    """

    def __init__(
        self,
        game: "Game",
        x: float,
        y: float,
        enemy_id: str,
        config: dict[str, Any],
        image: pygame.Surface | None = None,
        groups: tuple[pygame.sprite.Group, ...] | None = None,
    ) -> None:
        super().__init__(game, x, y, enemy_id, config, image=image, groups=groups)

        self.phase = 1
        self.phase_thresholds = [
            self.max_hp * 0.66,
            self.max_hp * 0.33,
        ]

    def update_phase(self) -> None:
        if self.hp <= self.phase_thresholds[1]:
            self.phase = 3
        elif self.hp <= self.phase_thresholds[0]:
            self.phase = 2
        else:
            self.phase = 1

    def update_behavior(self, dt: float) -> None:
        self.update_phase()

        if self.phase == 1:
            self.movement = "boss_pattern"
            self.fire = "single"
        elif self.phase == 2:
            self.movement = "boss_pattern"
            self.fire = "spread"
        else:
            self.movement = "boss_pattern"
            self.fire = "spread"

        super().update_behavior(dt)

    def die(self) -> None:
        self.game.event_bus.emit("boss_destroyed", boss=self, score=self.score)
        super().die()