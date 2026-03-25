from __future__ import annotations

from pathlib import Path

import pygame_gui

from .theme.retrowave_theme import THEME_DATA

def create_ui_manager(window_size: tuple[int, int]) -> pygame_gui.UIManager:
    return pygame_gui.UIManager(window_size, THEME_DATA)
