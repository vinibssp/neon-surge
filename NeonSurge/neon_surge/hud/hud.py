import pygame

from ..constants   import (
    SCREEN_W, HUD_H,
    C_BG, C_WHITE, C_NEON_GRN, C_NEON_CYN, C_BLOOD_RED,
    MODE_RACE, MODE_RACE_HC, MODE_SURV,
)
from ..utils       import draw_text
from ..components  import DashAbility


class HUD:
    """Top bar drawn during gameplay: mode label, elapsed timer, dash meter."""

    def draw(
        self, surf, fonts: dict, mode: str, phase: int,
        total_elapsed: float, dash: DashAbility,
    ) -> None:
        pygame.draw.rect(surf, C_BG, (0, 0, SCREEN_W, HUD_H))
        pygame.draw.line(surf, C_NEON_CYN, (0, HUD_H), (SCREEN_W, HUD_H), 2)

        cx = SCREEN_W // 2
        margin = 30  # Standardized horizontal margin

        if mode in (MODE_RACE, MODE_RACE_HC):
            label = "CORRIDA HARDCORE" if mode == MODE_RACE_HC else "CORRIDA"
            if mode == MODE_RACE:
                label += f" - FASE {phase}/10"
            draw_text(surf, label, fonts["sub"], C_WHITE, margin, 30, "esquerda", shadow=True)
        else:
            label = "MODO SOBREVIVÊNCIA" if mode == MODE_SURV else "SOBREVIVÊNCIA HARDCORE"
            color = C_WHITE if mode == MODE_SURV else C_BLOOD_RED
            draw_text(surf, label, fonts["sub"], color, margin, 30, "esquerda", shadow=True)

        draw_text(surf, f"{total_elapsed:.1f}s", fonts["sub"], C_NEON_GRN,
                  SCREEN_W - margin, 30, "direita", shadow=True)

        # Dash cooldown bar (centre)
        bar_color = C_NEON_GRN if dash.ready else (255, 20, 147)
        bar_w     = int(100 * dash.progress)
        pygame.draw.rect(surf, bar_color, (cx - 50, 25, bar_w, 10))
        pygame.draw.rect(surf, C_WHITE,   (cx - 50, 25, 100,   10), 1)
