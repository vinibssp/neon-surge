from __future__ import annotations

from typing import Callable

import pygame

from game.config import SCREEN_HEIGHT, SCREEN_WIDTH
from game.core.events import AudioContextChanged
from game.modes.game_mode_strategy import GameModeStrategy
from game.scenes.base_menu_scene import BaseMenuScene
from game.scenes.overlay_scene_factory import OverlayActionBinding, OverlaySceneFactory
from game.ui.types import UIControl


class GameOverScene(BaseMenuScene):
    def __init__(
        self,
        stack,
        reached_level: int,
        title: str = "Game Over",
        subtitle: str | None = None,
        retry_strategy_factory: Callable[[], GameModeStrategy] | None = None,
    ) -> None:
        super().__init__(stack)
        self.reached_level = reached_level
        self.retry_strategy_factory = retry_strategy_factory
        subtitle_text = subtitle if subtitle is not None else f"Level {self.reached_level}"
        overlay = OverlaySceneFactory.build(
            screen_size=(SCREEN_WIDTH, SCREEN_HEIGHT),
            ui_manager=self.ui_manager,
            title=title,
            panel_object_id="#overlay_panel",
            panel_size=(360, 260),
            body_text=subtitle_text,
            body_rect=pygame.Rect(14, 66, 332, 44),
            action_bindings=(
                OverlayActionBinding(
                    key="retry",
                    text="Retry",
                    rect=pygame.Rect(14, 116, 332, 56),
                    handler=self._retry,
                ),
                OverlayActionBinding(
                    key="menu",
                    text="Menu",
                    rect=pygame.Rect(14, 182, 332, 58),
                    object_id="#overlay_close_button",
                    handler=self._menu,
                ),
            ),
            on_cancel_key="menu",
        )
        self.panel = overlay.panel
        self.subtitle_box = overlay.body
        self.retry_button: UIControl = overlay.controls["retry"]
        self.menu_button: UIControl = overlay.controls["menu"]
        self.set_navigator(
            buttons=overlay.navigation_buttons,
            actions=overlay.navigation_actions,
            on_cancel=overlay.cancel_action,
        )

    def on_enter(self) -> None:
        self.stack.event_bus.publish(AudioContextChanged(context="game_over", reason="game_over_scene_entered"))

    def _retry(self) -> None:
        from game.scenes.game_scene import GameScene

        strategy_factory = self.retry_strategy_factory
        if strategy_factory is None:
            return
        self.stack.replace(GameScene(self.stack, mode=strategy_factory()))

    def _menu(self) -> None:
        from game.scenes.main_menu_scene import MainMenuScene

        self.stack.replace(MainMenuScene(self.stack))
