from __future__ import annotations

from pathlib import Path

import pygame_gui

_THEME_FILE = Path(__file__).resolve().parent / "retrowave_theme.json"
_PRELOADED_FONTS: list[dict[str, str | int]] = [
    {"name": "noto_sans", "point_size": 14, "style": "bold", "antialiased": "1"},
    {"name": "noto_sans", "point_size": 48, "style": "bold", "antialiased": "1"},
]


def create_ui_manager(window_size: tuple[int, int]) -> pygame_gui.UIManager:
    manager = pygame_gui.UIManager(window_size, str(_THEME_FILE))
    manager.preload_fonts(_PRELOADED_FONTS)
    return manager
