from __future__ import annotations

from typing import TYPE_CHECKING

import pygame

from src.entities.projectile import Projectile

if TYPE_CHECKING:
    from src.core.game import Game


class ProjectileFactory:
    """
    Фабрика снарядов.
    Создаёт снаряды игрока и врагов.
    """

    def __init__(self, game: "Game") -> None:
        self.game = game
        self.resource_manager = game.resource_manager

    def _make_default_surface(
        self,
        width: int,
        height: int,
        color: tuple[int, int, int],
        shape: str = "rect",
    ) -> pygame.Surface:
        surface = pygame.Surface((width, height), pygame.SRCALPHA)

        if shape == "circle":
            pygame.draw.circle(surface, color, (width // 2, height // 2), min(width, height) // 2)
        else:
            surface.fill(color)

        return surface

    def _load_projectile_image(self, projectile_key: str | None, owner: str) -> pygame.Surface:
        if projectile_key:
            path = f"assets/images/bullets/{projectile_key}.png"
            try:
                return self.resource_manager.load_image(path)
            except FileNotFoundError:
                pass

        if projectile_key == "enemy_mine":
            return self._make_default_surface(18, 18, (255, 180, 60), shape="circle")

        if owner == "player":
            return self._make_default_surface(6, 18, (80, 220, 255))

        return self._make_default_surface(6, 18, (255, 80, 80))

    def create_projectile(
        self,
        x: float,
        y: float,
        vx: float,
        vy: float,
        damage: int,
        owner: str,
        projectile_key: str | None = None,
        piercing: bool = False,
        lifetime: float = 5.0,
        groups: tuple[pygame.sprite.Group, ...] | None = None,
    ) -> Projectile:
        image = self._load_projectile_image(projectile_key, owner)

        projectile = Projectile(
            game=self.game,
            x=x,
            y=y,
            vx=vx,
            vy=vy,
            damage=damage,
            owner=owner,
            image=image,
            piercing=piercing,
            lifetime=lifetime,
            groups=groups,
        )

        if projectile_key == "enemy_mine":
            projectile.set_hitbox(1, 1, 16, 16)

        return projectile