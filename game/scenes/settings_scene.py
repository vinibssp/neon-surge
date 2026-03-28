from __future__ import annotations

import pygame
import pygame_gui

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


class SettingsScene(BaseMenuScene):
    def __init__(self, stack) -> None:
        super().__init__(stack)
        self._elapsed_time = 0.0
        self._background_renderer = CyberpunkMenuBackgroundRenderer()
        self._audio_settings_manager = self.stack.audio_settings_manager
        self._display_settings_manager = self.stack.display_settings_manager

        self._music_volume_value = 0.20
        self._sfx_volume_value = 0.20
        if self._audio_settings_manager is not None:
            self._music_volume_value = self._audio_settings_manager.settings.music_volume
            self._sfx_volume_value = self._audio_settings_manager.settings.sfx_volume

        self._is_fullscreen = False
        if self._display_settings_manager is not None:
            self._is_fullscreen = self._display_settings_manager.settings.fullscreen

        self._init_ui()

    def _init_ui(self) -> None:
        current_language = "pt_BR"
        if self.stack.localization_manager is not None:
            current_language = self.stack.localization_manager.language

        panel_x = (SCREEN_WIDTH // 2) - 430
        panel_w = 860

        # Header
        create_label(
            LabelConfig(
                text=self.t("settings.title"),
                rect=pygame.Rect((SCREEN_WIDTH // 2 - 430, 30), (860, 70)),
                variant="title",
            ),
            manager=self.ui_manager,
        )

        # Main Audio Panel
        self._audio_panel = create_panel(
            PanelConfig(
                rect=pygame.Rect((panel_x, 120), (panel_w, 230)),
                variant="card",
            ),
            manager=self.ui_manager,
        )

        create_label(
            LabelConfig(
                text=self.t("settings.audio_header"),
                rect=pygame.Rect((24, 10), (812, 40)),
                variant="settings_header",
            ),
            manager=self.ui_manager,
            container=self._audio_panel,
        )

        # Music Row
        create_label(
            LabelConfig(text=self.t("settings.music"), rect=pygame.Rect((40, 62), (120, 40)), variant="settings_label"),
            manager=self.ui_manager, container=self._audio_panel
        )
        self._music_value_label = create_label(
            LabelConfig(text=self._format_percent(self._music_volume_value), rect=pygame.Rect((742, 62), (80, 40)), variant="value"),
            manager=self.ui_manager, container=self._audio_panel
        )
        self._music_decrease_btn = create_button(
            ButtonConfig(text="-", rect=pygame.Rect((190, 62), (50, 40)), variant="ghost"),
            manager=self.ui_manager, container=self._audio_panel
        )
        self._music_slider = create_slider(
            SliderConfig(rect=pygame.Rect((250, 62), (430, 40)), value=self._music_volume_value, value_range=(0.0, 1.0)),
            manager=self.ui_manager, container=self._audio_panel
        )
        self._music_increase_btn = create_button(
            ButtonConfig(text="+", rect=pygame.Rect((690, 62), (50, 40)), variant="ghost"),
            manager=self.ui_manager, container=self._audio_panel
        )

        # SFX Row
        create_label(
            LabelConfig(text=self.t("settings.sfx"), rect=pygame.Rect((40, 132), (120, 40)), variant="settings_label"),
            manager=self.ui_manager, container=self._audio_panel
        )
        self._sfx_value_label = create_label(
            LabelConfig(text=self._format_percent(self._sfx_volume_value), rect=pygame.Rect((742, 132), (80, 40)), variant="value"),
            manager=self.ui_manager, container=self._audio_panel
        )
        self._sfx_decrease_btn = create_button(
            ButtonConfig(text="-", rect=pygame.Rect((190, 132), (50, 40)), variant="ghost"),
            manager=self.ui_manager, container=self._audio_panel
        )
        self._sfx_slider = create_slider(
            SliderConfig(rect=pygame.Rect((250, 132), (430, 40)), value=self._sfx_volume_value, value_range=(0.0, 1.0)),
            manager=self.ui_manager, container=self._audio_panel
        )
        self._sfx_increase_btn = create_button(
            ButtonConfig(text="+", rect=pygame.Rect((690, 132), (50, 40)), variant="ghost"),
            manager=self.ui_manager, container=self._audio_panel
        )

        # Preferences Panel
        self._pref_panel = create_panel(
            PanelConfig(
                rect=pygame.Rect((panel_x, 370), (panel_w, 260)),
                variant="card",
            ),
            manager=self.ui_manager,
        )
        
        create_label(
            LabelConfig(
                text=self.t("settings.preferences_header"),
                rect=pygame.Rect((24, 10), (812, 40)),
                variant="settings_header",
            ),
            manager=self.ui_manager,
            container=self._pref_panel,
        )

        create_label(
            LabelConfig(text=self.t("settings.identity"), rect=pygame.Rect((40, 60), (280, 40)), variant="settings_label"),
            manager=self.ui_manager,
            container=self._pref_panel,
        )

        self._change_name_button = create_button(
            ButtonConfig(
                text=self.t("settings.change_name"),
                rect=pygame.Rect((350, 60), (470, 40)),
                variant="primary",
            ),
            manager=self.ui_manager,
            container=self._pref_panel,
        )

        create_label(
            LabelConfig(text=self.t("settings.input"), rect=pygame.Rect((40, 112), (280, 40)), variant="settings_label"),
            manager=self.ui_manager,
            container=self._pref_panel,
        )

        self._controls_button = create_button(
            ButtonConfig(
                text=self.t("settings.controls"),
                rect=pygame.Rect((350, 112), (470, 40)),
                variant="primary",
            ),
            manager=self.ui_manager,
            container=self._pref_panel,
        )

        create_label(
            LabelConfig(text=self.t("settings.fullscreen"), rect=pygame.Rect((40, 164), (280, 40)), variant="settings_label"),
            manager=self.ui_manager,
            container=self._pref_panel,
        )

        self._fullscreen_button = create_button(
            ButtonConfig(
                text=self._fullscreen_button_text(),
                rect=pygame.Rect((350, 164), (470, 40)),
                variant="primary" if self._is_fullscreen else "ghost",
            ),
            manager=self.ui_manager,
            container=self._pref_panel,
        )

        create_label(
            LabelConfig(text=self.t("settings.language"), rect=pygame.Rect((40, 214), (170, 40)), variant="settings_label"),
            manager=self.ui_manager,
            container=self._pref_panel,
        )
        self._language_status_label = create_label(
            LabelConfig(
                text=self.t(
                    "settings.language.current",
                    language=self._language_display_name(current_language),
                ),
                rect=pygame.Rect((220, 214), (190, 40)),
                variant="value",
            ),
            manager=self.ui_manager,
            container=self._pref_panel,
        )
        self._language_pt_button = create_button(
            ButtonConfig(
                text=self.t("settings.language.pt"),
                rect=pygame.Rect((430, 214), (180, 40)),
                variant="primary" if current_language == "pt_BR" else "ghost",
            ),
            manager=self.ui_manager,
            container=self._pref_panel,
        )
        self._language_en_button = create_button(
            ButtonConfig(
                text=self.t("settings.language.en"),
                rect=pygame.Rect((630, 214), (190, 40)),
                variant="primary" if current_language == "en_US" else "ghost",
            ),
            manager=self.ui_manager,
            container=self._pref_panel,
        )

        # Back Button
        self._back_button = create_button(
            ButtonConfig(
                text=self.t("settings.back"),
                rect=pygame.Rect((SCREEN_WIDTH // 2 - 220, 650), (440, 58)),
                variant="danger",
            ),
            manager=self.ui_manager,
        )

        self.set_navigator(
            controls=[
                self._music_decrease_btn, self._music_increase_btn,
                self._sfx_decrease_btn, self._sfx_increase_btn,
                self._change_name_button,
                self._controls_button,
                self._fullscreen_button,
                self._language_pt_button,
                self._language_en_button,
                self._back_button,
            ],
            actions={
                self._music_decrease_btn: lambda: self._step_music(-0.05),
                self._music_increase_btn: lambda: self._step_music(0.05),
                self._sfx_decrease_btn: lambda: self._step_sfx(-0.05),
                self._sfx_increase_btn: lambda: self._step_sfx(0.05),
                self._change_name_button: self._change_name,
                self._controls_button: self._open_controls,
                self._fullscreen_button: self._toggle_fullscreen,
                self._language_pt_button: lambda: self._set_language("pt_BR"),
                self._language_en_button: lambda: self._set_language("en_US"),
                self._back_button: self._close,
            },
            on_cancel=self._close,
        )

    def _open_controls(self) -> None:
        from game.scenes.controls_scene import ControlsScene
        self.stack.push(ControlsScene(self.stack))

    def _change_name(self) -> None:
        from game.scenes.player_name_scene import PlayerNameScene
        self.stack.push(PlayerNameScene(self.stack, is_first_time=False))

    def handle_input(self, events: list[pygame.event.Event]) -> None:
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_F11:
                self._toggle_fullscreen()
                continue
            if event.type == pygame_gui.UI_HORIZONTAL_SLIDER_MOVED:
                if event.ui_element is self._music_slider:
                    self._set_music_volume(float(event.value))
                elif event.ui_element is self._sfx_slider:
                    self._set_sfx_volume(float(event.value))
        super().handle_input(events)

    def _set_music_volume(self, value: float) -> None:
        clamped = max(0.0, min(1.0, value))
        self._music_volume_value = clamped
        if self._audio_settings_manager is not None:
            self._audio_settings_manager.set_music_volume(clamped)
        self._music_value_label.set_text(self._format_percent(clamped))
        self._music_slider.set_current_value(clamped)

    def _set_sfx_volume(self, value: float) -> None:
        clamped = max(0.0, min(1.0, value))
        self._sfx_volume_value = clamped
        if self._audio_settings_manager is not None:
            self._audio_settings_manager.set_sfx_volume(clamped)
        self._sfx_value_label.set_text(self._format_percent(clamped))
        self._sfx_slider.set_current_value(clamped)

    def _step_music(self, delta: float) -> None:
        self._set_music_volume(self._music_volume_value + delta)

    def _step_sfx(self, delta: float) -> None:
        self._set_sfx_volume(self._sfx_volume_value + delta)

    def _set_language(self, language: str) -> None:
        manager = self.stack.localization_manager
        if manager is None:
            return
        manager.set_language(language)
        self.ui_manager.clear_and_reset()
        self._init_ui()

    def _toggle_fullscreen(self) -> None:
        if self._display_settings_manager is None:
            return
        self._display_settings_manager.toggle_fullscreen()
        self._is_fullscreen = self._display_settings_manager.settings.fullscreen
        self._fullscreen_button.set_text(self._fullscreen_button_text())

    def _fullscreen_button_text(self) -> str:
        state_key = "settings.fullscreen.on" if self._is_fullscreen else "settings.fullscreen.off"
        return self.t("settings.fullscreen.toggle", state=self.t(state_key))

    def _language_display_name(self, language: str) -> str:
        manager = self.stack.localization_manager
        if manager is None:
            return language
        return manager.display_language_name(language)

    @staticmethod
    def _format_percent(value: float) -> str:
        return f"{int(round(value * 100.0))}%"

    def on_menu_update(self, dt: float) -> None:
        self._elapsed_time += dt

    def render_menu_background(self, screen: pygame.Surface) -> None:
        self._background_renderer.render(screen, self._elapsed_time, SCREEN_WIDTH, SCREEN_HEIGHT)

    def _close(self) -> None:
        self.stack.pop()
