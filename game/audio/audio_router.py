from __future__ import annotations

from dataclasses import dataclass

from game.audio.audio_action import AudioAction, AudioState
from game.audio.audio_catalog import AudioCatalog
from game.audio.audio_settings import AudioSettings
from game.core.events import AudioContextChanged, AudioDuckRequested, AudioUnduckRequested, DomainEvent


DUCK_CUE = "__duck__"
UNDUCK_CUE = "__unduck__"


@dataclass(frozen=True)
class AudioRouter:
    catalog: AudioCatalog
    settings: AudioSettings

    def route(self, event: DomainEvent, state: AudioState) -> AudioAction | None:
        if isinstance(event, AudioDuckRequested):
            return AudioAction(
                cue=DUCK_CUE,
                group="music",
                priority=1000,
                loop=False,
                fade_ms=0,
            )

        if isinstance(event, AudioUnduckRequested):
            return AudioAction(
                cue=UNDUCK_CUE,
                group="music",
                priority=1000,
                loop=False,
                fade_ms=0,
            )

        if isinstance(event, AudioContextChanged):
            return self._route_context_change(event)

        cue = self.catalog.get_event_cue(type(event).__name__)
        if cue is None:
            return None

        return AudioAction(
            cue=cue,
            group=self.settings.resolve_group_for_cue(cue),
            priority=self.settings.resolve_priority_for_cue(cue),
            loop=False,
            fade_ms=0,
        )

    def _route_context_change(self, event: AudioContextChanged) -> AudioAction | None:
        if event.context == "pause":
            return None

        cue = self.catalog.get_music_cue(event.context)
        if cue is None:
            return None

        return AudioAction(
            cue=cue,
            group="music",
            priority=self.settings.resolve_priority_for_cue(cue),
            loop=event.context != "game_over",
            fade_ms=self.settings.music_transition_fade_ms,
        )
