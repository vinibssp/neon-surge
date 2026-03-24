from __future__ import annotations

from dataclasses import dataclass

import pygame

from game.config import SCREEN_HEIGHT, SCREEN_WIDTH
from game.modes.mode_config import OneVsOneConfig, RaceConfig, SurvivalConfig
from game.modes.one_vs_one_mode import OneVsOneMode
from game.modes.race_mode import RaceMode
from game.modes.survival_mode import SurvivalMode
from game.scenes.base_menu_scene import BaseMenuScene
from game.scenes.game_scene import GameScene
from game.scenes.menu_overlay_scenes import HelpOverlayScene, SettingsOverlayScene
from game.scenes.services import CyberpunkMenuBackgroundRenderer
from game.ui.components.base_widgets import create_button, create_centered_panel, create_text_box
from game.ui.types import UIControl, ButtonConfig, PanelConfig, TextBoxConfig


NEON_CYAN = (0, 220, 255)
NEON_MAGENTA = (255, 55, 220)
NEON_LIME = (150, 255, 70)


@dataclass(frozen=True)
class ModeCardData:
    title: str
    description: str
    color: tuple[int, int, int]


class MainMenuScene(BaseMenuScene):
    def __init__(self, stack) -> None:
        super().__init__(stack)
        self.elapsed_time = 0.0
        self._last_mode_card_index: int | None = None
        self.background_renderer = CyberpunkMenuBackgroundRenderer()

        self.menu_panel = create_centered_panel(
            manager=self.ui_manager,
            screen_size=(SCREEN_WIDTH, SCREEN_HEIGHT),
            config=PanelConfig(size=(560, 420), object_id="#menu_panel"),
        )
        self.mode_card = create_centered_panel(
            manager=self.ui_manager,
            screen_size=(560, 420),
            config=PanelConfig(size=(520, 220), object_id="#mode_card", container=self.menu_panel),
        )
        self.mode_card.set_relative_position((20, 20))

        self.mode_title_box = create_text_box(
            manager=self.ui_manager,
            container=self.mode_card,
            config=TextBoxConfig(html_text="", rect=pygame.Rect(12, 12, 496, 70), object_id="#mode_title"),
        )
        self.mode_description_box = create_text_box(
            manager=self.ui_manager,
            container=self.mode_card,
            config=TextBoxConfig(html_text="", rect=pygame.Rect(12, 88, 496, 120), object_id="#mode_description"),
        )

        self.race_button: UIControl = create_button(
            manager=self.ui_manager,
            container=self.menu_panel,
            config=ButtonConfig(text="Corrida", rect=pygame.Rect(20, 264, 164, 86), object_id="#mode_button_race"),
        )
        self.survival_button: UIControl = create_button(
            manager=self.ui_manager,
            container=self.menu_panel,
            config=ButtonConfig(text="Resistencia", rect=pygame.Rect(198, 264, 164, 86), object_id="#mode_button_survival"),
        )
        self.one_vs_one_button: UIControl = create_button(
            manager=self.ui_manager,
            container=self.menu_panel,
            config=ButtonConfig(text="1v1", rect=pygame.Rect(376, 264, 164, 86), object_id="#mode_button_1v1"),
        )

        self.exit_button: UIControl = create_button(
            manager=self.ui_manager,
            container=None,
            config=ButtonConfig(text="X", rect=pygame.Rect(SCREEN_WIDTH - 72, 20, 44, 44), object_id="#exit_button"),
        )
        self.settings_button: UIControl = create_button(
            manager=self.ui_manager,
            container=None,
            config=ButtonConfig(text="⚙", rect=pygame.Rect(SCREEN_WIDTH - 132, SCREEN_HEIGHT - 74, 50, 50), object_id="#settings_button"),
        )
        self.help_button: UIControl = create_button(
            manager=self.ui_manager,
            container=None,
            config=ButtonConfig(text="?", rect=pygame.Rect(SCREEN_WIDTH - 72, SCREEN_HEIGHT - 74, 50, 50), object_id="#help_button"),
        )

        self.set_navigator(
            buttons=[
                self.race_button,
                self.survival_button,
                self.one_vs_one_button,
                self.exit_button,
                self.settings_button,
                self.help_button,
            ],
            actions=[
                self._start_race,
                self._start_survival,
                self._start_one_vs_one,
                self._quit,
                self._open_settings,
                self._open_help,
            ],
            on_cancel=self._quit,
        )
        self.mode_cards = [
            ModeCardData(
                title="Corrida",
                description=RaceConfig().description,
                color=NEON_CYAN,
            ),
            ModeCardData(
                title="Resistencia",
                description=SurvivalConfig().description,
                color=NEON_MAGENTA,
            ),
            ModeCardData(
                title="1v1",
                description=OneVsOneConfig().description,
                color=NEON_LIME,
            ),
        ]
        self._sync_mode_card()

    def on_menu_update(self, dt: float) -> None:
        self.elapsed_time += dt
        self._sync_mode_card()

    def render_menu_background(self, screen: pygame.Surface) -> None:
        self.background_renderer.render(screen, self.elapsed_time, SCREEN_WIDTH, SCREEN_HEIGHT)

    def _start_race(self) -> None:
        self.stack.replace(GameScene(self.stack, mode=RaceMode()))

    def _start_survival(self) -> None:
        self.stack.replace(GameScene(self.stack, mode=SurvivalMode()))

    def _start_one_vs_one(self) -> None:
        self.stack.replace(GameScene(self.stack, mode=OneVsOneMode()))

    def _quit(self) -> None:
        while not self.stack.is_empty():
            self.stack.pop()

    def _open_settings(self) -> None:
        self.stack.push(SettingsOverlayScene(self.stack))

    def _open_help(self) -> None:
        self.stack.push(HelpOverlayScene(self.stack))

    def _sync_mode_card(self) -> None:
        selected_index = self.navigator.selected_index
        if selected_index < 0:
            self._last_mode_card_index = None
            self.mode_title_box.set_text("")
            self.mode_description_box.set_text("")
            return
        if selected_index >= len(self.mode_cards):
            return
        if self._last_mode_card_index == selected_index:
            return
        selected = self.mode_cards[selected_index]
        self.mode_title_box.set_text(
            f"<font color='{self._to_hex(selected.color)}'><b>{selected.title}</b></font>"
        )
        self.mode_description_box.set_text(selected.description)
        self._last_mode_card_index = selected_index

    @staticmethod
    def _to_hex(color: tuple[int, int, int]) -> str:
        red, green, blue = color
        return f"#{red:02x}{green:02x}{blue:02x}"
