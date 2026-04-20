from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
ASSETS_DIR = BASE_DIR / "assets"
CONFIGS_DIR = BASE_DIR / "configs"
SRC_DIR = BASE_DIR / "src"

DEFAULT_WINDOW_TITLE = "Cat Invaders"
IS_DEBUG = True