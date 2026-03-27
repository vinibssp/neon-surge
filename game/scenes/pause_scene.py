from __future__ import annotations

import pygame
from game.config import SCREEN_HEIGHT, SCREEN_WIDTH
from game.core.events import AudioContextChanged, AudioDuckRequested, AudioUnduckRequested
from game.scenes.menus._base_menu_scene import BaseMenuScene
from game.scenes.settings_scene import SettingsScene
from game.ui.components import ButtonConfig, LabelConfig, create_button, create_label


class PauseScene(BaseMenuScene):
    transparent = True

    def __init__(self, stack) -> None:
        super().__init__(stack)

        title = create_label(
            LabelConfig(
                text=self.t("pause.title"),
                rect=pygame.Rect((SCREEN_WIDTH // 2 - 160, 164), (320, 66)),
                variant="title",
            ),
            manager=self.ui_manager,
        )
        del title

        resume_button = create_button(
            ButtonConfig(
                text=self.t("pause.resume"),
                rect=pygame.Rect((SCREEN_WIDTH // 2 - 140, 280), (280, 56)),
                variant="primary",
            ),
            manager=self.ui_manager,
        )
        settings_button = create_button(
            ButtonConfig(
                text=self.t("pause.settings"),
                rect=pygame.Rect((SCREEN_WIDTH // 2 - 140, 350), (280, 56)),
                variant="primary",
            ),
            manager=self.ui_manager,
        )
        menu_button = create_button(
            ButtonConfig(
                text=self.t("pause.main_menu"),
                rect=pygame.Rect((SCREEN_WIDTH // 2 - 140, 420), (280, 56)),
                variant="danger",
            ),
            manager=self.ui_manager,
        )

        self.set_navigator(
            buttons=[resume_button, settings_button, menu_button],
            actions={
                resume_button: self._resume,
                settings_button: self._open_settings,
                menu_button: self._go_main_menu,
            },
            on_cancel=self._resume,
        )

    def on_enter(self) -> None:
        self.stack.event_bus.publish(AudioContextChanged(context="pause", reason="pause_opened"))
        self.stack.event_bus.publish(AudioDuckRequested(reason="pause_opened"))

    def on_exit(self) -> None:
        self.stack.event_bus.publish(AudioUnduckRequested(reason="pause_closed"))

    def render_menu_background(self, screen: pygame.Surface) -> None:
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 140))
        screen.blit(overlay, (0, 0))

    def _resume(self) -> None:
        self.stack.pop()
        self.stack.event_bus.publish(AudioContextChanged(context="gameplay", reason="pause_resumed"))

    def _open_settings(self) -> None:
        self.stack.push(SettingsScene(self.stack))

    def _go_main_menu(self) -> None:
        self.stack.pop()
        from game.scenes.main_menu_scene import MainMenuScene

        self.stack.replace(MainMenuScene(self.stack))
