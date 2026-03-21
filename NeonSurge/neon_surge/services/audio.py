import pygame


class AudioManager:
    """Wraps pygame.mixer — volume, mute toggle, and music lifecycle."""

    def __init__(self, track_path: str, default_volume: float = 0.4) -> None:
        self._volume    = default_volume
        self._saved_vol = default_volume
        self._muted     = False
        try:
            pygame.mixer.music.load(track_path)
            pygame.mixer.music.set_volume(self._volume)
            pygame.mixer.music.play(-1)
        except pygame.error:
            pass   # no audio device / missing file — game still runs

    # ── properties ────────────────────────────────────────────────────────────
    @property
    def muted(self) -> bool:
        return self._muted

    @property
    def volume(self) -> float:
        return self._volume

    # ── actions ───────────────────────────────────────────────────────────────
    def change_volume(self, delta: float) -> None:
        if self._muted:
            self.toggle_mute()
        self._volume = max(0.0, min(1.0, self._volume + delta))
        self._apply()

    def toggle_mute(self) -> None:
        self._muted = not self._muted
        if self._muted:
            self._saved_vol = self._volume
            self._volume    = 0.0
        else:
            self._volume = self._saved_vol if self._saved_vol > 0 else 0.4
        self._apply()

    def _apply(self) -> None:
        try:
            pygame.mixer.music.set_volume(self._volume)
        except Exception:
            pass
