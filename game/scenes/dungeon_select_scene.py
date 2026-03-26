from __future__ import annotations

import pygame

from game.config import SCREEN_HEIGHT, SCREEN_WIDTH
from game.modes.dungeons_mode import DungeonsMode
from game.scenes.game_scene import GameScene
from game.scenes.menus._base_menu_scene import BaseMenuScene
from game.scenes.services import CyberpunkMenuBackgroundRenderer
from game.ui.components import ButtonConfig, LabelConfig, PanelConfig, create_button, create_label, create_panel
from game.ui.gui_theme import register_custom_element_themes


class DungeonSelectScene(BaseMenuScene):
    def __init__(self, stack) -> None:
        super().__init__(stack)
        self._elapsed_time = 0.0
        self._background_renderer = CyberpunkMenuBackgroundRenderer()

        title = create_label(
            LabelConfig(
                text="SELECAO DE DUNGEON",
                rect=pygame.Rect((SCREEN_WIDTH // 2 - 320, 90), (640, 60)),
                object_id="dungeon_select_title",
            ),
            manager=self.ui_manager,
        )
        del title

        panel = create_panel(
            PanelConfig(
                rect=pygame.Rect((SCREEN_WIDTH // 2 - 360, 180), (720, 320)),
                variant="card",
                object_id="dungeon_select_panel",
            ),
            manager=self.ui_manager,
        )

        self._themes = DungeonsMode.default_themes()
        self._theme_buttons: list[object] = []
        self._theme_by_button: dict[object, object] = {}

        button_width = 260
        button_height = 48
        gap_y = 18
        start_y = 22
        for index, theme in enumerate(self._themes):
            button_rect = pygame.Rect((32, start_y + index * (button_height + gap_y)), (button_width, button_height))
            button = create_button(
                ButtonConfig(
                    text=theme.name,
                    rect=button_rect,
                    variant="primary",
                    object_id=f"dungeon_{theme.name.lower()}_button",
                ),
                manager=self.ui_manager,
                container=panel,
            )
            label_rect = pygame.Rect((310, start_y + index * (button_height + gap_y)), (380, button_height))
            create_label(
                LabelConfig(
                    text=theme.description,
                    rect=label_rect,
                    object_id="dungeon_desc_label",
                ),
                manager=self.ui_manager,
                container=panel,
            )
            self._theme_buttons.append(button)
            self._theme_by_button[button] = theme

        back_button = create_button(
            ButtonConfig(
                text="VOLTAR",
                rect=pygame.Rect((SCREEN_WIDTH // 2 - 90, 540), (180, 48)),
                variant="primary",
                object_id="dungeon_back_button",
            ),
            manager=self.ui_manager,
        )

        self._register_theme_colors()

        controls = [*self._theme_buttons, back_button]
        actions = {button: (lambda b=button: self._start_theme(b)) for button in self._theme_buttons}
        actions[back_button] = self._back
        self.set_navigator(controls=controls, actions=actions, on_cancel=self._back)

    def render_menu_background(self, screen: pygame.Surface) -> None:
        self._background_renderer.render(screen, self._elapsed_time, SCREEN_WIDTH, SCREEN_HEIGHT)

    def on_menu_update(self, dt: float) -> None:
        self._elapsed_time += dt

    def _start_theme(self, button) -> None:
        theme = self._theme_by_button.get(button)
        if theme is None:
            return
        mode = DungeonsMode(theme=theme)
        self.stack.replace(GameScene(self.stack, mode))

    def _back(self) -> None:
        self.stack.pop()

    def _register_theme_colors(self) -> None:
        theme_overrides: dict[str, dict] = {
            "dungeon_select_title": {
                "colours": {"normal_text": "#c6d6ff"},
                "font": {"name": "noto_sans", "size": "40", "bold": "1"},
            }
        }

        for theme in self._themes:
            theme_overrides[f"dungeon_{theme.name.lower()}_button"] = {
                "colours": {
                    "normal_bg": _rgb_to_hex(theme.wall_fill),
                    "hovered_bg": _rgb_to_hex(_scale_color(theme.wall_fill, 1.18)),
                    "selected_bg": _rgb_to_hex(_scale_color(theme.wall_fill, 1.28)),
                    "active_bg": _rgb_to_hex(_scale_color(theme.wall_fill, 1.36)),
                    "normal_text": _rgb_to_hex(theme.enemy_primary),
                    "hovered_text": "#f0f6ff",
                    "selected_text": "#f0f6ff",
                    "normal_border": _rgb_to_hex(theme.wall_edge),
                    "hovered_border": _rgb_to_hex(_scale_color(theme.wall_edge, 1.15)),
                    "selected_border": _rgb_to_hex(_scale_color(theme.wall_edge, 1.25)),
                },
                "font": {"name": "noto_sans", "size": "16", "bold": "1"},
            }

        register_custom_element_themes(self.ui_manager, theme_overrides)


def _rgb_to_hex(color: tuple[int, int, int]) -> str:
    return f"#{color[0]:02x}{color[1]:02x}{color[2]:02x}"


def _scale_color(color: tuple[int, int, int], factor: float) -> tuple[int, int, int]:
    return (
        min(255, int(color[0] * factor)),
        min(255, int(color[1] * factor)),
        min(255, int(color[2] * factor)),
    )
