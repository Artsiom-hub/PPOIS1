from __future__ import annotations

import math
from typing import TYPE_CHECKING, Any

import pygame

from src.entities.base_entity import BaseEntity

if TYPE_CHECKING:
    from src.core.game import Game


class Enemy(BaseEntity):
    """
    Базовый враг.
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
        super().__init__(game, x, y, image=image, groups=groups)

        self.enemy_id = enemy_id
        self.base_image = self.image.copy()
        self.hp = int(config.get("hp", 1))
        self.max_hp = self.hp
        self.speed = float(config.get("speed", 100))
        self.score = int(config.get("score", 100))

        self.movement = str(config.get("movement", "straight"))
        self.fire = str(config.get("fire", "none"))
        self.weapon = config.get("weapon")
        self.drop_table = str(config.get("drop_table", "basic"))

        self.shield = int(config.get("shield", 0))

        self.fire_timer = 0.0
        self.behavior_time = 0.0
        self.spawn_x = x
        self.spawn_y = y

        self.dive_initialized = False
        self.dive_vx = 0.0
        self.dive_vy = 0.0

    def take_damage(self, amount: int) -> None:
        if not self.is_alive:
            return

        remaining_damage = amount

        if self.shield > 0:
            absorbed = min(self.shield, remaining_damage)
            self.shield -= absorbed
            remaining_damage -= absorbed

        if remaining_damage > 0:
            self.hp -= remaining_damage

        self.game.event_bus.emit(
            "enemy_damaged",
            enemy=self,
            damage=amount,
            hp=self.hp,
            shield=self.shield,
        )

        if self.hp <= 0:
            self.die()

    def die(self) -> None:
        if not self.is_alive:
            return

        self.is_alive = False

        self.game.event_bus.emit("enemy_destroyed", enemy=self, score=self.score)
        self.game.event_bus.emit("drop_requested", enemy=self, drop_table=self.drop_table)

        self.kill()

    def try_shoot(self) -> None:
        if not self.weapon or self.fire == "none" or self.fire_timer > 0 or not self.is_alive:
            return

        weapon_cfg = self.game.weapons_config.get(self.weapon, {})
        cooldown = float(weapon_cfg.get("cooldown", 1.0))
        self.fire_timer = cooldown

        self.game.event_bus.emit(
            "enemy_shot_requested",
            enemy=self,
            weapon_id=self.weapon,
        )

    def update_behavior(self, dt: float) -> None:
        self.behavior_time += dt

        cfg = self.game.ai_config.get("enemy_behavior", {})
        player = getattr(self.game, "current_player", None)

        if self.movement == "straight":
            self.vx = 0.0
            self.vy = self.speed

        elif self.movement == "zigzag":
            tracking_strength = float(cfg.get("zigzag_tracking_strength", 0.6))
            dx = 0.0

            if player is not None and getattr(player, "is_alive", False):
                dx = player.x - self.x

            tracking = max(-70.0, min(70.0, dx * tracking_strength))
            self.vx = math.sin(self.behavior_time * 4.0) * 120.0 + tracking
            self.vy = self.speed

        elif self.movement == "hover":
            follow_strength = float(cfg.get("hover_follow_strength", 1.2))
            dx = 0.0

            if player is not None and getattr(player, "is_alive", False):
                dx = player.x - self.x
                follow = max(-120.0, min(120.0, dx * follow_strength))
                wobble = math.sin(self.behavior_time * 2.5) * 35.0
                self.vx = follow + wobble
            else:
                self.vx = math.sin(self.behavior_time * 2.5) * 80.0

            self.vy = self.speed * 0.35

        elif self.movement == "slow_forward":
            self.vx = 0.0
            self.vy = self.speed * 0.6

        elif self.movement == "dive":
            dive_speed_multiplier = float(cfg.get("dive_speed_multiplier", 1.6))

            if not hasattr(self, "dive_initialized"):
                self.dive_initialized = False
                self.dive_vx = 0.0
                self.dive_vy = 0.0

            if not self.dive_initialized:
                if player is not None and getattr(player, "is_alive", False):
                    dx = player.x - self.x
                    dy = player.y - self.y
                    length = (dx * dx + dy * dy) ** 0.5

                    if length > 0:
                        dive_speed = self.speed * dive_speed_multiplier
                        self.dive_vx = (dx / length) * dive_speed
                        self.dive_vy = (dy / length) * dive_speed
                    else:
                        self.dive_vx = 0.0
                        self.dive_vy = self.speed * dive_speed_multiplier
                else:
                    self.dive_vx = 0.0
                    self.dive_vy = self.speed * dive_speed_multiplier

                self.dive_initialized = True

            self.vx = self.dive_vx
            self.vy = self.dive_vy

        elif self.movement == "teleport":
            chase_strength = float(cfg.get("teleport_chase_strength", 2.0))
            dx = 0.0

            if player is not None and getattr(player, "is_alive", False):
                dx = player.x - self.x
                chase = max(-260.0, min(260.0, dx * chase_strength))
                jitter = math.sin(self.behavior_time * 7.0) * 80.0
                self.vx = chase + jitter
            else:
                self.vx = math.sin(self.behavior_time * 7.0) * 220.0

            self.vy = self.speed * 0.5

        elif self.movement == "boss_pattern":
            self.vx = math.sin(self.behavior_time * 1.5) * 140.0
            self.vy = 40.0 if self.y < 120 else 0.0

        else:
            self.vx = 0.0
            self.vy = self.speed
    def _animate_visual(self) -> None:
        if not hasattr(self, "base_image"):
            self.base_image = self.image.copy()

        current_center = self.rect.center
        phase = int(self.behavior_time * 8) % 2

        if self.enemy_id in {"scout", "zigzag_scout", "shooter_drone", "teleporter"}:
            if phase == 0:
                self.image = self.base_image
            else:
                w = self.base_image.get_width()
                h = self.base_image.get_height()
                self.image = pygame.transform.scale(self.base_image, (w, max(2, h - 2)))

            self.rect = self.image.get_rect(center=current_center)
            self._sync_hitbox()
    def update(self, dt: float) -> None:
        if not self.is_alive:
            return
        self._animate_visual()
        if self.fire_timer > 0:
            self.fire_timer = max(0.0, self.fire_timer - dt)

        self.update_behavior(dt)
        super().update(dt)

        if self.fire in {"single", "sniper", "spread", "drop_mines"}:
            self.try_shoot()

        if self.rect.top > self.game.height + 100:
            self.kill_entity()