from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class ConfigLoader:
    """
    Загрузчик конфигов из JSON.
    Отвечает только за чтение и базовую валидацию файлов.
    """

    def __init__(self, config_dir: str | Path) -> None:
        self.config_dir = Path(config_dir)

    def _resolve_path(self, filename: str | Path) -> Path:
        path = self.config_dir / filename
        if not path.exists():
            raise FileNotFoundError(f"Конфигурационный файл не найден: {path}")
        return path

    def load_json(self, filename: str | Path) -> dict[str, Any]:
        path = self._resolve_path(filename)

        with path.open("r", encoding="utf-8") as file:
            data = json.load(file)

        if not isinstance(data, dict):
            raise ValueError(f"Ожидался JSON-объект в файле {path}, получено: {type(data).__name__}")

        return data

    def load_json_list(self, filename: str | Path) -> list[Any]:
        path = self._resolve_path(filename)

        with path.open("r", encoding="utf-8") as file:
            data = json.load(file)

        if not isinstance(data, list):
            raise ValueError(f"Ожидался JSON-массив в файле {path}, получено: {type(data).__name__}")

        return data

    def load_waves(self, folder_name: str | Path = "waves") -> list[dict[str, Any]]:
        waves_dir = self.config_dir / folder_name

        if not waves_dir.exists():
            raise FileNotFoundError(f"Папка с волнами не найдена: {waves_dir}")

        if not waves_dir.is_dir():
            raise NotADirectoryError(f"Путь к волнам не является директорией: {waves_dir}")

        wave_files = sorted(waves_dir.glob("wave_*.json"))
        if not wave_files:
            raise FileNotFoundError(f"В папке {waves_dir} не найдено ни одного файла вида wave_*.json")

        waves: list[dict[str, Any]] = []
        for wave_file in wave_files:
            with wave_file.open("r", encoding="utf-8") as file:
                data = json.load(file)

            if not isinstance(data, dict):
                raise ValueError(
                    f"Файл волны должен содержать JSON-объект: {wave_file}"
                )

            waves.append(data)

        return waves