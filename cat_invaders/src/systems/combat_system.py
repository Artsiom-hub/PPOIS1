from __future__ import annotations

import pygame

from src.entities.explosion import Explosion


class CombatSystem:
    """
    Система боёвки:
    - пули игрока против врагов
    - пули врагов против игрока
    - столкновения враг/игрок
    - столкновения пуль со щитами
    """

    def __init__(
        self,
        game,
        player,
        enemy_group: pygame.sprite.Group,
        projectile_group: pygame.sprite.Group,
        shield_group: pygame.sprite.Group | None = None,
        explosion_group: pygame.sprite.Group | None = None,
        all_sprites_group: pygame.sprite.Group | None = None,
    ) -> None:
        self.game = game
        self.player = player
        self.enemy_group = enemy_group
        self.projectile_group = projectile_group
        self.shield_group = shield_group if shield_group is not None else pygame.sprite.Group()
        self.explosion_group = explosion_group if explosion_group is not None else pygame.sprite.Group()
        self.all_sprites_group = all_sprites_group
        audio_cfg = self.game.game_config.get("audio", {})
        self.explosion_sound = self._safe_load_sound(audio_cfg.get("sound_explosion"))
        self.player_hit_sound = self._safe_load_sound(audio_cfg.get("sound_player_hit"))
    def _safe_load_sound(self, path: str | None):
        if not path:
            return None
        try:
            sound = self.game.resource_manager.load_sound(path)
            sound.set_volume(float(self.game.game_config.get("audio", {}).get("effects_volume", 0.7)))
            return sound
        except FileNotFoundError:
            return None

    def update(self, dt: float) -> None:
        self._handle_player_projectiles_vs_enemies()
        self._handle_enemy_projectiles_vs_player()
        self._handle_projectiles_vs_shields()
        self._handle_enemy_vs_player()
        self._handle_enemy_vs_shields()

    def _spawn_explosion(self, x: float, y: float) -> None:
        explosion = Explosion(
            game=self.game,
            x=x,
            y=y,
        )
        self.explosion_group.add(explosion)

        if self.all_sprites_group is not None:
            self.all_sprites_group.add(explosion)

        self.game.event_bus.emit("explosion_spawned", explosion=explosion)
        if self.explosion_sound is not None:
            self.explosion_sound.play()

    def _handle_player_projectiles_vs_enemies(self) -> None:
        player_projectiles = [p for p in self.projectile_group if getattr(p, "owner", None) == "player"]

        for projectile in player_projectiles:
            if not projectile.alive():
                continue

            hits = pygame.sprite.spritecollide(projectile, self.enemy_group, dokill=False)
            for enemy in hits:
                if not projectile.hitbox.colliderect(enemy.hitbox):
                    continue

                enemy.take_damage(projectile.damage)
                self.game.event_bus.emit(
                    "projectile_hit_enemy",
                    projectile=projectile,
                    enemy=enemy,
                    damage=projectile.damage,
                )

                if not projectile.piercing:
                    self._spawn_explosion(projectile.x, projectile.y)
                    projectile.kill_entity()
                    break

    def _handle_enemy_projectiles_vs_player(self) -> None:
        if self.player is None or not self.player.is_alive:
            return

        enemy_projectiles = [p for p in self.projectile_group if getattr(p, "owner", None) == "enemy"]

        for projectile in enemy_projectiles:
            if not projectile.alive():
                continue

            if self.player.hitbox.colliderect(projectile.hitbox):
                self.player.take_damage(projectile.damage)
                self.game.event_bus.emit(
                    "projectile_hit_player",
                    projectile=projectile,
                    player=self.player,
                    damage=projectile.damage,
                )
                if self.player_hit_sound is not None:
                    self.player_hit_sound.play()

                self._spawn_explosion(projectile.x, projectile.y)
                projectile.kill_entity()

    def _handle_projectiles_vs_shields(self) -> None:
        if len(self.shield_group) == 0:
            return

        for projectile in list(self.projectile_group):
            if not projectile.alive():
                continue

            hits = pygame.sprite.spritecollide(projectile, self.shield_group, dokill=False)
            for shield in hits:
                if not projectile.hitbox.colliderect(shield.hitbox):
                    continue

                shield.take_damage(projectile.damage)
                self.game.event_bus.emit(
                    "projectile_hit_shield",
                    projectile=projectile,
                    shield=shield,
                    damage=projectile.damage,
                )

                if not projectile.piercing:
                    self._spawn_explosion(projectile.x, projectile.y)
                    projectile.kill_entity()
                    break

    def _handle_enemy_vs_player(self) -> None:
        if self.player is None or not self.player.is_alive:
            return

        hits = pygame.sprite.spritecollide(self.player, self.enemy_group, dokill=False)
        for enemy in hits:
            if not self.player.hitbox.colliderect(enemy.hitbox):
                continue

            self.player.take_damage(max(1, enemy.hp))
            enemy.take_damage(enemy.hp)

            self.game.event_bus.emit(
                "enemy_collided_with_player",
                enemy=enemy,
                player=self.player,
            )

            self._spawn_explosion(enemy.x, enemy.y)

    def _handle_enemy_vs_shields(self) -> None:
        if len(self.shield_group) == 0:
            return

        for enemy in list(self.enemy_group):
            if not enemy.alive():
                continue

            hits = pygame.sprite.spritecollide(enemy, self.shield_group, dokill=False)
            for shield in hits:
                if not enemy.hitbox.colliderect(shield.hitbox):
                    continue

                shield.take_damage(max(1, enemy.hp))
                enemy.take_damage(enemy.hp)

                self.game.event_bus.emit(
                    "enemy_collided_with_shield",
                    enemy=enemy,
                    shield=shield,
                )

                self._spawn_explosion(enemy.x, enemy.y)

    def shutdown(self) -> None:
        return None