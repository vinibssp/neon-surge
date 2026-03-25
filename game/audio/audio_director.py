from __future__ import annotations

from dataclasses import dataclass, field

from game.audio.audio_action import AudioAction, AudioState
from game.audio.audio_catalog import AudioCatalog
from game.audio.audio_router import DUCK_CUE, UNDUCK_CUE, AudioRouter
from game.audio.audio_settings import AudioSettings
from game.audio.mixer_backend import MixerBackend
from game.core.events import AudioContextChanged, DomainEvent, EventBus, SubscriptionToken


@dataclass
class AudioDirector:
    event_bus: EventBus
    router: AudioRouter
    backend: MixerBackend
    catalog: AudioCatalog
    settings: AudioSettings
    state: AudioState = field(
        default_factory=lambda: AudioState(
            current_context="menu",
            current_track=None,
            is_ducked=False,
            pending_transition=None,
        )
    )

    def initialize(self) -> None:
        self.backend.initialize()
        self._event_tokens = [self.event_bus.on(DomainEvent, self._on_domain_event)]

    def shutdown(self) -> None:
        for token in self._event_tokens:
            self.event_bus.off(token)
        self._event_tokens.clear()
        self.backend.stop()

    def _on_domain_event(self, event: DomainEvent) -> None:
        if isinstance(event, AudioContextChanged):
            self.state.current_context = event.context

        action = self.router.route(event, self.state)
        if action is None:
            return

        if action.cue == DUCK_CUE:
            self.backend.duck()
            self.state.is_ducked = True
            self.state.current_context = "pause"
            return

        if action.cue == UNDUCK_CUE:
            self.backend.unduck()
            self.state.is_ducked = False
            return

        if action.group == "music":
            self._apply_music_action(action)
            return

        file_name = self.catalog.get_file_name(action.cue)
        if file_name is None:
            return
        self.backend.play_sfx(action, file_name)

    def _apply_music_action(self, action: AudioAction) -> None:
        if self.state.is_ducked:
            self.backend.unduck()
            self.state.is_ducked = False

        if self.state.current_track == action.cue:
            return

        file_name = self.catalog.get_file_name(action.cue)
        if file_name is None:
            return

        self.state.pending_transition = action
        self.backend.transition_music(
            next_file_name=file_name,
            fade_out_ms=max(0, action.fade_ms),
            fade_in_ms=max(0, action.fade_ms),
            loop=action.loop,
            volume_override=action.volume_override,
        )
        self.state.current_track = action.cue
        self.state.pending_transition = None

    _event_tokens: list[SubscriptionToken] = field(default_factory=list)
