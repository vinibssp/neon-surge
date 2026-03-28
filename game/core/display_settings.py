from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import pygame

from game.config import SCREEN_HEIGHT, SCREEN_WIDTH


@dataclass
class DisplaySettings:
    fullscreen: bool = False


class DisplaySettingsManager:
    def __init__(self, settings_path: Path | None = None) -> None:
        self.settings = DisplaySettings()
        self._settings_path = settings_path or (Path(__file__).resolve().parent.parent / "assets" / "display_settings.json")
        self.load()

    def load(self) -> None:
        if not self._settings_path.exists():
            return
        try:
            raw_data = json.loads(self._settings_path.read_text(encoding="utf-8"))
        except Exception:
            return

        fullscreen = raw_data.get("fullscreen")
        if isinstance(fullscreen, bool):
            self.settings.fullscreen = fullscreen

    def save(self) -> None:
        payload = {"fullscreen": self.settings.fullscreen}
        try:
            self._settings_path.parent.mkdir(parents=True, exist_ok=True)
            self._settings_path.write_text(json.dumps(payload, ensure_ascii=True, indent=2), encoding="utf-8")
        except Exception:
            return

    def apply_display_mode(self) -> pygame.Surface:
        flags = pygame.FULLSCREEN if self.settings.fullscreen else 0
        return pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), flags)

    def set_fullscreen(self, fullscreen: bool) -> pygame.Surface:
        if self.settings.fullscreen == fullscreen:
            current_surface = pygame.display.get_surface()
            if current_surface is not None:
                return current_surface
            return self.apply_display_mode()

        self.settings.fullscreen = fullscreen
        self.save()
        return self.apply_display_mode()

    def toggle_fullscreen(self) -> pygame.Surface:
        return self.set_fullscreen(not self.settings.fullscreen)
