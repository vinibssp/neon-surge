from __future__ import annotations

import pygame

from game.config import SCREEN_HEIGHT, SCREEN_WIDTH
from game.scenes.menus._base_menu_scene import BaseMenuScene
from game.scenes.services import CyberpunkMenuBackgroundRenderer
from game.ui.components import (
    ButtonConfig,
    LabelConfig,
    PanelConfig,
    SliderConfig,
    create_button,
    create_label,
    create_panel,
    create_slider,
)
from game.ui.gui_theme import register_custom_element_themes


class SettingsScene(BaseMenuScene):
    def __init__(self, stack) -> None:
        super().__init__(stack)
        self._elapsed_time = 0.0
        self._background_renderer = CyberpunkMenuBackgroundRenderer()
        self._audio_settings_manager = self.stack.audio_settings_manager
        self._slider_moved_user_type = "ui_horizontal_slider_moved"

        self._music_volume_value = 0.20
        self._sfx_volume_value = 0.20
        if self._audio_settings_manager is not None:
            self._music_volume_value = self._audio_settings_manager.settings.music_volume
            self._sfx_volume_value = self._audio_settings_manager.settings.sfx_volume

        self._register_settings_themes()

        panel = create_panel(
            PanelConfig(
                rect=pygame.Rect((SCREEN_WIDTH // 2 - 370, 170), (740, 340)),
                variant="card",
                object_id="settings_audio_panel",
            ),
            manager=self.ui_manager,
        )

        title = create_label(
            LabelConfig(
                text="CONFIG",
                rect=pygame.Rect((SCREEN_WIDTH // 2 - 140, 100), (280, 56)),
                object_id="settings_title_label",
            ),
            manager=self.ui_manager,
        )
        line_1 = create_label(
            LabelConfig(
                text="AUDIO",
                rect=pygame.Rect((270, 20), (200, 44)),
                object_id="settings_audio_section_label",
            ),
            manager=self.ui_manager,
            container=panel,
        )

        music_label = create_label(
            LabelConfig(
                text="Musica",
                rect=pygame.Rect((40, 84), (120, 36)),
                object_id="settings_music_label",
            ),
            manager=self.ui_manager,
            container=panel,
        )

        self._music_value_label = create_label(
            LabelConfig(
                text=self._format_percent(self._music_volume_value),
                rect=pygame.Rect((580, 84), (100, 36)),
                object_id="settings_music_value_label",
            ),
            manager=self.ui_manager,
            container=panel,
        )

        self._music_decrease_button = create_button(
            ButtonConfig(
                text="-",
                rect=pygame.Rect((40, 124), (64, 42)),
                object_id="settings_music_decrease_button",
            ),
            manager=self.ui_manager,
            container=panel,
        )
        self._music_slider = create_slider(
            SliderConfig(
                rect=pygame.Rect((120, 124), (460, 42)),
                value=self._music_volume_value,
                value_range=(0.0, 1.0),
                click_increment=0.01,
                object_id="settings_music_slider",
            ),
            manager=self.ui_manager,
            container=panel,
        )
        self._music_increase_button = create_button(
            ButtonConfig(
                text="+",
                rect=pygame.Rect((596, 124), (64, 42)),
                object_id="settings_music_increase_button",
            ),
            manager=self.ui_manager,
            container=panel,
        )

        sfx_label = create_label(
            LabelConfig(
                text="SFX",
                rect=pygame.Rect((40, 194), (120, 36)),
                object_id="settings_sfx_label",
            ),
            manager=self.ui_manager,
            container=panel,
        )
        self._sfx_value_label = create_label(
            LabelConfig(
                text=self._format_percent(self._sfx_volume_value),
                rect=pygame.Rect((580, 194), (100, 36)),
                object_id="settings_sfx_value_label",
            ),
            manager=self.ui_manager,
            container=panel,
        )
        self._sfx_decrease_button = create_button(
            ButtonConfig(
                text="-",
                rect=pygame.Rect((40, 234), (64, 42)),
                object_id="settings_sfx_decrease_button",
            ),
            manager=self.ui_manager,
            container=panel,
        )
        self._sfx_slider = create_slider(
            SliderConfig(
                rect=pygame.Rect((120, 234), (460, 42)),
                value=self._sfx_volume_value,
                value_range=(0.0, 1.0),
                click_increment=0.01,
                object_id="settings_sfx_slider",
            ),
            manager=self.ui_manager,
            container=panel,
        )
        self._sfx_increase_button = create_button(
            ButtonConfig(
                text="+",
                rect=pygame.Rect((596, 234), (64, 42)),
                object_id="settings_sfx_increase_button",
            ),
            manager=self.ui_manager,
            container=panel,
        )
        del title, line_1, music_label, sfx_label

        back_button = create_button(
            ButtonConfig(
                text="Voltar",
                rect=pygame.Rect((SCREEN_WIDTH // 2 - 130, 520), (260, 56)),
                object_id="settings_back_button",
            ),
            manager=self.ui_manager,
        )
        
        change_name_button = create_button(
            ButtonConfig(
                text="Alterar Nome",
                rect=pygame.Rect((SCREEN_WIDTH // 2 - 130, 580), (260, 56)),
                variant="primary",
                object_id="settings_change_name_button",
            ),
            manager=self.ui_manager,
        )

        self.set_navigator(
            buttons=[
                self._music_decrease_button,
                self._music_increase_button,
                self._sfx_decrease_button,
                self._sfx_increase_button,
                back_button,
                change_name_button,
            ],
            actions={
                self._music_decrease_button: lambda: self._step_music(-0.05),
                self._music_increase_button: lambda: self._step_music(0.05),
                self._sfx_decrease_button: lambda: self._step_sfx(-0.05),
                self._sfx_increase_button: lambda: self._step_sfx(0.05),
                back_button: self._close,
                change_name_button: self._change_name,
            },
            on_cancel=self._close,
        )

    def _change_name(self) -> None:
        from game.scenes.player_name_scene import PlayerNameScene
        self.stack.push(PlayerNameScene(self.stack, is_first_time=False))

    def handle_input(self, events: list[pygame.event.Event]) -> None:
        for event in events:
            if event.type != pygame.USEREVENT:
                continue
            if getattr(event, "user_type", None) != self._slider_moved_user_type:
                continue
            ui_element = getattr(event, "ui_element", None)
            if ui_element is self._music_slider:
                self._set_music_volume(self._coerce_float(getattr(event, "value", self._music_volume_value)))
            elif ui_element is self._sfx_slider:
                self._set_sfx_volume(self._coerce_float(getattr(event, "value", self._sfx_volume_value)))
        super().handle_input(events)

    def _register_settings_themes(self) -> None:
        register_custom_element_themes(
            self.ui_manager,
            {
                "settings_audio_panel": {
                    "colours": {
                        "dark_bg": "#1a0f0d",
                        "normal_border": "#ff9d85",
                    },
                    "misc": {
                        "border_width": 2,
                        "shadow_width": 0,
                        "shape": "rectangle",
                    },
                },
                "settings_title_label": {
                    "colours": {
                        "normal_text": "#ffd2c7",
                    },
                    "font": {
                        "name": "noto_sans",
                        "size": "48",
                        "bold": "1",
                    },
                },
                "settings_audio_section_label": {
                    "colours": {
                        "normal_text": "#ffb7a4",
                    },
                    "font": {
                        "name": "noto_sans",
                        "size": "24",
                        "bold": "1",
                    },
                },
                "settings_music_label": {
                    "colours": {
                        "normal_text": "#ffe3db",
                    },
                    "font": {
                        "name": "noto_sans",
                        "size": "18",
                        "bold": "0",
                    },
                },
                "settings_sfx_label": {
                    "colours": {
                        "normal_text": "#ffe3db",
                    },
                    "font": {
                        "name": "noto_sans",
                        "size": "18",
                        "bold": "0",
                    },
                },
                "settings_music_value_label": {
                    "colours": {
                        "normal_text": "#ffd5cb",
                    },
                    "font": {
                        "name": "noto_sans",
                        "size": "18",
                        "bold": "1",
                    },
                },
                "settings_sfx_value_label": {
                    "colours": {
                        "normal_text": "#ffd5cb",
                    },
                    "font": {
                        "name": "noto_sans",
                        "size": "18",
                        "bold": "1",
                    },
                },
                "settings_music_slider": {
                    "colours": {
                        "normal_bg": "#2a1714",
                        "hovered_bg": "#3b211d",
                        "filled_bar": "#ff9d85",
                        "unfilled_bar": "#1f110f",
                        "normal_border": "#ff9d85",
                        "hovered_border": "#ffb59f",
                    },
                    "misc": {
                        "border_width": 2,
                    },
                },
                "settings_sfx_slider": {
                    "colours": {
                        "normal_bg": "#2a1714",
                        "hovered_bg": "#3b211d",
                        "filled_bar": "#ffd96f",
                        "unfilled_bar": "#1f110f",
                        "normal_border": "#ffcfbf",
                        "hovered_border": "#ffe1d5",
                    },
                    "misc": {
                        "border_width": 2,
                    },
                },
                "settings_music_decrease_button": {
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
                        "size": "24",
                        "bold": "1",
                    },
                },
                "settings_music_increase_button": {
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
                        "size": "24",
                        "bold": "1",
                    },
                },
                "settings_sfx_decrease_button": {
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
                        "size": "24",
                        "bold": "1",
                    },
                },
                "settings_sfx_increase_button": {
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
                        "size": "24",
                        "bold": "1",
                    },
                },
                "settings_back_button": {
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
            },
            rebuild_all=True,
        )

    def _set_music_volume(self, value: float) -> None:
        clamped = self._clamp01(value)
        self._music_volume_value = clamped
        if self._audio_settings_manager is not None:
            self._audio_settings_manager.set_music_volume(clamped)
        self._music_value_label.set_text(self._format_percent(clamped))
        self._sync_slider(self._music_slider, clamped)

    def _set_sfx_volume(self, value: float) -> None:
        clamped = self._clamp01(value)
        self._sfx_volume_value = clamped
        if self._audio_settings_manager is not None:
            self._audio_settings_manager.set_sfx_volume(clamped)
        self._sfx_value_label.set_text(self._format_percent(clamped))
        self._sync_slider(self._sfx_slider, clamped)

    def _step_music(self, delta: float) -> None:
        self._set_music_volume(self._music_volume_value + delta)

    def _step_sfx(self, delta: float) -> None:
        self._set_sfx_volume(self._sfx_volume_value + delta)

    @staticmethod
    def _sync_slider(slider: object, value: float) -> None:
        set_current_value = getattr(slider, "set_current_value", None)
        if callable(set_current_value):
            set_current_value(value)

    @staticmethod
    def _coerce_float(value: object) -> float:
        if isinstance(value, (int, float)):
            return float(value)
        return 0.0

    @staticmethod
    def _clamp01(value: float) -> float:
        return max(0.0, min(1.0, value))

    @staticmethod
    def _format_percent(value: float) -> str:
        return f"{int(round(value * 100.0))}%"

    def on_menu_update(self, dt: float) -> None:
        self._elapsed_time += dt

    def render_menu_background(self, screen: pygame.Surface) -> None:
        self._background_renderer.render(
            screen=screen,
            elapsed_time=self._elapsed_time,
            width=SCREEN_WIDTH,
            height=SCREEN_HEIGHT,
        )

    def _close(self) -> None:
        self.stack.pop()
