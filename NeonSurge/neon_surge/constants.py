"""
neon_surge/constants.py
=======================
All game-wide constants and configuration values.
Change numbers here — never scatter magic values across the codebase.
"""
import pygame

pygame.init()
_info = pygame.display.Info()

# ── Display ───────────────────────────────────────────────────────────────────
SCREEN_W: int = _info.current_w
SCREEN_H: int = _info.current_h
FPS:      int = 60
HUD_H:    int = 60          # pixel height of the top HUD bar

# ── File paths ────────────────────────────────────────────────────────────────
RANKING_FILE = "data/ranking_completo.json"
MUSIC_FILE   = "assets/trilha.mp3"

# ── Colours ───────────────────────────────────────────────────────────────────
C_BG        = (5,   5,   8)
C_WHITE     = (255, 255, 255)
C_NEON_GRN  = (57,  255,  20)
C_NEON_CYN  = (0,   255, 255)
C_NEON_PNK  = (255,  20, 147)
C_NEON_ORG  = (255, 100,   0)
C_GOLD      = (255, 215,   0)
C_BLOOD_RED = (255,  30,  30)
C_DARK_GRAY = (35,   40,  50)
C_LT_GRAY   = (200, 200, 210)
C_DARK_BLUE = (15,   20,  30)
C_PANEL     = (15,   20,  30, 230)

# ── Player physics ────────────────────────────────────────────────────────────
PLAYER_ACCEL    = 1.8
PLAYER_FRICTION = 0.82
PLAYER_SIZE     = 16
DASH_SPEED      = 25
DASH_DURATION   = 10    # active invincibility frames
DASH_COOLDOWN   = 45    # frames between dashes

# ── Enemy ─────────────────────────────────────────────────────────────────────
ENEMY_BASE_SPEED  = 4.0
ENEMY_CHARGE_MULT = 4.0   # speed multiplier during the charge attack

# ── Survival-mode spawning ────────────────────────────────────────────────────
SURV_SPAWN_INTERVAL = 3.0
SURV_MAX_SPEED      = 8.0
SURV_SPEED_GROWTH   = 0.05

HC_SPAWN_INTERVAL = 1.5
HC_MAX_SPEED      = 12.0
HC_SPEED_GROWTH   = 0.1

# ── Game mode tokens ──────────────────────────────────────────────────────────
MODE_RACE    = "CORRIDA"
MODE_RACE_HC = "CORRIDA_HARDCORE"
MODE_SURV    = "SOBREVIVENCIA"
MODE_HC      = "HARDCORE"
