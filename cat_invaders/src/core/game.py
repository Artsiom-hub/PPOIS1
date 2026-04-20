from __future__ import annotations

import importlib
from typing import Any

import pygame

from settings import BASE_DIR, CONFIGS_DIR
from src.core.event_bus import EventBus
from src.core.high_score_manager import HighScoreManager
from src.core.resource_manager import ResourceManager
from src.core.scene_manager import SceneManager


class Game:
    """
    Центральный объект игры.
    """

    def __init__(self, configs: dict[str, Any]) -> None:
        self.configs = configs
        self.game_config = configs["game"]
        self.player_config = configs["player"]
        self.enemies_config = configs["enemies"]
        self.weapons_config = configs["weapons"]
        self.drops_config = configs["drops"]
        self.ai_config = configs["ai"]
        self.waves_config = configs["waves"]

        window_cfg = self.game_config.get("window", {})
        perf_cfg = self.game_config.get("performance", {})

        self.width = int(window_cfg.get("width", 900))
        self.height = int(window_cfg.get("height", 700))
        self.caption = window_cfg.get("caption", "Space Invaders")
        self.fullscreen = bool(window_cfg.get("fullscreen", False))
        self.fps = int(perf_cfg.get("fps", 60))

        self.is_running = True
        self.is_paused = False
        self.current_player = None

        self.event_bus = EventBus()
        self.resource_manager = ResourceManager(BASE_DIR)
        self.scene_manager = SceneManager(self)
        self.high_score_manager = HighScoreManager(CONFIGS_DIR / "high_scores.json")
        print("HIGH SCORE MANAGER READY")
        self.clock = pygame.time.Clock()
        self.screen = self._create_display()

        self._apply_audio_settings()
        self._register_default_scenes()

    def _create_display(self) -> pygame.Surface:
        flags = 0
        if self.fullscreen:
            flags |= pygame.FULLSCREEN

        screen = pygame.display.set_mode((self.width, self.height), flags)
        pygame.display.set_caption(self.caption)
        return screen

    def _apply_audio_settings(self) -> None:
        audio_cfg = self.game_config.get("audio", {})
        master_volume = float(audio_cfg.get("master_volume", 1.0))
        music_volume = float(audio_cfg.get("music_volume", 0.5))
        pygame.mixer.music.set_volume(max(0.0, min(1.0, master_volume * music_volume)))

    def _register_default_scenes(self) -> None:
        scene_imports = {
            "menu": "src.scenes.menu_scene:MenuScene",
            "gameplay": "src.scenes.gameplay_scene:GameplayScene",
            "pause": "src.scenes.pause_scene:PauseScene",
            "game_over": "src.scenes.game_over_scene:GameOverScene",
            "help": "src.scenes.help_scene:HelpScene",
            "scores": "src.scenes.score_scene:ScoreScene",
        }

        for scene_name, import_path in scene_imports.items():
            scene_cls = self._import_scene(import_path)
            self.scene_manager.register(scene_name, scene_cls)

    def _import_scene(self, import_path: str):
        module_name, class_name = import_path.split(":")
        try:
            module = importlib.import_module(module_name)
            scene_cls = getattr(module, class_name)
            return scene_cls
        except Exception as exc:
            raise ImportError(
                f"Не удалось импортировать сцену '{class_name}' из модуля '{module_name}'. "
                f"Исходная ошибка: {type(exc).__name__}: {exc}"
            ) from exc

    def change_scene(self, scene_name: str, **kwargs) -> None:
        self.scene_manager.change_scene(scene_name, **kwargs)

    def stop(self) -> None:
        self.is_running = False

    def process_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.stop()
                continue

            self.scene_manager.handle_event(event)

    def update(self, dt: float) -> None:
        if self.is_paused:
            return
        self.scene_manager.update(dt)

    def render(self) -> None:
        self.scene_manager.render(self.screen)
        pygame.display.flip()

    def run(self) -> None:
        if self.scene_manager.current_scene is None:
            if self.scene_manager.has_scene("menu"):
                self.change_scene("menu")
            elif self.scene_manager.has_scene("gameplay"):
                self.change_scene("gameplay")
            else:
                raise RuntimeError(
                    "Не зарегистрировано ни одной стартовой сцены. "
                    "Минимум должна существовать сцена 'menu' или 'gameplay'."
                )

        while self.is_running:
            dt = self.clock.tick(self.fps) / 1000.0
            self.process_events()
            self.update(dt)
            self.render()

        self.shutdown()

    def shutdown(self) -> None:
        self.resource_manager.unload_all()
        self.event_bus.clear()