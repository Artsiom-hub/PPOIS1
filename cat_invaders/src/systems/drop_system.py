from __future__ import annotations

import pygame

from src.factories.drop_factory import DropFactory


class DropSystem:
    """
    Система дропов:
    - создаёт предметы после смерти врагов
    - проверяет подбор игроком
    """

    def __init__(
        self,
        game,
        player,
        drop_group: pygame.sprite.Group,
        all_sprites_group: pygame.sprite.Group | None = None,
    ) -> None:
        self.game = game
        self.player = player
        self.drop_group = drop_group
        self.all_sprites_group = all_sprites_group

        self.drop_factory = DropFactory(game)

        self.game.event_bus.subscribe("drop_requested", self.on_drop_requested)
        audio_cfg = self.game.game_config.get("audio", {})
        self.drop_pickup_sound = self._safe_load_sound(audio_cfg.get("sound_drop_pickup"))
    def _safe_load_sound(self, path: str | None):
        if not path:
            return None
        try:
            sound = self.game.resource_manager.load_sound(path)
            sound.set_volume(float(self.game.game_config.get("audio", {}).get("effects_volume", 0.7)))
            return sound
        except FileNotFoundError:
            return None
    def on_drop_requested(self, enemy, drop_table: str | None = None, **kwargs) -> None:
        item = self.drop_factory.create_drop_from_enemy(
            enemy=enemy,
            drop_table_id=drop_table,
        )
        if item is None:
            return

        self.drop_group.add(item)
        if self.all_sprites_group is not None:
            self.all_sprites_group.add(item)

        self.game.event_bus.emit("drop_spawned", item=item)

    def update(self, dt: float) -> None:
        self.drop_group.update(dt)

        if self.player is None or not self.player.is_alive:
            return

        collected = pygame.sprite.spritecollide(self.player, self.drop_group, dokill=False)
        for item in collected:
            if self.player.hitbox.colliderect(item.hitbox):
                item.apply_to(self.player)
                if self.drop_pickup_sound is not None:
                    self.drop_pickup_sound.play()

    def shutdown(self) -> None:
        self.game.event_bus.unsubscribe("drop_requested", self.on_drop_requested)