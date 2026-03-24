from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

AudioGroup = Literal["music", "ui", "player", "enemy", "ambient"]
AudioContext = Literal["menu", "gameplay", "pause", "game_over"]


@dataclass(frozen=True)
class AudioAction:
    cue: str
    group: AudioGroup
    priority: int
    loop: bool = False
    fade_ms: int = 0
    volume_override: float | None = None


@dataclass
class AudioState:
    current_context: AudioContext
    current_track: str | None
    is_ducked: bool
    pending_transition: AudioAction | None
