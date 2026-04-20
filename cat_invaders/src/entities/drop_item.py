from __future__ import annotations

from typing import TYPE_CHECKING

import pygame

from src.entities.base_entity import BaseEntity

if TYPE_CHECKING:
    from src.core.game import Game
    from src.entities.player import Player


class DropItem(BaseEntity):
    """
    Выпадающий предмет.
    """

    def __init__(
        self,
        game: "Game",
        x: float,
        y: float,
        item_type: str,
        image: pygame.Surface | None = None,
        fall_speed: float = 160.0,
        lifetime: float = 8.0,
        groups: tuple[pygame.sprite.Group, ...] | None = None,
    ) -> None:
        super().__init__(game, x, y, image=image, groups=groups)

        self.item_type = item_type
        self.vy = fall_speed
        self.lifetime = lifetime
        self.age = 0.0

    def apply_to(self, player: "Player") -> None:
        player.apply_drop(self.item_type)
        self.game.event_bus.emit("drop_collected", item=self, player=player)
        self.kill_entity()

    def update(self, dt: float) -> None:
        self.age += dt
        if self.age >= self.lifetime:
            self.kill_entity()
            return

        super().update(dt)

        if self.rect.top > self.game.height:
            self.kill_entity()