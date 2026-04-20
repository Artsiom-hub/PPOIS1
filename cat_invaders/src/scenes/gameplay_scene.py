from __future__ import annotations

import pygame

from src.core.scene_manager import BaseScene
from src.entities.player import Player
from src.entities.shield import Shield
from src.systems.animation_system import AnimationSystem
from src.systems.combat_system import CombatSystem
from src.systems.drop_system import DropSystem
from src.systems.enemy_ai_system import EnemyAISystem
from src.systems.score_system import ScoreSystem
from src.systems.wave_system import WaveSystem
from src.systems.weapon_system import WeaponSystem
from src.ui.hud import HUD


class GameplayScene(BaseScene):
    def on_enter(self, **kwargs) -> None:
        self.background_color = (5, 5, 15)

        self.all_sprites = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.projectiles = pygame.sprite.Group()
        self.drops = pygame.sprite.Group()
        self.shields = pygame.sprite.Group()
        self.effects = pygame.sprite.Group()

        self.big_font = pygame.font.Font(None, 48)

        self.player = self._create_player()
        self.all_sprites.add(self.player)

        self._create_default_shields()

        self.wave_system = WaveSystem(self.game, self.enemies, self.all_sprites)
        self.enemy_ai_system = EnemyAISystem(self.game, self.enemies, self.player)
        self.weapon_system = WeaponSystem(self.game, self.projectiles, self.all_sprites)
        self.drop_system = DropSystem(self.game, self.player, self.drops, self.all_sprites)
        self.combat_system = CombatSystem(
            self.game,
            self.player,
            self.enemies,
            self.projectiles,
            self.shields,
            self.effects,
            self.all_sprites,
        )
        self.score_system = ScoreSystem(self.game)
        self.animation_system = AnimationSystem(self.game, self.effects)
        self.hud = HUD(self.game, self.player, self.score_system, self.wave_system)

        self.current_wave = 1
        self.overlay_message = ""
        self.overlay_timer = 0.0
        self.game.current_player = self.player
        self.game.event_bus.subscribe("player_game_over", self.on_player_game_over)
        self.game.event_bus.subscribe("wave_started", self.on_wave_started)
        self.game.event_bus.subscribe("all_waves_completed", self.on_all_waves_completed)
        audio_cfg = self.game.game_config.get("audio", {})
        music_path = audio_cfg.get("music_gameplay")
        if music_path:
            try:
                self.game.resource_manager.play_music(music_path, loops=-1)
            except FileNotFoundError:
                pass
    def _create_player(self) -> Player:
        player_image = self._load_player_image()

        return Player(
            game=self.game,
            x=self.game.width / 2,
            y=self.game.height - 70,
            config=self.game.player_config,
            image=player_image,
        )

    def _load_player_image(self) -> pygame.Surface:
        sprite_path = self.game.player_config.get("player", {}).get("sprite")
        if sprite_path:
            try:
                return self.game.resource_manager.load_image(sprite_path)
            except FileNotFoundError:
                pass

        surface = pygame.Surface((56, 40), pygame.SRCALPHA)
        pygame.draw.polygon(
            surface,
            (80, 220, 255),
            [(28, 0), (56, 34), (40, 40), (16, 40), (0, 34)],
        )
        return surface

    def _create_default_shields(self) -> None:
        positions = [
            self.game.width * 0.2,
            self.game.width * 0.4,
            self.game.width * 0.6,
            self.game.width * 0.8,
        ]

        for x in positions:
            shield_image = pygame.Surface((70, 35), pygame.SRCALPHA)
            shield_image.fill((80, 180, 120))

            shield = Shield(
                game=self.game,
                x=x,
                y=self.game.height - 150,
                hp=8,
                image=shield_image,
            )
            shield.set_hitbox(0, 0, 70, 35)

            self.shields.add(shield)
            self.all_sprites.add(shield)

    def on_wave_started(self, wave_number: int, **kwargs) -> None:
        self.current_wave = wave_number
        self.overlay_message = f"WAVE {wave_number}"
        self.overlay_timer = 1.5

    def on_all_waves_completed(self, **kwargs) -> None:
        self.overlay_message = "VICTORY"
        self.overlay_timer = 3.0

    def on_player_game_over(self, **kwargs) -> None:
        self.is_finished = True
        self.next_scene_name = "game_over"
        self.next_scene_kwargs = {
            "score": self.score_system.score,
            "wave": self.current_wave,
        }

    def handle_event(self, event) -> None:
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.is_finished = True
            self.next_scene_name = "pause"

    def update(self, dt: float) -> None:
        if not self.player.is_alive:
            return

        self.player.update(dt)
        self.wave_system.update(dt)
        self.enemy_ai_system.update(dt)
        self.projectiles.update(dt)
        self.drop_system.update(dt)
        self.combat_system.update(dt)
        self.animation_system.update(dt)

        if self.overlay_timer > 0:
            self.overlay_timer = max(0.0, self.overlay_timer - dt)

        if self.wave_system.completed and self.overlay_timer <= 0:
            self.is_finished = True
            self.next_scene_name = "menu"

    def render(self, screen) -> None:
        screen.fill(self.background_color)
        self._draw_stars(screen)
        self.all_sprites.draw(screen)
        self.hud.draw(screen)

        if self.overlay_timer > 0 and self.overlay_message:
            text = self.big_font.render(self.overlay_message, True, (255, 255, 255))
            screen.blit(text, text.get_rect(center=(self.game.width // 2, 120)))

    def _draw_stars(self, screen) -> None:
        for i in range(50):
            x = (i * 97) % self.game.width
            y = (i * 53) % self.game.height
            screen.fill((180, 180, 200), (x, y, 2, 2))

    def on_exit(self) -> None:
        self._shutdown_systems()
        if hasattr(self.game, "current_player"):
            self.game.current_player = None
        self.game.resource_manager.stop_music()

    def _shutdown_systems(self) -> None:
        if hasattr(self, "weapon_system"):
            self.weapon_system.shutdown()
        if hasattr(self, "drop_system"):
            self.drop_system.shutdown()
        if hasattr(self, "score_system"):
            self.score_system.shutdown()

        self.game.event_bus.unsubscribe("player_game_over", self.on_player_game_over)
        self.game.event_bus.unsubscribe("wave_started", self.on_wave_started)
        self.game.event_bus.unsubscribe("all_waves_completed", self.on_all_waves_completed)