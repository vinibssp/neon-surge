from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

import pygame


@dataclass
class InputSettings:
    # Keyboard mappings
    up: list[int] = field(default_factory=lambda: [pygame.K_w, pygame.K_UP])
    down: list[int] = field(default_factory=lambda: [pygame.K_s, pygame.K_DOWN])
    left: list[int] = field(default_factory=lambda: [pygame.K_a, pygame.K_LEFT])
    right: list[int] = field(default_factory=lambda: [pygame.K_d, pygame.K_RIGHT])
    dash: list[int] = field(default_factory=lambda: [pygame.K_SPACE, pygame.K_LSHIFT, pygame.K_RSHIFT])
    parry: list[int] = field(default_factory=lambda: [pygame.K_j, pygame.K_z])
    bomb: list[int] = field(default_factory=lambda: [pygame.K_i, pygame.K_x])

    # Joystick mappings (button indices)
    joy_dash: list[int] = field(default_factory=lambda: [0, 1])  # Usually A/B or X/O
    joy_parry: list[int] = field(default_factory=lambda: [2, 3]) # Usually X/Y or Square/Triangle
    joy_bomb: list[int] = field(default_factory=lambda: [4, 5])  # Usually Bumpers/Triggers
    joy_pause: list[int] = field(default_factory=lambda: [6, 7]) # Usually Select/Start or Share/Options

    # Deadzone for axes
    joy_deadzone: float = 0.2

    def to_dict(self) -> dict:
        return {
            "up": self.up,
            "down": self.down,
            "left": self.left,
            "right": self.right,
            "dash": self.dash,
            "parry": self.parry,
            "bomb": self.bomb,
            "joy_dash": self.joy_dash,
            "joy_parry": self.joy_parry,
            "joy_bomb": self.joy_bomb,
            "joy_pause": self.joy_pause,
            "joy_deadzone": self.joy_deadzone,
        }

    @classmethod
    def from_dict(cls, data: dict) -> InputSettings:
        return cls(
            up=data.get("up", [pygame.K_w, pygame.K_UP]),
            down=data.get("down", [pygame.K_s, pygame.K_DOWN]),
            left=data.get("left", [pygame.K_a, pygame.K_LEFT]),
            right=data.get("right", [pygame.K_d, pygame.K_RIGHT]),
            dash=data.get("dash", [pygame.K_SPACE, pygame.K_LSHIFT, pygame.K_RSHIFT]),
            parry=data.get("parry", [pygame.K_j, pygame.K_z]),
            bomb=data.get("bomb", [pygame.K_i, pygame.K_x]),
            joy_dash=data.get("joy_dash", [0, 1]),
            joy_parry=data.get("joy_parry", [2, 3]),
            joy_bomb=data.get("joy_bomb", [4, 5]),
            joy_pause=data.get("joy_pause", [6, 7]),
            joy_deadzone=data.get("joy_deadzone", 0.2),
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
