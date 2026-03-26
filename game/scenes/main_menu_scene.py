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
from game.scenes.guide_scene import GuideScene
from game.scenes.menus._base_menu_scene import BaseMenuScene
from game.scenes.settings_scene import SettingsScene
from game.scenes.training_setup_scene import TrainingSetupScene
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
                rect=pygame.Rect((SCREEN_WIDTH // 2 - 190, 120), (380, 64)),
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

        button_width = 246
        button_height = 58
        horizontal_gap = 18
        vertical_gap = 18
        columns = 4
        rows = 2
        grid_width = columns * button_width + (columns - 1) * horizontal_gap
        grid_height = rows * button_height + (rows - 1) * vertical_gap
        start_x = (SCREEN_WIDTH - grid_width) // 2
        start_y = max(250, (SCREEN_HEIGHT - grid_height) // 2)

        button_specs = [
            ("Corrida", "race_button", 0, 0),
            ("Corrida Infinita", "race_infinite_button", 1, 0),
            ("Sobrevivencia", "survival_button", 2, 0),
            ("Hardcore", "hardcore_button", 3, 0),
            ("Labirinto", "labyrinth_button", 0, 1),
            ("Treino", "training_button", 1, 1),
            ("Guia", "guide_button", 2, 1),
            ("Config", "settings_button", 3, 1),
        ]

        menu_buttons = {}
        for text, object_id, column, row in button_specs:
            rect = pygame.Rect(
                (start_x + column * (button_width + horizontal_gap), start_y + row * (button_height + vertical_gap)),
                (button_width, button_height),
            )
            menu_buttons[object_id] = create_button(
                ButtonConfig(
                    text=text,
                    rect=rect,
                    variant="primary",
                    object_id=object_id,
                ),
                manager=self.ui_manager,
            )

        race_button = menu_buttons["race_button"]
        race_infinite_button = menu_buttons["race_infinite_button"]
        survival_button = menu_buttons["survival_button"]
        hardcore_button = menu_buttons["hardcore_button"]
        labyrinth_button = menu_buttons["labyrinth_button"]
        training_button = menu_buttons["training_button"]
        guide_button = menu_buttons["guide_button"]
        settings_button = menu_buttons["settings_button"]

        self.set_navigator(
            buttons=[
                race_button,
                race_infinite_button,
                survival_button,
                hardcore_button,
                labyrinth_button,
                training_button,
                guide_button,
                settings_button,
            ],
            actions={
                race_button: lambda: self.stack.replace(GameScene(self.stack, RaceMode())),
                race_infinite_button: lambda: self.stack.replace(GameScene(self.stack, RaceInfiniteMode())),
                survival_button: lambda: self.stack.replace(GameScene(self.stack, SurvivalMode())),
                hardcore_button: lambda: self.stack.replace(GameScene(self.stack, SurvivalHardcoreMode())),
                labyrinth_button: lambda: self.stack.replace(GameScene(self.stack, LabyrinthMode())),
                training_button: lambda: self.stack.push(TrainingSetupScene(self.stack)),
                guide_button: lambda: self.stack.push(GuideScene(self.stack)),
                settings_button: lambda: self.stack.push(SettingsScene(self.stack)),
            },
            on_cancel=self._quit,
        )

    def _register_main_menu_button_themes(self) -> None:
        button_themes: dict[str, dict] = {
            "race_button": {
                "colours": {
                    "normal_bg": "#0a1f3e",
                    "hovered_bg": "#0f2f5c",
                    "selected_bg": "#154078",
                    "active_bg": "#1a4f92",
                    "normal_text": "#8fd6ff",
                    "hovered_text": "#e0f5ff",
                    "selected_text": "#e0f5ff",
                    "normal_border": "#2f9dff",
                    "hovered_border": "#66b9ff",
                    "selected_border": "#99d1ff",
                },
                "font": {
                    "name": "noto_sans",
                    "size": "16",
                    "bold": "1",
                },
            },
            "race_infinite_button": {
                "colours": {
                    "normal_bg": "#201044",
                    "hovered_bg": "#2f1964",
                    "selected_bg": "#3d2382",
                    "active_bg": "#4b2da0",
                    "normal_text": "#c9a8ff",
                    "hovered_text": "#f0e6ff",
                    "selected_text": "#f0e6ff",
                    "normal_border": "#9f6bff",
                    "hovered_border": "#bb96ff",
                    "selected_border": "#d5c0ff",
                },
                "font": {
                    "name": "noto_sans",
                    "size": "16",
                    "bold": "1",
                },
            },
            "survival_button": {
                "colours": {
                    "normal_bg": "#3c1030",
                    "hovered_bg": "#561848",
                    "selected_bg": "#711f60",
                    "active_bg": "#8b2878",
                    "normal_text": "#ff95dd",
                    "hovered_text": "#ffe4f8",
                    "selected_text": "#ffe4f8",
                    "normal_border": "#ff5ec8",
                    "hovered_border": "#ff95dd",
                    "selected_border": "#ffc3ec",
                },
                "font": {
                    "name": "noto_sans",
                    "size": "16",
                    "bold": "1",
                },
            },
            "hardcore_button": {
                "colours": {
                    "normal_bg": "#3f1b04",
                    "hovered_bg": "#5b2808",
                    "selected_bg": "#75350b",
                    "active_bg": "#8f410f",
                    "normal_text": "#ffbd85",
                    "hovered_text": "#ffeddc",
                    "selected_text": "#ffeddc",
                    "normal_border": "#ff8e3a",
                    "hovered_border": "#ffad6b",
                    "selected_border": "#ffc89b",
                },
                "font": {
                    "name": "noto_sans",
                    "size": "16",
                    "bold": "1",
                },
            },
            "labyrinth_button": {
                "colours": {
                    "normal_bg": "#112f15",
                    "hovered_bg": "#19461f",
                    "selected_bg": "#215f2a",
                    "active_bg": "#2a7834",
                    "normal_text": "#92f5a0",
                    "hovered_text": "#ddffe3",
                    "selected_text": "#ddffe3",
                    "normal_border": "#4ee06a",
                    "hovered_border": "#7ff08e",
                    "selected_border": "#b4f7bf",
                },
                "font": {
                    "name": "noto_sans",
                    "size": "16",
                    "bold": "1",
                },
            },
            "training_button": {
                "colours": {
                    "normal_bg": "#0b3140",
                    "hovered_bg": "#11495d",
                    "selected_bg": "#17627a",
                    "active_bg": "#1d7a96",
                    "normal_text": "#91ebff",
                    "hovered_text": "#ddf8ff",
                    "selected_text": "#ddf8ff",
                    "normal_border": "#49d4ff",
                    "hovered_border": "#86e5ff",
                    "selected_border": "#b6efff",
                },
                "font": {
                    "name": "noto_sans",
                    "size": "16",
                    "bold": "1",
                },
            },
            "guide_button": {
                "colours": {
                    "normal_bg": "#3f3805",
                    "hovered_bg": "#5a5009",
                    "selected_bg": "#75680c",
                    "active_bg": "#908110",
                    "normal_text": "#fff1a1",
                    "hovered_text": "#fffbe1",
                    "selected_text": "#fffbe1",
                    "normal_border": "#f1dc3b",
                    "hovered_border": "#f7e570",
                    "selected_border": "#fbef9e",
                },
                "font": {
                    "name": "noto_sans",
                    "size": "16",
                    "bold": "1",
                },
            },
            "settings_button": {
                "colours": {
                    "normal_bg": "#35201d",
                    "hovered_bg": "#4d2f2a",
                    "selected_bg": "#664039",
                    "active_bg": "#7f5148",
                    "normal_text": "#ffd5cb",
                    "hovered_text": "#ffefeb",
                    "selected_text": "#ffefeb",
                    "normal_border": "#ff9d85",
                    "hovered_border": "#ffb59f",
                    "selected_border": "#ffcfbf",
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
