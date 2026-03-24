from __future__ import annotations

from typing import Callable

import pygame

from game.config import SCREEN_HEIGHT, SCREEN_WIDTH
from game.core.scene_stack import Scene
from game.ui.gui_theme import create_ui_manager
from game.ui.navigation import UINavigationInputHandler, UINavigator
from game.ui.types import UIControl


class BaseMenuScene(Scene):
    def __init__(self, stack) -> None:
        super().__init__(stack)
        self.ui_manager = create_ui_manager((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.ui_input = UINavigationInputHandler()
        self.navigator: UINavigator | None = None

    def set_navigator(
        self,
        buttons: list[UIControl],
        actions: list[Callable[[], None]] | None = None,
        on_cancel: Callable[[], None] | None = None,
    ) -> None:
        self.navigator = UINavigator(buttons=buttons, actions=actions, on_cancel=on_cancel)

    def handle_input(self, events: list[pygame.event.Event]) -> None:
        for event in events:
            self.ui_manager.process_events(event)

        if self.navigator is None:
            return

        commands = self.ui_input.build_commands(events)
        for command in commands:
            command.execute(self.navigator)

    def update(self, dt: float) -> None:
        self.ui_manager.update(dt)
        if self.navigator is not None:
            self.navigator.sync_hover_state()
        self.on_menu_update(dt)

    def render(self, screen: pygame.Surface) -> None:
        self.render_menu_background(screen)
        self.ui_manager.draw_ui(screen)
        self.render_menu_foreground(screen)

    def on_menu_update(self, dt: float) -> None:
        del dt

    def render_menu_background(self, screen: pygame.Surface) -> None:
        del screen

    def render_menu_foreground(self, screen: pygame.Surface) -> None:
        del screen
