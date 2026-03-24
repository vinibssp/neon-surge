from __future__ import annotations

import pygame
from pygame import Vector2

from game.config import MENU_MOUNTAIN_FILL_COLOR, PAUSE_OVERLAY_COLOR, SCREEN_HEIGHT, SCREEN_WIDTH
from game.core.scene_stack import Scene
from game.ui.elements import Button, Container, Label
from game.ui.navigation import UINavigationInputHandler, UINavigator

NEON_CYAN = (0, 220, 255)
NEON_MAGENTA = (255, 55, 220)
WHITE = (245, 245, 245)


class MenuOverlayScene(Scene):
    transparent = True

    def __init__(
        self,
        stack,
        title: str,
        accent_color: tuple[int, int, int],
        body_text: str = "Painel em construcao...",
    ) -> None:
        super().__init__(stack)
        panel_size = Vector2(560, 320)
        panel_pos = Vector2((SCREEN_WIDTH - panel_size.x) * 0.5, (SCREEN_HEIGHT - panel_size.y) * 0.5)
        self.root = Container(
            position=panel_pos,
            size=panel_size,
            orientation="vertical",
            padding=14,
            draw_panel=True,
            panel_color=MENU_MOUNTAIN_FILL_COLOR,
            border_color=accent_color,
        )
        self.title_label = Label(
            position=Vector2(),
            size=Vector2(530, 54),
            text=title,
            color=accent_color,
            draw_panel=False,
            font_size=42,
            margin=6,
        )
        self.body_label = Label(
            position=Vector2(),
            size=Vector2(530, 120),
            text=body_text,
            color=(235, 235, 242),
            draw_panel=False,
            font_size=32,
            margin=10,
        )
        self.close_button = Button(
            position=Vector2(),
            size=Vector2(530, 58),
            text="x",
            callback=self._close,
            base_color=MENU_MOUNTAIN_FILL_COLOR,
            hover_color=accent_color,
            border_color=accent_color,
            text_color=accent_color,
            hover_border_color=WHITE,
            hover_text_color=MENU_MOUNTAIN_FILL_COLOR,
            font_size=40,
        )
        self.root.add_child(self.title_label)
        self.root.add_child(self.body_label)
        self.root.add_child(self.close_button)

        self.ui_input = UINavigationInputHandler()
        self.navigator = UINavigator(buttons=[self.close_button], on_cancel=self._close)

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

    def _close(self) -> None:
        self.stack.pop()


class SettingsOverlayScene(MenuOverlayScene):
    def __init__(self, stack) -> None:
        super().__init__(stack, title="Configuracoes", accent_color=NEON_CYAN)


class HelpOverlayScene(MenuOverlayScene):
    def __init__(self, stack) -> None:
        super().__init__(stack, title="Ajuda", accent_color=NEON_MAGENTA)
