from __future__ import annotations

from pathlib import Path
from typing import Any

import pygame


class ResourceManager:
    """
    Кеширует изображения, звуки и шрифты.
    """

    def __init__(self, base_dir: str | Path) -> None:
        self.base_dir = Path(base_dir)

        self._images: dict[tuple[str, bool], pygame.Surface] = {}
        self._sounds: dict[str, pygame.mixer.Sound] = {}
        self._fonts: dict[tuple[str, int], pygame.font.Font] = {}

    def _resolve(self, relative_path: str | Path) -> Path:
        path = self.base_dir / relative_path
        if not path.exists():
            raise FileNotFoundError(f"Ресурс не найден: {path}")
        return path

    def load_image(self, relative_path: str | Path, alpha: bool = True) -> pygame.Surface:
        key = (str(relative_path), alpha)
        if key in self._images:
            return self._images[key]

        path = self._resolve(relative_path)
        image = pygame.image.load(path.as_posix())
        image = image.convert_alpha() if alpha else image.convert()

        self._images[key] = image
        return image

    def load_scaled_image(
        self,
        relative_path: str | Path,
        size: tuple[int, int],
        alpha: bool = True,
    ) -> pygame.Surface:
        image = self.load_image(relative_path, alpha=alpha)
        return pygame.transform.scale(image, size)

    def load_sound(self, relative_path: str | Path) -> pygame.mixer.Sound:
        key = str(relative_path)
        if key in self._sounds:
            return self._sounds[key]

        path = self._resolve(relative_path)
        sound = pygame.mixer.Sound(path.as_posix())
        self._sounds[key] = sound
        return sound

    def play_music(self, relative_path: str | Path, loops: int = -1) -> None:
        path = self._resolve(relative_path)
        pygame.mixer.music.load(path.as_posix())
        pygame.mixer.music.play(loops)

    def stop_music(self) -> None:
        pygame.mixer.music.stop()

    def load_font(self, relative_path: str | Path, size: int) -> pygame.font.Font:
        key = (str(relative_path), size)
        if key in self._fonts:
            return self._fonts[key]

        path = self._resolve(relative_path)
        font = pygame.font.Font(path.as_posix(), size)
        self._fonts[key] = font
        return font

    def get_default_font(self, size: int) -> pygame.font.Font:
        key = ("__default__", size)
        if key in self._fonts:
            return self._fonts[key]

        font = pygame.font.Font(None, size)
        self._fonts[key] = font
        return font

    def unload_all(self) -> None:
        self._images.clear()
        self._sounds.clear()
        self._fonts.clear()

    def stats(self) -> dict[str, Any]:
        return {
            "images": len(self._images),
            "sounds": len(self._sounds),
            "fonts": len(self._fonts),
        }