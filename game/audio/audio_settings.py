from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

from game.audio.audio_action import AudioGroup

PriorityName = Literal[
    "player_death",
    "portal_enter",
    "player_dash",
    "enemy_shoot",
    "collectible",
    "ui_confirm",
    "ui_cancel",
    "ui_navigate",
]


@dataclass(frozen=True)
class ChannelLayout:
    ui: int = 0
    player: int = 1
    enemy_pool: tuple[int, int, int, int] = (2, 3, 4, 5)
    ambient_pool: tuple[int, int] = (6, 7)


@dataclass
class AudioSettings:
    master_volume: float = 1.0
    music_volume: float = 0.70
    sfx_volume: float = 0.85
    group_volume: dict[AudioGroup, float] = field(
        default_factory=lambda: {
            "music": 1.0,
            "ui": 1.0,
            "player": 1.0,
            "enemy": 0.85,
            "ambient": 0.9,
        }
    )
    muted_groups: set[AudioGroup] = field(default_factory=set)
    channel_layout: ChannelLayout = field(default_factory=ChannelLayout)
    reserved_channels: int = 8
    duck_factor: float = 0.35
    enemy_cue_min_interval_seconds: dict[str, float] = field(
        default_factory=lambda: {
            "enemy_shoot": 0.10,
            "explosion": 0.12,
        }
    )
    sfx_priority: dict[PriorityName, int] = field(
        default_factory=lambda: {
            "player_death": 100,
            "portal_enter": 90,
            "player_dash": 80,
            "enemy_shoot": 60,
            "collectible": 40,
            "ui_confirm": 95,
            "ui_cancel": 95,
            "ui_navigate": 30,
        }
    )
    cue_group: dict[str, AudioGroup] = field(
        default_factory=lambda: {
            "ui_navigate": "ui",
            "ui_confirm": "ui",
            "ui_cancel": "ui",
            "player_dash": "player",
            "player_hurt": "player",
            "player_death": "player",
            "collectible": "ambient",
            "enemy_shoot": "enemy",
            "portal_activated": "ambient",
            "portal_enter": "ambient",
            "explosion": "enemy",
            "music_menu": "music",
            "music_gameplay": "music",
            "music_game_over": "music",
        }
    )
    cue_priority: dict[str, int] = field(
        default_factory=lambda: {
            "ui_navigate": 30,
            "ui_confirm": 95,
            "ui_cancel": 95,
            "player_dash": 80,
            "player_hurt": 85,
            "player_death": 100,
            "collectible": 40,
            "enemy_shoot": 60,
            "portal_activated": 70,
            "portal_enter": 90,
            "explosion": 75,
            "music_menu": 10,
            "music_gameplay": 10,
            "music_game_over": 10,
        }
    )
    music_transition_fade_ms: int = 450

    def resolve_group_volume(self, group: AudioGroup) -> float:
        if group in self.muted_groups:
            return 0.0
        per_group = self.group_volume.get(group, 1.0)
        if group == "music":
            return self.master_volume * self.music_volume * per_group
        return self.master_volume * self.sfx_volume * per_group

    def resolve_group_for_cue(self, cue: str) -> AudioGroup:
        return self.cue_group.get(cue, "ambient")

    def resolve_priority_for_cue(self, cue: str) -> int:
        return self.cue_priority.get(cue, 50)


def build_default_audio_settings() -> AudioSettings:
    return AudioSettings()
