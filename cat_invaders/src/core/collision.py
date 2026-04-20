from __future__ import annotations

from typing import Iterable, TypeVar

import pygame


T = TypeVar("T")


class Collision:
    """
    Набор утилит для проверки коллизий.
    """

    @staticmethod
    def rect_vs_rect(a: pygame.Rect, b: pygame.Rect) -> bool:
        return a.colliderect(b)

    @staticmethod
    def point_vs_rect(point: tuple[int, int], rect: pygame.Rect) -> bool:
        return rect.collidepoint(point)

    @staticmethod
    def circle_vs_circle(
        center_a: tuple[float, float],
        radius_a: float,
        center_b: tuple[float, float],
        radius_b: float,
    ) -> bool:
        dx = center_a[0] - center_b[0]
        dy = center_a[1] - center_b[1]
        radius_sum = radius_a + radius_b
        return (dx * dx + dy * dy) <= (radius_sum * radius_sum)

    @staticmethod
    def entity_vs_entity(entity_a: object, entity_b: object) -> bool:
        rect_a = getattr(entity_a, "rect", None)
        rect_b = getattr(entity_b, "rect", None)

        if not isinstance(rect_a, pygame.Rect) or not isinstance(rect_b, pygame.Rect):
            raise AttributeError("Обе сущности должны иметь атрибут rect типа pygame.Rect")

        return rect_a.colliderect(rect_b)

    @staticmethod
    def entity_vs_group(entity: object, group: Iterable[T]) -> list[T]:
        rect = getattr(entity, "rect", None)
        if not isinstance(rect, pygame.Rect):
            raise AttributeError("Сущность должна иметь атрибут rect типа pygame.Rect")

        collided: list[T] = []
        for item in group:
            item_rect = getattr(item, "rect", None)
            if isinstance(item_rect, pygame.Rect) and rect.colliderect(item_rect):
                collided.append(item)

        return collided

    @staticmethod
    def spritecollide(
        sprite: pygame.sprite.Sprite,
        group: pygame.sprite.Group,
        dokill: bool = False,
    ) -> list[pygame.sprite.Sprite]:
        return pygame.sprite.spritecollide(sprite, group, dokill)

    @staticmethod
    def groupcollide(
        group_a: pygame.sprite.Group,
        group_b: pygame.sprite.Group,
        dokill_a: bool = False,
        dokill_b: bool = False,
    ) -> dict[pygame.sprite.Sprite, list[pygame.sprite.Sprite]]:
        return pygame.sprite.groupcollide(group_a, group_b, dokill_a, dokill_b)