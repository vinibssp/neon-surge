from __future__ import annotations

import json
from pathlib import Path
from typing import Callable

from game.audio.audio_settings import AudioSettings
from game.audio.mixer_backend import MixerBackend


class AudioSettingsManager:
    def __init__(
        self,
        settings: AudioSettings,
        backend: MixerBackend,
        is_ducked_provider: Callable[[], bool] | None = None,
        settings_path: Path | None = None,
    ) -> None:
        self.settings = settings
        self.backend = backend
        self.is_ducked_provider = is_ducked_provider or (lambda: False)
        self._settings_path = settings_path or (Path(__file__).resolve().parent.parent / "assets" / "audio_settings.json")
        self.load()

    def load(self) -> None:
        if not self._settings_path.exists():
            return

        try:
            raw_data = json.loads(self._settings_path.read_text(encoding="utf-8"))
        except Exception:
            return

        music_volume = raw_data.get("music_volume")
        sfx_volume = raw_data.get("sfx_volume")

        if isinstance(music_volume, (int, float)):
            self.settings.music_volume = self._clamp01(float(music_volume))
        if isinstance(sfx_volume, (int, float)):
            self.settings.sfx_volume = self._clamp01(float(sfx_volume))

    def save(self) -> None:
        payload = {
            "music_volume": self.settings.music_volume,
            "sfx_volume": self.settings.sfx_volume,
        }

        try:
            self._settings_path.parent.mkdir(parents=True, exist_ok=True)
            self._settings_path.write_text(json.dumps(payload, ensure_ascii=True, indent=2), encoding="utf-8")
        except Exception:
            return

    def set_music_volume(self, value: float) -> None:
        self.settings.music_volume = self._clamp01(value)
        self._apply_and_persist()

    def set_sfx_volume(self, value: float) -> None:
        self.settings.sfx_volume = self._clamp01(value)
        self._apply_and_persist()

    def adjust_music_volume(self, delta: float) -> None:
        self.set_music_volume(self.settings.music_volume + delta)

    def adjust_sfx_volume(self, delta: float) -> None:
        self.set_sfx_volume(self.settings.sfx_volume + delta)

    def get_music_volume_percent(self) -> int:
        return int(round(self.settings.music_volume * 100.0))

    def get_sfx_volume_percent(self) -> int:
        return int(round(self.settings.sfx_volume * 100.0))

    def _apply_and_persist(self) -> None:
        self.backend.apply_runtime_settings(is_ducked=self.is_ducked_provider())
        self.save()

    @staticmethod
    def _clamp01(value: float) -> float:
        return max(0.0, min(1.0, value))
