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

        if mode in (MODE_RACE, MODE_RACE_HC):
            label = "CORRIDA HARDCORE" if mode == MODE_RACE_HC else "CORRIDA"
            draw_text(surf, f"{label} - FASE {phase}/10", fonts["sub"], C_WHITE, 20, 30, "esquerda")
        else:
            label = "MODO SOBREVIVÊNCIA" if mode == MODE_SURV else "SOBREVIVÊNCIA HARDCORE"
            color = C_WHITE if mode == MODE_SURV else C_BLOOD_RED
            draw_text(surf, label, fonts["sub"], color, 20, 30, "esquerda")

        draw_text(surf, f"{total_elapsed:.1f}s", fonts["sub"], C_NEON_GRN,
                  SCREEN_W - 20, 30, "direita")

        # Dash cooldown bar (centre)
        bar_color = C_NEON_GRN if dash.ready else (255, 20, 147)
        bar_w     = int(100 * dash.progress)
        pygame.draw.rect(surf, bar_color, (cx - 50, 25, bar_w, 10))
        pygame.draw.rect(surf, C_WHITE,   (cx - 50, 25, 100,   10), 1)
