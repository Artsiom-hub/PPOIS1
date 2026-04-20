from __future__ import annotations

import pygame

from src.factories.enemy_factory import EnemyFactory


class WaveSystem:
    """
    Система волн.
    Читает configs["waves"], спавнит врагов по таймингам и переключает волны.
    """

    def __init__(
        self,
        game,
        enemy_group: pygame.sprite.Group,
        all_sprites_group: pygame.sprite.Group | None = None,
    ) -> None:
        self.game = game
        self.enemy_group = enemy_group
        self.all_sprites_group = all_sprites_group

        self.enemy_factory = EnemyFactory(game)

        gameplay_cfg = self.game.game_config.get("gameplay", {})
        starting_wave = int(gameplay_cfg.get("starting_wave", 1))

        self.waves = self.game.waves_config
        self.current_wave_index = max(0, starting_wave - 1)

        self.wave_started = False
        self.wave_finished = False
        self.wave_timer = 0.0
        self.spawn_index = 0
        self.completed = False

        self.pending_spawns: list[dict] = []

    @property
    def current_wave(self) -> dict | None:
        if 0 <= self.current_wave_index < len(self.waves):
            return self.waves[self.current_wave_index]
        return None

    @property
    def current_wave_number(self) -> int:
        wave = self.current_wave
        if wave is None:
            return 0
        return int(wave.get("wave_id", self.current_wave_index + 1))

    def start_wave(self) -> None:
        wave = self.current_wave
        if wave is None:
            self.completed = True
            return

        self.wave_timer = 0.0
        self.spawn_index = 0
        self.wave_started = True
        self.wave_finished = False
        self.pending_spawns = sorted(wave.get("spawns", []), key=lambda s: float(s.get("time", 0.0)))

        self.game.event_bus.emit(
            "wave_started",
            wave_number=self.current_wave_number,
            wave_config=wave,
        )

    def update(self, dt: float) -> None:
        if self.completed:
            return

        if not self.wave_started:
            self.start_wave()
            return

        self.wave_timer += dt
        self._process_spawns()

        if self._is_wave_cleared():
            self._finish_wave()

    def _process_spawns(self) -> None:
        while self.spawn_index < len(self.pending_spawns):
            spawn = self.pending_spawns[self.spawn_index]
            spawn_time = float(spawn.get("time", 0.0))

            if spawn_time > self.wave_timer:
                break

            self._spawn_entry(spawn)
            self.spawn_index += 1

    def _spawn_entry(self, spawn: dict) -> None:
        enemy_type = str(spawn.get("enemy_type"))
        count = int(spawn.get("count", 1))
        formation = str(spawn.get("formation", "line"))
        start_x = float(spawn.get("start_x", 100))
        start_y = float(spawn.get("start_y", -50))
        spacing = float(spawn.get("spacing", 60.0))

        enemies = self.enemy_factory.create_wave_batch(
            enemy_id=enemy_type,
            count=count,
            start_x=start_x,
            start_y=start_y,
            spacing=spacing,
            formation=formation,
        )

        for enemy in enemies:
            self.enemy_group.add(enemy)
            if self.all_sprites_group is not None:
                self.all_sprites_group.add(enemy)

            self.game.event_bus.emit("enemy_spawned", enemy=enemy, wave_number=self.current_wave_number)

    def _is_wave_cleared(self) -> bool:
        all_spawns_done = self.spawn_index >= len(self.pending_spawns)
        no_enemies_left = len(self.enemy_group) == 0
        return all_spawns_done and no_enemies_left

    def _finish_wave(self) -> None:
        if self.wave_finished:
            return

        self.wave_finished = True
        self.game.event_bus.emit(
            "wave_completed",
            wave_number=self.current_wave_number,
        )

        self.current_wave_index += 1
        if self.current_wave_index >= len(self.waves):
            self.completed = True
            self.game.event_bus.emit("all_waves_completed")
            return

        self.wave_started = False

    def reset(self) -> None:
        gameplay_cfg = self.game.game_config.get("gameplay", {})
        starting_wave = int(gameplay_cfg.get("starting_wave", 1))

        self.current_wave_index = max(0, starting_wave - 1)
        self.wave_started = False
        self.wave_finished = False
        self.wave_timer = 0.0
        self.spawn_index = 0
        self.completed = False
        self.pending_spawns = []

    def shutdown(self) -> None:
        return None