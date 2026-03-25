from __future__ import annotations

import math

import pygame
from pygame_gui.elements import UITextBox

from game.config import PAUSE_OVERLAY_COLOR, SCREEN_HEIGHT, SCREEN_WIDTH
from game.core.events import AudioDuckRequested, AudioUnduckRequested
from game.scenes.base_menu_scene import BaseMenuScene
from game.scenes.overlay_scene_factory import OverlayActionBinding, OverlaySceneFactory
from game.ui.components.base_widgets import create_button, create_centered_panel, create_text_box
from game.ui.components.overlay_builder import draw_overlay_backdrop
from game.ui.types import ButtonConfig, PanelConfig, TextBoxConfig, UIControl


class PauseSettingsScene(BaseMenuScene):
    transparent = True

    def __init__(self, stack) -> None:
        super().__init__(stack)
        self._overlay_elapsed_time = 0.0

        self.panel = create_centered_panel(
            manager=self.ui_manager,
            screen_size=(SCREEN_WIDTH, SCREEN_HEIGHT),
            config=PanelConfig(size=(560, 360), object_id="#overlay_panel_settings"),
        )

        self.title: UITextBox = create_text_box(
            manager=self.ui_manager,
            container=self.panel,
            config=TextBoxConfig(
                html_text="<font color='#00dcff' size='6'><b>CONFIGURACOES DE AUDIO</b></font>",
                rect=pygame.Rect(20, 14, 520, 40),
                object_id="#main_menu_subtitle",
            ),
        )

        self.music_label: UITextBox = create_text_box(
            manager=self.ui_manager,
            container=self.panel,
            config=TextBoxConfig(
                html_text="", rect=pygame.Rect(140, 92, 280, 52), object_id="#volume_label_box"
            ),
        )
        self.sfx_label: UITextBox = create_text_box(
            manager=self.ui_manager,
            container=self.panel,
            config=TextBoxConfig(
                html_text="", rect=pygame.Rect(140, 172, 280, 52), object_id="#volume_label_box"
            ),
        )

        self.music_minus: UIControl = create_button(
            manager=self.ui_manager,
            container=self.panel,
            config=ButtonConfig(text="-", rect=pygame.Rect(68, 92, 56, 52), object_id="#footer_control_red"),
        )
        self.music_plus: UIControl = create_button(
            manager=self.ui_manager,
            container=self.panel,
            config=ButtonConfig(text="+", rect=pygame.Rect(436, 92, 56, 52), object_id="#footer_control_green"),
        )
        self.sfx_minus: UIControl = create_button(
            manager=self.ui_manager,
            container=self.panel,
            config=ButtonConfig(text="-", rect=pygame.Rect(68, 172, 56, 52), object_id="#footer_control_red"),
        )
        self.sfx_plus: UIControl = create_button(
            manager=self.ui_manager,
            container=self.panel,
            config=ButtonConfig(text="+", rect=pygame.Rect(436, 172, 56, 52), object_id="#footer_control_green"),
        )
        self.back_button: UIControl = create_button(
            manager=self.ui_manager,
            container=self.panel,
            config=ButtonConfig(
                text="VOLTAR",
                rect=pygame.Rect(140, 270, 280, 56),
                object_id="#menu_action_button",
            ),
        )

        self.set_navigator(
            buttons=[
                self.music_minus,
                self.music_plus,
                self.sfx_minus,
                self.sfx_plus,
                self.back_button,
            ],
            actions=[
                self._decrease_music,
                self._increase_music,
                self._decrease_sfx,
                self._increase_sfx,
                self._close,
            ],
            on_cancel=self._close,
        )

        self._sync_labels()

    def on_menu_update(self, dt: float) -> None:
        self._overlay_elapsed_time += dt

    def render_menu_background(self, screen: pygame.Surface) -> None:
        alpha = 132 + int(14 * (0.5 + 0.5 * math.sin(self._overlay_elapsed_time * 2.6)))
        draw_overlay_backdrop(
            screen,
            screen_size=(SCREEN_WIDTH, SCREEN_HEIGHT),
            color=PAUSE_OVERLAY_COLOR,
            alpha=alpha,
        )

    def _decrease_music(self) -> None:
        manager = self.stack.audio_settings_manager
        if manager is None:
            return
        manager.adjust_music_volume(-0.05)
        self._sync_labels()

    def _increase_music(self) -> None:
        manager = self.stack.audio_settings_manager
        if manager is None:
            return
        manager.adjust_music_volume(0.05)
        self._sync_labels()

    def _decrease_sfx(self) -> None:
        manager = self.stack.audio_settings_manager
        if manager is None:
            return
        manager.adjust_sfx_volume(-0.05)
        self._sync_labels()

    def _increase_sfx(self) -> None:
        manager = self.stack.audio_settings_manager
        if manager is None:
            return
        manager.adjust_sfx_volume(0.05)
        self._sync_labels()

    def _sync_labels(self) -> None:
        manager = self.stack.audio_settings_manager
        if manager is None:
            self.music_label.set_text("<b>MUSICA:</b> indisponivel")
            self.sfx_label.set_text("<b>SFX:</b> indisponivel")
            return
        self.music_label.set_text(f"<b>MUSICA:</b> {manager.get_music_volume_percent()}%")
        self.sfx_label.set_text(f"<b>SFX:</b> {manager.get_sfx_volume_percent()}%")

    def _close(self) -> None:
        self.stack.pop()


class PauseScene(BaseMenuScene):
    transparent = True

    def __init__(self, stack) -> None:
        super().__init__(stack)
        self._overlay_elapsed_time = 0.0

        overlay = OverlaySceneFactory.build(
            screen_size=(SCREEN_WIDTH, SCREEN_HEIGHT),
            ui_manager=self.ui_manager,
            title="Pausado",
            panel_object_id="#overlay_panel",
            panel_size=(420, 320),
            action_bindings=(
                OverlayActionBinding(
                    key="continue",
                    text="Voltar pro Jogo",
                    rect=pygame.Rect(14, 76, 392, 56),
                    object_id="#footer_control_green",
                    handler=self._continue,
                ),
                OverlayActionBinding(
                    key="settings",
                    text="Configuracoes",
                    rect=pygame.Rect(14, 140, 392, 56),
                    handler=self._open_settings,
                ),
                OverlayActionBinding(
                    key="leave",
                    text="Abandonar Partida",
                    rect=pygame.Rect(14, 248, 392, 58),
                    object_id="#footer_control_red",
                    handler=self._leave_match,
                ),
            ),
            on_cancel_key="continue",
        )
        self.panel = overlay.panel
        self.continue_button: UIControl = overlay.controls["continue"]
        self.settings_button: UIControl = overlay.controls["settings"]
        self.leave_button: UIControl = overlay.controls["leave"]

        self.set_navigator(
            buttons=overlay.navigation_buttons,
            actions=overlay.navigation_actions,
            on_cancel=overlay.cancel_action,
        )

    def on_enter(self) -> None:
        self.stack.event_bus.publish(AudioDuckRequested(reason="pause_scene_entered"))

    def on_exit(self) -> None:
        self.stack.event_bus.publish(AudioUnduckRequested(reason="pause_scene_exited"))

    def on_menu_update(self, dt: float) -> None:
        self._overlay_elapsed_time += dt

    def render_menu_background(self, screen: pygame.Surface) -> None:
        alpha = 132 + int(14 * (0.5 + 0.5 * math.sin(self._overlay_elapsed_time * 2.6)))
        draw_overlay_backdrop(
            screen,
            screen_size=(SCREEN_WIDTH, SCREEN_HEIGHT),
            color=PAUSE_OVERLAY_COLOR,
            alpha=alpha,
        )

    def _continue(self) -> None:
        self.stack.pop()

    def _open_settings(self) -> None:
        self.stack.push(PauseSettingsScene(self.stack))

    def _leave_match(self) -> None:
        from game.scenes.main_menu_scene import MainMenuScene

        self.stack.pop()
        self.stack.replace(MainMenuScene(self.stack))
