from __future__ import annotations

from typing import TYPE_CHECKING

import pygame

from src.entities.base_entity import BaseEntity

if TYPE_CHECKING:
    from src.core.game import Game


class Explosion(BaseEntity):
    """
    Анимированный взрыв.
    Если кадров нет, генерирует процедурную анимацию.
    """

    def __init__(
        self,
        game: "Game",
        x: float,
        y: float,
        frames: list[pygame.Surface] | None = None,
        frame_duration: float = 0.05,
        lifetime: float = 0.30,
        groups: tuple[pygame.sprite.Group, ...] | None = None,
    ) -> None:
        self.procedural_frames = frames or self._generate_default_frames()
        image = self.procedural_frames[0]

        super().__init__(game, x, y, image=image, groups=groups)

        self.frames = self.procedural_frames
        self.frame_duration = frame_duration
        self.lifetime = lifetime
        self.age = 0.0
        self.frame_index = 0

    @staticmethod
    def _generate_default_frames() -> list[pygame.Surface]:
        frames: list[pygame.Surface] = []

        sizes = [12, 18, 24, 30, 22, 14]
        colors = [
            (255, 255, 255),
            (255, 230, 120),
            (255, 180, 60),
            (255, 120, 40),
            (255, 90, 30),
            (120, 120, 120),
        ]

        for size, color in zip(sizes, colors):
            surface = pygame.Surface((40, 40), pygame.SRCALPHA)
            pygame.draw.circle(surface, color, (20, 20), size // 2)
            pygame.draw.circle(surface, (255, 255, 255, 120), (20, 20), max(2, size // 5))
            frames.append(surface)

        return frames

    def update(self, dt: float) -> None:
        self.age += dt

        frame_count = len(self.frames)
        if frame_count > 0:
            self.frame_index = min(int(self.age / self.frame_duration), frame_count - 1)
            current_center = self.rect.center
            self.image = self.frames[self.frame_index]
            self.rect = self.image.get_rect(center=current_center)
            self._sync_hitbox()

        if self.age >= self.lifetime:
            self.kill_entity()