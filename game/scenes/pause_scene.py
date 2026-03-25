from __future__ import annotations

import math

import pygame
from pygame_gui.elements import UITextBox

from game.config import SCREEN_HEIGHT, SCREEN_WIDTH
from game.modes.game_mode_strategy import GameModeStrategy
from game.scenes.menus._base_menu_scene import BaseMenuScene
from game.ui.components import ButtonConfig, LabelConfig
from game.ui.ui_factory import UIFactory


class PauseScene(BaseMenuScene):
    transparent = True

    def __init__(self, stack) -> None:
        super().__init__(stack)
        self._overlay_elapsed_time = 0.0

        title = UIFactory.label(
            LabelConfig(
                text="PAUSADO",
                rect=pygame.Rect((SCREEN_WIDTH // 2 - 120, 170), (240, 56)),
                variant="title",
            ),
            manager=self.ui_manager,
        )
        del title

        resume_button = UIFactory.button(
            ButtonConfig(
                text="Continuar",
                rect=pygame.Rect((SCREEN_WIDTH // 2 - 140, 280), (280, 56)),
                variant="primary",
            ),
            manager=self.ui_manager,
        )
        restart_button = UIFactory.button(
            ButtonConfig(
                text="Reiniciar",
                rect=pygame.Rect((SCREEN_WIDTH // 2 - 140, 350), (280, 56)),
                variant="primary",
            ),
            manager=self.ui_manager,
        )
        menu_button = UIFactory.button(
            ButtonConfig(
                text="Menu Principal",
                rect=pygame.Rect((SCREEN_WIDTH // 2 - 140, 420), (280, 56)),
                variant="danger",
            ),
            manager=self.ui_manager,
        )

        self.set_navigator(
            buttons=[resume_button, restart_button, menu_button],
            actions={
                resume_button: self._resume,
                restart_button: self._restart,
                menu_button: self._go_main_menu,
            },
            on_cancel=self._resume,
        )

    def render_menu_background(self, screen: pygame.Surface) -> None:
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 140))
        screen.blit(overlay, (0, 0))

    def _resume(self) -> None:
        self.stack.pop()

    def _open_settings(self) -> None:
        self.stack.push(PauseSettingsScene(self.stack))

        self.stack.pop()
        self.stack.replace(GameScene(self.stack, self.retry_strategy_factory()))

    def _go_main_menu(self) -> None:
        self.stack.pop()
        from game.scenes.main_menu_scene import MainMenuScene

        self.stack.replace(MainMenuScene(self.stack))
