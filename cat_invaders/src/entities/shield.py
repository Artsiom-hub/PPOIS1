from __future__ import annotations

from typing import TYPE_CHECKING

import pygame

from src.entities.base_entity import BaseEntity

if TYPE_CHECKING:
    from src.core.game import Game


class Shield(BaseEntity):
    """
    Щит / баррикада.
    """

    def __init__(
        self,
        game: "Game",
        x: float,
        y: float,
        hp: int = 10,
        image: pygame.Surface | None = None,
        groups: tuple[pygame.sprite.Group, ...] | None = None,
    ) -> None:
        super().__init__(game, x, y, image=image, groups=groups)

        self.hp = hp
        self.max_hp = hp

    def take_damage(self, amount: int) -> None:
        if not self.is_alive:
            return

        self.hp -= amount
        self.game.event_bus.emit("shield_damaged", shield=self, damage=amount, hp=self.hp)

        if self.hp <= 0:
            self.kill_entity()
            self.game.event_bus.emit("shield_destroyed", shield=self)