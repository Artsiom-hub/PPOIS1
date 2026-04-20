from __future__ import annotations

import pygame


class EnemyAISystem:
    """
    Отдельная система AI врагов.
    Сейчас она в основном оркестрирует обновление врагов и оставляет
    детальную механику внутри Enemy.update_behavior().

    Это нормальный промежуточный слой:
    потом сюда можно вынести стратегии полностью.
    """

    def __init__(
        self,
        game,
        enemy_group: pygame.sprite.Group,
        player=None,
    ) -> None:
        self.game = game
        self.enemy_group = enemy_group
        self.player = player

    def update(self, dt: float) -> None:
        for enemy in list(self.enemy_group):
            if not enemy.is_alive:
                continue

            # Пока AI живёт в самой сущности.
            # Система просто запускает update врага.
            enemy.update(dt)

    def shutdown(self) -> None:
        return None