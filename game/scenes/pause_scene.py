from __future__ import annotations

from typing import Callable

import pygame
from pygame import Vector2

from game.config import PAUSE_OVERLAY_COLOR, SCREEN_HEIGHT, SCREEN_WIDTH
from game.core.scene_stack import Scene
from game.modes.game_mode_strategy import GameModeStrategy
from game.ui.elements import Button, Container, Label
from game.ui.navigation import UINavigationInputHandler, UINavigator


class PauseScene(Scene):
    transparent = True

    def __init__(self, stack, retry_strategy_factory: Callable[[], GameModeStrategy]) -> None:
        super().__init__(stack)
        self.retry_strategy_factory = retry_strategy_factory

        panel_size = Vector2(420, 320)
        panel_pos = Vector2((SCREEN_WIDTH - panel_size.x) * 0.5, (SCREEN_HEIGHT - panel_size.y) * 0.5)
        self.root = Container(position=panel_pos, size=panel_size, orientation="vertical", padding=16)
        self.root.add_child(Label(position=Vector2(), size=Vector2(388, 44), text="Pausado"))

        self.continue_button = Button(
            position=Vector2(),
            size=Vector2(388, 56),
            text="Continuar",
            callback=self._continue,
        )
        self.restart_button = Button(
            position=Vector2(),
            size=Vector2(388, 56),
            text="Reiniciar",
            callback=self._restart,
        )
        self.menu_button = Button(
            position=Vector2(),
            size=Vector2(388, 56),
            text="Voltar ao menu",
            callback=self._back_to_menu,
        )

        self.root.add_child(self.continue_button)
        self.root.add_child(self.restart_button)
        self.root.add_child(self.menu_button)

        self.ui_input = UINavigationInputHandler()
        self.navigator = UINavigator(
            buttons=[self.continue_button, self.restart_button, self.menu_button],
            on_cancel=self._continue,
        )

    def handle_input(self, events: list[pygame.event.Event]) -> None:
        commands = self.ui_input.build_commands(events)
        for command in commands:
            command.execute(self.navigator)

    def update(self, dt: float) -> None:
        self.root.update(dt)
        self.navigator.sync_hover_state()

    def render(self, screen: pygame.Surface) -> None:
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(140)
        overlay.fill(PAUSE_OVERLAY_COLOR)
        screen.blit(overlay, (0, 0))
        self.root.render(screen)

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
