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
        self._slider_moved_user_type = pygame_gui.UI_HORIZONTAL_SLIDER_MOVED

        self._music_volume_value = 0.20
        self._sfx_volume_value = 0.20
        if self._audio_settings_manager is not None:
            self._music_volume_value = self._audio_settings_manager.settings.music_volume
            self._sfx_volume_value = self._audio_settings_manager.settings.sfx_volume

        self._init_ui()

    def _init_ui(self) -> None:
        # Header
        create_label(
            LabelConfig(
                text="CONFIGURAÇÕES DE SISTEMA",
                rect=pygame.Rect((SCREEN_WIDTH // 2 - 400, 40), (800, 80)),
                variant="title",
            ),
            manager=self.ui_manager,
        )

        # Audio Panel
        self._audio_panel = create_panel(
            PanelConfig(
                rect=pygame.Rect((SCREEN_WIDTH // 2 - 400, 160), (800, 280)),
                variant="card",
            ),
            manager=self.ui_manager,
        )

        create_label(
            LabelConfig(
                text="CONTROLE DE ÁUDIO",
                rect=pygame.Rect((20, 10), (760, 40)),
                variant="settings_header",
            ),
            manager=self.ui_manager,
            container=self._audio_panel,
        )

        # Music Row
        create_label(
            LabelConfig(
                text="MÚSICA",
                rect=pygame.Rect((40, 70), (120, 40)),
                variant="settings_label",
            ),
            manager=self.ui_manager,
            container=self._audio_panel,
        )
        self._music_value_label = create_label(
            LabelConfig(
                text=self._format_percent(self._music_volume_value),
                rect=pygame.Rect((680, 70), (80, 40)),
                variant="value",
            ),
            manager=self.ui_manager,
            container=self._audio_panel,
        )
        self._music_decrease_btn = create_button(
            ButtonConfig(text="-", rect=pygame.Rect((180, 70), (50, 40)), variant="ghost"),
            manager=self.ui_manager, container=self._audio_panel
        )
        self._music_slider = create_slider(
            SliderConfig(
                rect=pygame.Rect((240, 70), (380, 40)),
                value=self._music_volume_value,
                value_range=(0.0, 1.0),
            ),
            manager=self.ui_manager,
            container=self._audio_panel,
        )
        self._music_increase_btn = create_button(
            ButtonConfig(text="+", rect=pygame.Rect((630, 70), (50, 40)), variant="ghost"),
            manager=self.ui_manager, container=self._audio_panel
        )

        # SFX Row
        create_label(
            LabelConfig(
                text="EFEITOS",
                rect=pygame.Rect((40, 140), (120, 40)),
                variant="settings_label",
            ),
            manager=self.ui_manager,
            container=self._audio_panel,
        )
        self._sfx_value_label = create_label(
            LabelConfig(
                text=self._format_percent(self._sfx_volume_value),
                rect=pygame.Rect((680, 140), (80, 40)),
                variant="value",
            ),
            manager=self.ui_manager,
            container=self._audio_panel,
        )
        self._sfx_decrease_btn = create_button(
            ButtonConfig(text="-", rect=pygame.Rect((180, 140), (50, 40)), variant="ghost"),
            manager=self.ui_manager, container=self._audio_panel
        )
        self._sfx_slider = create_slider(
            SliderConfig(
                rect=pygame.Rect((240, 140), (380, 40)),
                value=self._sfx_volume_value,
                value_range=(0.0, 1.0),
            ),
            manager=self.ui_manager,
            container=self._audio_panel,
        )
        self._sfx_increase_btn = create_button(
            ButtonConfig(text="+", rect=pygame.Rect((630, 140), (50, 40)), variant="ghost"),
            manager=self.ui_manager, container=self._audio_panel
        )

        # Profile / Identity Section
        self._profile_panel = create_panel(
            PanelConfig(
                rect=pygame.Rect((SCREEN_WIDTH // 2 - 400, 460), (800, 100)),
                variant="card",
            ),
            manager=self.ui_manager,
        )
        
        create_label(
            LabelConfig(
                text="IDENTIDADE OPERACIONAL",
                rect=pygame.Rect((20, 10), (300, 80)),
                variant="header",
            ),
            manager=self.ui_manager,
            container=self._profile_panel,
        )

        self._change_name_button = create_button(
            ButtonConfig(
                text="ALTERAR NOME DO PILOTO",
                rect=pygame.Rect((350, 25), (400, 50)),
                variant="primary",
            ),
            manager=self.ui_manager,
            container=self._profile_panel,
        )

        # Controls Section
        self._controls_panel = create_panel(
            PanelConfig(
                rect=pygame.Rect((SCREEN_WIDTH // 2 - 400, 570), (800, 100)),
                variant="card",
            ),
            manager=self.ui_manager,
        )

        create_label(
            LabelConfig(
                text="CONFIGURAÇÃO DE INPUT",
                rect=pygame.Rect((20, 10), (300, 80)),
                variant="header",
            ),
            manager=self.ui_manager,
            container=self._controls_panel,
        )

        self._controls_button = create_button(
            ButtonConfig(
                text="AJUSTAR CONTROLES",
                rect=pygame.Rect((350, 25), (400, 50)),
                variant="primary",
            ),
            manager=self.ui_manager,
            container=self._controls_panel,
        )

        # Back Button
        self._back_button = create_button(
            ButtonConfig(
                text="VOLTAR",
                rect=pygame.Rect((SCREEN_WIDTH // 2 - 150, 680), (300, 40)),
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
                self._back_button,
            ],
            actions={
                self._music_decrease_btn: lambda: self._step_music(-0.05),
                self._music_increase_btn: lambda: self._step_music(0.05),
                self._sfx_decrease_btn: lambda: self._step_sfx(-0.05),
                self._sfx_increase_btn: lambda: self._step_sfx(0.05),
                self._change_name_button: self._change_name,
                self._controls_button: self._open_controls,
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

    @staticmethod
    def _format_percent(value: float) -> str:
        return f"{int(round(value * 100.0))}%"

    def on_menu_update(self, dt: float) -> None:
        self._elapsed_time += dt

    def render_menu_background(self, screen: pygame.Surface) -> None:
        self._background_renderer.render(screen, self._elapsed_time, SCREEN_WIDTH, SCREEN_HEIGHT)

    def _close(self) -> None:
        self.stack.pop()
