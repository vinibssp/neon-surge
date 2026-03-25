from __future__ import annotations

import pygame

from game.config import SCREEN_HEIGHT, SCREEN_WIDTH
from game.core.events import AudioContextChanged
from game.modes.labyrinth_mode import LabyrinthMode
from game.modes.race_infinite_mode import RaceInfiniteMode
from game.modes.race_mode import RaceMode
from game.modes.survival_hardcore_mode import SurvivalHardcoreMode
from game.modes.survival_mode import SurvivalMode
from game.scenes.game_scene import GameScene
from game.scenes.menus._base_menu_scene import BaseMenuScene
from game.scenes.services import CyberpunkMenuBackgroundRenderer
from game.ui.components import ButtonConfig, LabelConfig, create_button, create_label
from game.ui.gui_theme import register_custom_element_themes


class MainMenuScene(BaseMenuScene):
    def __init__(self, stack) -> None:
        super().__init__(stack)
        self._elapsed_time = 0.0
        self._background_renderer = CyberpunkMenuBackgroundRenderer()
        self._register_main_menu_button_themes()

        title = create_label(
            LabelConfig(
                text="NEON SURGE 2",
                rect=pygame.Rect((SCREEN_WIDTH // 2 - 180, 120), (360, 64)),
                variant="title",
            ),
            manager=self.ui_manager,
        )
        subtitle = create_label(
            LabelConfig(
                text="Selecione um modo",
                rect=pygame.Rect((SCREEN_WIDTH // 2 - 150, 180), (300, 40)),
                variant="subtitle",
            ),
            manager=self.ui_manager,
        )
        del title, subtitle

        race_button = create_button(
            ButtonConfig(
                text="Corrida",
                rect=pygame.Rect((SCREEN_WIDTH // 2 - 140, 270), (280, 56)),
                variant="primary",
                object_id="race_button",
            ),
            manager=self.ui_manager,
        )
        survival_button = create_button(
            ButtonConfig(
                text="Sobrevivencia",
                rect=pygame.Rect((SCREEN_WIDTH // 2 - 140, 340), (280, 56)),
                variant="primary",
                object_id="survival_button",
            ),
            manager=self.ui_manager,
        )
        labyrinth_button = create_button(
            ButtonConfig(
                text="Labirinto",
                rect=pygame.Rect((SCREEN_WIDTH // 2 - 140, 410), (280, 56)),
                variant="primary",
                object_id="labyrinth_button",
            ),
            manager=self.ui_manager,
        )
        quit_button = create_button(
            ButtonConfig(
                text="Sair",
                rect=pygame.Rect((SCREEN_WIDTH // 2 - 140, 492), (280, 52)),
                variant="danger",
                object_id="quit_button",
            ),
            manager=self.ui_manager,
        )

        self.set_navigator(
            buttons=[race_button, survival_button, labyrinth_button, quit_button],
            actions={
                race_button: lambda: self.stack.replace(GameScene(self.stack, RaceMode())),
                survival_button: lambda: self.stack.replace(GameScene(self.stack, SurvivalMode())),
                labyrinth_button: lambda: self.stack.replace(GameScene(self.stack, LabyrinthMode())),
                quit_button: self._quit,
            },
            on_cancel=self._quit,
        )

    def _register_main_menu_button_themes(self) -> None:
        button_themes: dict[str, dict] = {
            "race_button": {
                "colours": {
                    "normal_bg": "#142400",
                    "hovered_bg": "#1f3600",
                    "selected_bg": "#284800",
                    "active_bg": "#2f5a00",
                    "normal_text": "#c6ff72",
                    "hovered_text": "#f1ffd1",
                    "selected_text": "#f1ffd1",
                    "normal_border": "#7fff00",
                    "hovered_border": "#b7ff4a",
                    "selected_border": "#d1ff7f",
                },
                "font": {
                    "name": "noto_sans",
                    "size": "16",
                    "bold": "1",
                },
            },
            "survival_button": {
                "colours": {
                    "normal_bg": "#2a1f00",
                    "hovered_bg": "#3c2d00",
                    "selected_bg": "#4f3a00",
                    "active_bg": "#624700",
                    "normal_text": "#ffd86b",
                    "hovered_text": "#fff1ca",
                    "selected_text": "#fff1ca",
                    "normal_border": "#ffbf3b",
                    "hovered_border": "#ffd86b",
                    "selected_border": "#ffe39c",
                },
                "font": {
                    "name": "noto_sans",
                    "size": "16",
                    "bold": "1",
                },
            },
            "labyrinth_button": {
                "colours": {
                    "normal_bg": "#191035",
                    "hovered_bg": "#281c54",
                    "selected_bg": "#35256e",
                    "active_bg": "#443090",
                    "normal_text": "#b8a6ff",
                    "hovered_text": "#ece6ff",
                    "selected_text": "#ece6ff",
                    "normal_border": "#8f72ff",
                    "hovered_border": "#b8a6ff",
                    "selected_border": "#d5c9ff",
                },
                "font": {
                    "name": "noto_sans",
                    "size": "16",
                    "bold": "1",
                },
            },
            "quit_button": {
                "colours": {
                    "normal_bg": "#3a0917",
                    "hovered_bg": "#541127",
                    "selected_bg": "#6f1834",
                    "active_bg": "#8a2143",
                    "normal_text": "#ff7aa3",
                    "hovered_text": "#ffd8e4",
                    "selected_text": "#ffd8e4",
                    "normal_border": "#ff4f86",
                    "hovered_border": "#ff7aa3",
                    "selected_border": "#ffabc5",
                },
                "font": {
                    "name": "noto_sans",
                    "size": "16",
                    "bold": "1",
                },
            },
        }

        register_custom_element_themes(self.ui_manager, button_themes, rebuild_all=True)

    def on_enter(self) -> None:
        self.stack.event_bus.publish(AudioContextChanged(context="menu", reason="main_menu_entered"))

    def on_menu_update(self, dt: float) -> None:
        self._elapsed_time += dt

    def render_menu_background(self, screen: pygame.Surface) -> None:
        self._background_renderer.render(
            screen=screen,
            elapsed_time=self._elapsed_time,
            width=SCREEN_WIDTH,
            height=SCREEN_HEIGHT,
        )

    def _quit(self) -> None:
        self.stack.pop()
