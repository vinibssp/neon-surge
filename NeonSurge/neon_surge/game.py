"""
neon_surge/game.py
==================
Top-level Game controller — owns display, clock, services and the
screen state machine.

Adding a new screen:
  1. Write a Screen subclass in screens/.
  2. Import and register it in self.screens below.
  3. Return its key string from any existing screen's handle_event/update.
"""
from __future__ import annotations

import sys
from typing import Dict, Optional

import pygame

from .constants import (
    SCREEN_W, SCREEN_H, FPS, C_BG,
    MUSIC_FILE, RANKING_FILE,
    MODE_RACE, MODE_RACE_HC,
)
from .level    import Level
from .services import AudioManager, RankingManager
from .hud      import VolumeWidget
from .screens  import (
    Screen,
    InputNameScreen, AskModeScreen, ModeMenuScreen,
    InfoModesScreen, HotkeysScreen,  EnemyInfoScreen,
    GameScreen,      PauseScreen,    RankingScreen,
)


class Game:
    """
    Owns the display, clock, services and the screen state machine.

    Shared mutable state accessed by screens via self.game:
        player_name          str
        current_mode         str   (MODE_RACE | MODE_RACE_HC | …)
        came_from_game_over  bool
        level                Level | None
        race_timer           float  (accumulated across phases)

    Suggested future extensions (see README):
        EventBus, AssetManager, Config/Settings,
        AchievementSystem, PowerUpSystem, WaveDefinition
    """

    def __init__(self) -> None:
        pygame.mixer.init()
        self.is_fullscreen = True
        self.real_screen   = pygame.display.set_mode((SCREEN_W, SCREEN_H), pygame.FULLSCREEN)
        self.canvas        = pygame.Surface((SCREEN_W, SCREEN_H))
        pygame.display.set_caption("Neon Surge - Hardcore Edition")

        self.clock = pygame.time.Clock()
        self.dt    = 0.0

        # CRT scanline overlay — baked once at startup
        self.crt = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        for y in range(0, SCREEN_H, 3):
            pygame.draw.line(self.crt, (0, 0, 0, 40), (0, y), (SCREEN_W, y))

        fn = "Consolas" if pygame.font.match_font("Consolas") else None
        self.fonts: Dict[str, pygame.font.Font] = {
            "title": pygame.font.SysFont("Impact", 85),
            "sub":   pygame.font.SysFont(fn, 30, bold=True),
            "text":  pygame.font.SysFont(fn, 22),
            "desc":  pygame.font.SysFont(fn, 19),
        }

        # ── Services ──────────────────────────────────────────────────────────
        self.audio         = AudioManager(MUSIC_FILE)
        self.ranking       = RankingManager(RANKING_FILE)
        self.volume_widget = VolumeWidget()

        # ── Shared gameplay state ─────────────────────────────────────────────
        self.player_name:         str            = ""
        self.current_mode:        str            = ""
        self.came_from_game_over: bool           = False
        self.level:               Optional[Level] = None
        self.race_timer:          float          = 0.0

        # ── Screen registry ───────────────────────────────────────────────────
        self.screens: Dict[str, Screen] = {
            "INPUT_NOME":      InputNameScreen(self),
            "PERGUNTA_MODO":   AskModeScreen(self),
            "MENU_MODO":       ModeMenuScreen(self),
            "TELA_INFO_MODOS": InfoModesScreen(self),
            "TELA_HOTKEYS":    HotkeysScreen(self),
            "TELA_INIMIGOS":   EnemyInfoScreen(self),
            "JOGANDO":         GameScreen(self),
            "PAUSA":           PauseScreen(self),
            "RANKING":         RankingScreen(self),
        }
        self.current_state = "INPUT_NOME"

    # ── display ───────────────────────────────────────────────────────────────

    def mouse_pos(self) -> tuple:
        mx, my = pygame.mouse.get_pos()
        if not self.is_fullscreen:
            w, h = self.real_screen.get_size()
            mx   = mx * SCREEN_W / w
            my   = my * SCREEN_H / h
        return mx, my

    def toggle_fullscreen(self) -> None:
        self.is_fullscreen = not self.is_fullscreen
        if self.is_fullscreen:
            self.real_screen = pygame.display.set_mode((SCREEN_W, SCREEN_H), pygame.FULLSCREEN)
        else:
            w, h = int(SCREEN_W * 0.8), int(SCREEN_H * 0.8)
            self.real_screen = pygame.display.set_mode((w, h))

    # ── level factory ─────────────────────────────────────────────────────────

    def start_level(self, phase: int) -> None:
        """Instantiate a fresh Level.  Resets race_timer only at phase 1."""
        if phase == 1:
            self.race_timer = 0.0
        self.level = Level(self.current_mode, phase)

    # ── state machine ─────────────────────────────────────────────────────────

    def _transition(self, next_state: Optional[str]) -> None:
        if next_state and next_state != self.current_state:
            self.current_state = next_state

    # ── main loop ─────────────────────────────────────────────────────────────

    def run(self) -> None:
        while True:
            self.dt = self.clock.tick(FPS) / 1000.0

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_F11:
                        self.toggle_fullscreen()
                    elif event.key in (pygame.K_MINUS, pygame.K_KP_MINUS):
                        self.audio.change_volume(-0.1)
                    elif event.key in (pygame.K_PLUS, pygame.K_KP_PLUS, pygame.K_EQUALS):
                        self.audio.change_volume(0.1)

                # Volume widget consumes clicks in menu screens only
                if self.current_state not in ("JOGANDO", "PAUSA"):
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        if self.volume_widget.handle_click(*self.mouse_pos(), self.audio):
                            continue

                next_s = self.screens[self.current_state].handle_event(event)
                self._transition(next_s)

            next_s = self.screens[self.current_state].update(self.dt)
            self._transition(next_s)

            self.canvas.fill(C_BG)
            self.screens[self.current_state].draw(self.canvas)
            self.canvas.blit(self.crt, (0, 0))

            if self.is_fullscreen:
                self.real_screen.blit(self.canvas, (0, 0))
            else:
                w, h = self.real_screen.get_size()
                self.real_screen.blit(pygame.transform.scale(self.canvas, (w, h)), (0, 0))

            pygame.display.flip()
