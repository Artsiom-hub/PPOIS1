from __future__ import annotations

from typing import TYPE_CHECKING

import pygame

from src.entities.base_entity import BaseEntity

if TYPE_CHECKING:
    from src.core.game import Game


class Projectile(BaseEntity):
    """
    Универсальный снаряд.
    owner: 'player' | 'enemy'
    """

    def __init__(
        self,
        game: "Game",
        x: float,
        y: float,
        vx: float,
        vy: float,
        damage: int,
        owner: str,
        image: pygame.Surface | None = None,
        piercing: bool = False,
        lifetime: float = 5.0,
        groups: tuple[pygame.sprite.Group, ...] | None = None,
    ) -> None:
        super().__init__(game, x, y, image=image, groups=groups)

        self.vx = vx
        self.vy = vy
        self.damage = int(damage)
        self.owner = owner
        self.piercing = piercing
        self.lifetime = float(lifetime)
        self.age = 0.0

        self.base_image = self.image.copy()
        self.animation_timer = 0.0
        self.animation_frame = 0

    def _animate_bullet(self) -> None:
        self.animation_timer += 1

        # Для мин — небольшое вращение
        if self.rect.width >= 16 and self.rect.height >= 16:
            angle = (self.age * 360) % 360
            current_center = self.rect.center
            self.image = pygame.transform.rotate(self.base_image, angle)
            self.rect = self.image.get_rect(center=current_center)
            self._sync_hitbox()
            return

        # Для обычных пуль — мигание/пульсация
        phase = int(self.age * 20) % 2

        current_center = self.rect.center
        if phase == 0:
            self.image = self.base_image.copy()
        else:
            w = max(2, self.base_image.get_width() + 2)
            h = max(4, self.base_image.get_height() + 4)
            self.image = pygame.transform.scale(self.base_image, (w, h))

        self.rect = self.image.get_rect(center=current_center)
        self._sync_hitbox()

    def update(self, dt: float) -> None:
        self.age += dt
        if self.age >= self.lifetime:
            self.kill_entity()
            return

        self._animate_bullet()
        super().update(dt)

        if (
            self.rect.bottom < -50
            or self.rect.top > self.game.height + 50
            or self.rect.right < -50
            or self.rect.left > self.game.width + 50
        ):
            self.kill_entity()