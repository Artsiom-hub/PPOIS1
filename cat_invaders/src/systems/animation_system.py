from __future__ import annotations

import pygame


class AnimationSystem:
    """
    Система анимаций.
    Сейчас в основном обновляет группу эффектов/анимаций.
    """

    def __init__(
        self,
        game,
        animation_group: pygame.sprite.Group,
    ) -> None:
        self.game = game
        self.animation_group = animation_group

    def update(self, dt: float) -> None:
        self.animation_group.update(dt)

    def shutdown(self) -> None:
        return None