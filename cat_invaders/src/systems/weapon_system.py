from __future__ import annotations

from collections.abc import Iterable

import pygame

from src.factories.weapon_factory import WeaponFactory


class WeaponSystem:
    """
    Система стрельбы.
    """

    def __init__(
        self,
        game,
        projectile_group: pygame.sprite.Group,
        all_sprites_group: pygame.sprite.Group | None = None,
    ) -> None:
        self.game = game
        self.projectile_group = projectile_group
        self.all_sprites_group = all_sprites_group

        self.weapon_factory = WeaponFactory(game)

        audio_cfg = self.game.game_config.get("audio", {})
        self.player_shot_sound = self._safe_load_sound(audio_cfg.get("sound_player_shot"))
        self.enemy_shot_sound = self._safe_load_sound(audio_cfg.get("sound_enemy_shot"))

        self.game.event_bus.subscribe("player_shot_requested", self.on_player_shot_requested)
        self.game.event_bus.subscribe("enemy_shot_requested", self.on_enemy_shot_requested)

    def _safe_load_sound(self, path: str | None):
        if not path:
            return None
        try:
            sound = self.game.resource_manager.load_sound(path)
            sound.set_volume(float(self.game.game_config.get("audio", {}).get("effects_volume", 0.7)))
            return sound
        except FileNotFoundError:
            return None

    def _spawn_result(self, result) -> None:
        if result is None:
            return

        if isinstance(result, pygame.sprite.Sprite):
            self.projectile_group.add(result)
            if self.all_sprites_group is not None:
                self.all_sprites_group.add(result)
            self.game.event_bus.emit("projectile_spawned", projectile=result)
            return

        if isinstance(result, Iterable):
            for item in result:
                if isinstance(item, pygame.sprite.Sprite):
                    self.projectile_group.add(item)
                    if self.all_sprites_group is not None:
                        self.all_sprites_group.add(item)
                    self.game.event_bus.emit("projectile_spawned", projectile=item)

    def on_player_shot_requested(self, player, weapon_id: str, **kwargs) -> None:
        result = self.weapon_factory.create_shot(
            weapon_id=weapon_id,
            shooter=player,
            owner="player",
        )
        self._spawn_result(result)

        if self.player_shot_sound is not None:
            self.player_shot_sound.play()

    def on_enemy_shot_requested(self, enemy, weapon_id: str, **kwargs) -> None:
        result = self.weapon_factory.create_shot(
            weapon_id=weapon_id,
            shooter=enemy,
            owner="enemy",
        )
        self._spawn_result(result)

        if self.enemy_shot_sound is not None:
            self.enemy_shot_sound.play()

    def shutdown(self) -> None:
        self.game.event_bus.unsubscribe("player_shot_requested", self.on_player_shot_requested)
        self.game.event_bus.unsubscribe("enemy_shot_requested", self.on_enemy_shot_requested)