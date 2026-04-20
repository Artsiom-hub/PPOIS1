from __future__ import annotations

from typing import TYPE_CHECKING

import pygame

from src.entities.projectile import Projectile
from src.factories.projectile_factory import ProjectileFactory

if TYPE_CHECKING:
    from src.core.game import Game
    from src.entities.base_entity import BaseEntity


class WeaponFactory:
    def __init__(self, game: "Game") -> None:
        self.game = game
        self.projectile_factory = ProjectileFactory(game)

    def create_shot(
        self,
        weapon_id: str,
        shooter: "BaseEntity",
        owner: str,
        groups: tuple[pygame.sprite.Group, ...] | None = None,
    ) -> Projectile | list[Projectile]:
        weapon_cfg = self.game.weapons_config.get(weapon_id)
        if weapon_cfg is None:
            raise KeyError(f"Оружие '{weapon_id}' не найдено в weapons.json")

        weapon_type = str(weapon_cfg.get("type", "single"))
        damage = int(weapon_cfg.get("damage", 1))
        projectile_key = weapon_cfg.get("projectile")
        piercing = bool(weapon_cfg.get("piercing", False))

        if owner == "player":
            origin_x = shooter.x
            origin_y = shooter.rect.top
            default_speed = -700.0
        else:
            origin_x = shooter.x
            origin_y = shooter.rect.bottom
            default_speed = 320.0

        if weapon_type == "spread":
            bullets = int(weapon_cfg.get("bullets", 3))
            angle = float(weapon_cfg.get("angle", 20))
            spread_speed = float(weapon_cfg.get("speed", abs(default_speed)))
            return self._create_spread(
                x=origin_x,
                y=origin_y,
                bullets=bullets,
                total_angle=angle,
                damage=damage,
                owner=owner,
                projectile_key=projectile_key,
                speed=spread_speed,
                groups=groups,
            )

        if weapon_type == "laser":
            lifetime = float(weapon_cfg.get("duration", 0.4))
            return self.projectile_factory.create_projectile(
                x=origin_x,
                y=origin_y,
                vx=0.0,
                vy=-1100.0 if owner == "player" else 700.0,
                damage=damage,
                owner=owner,
                projectile_key=projectile_key,
                piercing=True,
                lifetime=lifetime,
                groups=groups,
            )

        if weapon_type == "mine":
            speed = float(weapon_cfg.get("speed", 140.0))
            lifetime = float(weapon_cfg.get("lifetime", 8.0))
            return self.projectile_factory.create_projectile(
                x=origin_x,
                y=origin_y,
                vx=0.0,
                vy=speed if owner == "enemy" else -speed,
                damage=damage,
                owner=owner,
                projectile_key=projectile_key,
                piercing=piercing,
                lifetime=lifetime,
                groups=groups,
            )

        if weapon_id == "enemy_sniper" and owner == "enemy":
            player = getattr(self.game, "current_player", None)

            if player is not None and getattr(player, "is_alive", False):
                dx = player.x - origin_x
                dy = player.y - origin_y
                length = (dx * dx + dy * dy) ** 0.5

                if length > 0:
                    speed = 420.0
                    vx = (dx / length) * speed
                    vy = (dy / length) * speed
                else:
                    vx = 0.0
                    vy = 320.0
            else:
                vx = 0.0
                vy = 320.0

            return self.projectile_factory.create_projectile(
                x=origin_x,
                y=origin_y,
                vx=vx,
                vy=vy,
                damage=damage,
                owner=owner,
                projectile_key=projectile_key,
                piercing=piercing,
                groups=groups,
            )

        speed = float(weapon_cfg.get("speed", abs(default_speed)))
        vy = -speed if owner == "player" else speed

        return self.projectile_factory.create_projectile(
            x=origin_x,
            y=origin_y,
            vx=0.0,
            vy=vy,
            damage=damage,
            owner=owner,
            projectile_key=projectile_key,
            piercing=piercing,
            groups=groups,
        )

    def _create_spread(
        self,
        x: float,
        y: float,
        bullets: int,
        total_angle: float,
        damage: int,
        owner: str,
        projectile_key: str | None,
        speed: float,
        groups: tuple[pygame.sprite.Group, ...] | None = None,
    ) -> list[Projectile]:
        if bullets <= 1:
            return [
                self.projectile_factory.create_projectile(
                    x=x,
                    y=y,
                    vx=0.0,
                    vy=-speed if owner == "player" else speed,
                    damage=damage,
                    owner=owner,
                    projectile_key=projectile_key,
                    groups=groups,
                )
            ]

        shots: list[Projectile] = []
        start_angle = -total_angle / 2
        step = total_angle / (bullets - 1)

        base_vector = pygame.math.Vector2(0, -1 if owner == "player" else 1)

        for i in range(bullets):
            current_angle = start_angle + step * i
            vec = base_vector.rotate(current_angle)

            shots.append(
                self.projectile_factory.create_projectile(
                    x=x,
                    y=y,
                    vx=vec.x * speed,
                    vy=vec.y * speed,
                    damage=damage,
                    owner=owner,
                    projectile_key=projectile_key,
                    groups=groups,
                )
            )

        return shots