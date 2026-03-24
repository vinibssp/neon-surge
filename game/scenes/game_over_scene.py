from __future__ import annotations

from typing import Callable

import pygame
from pygame import Vector2

from game.config import SCREEN_HEIGHT, SCREEN_WIDTH
from game.core.scene_stack import Scene
from game.ui.elements import Button, Container, Label
from game.ui.navigation import UINavigationInputHandler, UINavigator
from game.modes.game_mode_strategy import GameModeStrategy


class GameOverScene(Scene):
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
        panel_size = Vector2(360, 260)
        panel_pos = Vector2((SCREEN_WIDTH - panel_size.x) * 0.5, (SCREEN_HEIGHT - panel_size.y) * 0.5)
        self.root = Container(position=panel_pos, size=panel_size, orientation="vertical", padding=16)
        subtitle_text = subtitle if subtitle is not None else f"Level {self.reached_level}"
        self.root.add_child(Label(position=Vector2(), size=Vector2(320, 42), text=title))
        self.root.add_child(Label(position=Vector2(), size=Vector2(320, 42), text=subtitle_text))
        self.retry_button = Button(position=Vector2(), size=Vector2(320, 58), text="Retry", callback=self._retry)
        self.root.add_child(self.retry_button)
        self.menu_button = Button(position=Vector2(), size=Vector2(320, 58), text="Menu", callback=self._menu)
        self.root.add_child(self.menu_button)
        self.ui_input = UINavigationInputHandler()
        self.navigator = UINavigator(
            buttons=[self.retry_button, self.menu_button],
            on_cancel=self._menu,
        )

    def handle_input(self, events: list[pygame.event.Event]) -> None:
        commands = self.ui_input.build_commands(events)
        for command in commands:
            command.execute(self.navigator)

    def update(self, dt: float) -> None:
        self.root.update(dt)
        self.navigator.sync_hover_state()

    def render(self, screen: pygame.Surface) -> None:
        self.root.render(screen)

    def _retry(self) -> None:
        from game.scenes.game_scene import GameScene

        strategy_factory = self.retry_strategy_factory
        if strategy_factory is None:
            return
        self.stack.replace(GameScene(self.stack, mode=strategy_factory()))

    def _menu(self) -> None:
        from game.scenes.main_menu_scene import MainMenuScene

        self.stack.replace(MainMenuScene(self.stack))
