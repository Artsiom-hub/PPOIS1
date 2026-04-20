from __future__ import annotations

import random
from typing import TYPE_CHECKING

import pygame

from src.entities.drop_item import DropItem

if TYPE_CHECKING:
    from src.core.game import Game
    from src.entities.enemy import Enemy


class DropFactory:
    """
    Фабрика выпадающих предметов.
    Создаёт DropItem по таблицам из drops.json.
    """

    def __init__(self, game: "Game") -> None:
        self.game = game
        self.resource_manager = game.resource_manager

    def _make_default_surface(self, item_type: str) -> pygame.Surface:
        surface = pygame.Surface((24, 24), pygame.SRCALPHA)

        colors = {
            "spread_shot": (80, 220, 255),
            "rapid_cannon": (255, 220, 80),
            "laser_beam": (255, 80, 220),
            "repair": (80, 255, 120),
            "shield": (80, 140, 255),
            "extra_life": (255, 80, 80),
            "score_bonus": (255, 255, 255),
        }

        color = colors.get(item_type, (180, 180, 180))
        pygame.draw.rect(surface, color, surface.get_rect(), border_radius=6)
        return surface

    def _load_drop_image(self, item_type: str) -> pygame.Surface:
        path = f"assets/images/drops/{item_type}.png"
        try:
            return self.resource_manager.load_image(path)
        except FileNotFoundError:
            return self._make_default_surface(item_type)

    def roll_drop_item(self, drop_table_id: str) -> str | None:
        table = self.game.drops_config.get(drop_table_id)

        if not isinstance(table, list) or not table:
            return None

        roll = random.random()
        cumulative = 0.0

        for entry in table:
            item = entry.get("item")
            chance = float(entry.get("chance", 0.0))
            cumulative += chance

            if roll <= cumulative:
                return str(item)

        return None

    def create_drop(
        self,
        x: float,
        y: float,
        item_type: str,
        groups: tuple[pygame.sprite.Group, ...] | None = None,
    ) -> DropItem:
        image = self._load_drop_image(item_type)

        return DropItem(
            game=self.game,
            x=x,
            y=y,
            item_type=item_type,
            image=image,
            groups=groups,
        )

    def create_drop_from_enemy(
        self,
        enemy: "Enemy",
        drop_table_id: str | None = None,
        groups: tuple[pygame.sprite.Group, ...] | None = None,
    ) -> DropItem | None:
        table_id = drop_table_id or enemy.drop_table
        item_type = self.roll_drop_item(table_id)

        if item_type is None:
            return None

        return self.create_drop(
            x=enemy.x,
            y=enemy.y,
            item_type=item_type,
            groups=groups,
        )