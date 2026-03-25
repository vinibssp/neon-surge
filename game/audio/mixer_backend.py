from __future__ import annotations

import logging
from pathlib import Path
import time

import pygame

from game.audio.audio_action import AudioAction, AudioGroup
from game.audio.audio_settings import AudioSettings

_logger = logging.getLogger(__name__)
MUSIC_ENDED_EVENT = pygame.USEREVENT + 7


class MixerBackend:
    def __init__(self, settings: AudioSettings) -> None:
        self.settings = settings
        self._sounds_dir = Path(__file__).resolve().parent.parent / "assets" / "sounds"
        self._sound_cache: dict[str, pygame.mixer.Sound] = {}
        self._channel_priority: dict[int, int] = {}
        self._last_enemy_cue_played_at: dict[str, float] = {}
        self._mixer_available = False

    def initialize(self) -> None:
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init()
            pygame.mixer.set_num_channels(max(self.settings.reserved_channels, 8))
            pygame.mixer.set_reserved(self.settings.reserved_channels)
            self._mixer_available = True
        except Exception:
            self._mixer_available = False
            _logger.exception("Audio mixer initialization failed; continuing in silent mode")

    def play_sfx(self, action: AudioAction, file_name: str) -> None:
        if action.group == "music":
            return
        if not self._mixer_available:
            return

        try:
            if action.group == "enemy" and self._is_enemy_rate_limited(action.cue):
                return

            sound = self._load_sound(file_name)
            if sound is None:
                return

            channel_id = self._select_channel_id(action.group, action.priority)
            if channel_id is None:
                return

            channel = pygame.mixer.Channel(channel_id)
            volume = self.settings.resolve_group_volume(action.group)
            if action.volume_override is not None:
                volume = max(0.0, min(1.0, action.volume_override))
            sound.set_volume(volume)
            loops = -1 if action.loop else 0
            channel.play(sound, loops=loops)
            self._channel_priority[channel_id] = action.priority
            if action.group == "enemy":
                self._last_enemy_cue_played_at[action.cue] = time.monotonic()
        except Exception:
            _logger.exception("Failed to play SFX cue=%s group=%s", action.cue, action.group)

    def play_music(self, file_name: str, loop: bool = True, fade_ms: int = 0, volume_override: float | None = None) -> None:
        if not self._mixer_available:
            return

        try:
            track_path = self._sounds_dir / file_name
            pygame.mixer.music.load(str(track_path))
            volume = self.settings.resolve_group_volume("music")
            if volume_override is not None:
                volume = max(0.0, min(1.0, volume_override))
            pygame.mixer.music.set_volume(volume)
            loops = -1 if loop else 0
            pygame.mixer.music.set_endevent(0 if loop else MUSIC_ENDED_EVENT)
            pygame.mixer.music.play(loops=loops, fade_ms=max(0, fade_ms))
        except Exception:
            _logger.exception("Failed to play music file=%s", file_name)

    def transition_music(
        self,
        next_file_name: str,
        fade_out_ms: int,
        fade_in_ms: int,
        loop: bool = True,
        volume_override: float | None = None,
    ) -> None:
        if not self._mixer_available:
            return

        try:
            if pygame.mixer.music.get_busy():
                pygame.mixer.music.fadeout(max(0, fade_out_ms))
            self.play_music(
                file_name=next_file_name,
                loop=loop,
                fade_ms=max(0, fade_in_ms),
                volume_override=volume_override,
            )
        except Exception:
            _logger.exception("Failed to transition music to file=%s", next_file_name)

    def stop(self, group: AudioGroup | None = None) -> None:
        if not self._mixer_available:
            return

        try:
            if group is None:
                pygame.mixer.stop()
                pygame.mixer.music.stop()
                return

            if group == "music":
                pygame.mixer.music.stop()
                return

            for channel_id in self._channels_for_group(group):
                pygame.mixer.Channel(channel_id).stop()
        except Exception:
            _logger.exception("Failed to stop audio group=%s", group)

    def fade(self, group: AudioGroup, fade_ms: int) -> None:
        if not self._mixer_available:
            return

        try:
            if group == "music":
                pygame.mixer.music.fadeout(max(0, fade_ms))
                return

            fade_ms = max(0, fade_ms)
            for channel_id in self._channels_for_group(group):
                channel = pygame.mixer.Channel(channel_id)
                if channel.get_busy():
                    channel.fadeout(fade_ms)
        except Exception:
            _logger.exception("Failed to fade group=%s", group)

    def duck(self) -> None:
        if not self._mixer_available:
            return

        try:
            base = self.settings.resolve_group_volume("music")
            pygame.mixer.music.set_volume(base * self.settings.duck_factor)
        except Exception:
            _logger.exception("Failed to duck music")

    def unduck(self) -> None:
        if not self._mixer_available:
            return

        try:
            pygame.mixer.music.set_volume(self.settings.resolve_group_volume("music"))
        except Exception:
            _logger.exception("Failed to unduck music")

    def apply_runtime_settings(self, is_ducked: bool = False) -> None:
        if not self._mixer_available:
            return

        try:
            music_volume = self.settings.resolve_group_volume("music")
            if is_ducked:
                music_volume *= self.settings.duck_factor
            pygame.mixer.music.set_volume(music_volume)

            for group in ("ui", "player", "enemy", "ambient"):
                group_volume = self.settings.resolve_group_volume(group)
                for channel_id in self._channels_for_group(group):
                    pygame.mixer.Channel(channel_id).set_volume(group_volume)
        except Exception:
            _logger.exception("Failed to apply runtime audio settings")

    def _load_sound(self, file_name: str) -> pygame.mixer.Sound | None:
        cached = self._sound_cache.get(file_name)
        if cached is not None:
            return cached

        try:
            sound_path = self._sounds_dir / file_name
            sound = pygame.mixer.Sound(str(sound_path))
            self._sound_cache[file_name] = sound
            return sound
        except Exception:
            _logger.exception("Failed to load sound file=%s", file_name)
            return None

    def _is_enemy_rate_limited(self, cue: str) -> bool:
        min_interval = self.settings.enemy_cue_min_interval_seconds.get(cue)
        if min_interval is None:
            return False

        last_played_at = self._last_enemy_cue_played_at.get(cue)
        if last_played_at is None:
            return False

        return (time.monotonic() - last_played_at) < min_interval

    def _select_channel_id(self, group: AudioGroup, priority: int) -> int | None:
        channel_ids = self._channels_for_group(group)
        if not channel_ids:
            return None

        for channel_id in channel_ids:
            channel = pygame.mixer.Channel(channel_id)
            if not channel.get_busy():
                return channel_id

        if group != "enemy":
            return channel_ids[0]

        candidate_id = None
        candidate_priority = None
        for channel_id in channel_ids:
            current_priority = self._channel_priority.get(channel_id, 0)
            if candidate_priority is None or current_priority < candidate_priority:
                candidate_priority = current_priority
                candidate_id = channel_id

        if candidate_id is None:
            return None
        if candidate_priority is not None and candidate_priority > priority:
            return None
        return candidate_id

    def _channels_for_group(self, group: AudioGroup) -> list[int]:
        layout = self.settings.channel_layout
        if group == "ui":
            return [layout.ui]
        if group == "player":
            return [layout.player]
        if group == "enemy":
            return list(layout.enemy_pool)
        if group == "ambient":
            return list(layout.ambient_pool)
        return []
