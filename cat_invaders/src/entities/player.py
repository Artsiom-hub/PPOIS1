from __future__ import annotations

from typing import TYPE_CHECKING, Any

import pygame

from src.entities.base_entity import BaseEntity

if TYPE_CHECKING:
    from src.core.game import Game


class Player(BaseEntity):
    """
    Игрок.
    Сам игрок не создаёт снаряды напрямую.
    Он только сообщает, что хочет выстрелить.
    Реальные снаряды должен создавать WeaponSystem / WeaponFactory.
    """

    def __init__(
        self,
        game: "Game",
        x: float,
        y: float,
        config: dict[str, Any],
        image: pygame.Surface | None = None,
        groups: tuple[pygame.sprite.Group, ...] | None = None,
    ) -> None:
        super().__init__(game, x, y, image=image, groups=groups)

        player_cfg = config.get("player", {})
        weapon_cfg = config.get("weapon", {})
        movement_cfg = config.get("movement", {})
        bounds_cfg = config.get("bounds", {})

        self.speed = float(player_cfg.get("speed", 420))
        self.hp = int(player_cfg.get("hp", 1))
        self.max_hp = self.hp
        self.lives = int(player_cfg.get("lives", 3))

        self.default_weapon = str(weapon_cfg.get("default", "blaster"))
        self.current_weapon = self.default_weapon
        self.base_fire_rate = float(weapon_cfg.get("fire_rate", 0.25))

        self.fire_timer = 0.0

        self.acceleration = float(movement_cfg.get("acceleration", 1800))
        self.friction = float(movement_cfg.get("friction", 0.85))

        self.min_x = float(bounds_cfg.get("min_x", 20))
        self.max_x = float(bounds_cfg.get("max_x", game.width - 20))

        self.invulnerable_time = float(
            game.game_config.get("gameplay", {}).get("invulnerability_time", 1.0)
        )
        self.invulnerable_timer = 0.0

        hitbox_cfg = player_cfg.get("hitbox")
        if isinstance(hitbox_cfg, dict):
            self.set_hitbox(
                int(hitbox_cfg.get("x", 0)),
                int(hitbox_cfg.get("y", 0)),
                int(hitbox_cfg.get("w", self.rect.width)),
                int(hitbox_cfg.get("h", self.rect.height)),
            )

    def handle_input(self) -> None:
        keys = pygame.key.get_pressed()
        controls = self.game.game_config["controls"]

        move_dir = 0
        if keys[getattr(pygame, controls["move_left"])] or keys[pygame.K_a]:
            move_dir -= 1
        if keys[getattr(pygame, controls["move_right"])] or keys[pygame.K_d]:
            move_dir += 1

        self.vx = move_dir * self.speed

        if keys[pygame.K_SPACE]:
            self.try_shoot()

    def try_shoot(self) -> None:
        if self.fire_timer > 0 or not self.is_alive:
            return

        weapon_cfg = self.game.weapons_config.get(self.current_weapon, {})
        cooldown = float(weapon_cfg.get("cooldown", self.base_fire_rate))
        self.fire_timer = cooldown

        self.game.event_bus.emit(
            "player_shot_requested",
            player=self,
            weapon_id=self.current_weapon,
        )

    def apply_drop(self, item_type: str) -> None:
        if item_type in self.game.weapons_config:
            self.current_weapon = item_type
            self.game.event_bus.emit(
                "player_weapon_changed",
                player=self,
                weapon_id=item_type,
            )
            return

        if item_type == "repair":
            self.hp = min(self.max_hp, self.hp + 1)
            return

        if item_type == "extra_life":
            self.lives += 1
            return

        if item_type == "shield":
            self.game.event_bus.emit("shield_requested", owner=self)

    def take_damage(self, amount: int) -> None:
        if not self.is_alive or self.invulnerable_timer > 0:
            return

        self.hp -= amount
        self.invulnerable_timer = self.invulnerable_time

        self.game.event_bus.emit(
            "player_damaged",
            player=self,
            damage=amount,
            hp=self.hp,
            lives=self.lives,
        )

        if self.hp <= 0:
            self.lives -= 1
            self.game.event_bus.emit("player_destroyed", player=self)

            if self.lives <= 0:
                self.kill_entity()
                self.game.event_bus.emit("player_game_over", player=self)
                return

            self.hp = self.max_hp
            self.x = self.game.width / 2
            self.y = self.game.height - 70
            self.vx = 0.0
            self.vy = 0.0
            self.sync_rect()

    def update(self, dt: float) -> None:
        if not self.is_alive:
            return

        if self.fire_timer > 0:
            self.fire_timer = max(0.0, self.fire_timer - dt)

        if self.invulnerable_timer > 0:
            self.invulnerable_timer = max(0.0, self.invulnerable_timer - dt)

        self.handle_input()
        super().update(dt)

        self.x = max(self.min_x, min(self.max_x, self.x))
        self.sync_rect()