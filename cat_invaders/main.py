from __future__ import annotations

import sys
import traceback
from pathlib import Path
from typing import Any, Dict

import pygame

from settings import (
    BASE_DIR,
    CONFIGS_DIR,
    DEFAULT_WINDOW_TITLE,
    IS_DEBUG,
)

from src.core.config_loader import ConfigLoader
from src.core.game import Game


def ensure_project_structure() -> None:
    """
    Проверяет наличие ключевых директорий и файлов проекта.
    Не создает игровые конфиги автоматически, а сразу валит запуск,
    если структура повреждена или проект собран неправильно.
    """
    required_dirs = [
        BASE_DIR / "assets",
        BASE_DIR / "configs",
        BASE_DIR / "configs" / "waves",
        BASE_DIR / "src",
    ]

    required_files = [
        CONFIGS_DIR / "game.json",
        CONFIGS_DIR / "player.json",
        CONFIGS_DIR / "enemies.json",
        CONFIGS_DIR / "weapons.json",
        CONFIGS_DIR / "drops.json",
    ]

    missing_dirs = [str(path) for path in required_dirs if not path.exists()]
    missing_files = [str(path) for path in required_files if not path.exists()]

    if missing_dirs or missing_files:
        parts = []
        if missing_dirs:
            parts.append("Отсутствуют директории:\n" + "\n".join(missing_dirs))
        if missing_files:
            parts.append("Отсутствуют файлы:\n" + "\n".join(missing_files))
        raise FileNotFoundError("\n\n".join(parts))


def load_all_configs() -> Dict[str, Any]:
    """
    Загружает все основные конфиги приложения и все волны.
    Вся настраиваемая логика игры должна храниться именно снаружи, а не в коде.
    """
    loader = ConfigLoader(CONFIGS_DIR)

    game_config = loader.load_json("game.json")
    player_config = loader.load_json("player.json")
    enemies_config = loader.load_json("enemies.json")
    weapons_config = loader.load_json("weapons.json")
    drops_config = loader.load_json("drops.json")
    ai_config = loader.load_json("ai.json")
    waves_config = loader.load_waves("waves")

    return {
        "game": game_config,
        "player": player_config,
        "enemies": enemies_config,
        "weapons": weapons_config,
        "drops": drops_config,
        "ai": ai_config,
        "waves": waves_config,
    }


def validate_loaded_configs(configs: Dict[str, Any]) -> None:
    """
    Минимальная валидация критичных конфигов.
    Это не заменяет полноценную схему, но отсекает самые тупые ошибки.
    """
    required_root_keys = {"game", "player", "enemies", "weapons", "drops","ai", "waves"}
    missing = required_root_keys - set(configs.keys())
    if missing:
        raise ValueError(f"Не загружены обязательные конфиги: {sorted(missing)}")

    if not isinstance(configs["waves"], list) or len(configs["waves"]) < 20:
        raise ValueError(
            "Конфиги волн должны быть загружены списком и содержать не менее 20 волн."
        )

    game_cfg = configs["game"]
    if "window" not in game_cfg:
        raise ValueError("В game.json отсутствует секция 'window'.")

    if "caption" not in game_cfg["window"]:
        # Не критично, но задаем дефолт
        game_cfg["window"]["caption"] = DEFAULT_WINDOW_TITLE

    enemies_cfg = configs["enemies"]
    if not isinstance(enemies_cfg, dict):
        raise ValueError("enemies.json должен содержать объект с описанием врагов.")

    weapons_cfg = configs["weapons"]
    if not isinstance(weapons_cfg, dict):
        raise ValueError("weapons.json должен содержать объект с описанием оружия.")

    drops_cfg = configs["drops"]
    if not isinstance(drops_cfg, dict):
        raise ValueError("drops.json должен содержать объект с описанием дропов.")


def configure_pygame(game_config: Dict[str, Any]) -> None:
    """
    Инициализация pygame и базовых подсистем.
    """
    pygame.init()
    pygame.font.init()
    pygame.mixer.init()

    window_cfg = game_config.get("window", {})
    caption = window_cfg.get("caption", DEFAULT_WINDOW_TITLE)
    pygame.display.set_caption(caption)

    icon_path = window_cfg.get("icon")
    if icon_path:
        full_icon_path = BASE_DIR / icon_path
        if full_icon_path.exists():
            try:
                icon = pygame.image.load(full_icon_path.as_posix())
                pygame.display.set_icon(icon)
            except pygame.error:
                if IS_DEBUG:
                    print(f"[WARN] Не удалось загрузить иконку: {full_icon_path}")


def shutdown_pygame() -> None:
    """
    Корректное завершение pygame.
    """
    try:
        pygame.mixer.quit()
    except Exception:
        pass

    try:
        pygame.font.quit()
    except Exception:
        pass

    try:
        pygame.quit()
    except Exception:
        pass


def print_fatal_error(exc: BaseException) -> None:
    """
    Красивый вывод критической ошибки в консоль.
    """
    print("=" * 80)
    print("КРИТИЧЕСКАЯ ОШИБКА ЗАПУСКА SPACE INVADERS")
    print("=" * 80)
    print(f"{type(exc).__name__}: {exc}")

    if IS_DEBUG:
        print("\nТрассировка:")
        traceback.print_exc()

    print("=" * 80)


def main() -> int:
    """
    Главная точка входа в приложение.
    """
    try:
        ensure_project_structure()

        configs = load_all_configs()
        validate_loaded_configs(configs)
        configure_pygame(configs["game"])

        game = Game(configs=configs)
        game.run()

        return 0

    except KeyboardInterrupt:
        print("\n[INFO] Приложение остановлено пользователем.")
        return 0

    except Exception as exc:
        print_fatal_error(exc)
        return 1

    finally:
        shutdown_pygame()


if __name__ == "__main__":
    sys.exit(main())