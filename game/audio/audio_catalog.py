from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

from game.audio.audio_action import AudioContext

MusicContext = Literal["menu", "gameplay", "game_over"]


@dataclass(frozen=True)
class AudioCue:
    name: str
    file_name: str


@dataclass(frozen=True)
class AudioCatalog:
    cue_by_event: dict[str, str] = field(default_factory=dict)
    music_by_context: dict[MusicContext, str] = field(default_factory=dict)
    cues: dict[str, AudioCue] = field(default_factory=dict)

    def get_event_cue(self, event_name: str) -> str | None:
        return self.cue_by_event.get(event_name)

    def get_music_cue(self, context: AudioContext) -> str | None:
        if context == "pause":
            return None
        return self.music_by_context.get(context)

    def get_file_name(self, cue_name: str) -> str | None:
        cue = self.cues.get(cue_name)
        if cue is None:
            return None
        return cue.file_name


def build_default_audio_catalog() -> AudioCatalog:
    cue_names = {
        "ui_navigate": "menu_button.wav",
        "ui_confirm": "menu_accept.wav",
        "ui_cancel": "menu_reject.wav",
        "player_dash": "player_dash.wav",
        "player_hurt": "player_hurt.wav",
        "player_death": "player_death.wav",
        "collectible": "coin_collect.wav",
        "enemy_shoot": "enemy_shoot.wav",
        "portal_activated": "portal_activation.wav",
        "portal_enter": "portal_enter.wav",
        "explosion": "som_explosao.wav",
        "music_menu": "trilha_menu.wav",
        "music_gameplay": "trilha_gameplay.wav",
        "music_game_over": "trilha_game_over.wav",
    }

    cues = {
        cue_name: AudioCue(name=cue_name, file_name=file_name)
        for cue_name, file_name in cue_names.items()
    }

    cue_by_event = {
        "UINavigated": "ui_navigate",
        "UIConfirmed": "ui_confirm",
        "UICancelled": "ui_cancel",
        "DashStarted": "player_dash",
        "PlayerDamaged": "player_hurt",
        "PlayerDied": "player_death",
        "CollectibleCollected": "collectible",
        "EnemyShotFired": "enemy_shoot",
        # "PortalActivated": "portal_activated",
        "PortalEntered": "portal_enter",
        "ExplosionTriggered": "explosion",
    }

    music_by_context: dict[MusicContext, str] = {
        "menu": "music_menu",
        "gameplay": "music_gameplay",
        "game_over": "music_game_over",
    }

    return AudioCatalog(cue_by_event=cue_by_event, music_by_context=music_by_context, cues=cues)
