from __future__ import annotations

from pathlib import Path

import pygame_gui

_THEME_FILE = Path(__file__).resolve().parent / "retrowave_theme.json"


def create_ui_manager(window_size: tuple[int, int]) -> pygame_gui.UIManager:
    return pygame_gui.UIManager(window_size, str(_THEME_FILE))
