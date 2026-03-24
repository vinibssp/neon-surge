from __future__ import annotations

from typing import Callable

import pygame

from game.config import PAUSE_OVERLAY_COLOR, SCREEN_HEIGHT, SCREEN_WIDTH
from game.core.events import AudioDuckRequested, AudioUnduckRequested
from game.modes.game_mode_strategy import GameModeStrategy
from game.scenes.base_menu_scene import BaseMenuScene
from game.scenes.overlay_scene_factory import OverlayActionBinding, OverlaySceneFactory
from game.ui.components.overlay_builder import draw_overlay_backdrop
from game.ui.types import UIControl


class PauseScene(BaseMenuScene):
    transparent = True

    def __init__(self, stack, retry_strategy_factory: Callable[[], GameModeStrategy]) -> None:
        super().__init__(stack)
        self.retry_strategy_factory = retry_strategy_factory

        overlay = OverlaySceneFactory.build(
            screen_size=(SCREEN_WIDTH, SCREEN_HEIGHT),
            ui_manager=self.ui_manager,
            title="Pausado",
            panel_object_id="#overlay_panel",
            panel_size=(420, 320),
            action_bindings=(
                OverlayActionBinding(
                    key="continue",
                    text="Continuar",
                    rect=pygame.Rect(14, 248, 392, 58),
                    handler=self._continue,
                ),
                OverlayActionBinding(
                    key="restart",
                    text="Reiniciar",
                    rect=pygame.Rect(14, 140, 392, 56),
                    handler=self._restart,
                ),
                OverlayActionBinding(
                    key="menu",
                    text="X",
                    rect=pygame.Rect(362, 14, 44, 44),
                    object_id="#overlay_close_button",
                    handler=self._back_to_menu,
                ),
            ),
            on_cancel_key="continue",
        )
        self.panel = overlay.panel
        self.continue_button: UIControl = overlay.controls["continue"]
        self.restart_button: UIControl = overlay.controls["restart"]
        self.menu_button: UIControl = overlay.controls["menu"]

        self.set_navigator(
            buttons=overlay.navigation_buttons,
            actions=overlay.navigation_actions,
            on_cancel=overlay.cancel_action,
        )

    def on_enter(self) -> None:
        self.stack.event_bus.publish(AudioDuckRequested(reason="pause_scene_entered"))

    def on_exit(self) -> None:
        self.stack.event_bus.publish(AudioUnduckRequested(reason="pause_scene_exited"))

    def render_menu_background(self, screen: pygame.Surface) -> None:
        draw_overlay_backdrop(screen, screen_size=(SCREEN_WIDTH, SCREEN_HEIGHT), color=PAUSE_OVERLAY_COLOR)

    def _continue(self) -> None:
        self.stack.pop()

    def _restart(self) -> None:
        from game.scenes.game_scene import GameScene

        self.stack.pop()
        self.stack.replace(GameScene(self.stack, mode=self.retry_strategy_factory()))

    def _back_to_menu(self) -> None:
        from game.scenes.main_menu_scene import MainMenuScene

        self.stack.pop()
        self.stack.replace(MainMenuScene(self.stack))
