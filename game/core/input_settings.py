from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

import pygame


@dataclass
class InputSettings:
    up: list[int] = field(default_factory=lambda: [pygame.K_w, pygame.K_UP])
    down: list[int] = field(default_factory=lambda: [pygame.K_s, pygame.K_DOWN])
    left: list[int] = field(default_factory=lambda: [pygame.K_a, pygame.K_LEFT])
    right: list[int] = field(default_factory=lambda: [pygame.K_d, pygame.K_RIGHT])
    dash: list[int] = field(default_factory=lambda: [pygame.K_SPACE, pygame.K_LSHIFT, pygame.K_RSHIFT])
    parry: list[int] = field(default_factory=lambda: [pygame.K_j, pygame.K_z])
    bomb: list[int] = field(default_factory=lambda: [pygame.K_i, pygame.K_x])

    def to_dict(self) -> dict[str, list[int]]:
        return {
            "up": self.up,
            "down": self.down,
            "left": self.left,
            "right": self.right,
            "dash": self.dash,
            "parry": self.parry,
            "bomb": self.bomb,
        }

    @classmethod
    def from_dict(cls, data: dict[str, list[int]]) -> InputSettings:
        return cls(
            up=data.get("up", [pygame.K_w, pygame.K_UP]),
            down=data.get("down", [pygame.K_s, pygame.K_DOWN]),
            left=data.get("left", [pygame.K_a, pygame.K_LEFT]),
            right=data.get("right", [pygame.K_d, pygame.K_RIGHT]),
            dash=data.get("dash", [pygame.K_SPACE, pygame.K_LSHIFT, pygame.K_RSHIFT]),
            parry=data.get("parry", [pygame.K_j, pygame.K_z]),
            bomb=data.get("bomb", [pygame.K_i, pygame.K_x]),
        )


class InputSettingsManager:
    def __init__(self, settings_path: Path | None = None) -> None:
        self.settings = InputSettings()
        self._settings_path = settings_path or (Path(__file__).resolve().parent.parent / "assets" / "input_settings.json")
        self.load()

    def load(self) -> None:
        if not self._settings_path.exists():
            return

        try:
            raw_data = json.loads(self._settings_path.read_text(encoding="utf-8"))
            self.settings = InputSettings.from_dict(raw_data)
        except Exception:
            return

    def save(self) -> None:
        try:
            self._settings_path.parent.mkdir(parents=True, exist_ok=True)
            self._settings_path.write_text(
                json.dumps(self.settings.to_dict(), ensure_ascii=True, indent=2),
                encoding="utf-8"
            )
        except Exception:
            return
