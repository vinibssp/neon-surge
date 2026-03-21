import pygame

from ..constants  import SCREEN_W, SCREEN_H, C_WHITE, C_NEON_CYN, C_NEON_PNK, C_DARK_GRAY, C_LT_GRAY, C_NEON_GRN
from ..utils      import draw_text, make_panel, draw_sound_icon
from ..services   import AudioManager


class VolumeWidget:
    """Persistent +/− / mute control drawn on every menu screen."""

    def __init__(self) -> None:
        self._rect_mute  = pygame.Rect(0, 0, 45, 45)
        self._rect_minus = pygame.Rect(0, 0, 35, 35)
        self._rect_plus  = pygame.Rect(0, 0, 35, 35)

    def draw(self, surf, fonts: dict, audio: AudioManager, mx: float, my: float) -> None:
        W, H = 280, 56
        x    = SCREEN_W - W - 20
        y    = SCREEN_H - H - 20
        surf.blit(make_panel(W, H), (x, y))

        vol_str   = "MUDO" if audio.muted else f"{int(audio.volume * 100)}%"
        vol_color = C_LT_GRAY if audio.muted else C_NEON_GRN
        draw_text(surf, vol_str, fonts["sub"], vol_color, x + 20, y + H // 2, "esquerda")

        cy_btn   = y + H // 2
        cx_plus  = x + W - 30
        cx_minus = cx_plus - 45
        cx_mute  = cx_minus - 55

        for rect, cx_btn in [
            (self._rect_plus,  cx_plus),
            (self._rect_minus, cx_minus),
            (self._rect_mute,  cx_mute),
        ]:
            rect.center = (cx_btn, cy_btn)

        for rect, accent in [
            (self._rect_plus,  C_NEON_CYN),
            (self._rect_minus, C_NEON_CYN),
            (self._rect_mute,  C_NEON_PNK),
        ]:
            hov = rect.collidepoint(mx, my)
            pygame.draw.rect(surf, C_DARK_GRAY if hov else (10, 15, 25), rect, border_radius=6)
            pygame.draw.rect(surf, accent if hov else C_DARK_GRAY,       rect, 2, border_radius=6)

        draw_text(surf, "+", fonts["sub"], C_WHITE, self._rect_plus.centerx,  self._rect_plus.centery)
        draw_text(surf, "-", fonts["sub"], C_WHITE, self._rect_minus.centerx, self._rect_minus.centery)
        draw_sound_icon(surf, self._rect_mute.centerx, self._rect_mute.centery, audio.muted, C_WHITE)

    def handle_click(self, mx: float, my: float, audio: AudioManager) -> bool:
        """Returns True if the widget consumed the click."""
        if self._rect_mute.collidepoint(mx, my):
            audio.toggle_mute();  return True
        if self._rect_minus.collidepoint(mx, my):
            audio.change_volume(-0.1); return True
        if self._rect_plus.collidepoint(mx, my):
            audio.change_volume(0.1);  return True
        return False
