from __future__ import annotations

from typing import TYPE_CHECKING

import pygame

if TYPE_CHECKING:
    from src.core.game import Game


class BaseEntity(pygame.sprite.Sprite):
    """
    Базовая сущность игры.

    Общие возможности:
    - позиция в float
    - скорость
    - image / rect
    - отдельный hitbox
    - состояние жизни
    """

    def __init__(
        self,
        game: "Game",
        x: float,
        y: float,
        image: pygame.Surface | None = None,
        groups: tuple[pygame.sprite.Group, ...] | None = None,
    ) -> None:
        super().__init__(*(groups or ()))

        self.game = game

        self.x = float(x)
        self.y = float(y)

        self.vx = 0.0
        self.vy = 0.0

        self.is_alive = True

        self.image = image if image is not None else self._create_fallback_surface()
        self.rect = self.image.get_rect(center=(int(self.x), int(self.y)))

        self._hitbox_offset_x = 0
        self._hitbox_offset_y = 0
        self._hitbox_width = self.rect.width
        self._hitbox_height = self.rect.height

        self.hitbox = pygame.Rect(
            self.rect.x + self._hitbox_offset_x,
            self.rect.y + self._hitbox_offset_y,
            self._hitbox_width,
            self._hitbox_height,
        )

    def _create_fallback_surface(
        self,
        width: int = 32,
        height: int = 32,
    ) -> pygame.Surface:
        surface = pygame.Surface((width, height), pygame.SRCALPHA)
        surface.fill((255, 0, 255, 180))
        return surface

    def set_hitbox(self, x: int, y: int, w: int, h: int) -> None:
        self._hitbox_offset_x = x
        self._hitbox_offset_y = y
        self._hitbox_width = w
        self._hitbox_height = h
        self._sync_hitbox()

    def _sync_hitbox(self) -> None:
        self.hitbox.x = self.rect.x + self._hitbox_offset_x
        self.hitbox.y = self.rect.y + self._hitbox_offset_y
        self.hitbox.width = self._hitbox_width
        self.hitbox.height = self._hitbox_height

    def sync_rect(self) -> None:
        self.rect.center = (int(self.x), int(self.y))
        self._sync_hitbox()

    def move(self, dt: float) -> None:
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.sync_rect()

    def update(self, dt: float) -> None:
        self.move(dt)

    def render(self, screen: pygame.Surface) -> None:
        screen.blit(self.image, self.rect)

    def take_damage(self, amount: int) -> None:
        """
        Переопределяется в наследниках.
        """
        return None

    def kill_entity(self) -> None:
        self.is_alive = False
        self.kill()