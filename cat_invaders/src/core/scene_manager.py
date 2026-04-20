from __future__ import annotations

from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from src.core.game import Game


class BaseScene:
    def __init__(self, game: "Game") -> None:
        self.game = game
        self.is_finished = False
        self.next_scene_name: str | None = None
        self.next_scene_kwargs: dict = {}

    def on_enter(self, **kwargs) -> None:
        pass

    def on_exit(self) -> None:
        pass

    def handle_event(self, event) -> None:
        pass

    def update(self, dt: float) -> None:
        pass

    def render(self, screen) -> None:
        pass


class SceneManager:
    def __init__(self, game: "Game") -> None:
        self.game = game
        self._scene_classes: dict[str, type[BaseScene]] = {}
        self._current_scene: Optional[BaseScene] = None
        self._current_scene_name: Optional[str] = None

    @property
    def current_scene(self) -> Optional[BaseScene]:
        return self._current_scene

    @property
    def current_scene_name(self) -> Optional[str]:
        return self._current_scene_name

    def register(self, name: str, scene_cls: type[BaseScene]) -> None:
        if name in self._scene_classes:
            raise ValueError(f"Сцена '{name}' уже зарегистрирована")
        self._scene_classes[name] = scene_cls

    def has_scene(self, name: str) -> bool:
        return name in self._scene_classes

    def change_scene(self, name: str, **kwargs) -> None:
        if name not in self._scene_classes:
            raise KeyError(f"Сцена '{name}' не зарегистрирована")

        if self._current_scene is not None:
            self._current_scene.on_exit()

        scene_cls = self._scene_classes[name]
        self._current_scene = scene_cls(self.game)
        self._current_scene_name = name
        self._current_scene.on_enter(**kwargs)

    def handle_event(self, event) -> None:
        if self._current_scene is not None:
            self._current_scene.handle_event(event)

    def update(self, dt: float) -> None:
        if self._current_scene is None:
            return

        self._current_scene.update(dt)

        if self._current_scene.is_finished:
            next_scene_name = self._current_scene.next_scene_name
            next_scene_kwargs = self._current_scene.next_scene_kwargs

            if next_scene_name is None:
                raise RuntimeError(
                    f"Сцена '{self._current_scene_name}' завершена, но не указана следующая сцена"
                )

            self.change_scene(next_scene_name, **next_scene_kwargs)

    def render(self, screen) -> None:
        if self._current_scene is not None:
            self._current_scene.render(screen)