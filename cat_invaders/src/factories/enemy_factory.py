from __future__ import annotations

from typing import TYPE_CHECKING, Any

import pygame

from src.entities.boss import Boss
from src.entities.enemy import Enemy

if TYPE_CHECKING:
    from src.core.game import Game


class EnemyFactory:
    """
    Фабрика врагов по enemies.json.
    Создаёт обычных врагов и боссов.
    """

    BOSS_IDS = {"mini_boss", "boss", "final_boss"}

    def __init__(self, game: "Game") -> None:
        self.game = game
        self.resource_manager = game.resource_manager

    def _make_default_surface(self, enemy_id: str) -> pygame.Surface:
        size_map = {
            "scout": (36, 28),
            "zigzag_scout": (36, 28),
            "shooter_drone": (40, 30),
            "heavy_fighter": (56, 42),
            "kamikaze": (34, 26),
            "sniper": (42, 30),
            "mine_layer": (46, 32),
            "teleporter": (40, 30),
            "shielded": (50, 36),
            "mini_boss": (120, 80),
        }

        color_map = {
            "scout": (120, 255, 120),
            "zigzag_scout": (120, 220, 255),
            "shooter_drone": (255, 220, 120),
            "heavy_fighter": (255, 140, 120),
            "kamikaze": (255, 90, 90),
            "sniper": (220, 120, 255),
            "mine_layer": (255, 255, 120),
            "teleporter": (120, 255, 255),
            "shielded": (120, 120, 255),
            "mini_boss": (255, 80, 180),
        }

        width, height = size_map.get(enemy_id, (40, 30))
        color = color_map.get(enemy_id, (200, 200, 200))

        surface = pygame.Surface((width, height), pygame.SRCALPHA)
        pygame.draw.rect(surface, color, surface.get_rect(), border_radius=6)
        return surface

    def _load_enemy_image(self, enemy_id: str, config: dict[str, Any]) -> pygame.Surface:
        sprite_path = config.get("sprite")
        if sprite_path:
            try:
                return self.resource_manager.load_image(sprite_path)
            except FileNotFoundError:
                pass

        return self._make_default_surface(enemy_id)

    def create_enemy(
        self,
        enemy_id: str,
        x: float,
        y: float,
        groups: tuple[pygame.sprite.Group, ...] | None = None,
    ) -> Enemy:
        config = self.game.enemies_config.get(enemy_id)
        if config is None:
            raise KeyError(f"Враг '{enemy_id}' не найден в enemies.json")

        image = self._load_enemy_image(enemy_id, config)

        entity_cls = Boss if enemy_id in self.BOSS_IDS else Enemy

        enemy = entity_cls(
            game=self.game,
            x=x,
            y=y,
            enemy_id=enemy_id,
            config=config,
            image=image,
            groups=groups,
        )

        hitbox_cfg = config.get("hitbox")
        if isinstance(hitbox_cfg, dict):
            enemy.set_hitbox(
                int(hitbox_cfg.get("x", 0)),
                int(hitbox_cfg.get("y", 0)),
                int(hitbox_cfg.get("w", enemy.rect.width)),
                int(hitbox_cfg.get("h", enemy.rect.height)),
            )

        return enemy

    def create_wave_batch(
        self,
        enemy_id: str,
        count: int,
        start_x: float,
        start_y: float,
        spacing: float = 60.0,
        formation: str = "line",
        groups: tuple[pygame.sprite.Group, ...] | None = None,
    ) -> list[Enemy]:
        enemies: list[Enemy] = []

        if formation == "line":
            for i in range(count):
                enemies.append(
                    self.create_enemy(
                        enemy_id=enemy_id,
                        x=start_x + i * spacing,
                        y=start_y,
                        groups=groups,
                    )
                )
            return enemies

        if formation == "column":
            for i in range(count):
                enemies.append(
                    self.create_enemy(
                        enemy_id=enemy_id,
                        x=start_x,
                        y=start_y + i * spacing,
                        groups=groups,
                    )
                )
            return enemies

        if formation == "v_shape":
            center_index = count // 2
            for i in range(count):
                offset = i - center_index
                enemies.append(
                    self.create_enemy(
                        enemy_id=enemy_id,
                        x=start_x + offset * spacing,
                        y=start_y + abs(offset) * (spacing * 0.5),
                        groups=groups,
                    )
                )
            return enemies

        # fallback
        for i in range(count):
            enemies.append(
                self.create_enemy(
                    enemy_id=enemy_id,
                    x=start_x + i * spacing,
                    y=start_y,
                    groups=groups,
                )
            )

        return enemies