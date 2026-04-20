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

        # для стековой модели
        self.request_pop = False
        self.request_push_scene: str | None = None
        self.request_push_kwargs: dict = {}

    def on_enter(self, **kwargs) -> None:
        pass

    def on_exit(self) -> None:
        pass

    def on_pause(self) -> None:
        pass

    def on_resume(self) -> None:
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
        self._scene_stack: list[BaseScene] = []
        self._scene_name_stack: list[str] = []

    @property
    def current_scene(self) -> Optional[BaseScene]:
        return self._scene_stack[-1] if self._scene_stack else None

    @property
    def current_scene_name(self) -> Optional[str]:
        return self._scene_name_stack[-1] if self._scene_name_stack else None

    def register(self, name: str, scene_cls: type[BaseScene]) -> None:
        if name in self._scene_classes:
            raise ValueError(f"Сцена '{name}' уже зарегистрирована")
        self._scene_classes[name] = scene_cls

    def has_scene(self, name: str) -> bool:
        return name in self._scene_classes

    def _create_scene(self, name: str, **kwargs) -> BaseScene:
        if name not in self._scene_classes:
            raise KeyError(f"Сцена '{name}' не зарегистрирована")

        scene_cls = self._scene_classes[name]
        scene = scene_cls(self.game)
        scene.on_enter(**kwargs)
        return scene

    def change_scene(self, name: str, **kwargs) -> None:
        while self._scene_stack:
            scene = self._scene_stack.pop()
            self._scene_name_stack.pop()
            scene.on_exit()

        scene = self._create_scene(name, **kwargs)
        self._scene_stack.append(scene)
        self._scene_name_stack.append(name)

    def push_scene(self, name: str, **kwargs) -> None:
        current = self.current_scene
        if current is not None:
            current.on_pause()

        scene = self._create_scene(name, **kwargs)
        self._scene_stack.append(scene)
        self._scene_name_stack.append(name)

    def pop_scene(self) -> None:
        if not self._scene_stack:
            return

        scene = self._scene_stack.pop()
        self._scene_name_stack.pop()
        scene.on_exit()

        current = self.current_scene
        if current is not None:
            current.on_resume()

    def handle_event(self, event) -> None:
        scene = self.current_scene
        if scene is not None:
            scene.handle_event(event)

    def update(self, dt: float) -> None:
        scene = self.current_scene
        if scene is None:
            return

        scene.update(dt)

        if scene.request_pop:
            scene.request_pop = False
            self.pop_scene()
            return

        if scene.request_push_scene is not None:
            push_name = scene.request_push_scene
            push_kwargs = scene.request_push_kwargs

            scene.request_push_scene = None
            scene.request_push_kwargs = {}

            self.push_scene(push_name, **push_kwargs)
            return

        if scene.is_finished:
            next_scene_name = scene.next_scene_name
            next_scene_kwargs = scene.next_scene_kwargs

            if next_scene_name is None:
                raise RuntimeError(
                    f"Сцена '{self.current_scene_name}' завершена, но не указана следующая сцена"
                )

            self.change_scene(next_scene_name, **next_scene_kwargs)

    def render(self, screen) -> None:
        if not self._scene_stack:
            return

        for scene in self._scene_stack:
            scene.render(screen)