from __future__ import annotations

from typing import Callable

import pygame

from game.config import SCREEN_HEIGHT, SCREEN_WIDTH
from game.core.events import AudioContextChanged
from game.modes.game_mode_strategy import GameModeStrategy
from game.scenes.menus._base_menu_scene import BaseMenuScene
from game.ui.components import ButtonConfig, LabelConfig, create_button, create_label


class GameOverScene(BaseMenuScene):
    def __init__(
        self,
        stack,
        reached_level: int,
        title: str,
        subtitle: str,
        retry_strategy_factory: Callable[[], GameModeStrategy],
    ) -> None:
        super().__init__(stack)
        self.retry_strategy_factory = retry_strategy_factory

        title_label = create_label(
            LabelConfig(
                text=title,
                rect=pygame.Rect((SCREEN_WIDTH // 2 - 320, 140), (640, 64)),
                variant="title",
            ),
            manager=self.ui_manager,
        )
        subtitle_label = create_label(
            LabelConfig(
                text=subtitle,
                rect=pygame.Rect((SCREEN_WIDTH // 2 - 320, 204), (640, 42)),
                variant="subtitle",
            ),
            manager=self.ui_manager,
        )
        level_label = create_label(
            LabelConfig(
                text=f"Nivel alcancado: {reached_level}",
                rect=pygame.Rect((SCREEN_WIDTH // 2 - 180, 252), (360, 40)),
                variant="muted",
            ),
            manager=self.ui_manager,
        )
        del title_label, subtitle_label, level_label

        retry_button = create_button(
            ButtonConfig(
                text="Tentar Novamente",
                rect=pygame.Rect((SCREEN_WIDTH // 2 - 140, 340), (280, 56)),
                variant="primary",
            ),
            manager=self.ui_manager,
        )
        menu_button = create_button(
            ButtonConfig(
                text="Menu Principal",
                rect=pygame.Rect((SCREEN_WIDTH // 2 - 140, 412), (280, 56)),
                variant="danger",
            ),
            manager=self.ui_manager,
        )

        self.set_navigator(
            buttons=[retry_button, menu_button],
            actions={
                retry_button: self._retry,
                menu_button: self._go_main_menu,
            },
            on_cancel=self._go_main_menu,
        )

    def on_enter(self) -> None:
        self.stack.event_bus.publish(AudioContextChanged(context="game_over", reason="game_over_entered"))

    def _retry(self) -> None:
        from game.scenes.game_scene import GameScene

        self.stack.replace(GameScene(self.stack, self.retry_strategy_factory()))

    def _go_main_menu(self) -> None:
        from game.scenes.main_menu_scene import MainMenuScene

        self.stack.replace(MainMenuScene(self.stack))
