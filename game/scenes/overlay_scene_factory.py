from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

import pygame
from pygame_gui import UIManager
from pygame_gui.elements import UIPanel, UITextBox

from game.ui.components.overlay_builder import create_standard_overlay
from game.ui.types import OverlayActionConfig, StandardOverlayLayoutSpec, UIControl


@dataclass(frozen=True)
class OverlayActionBinding:
    key: str
    text: str
    rect: pygame.Rect
    handler: Callable[[], None]
    object_id: str = "#menu_action_button"


@dataclass(frozen=True)
class OverlaySceneBuildResult:
    panel: UIPanel
    body: UITextBox | None
    controls: dict[str, UIControl]
    navigation_buttons: list[UIControl]
    navigation_actions: list[Callable[[], None]]
    cancel_action: Callable[[], None] | None


class OverlaySceneFactory:
    @staticmethod
    def build(
        screen_size: tuple[int, int],
        ui_manager: UIManager,
        title: str,
        panel_object_id: str,
        action_bindings: tuple[OverlayActionBinding, ...],
        panel_size: tuple[int, int] = (560, 320),
        body_text: str | None = None,
        body_rect: pygame.Rect | None = None,
        title_rect: pygame.Rect | None = None,
        on_cancel_key: str | None = None,
    ) -> OverlaySceneBuildResult:
        overlay_actions = tuple(
            OverlayActionConfig(
                key=binding.key,
                text=binding.text,
                rect=binding.rect,
                object_id=binding.object_id,
            )
            for binding in action_bindings
        )

        overlay = create_standard_overlay(
            manager=ui_manager,
            screen_size=screen_size,
            layout=StandardOverlayLayoutSpec(
                title=title,
                panel_object_id=panel_object_id,
                panel_size=panel_size,
                title_rect=title_rect,
                body_text=body_text,
                body_rect=body_rect,
                actions=overlay_actions,
            ),
        )

        navigation_buttons = [overlay.actions[binding.key] for binding in action_bindings]
        navigation_actions = [binding.handler for binding in action_bindings]
        cancel_action = None
        if on_cancel_key is not None:
            for binding in action_bindings:
                if binding.key == on_cancel_key:
                    cancel_action = binding.handler
                    break

        return OverlaySceneBuildResult(
            panel=overlay.panel,
            body=overlay.body,
            controls=overlay.actions,
            navigation_buttons=navigation_buttons,
            navigation_actions=navigation_actions,
            cancel_action=cancel_action,
        )
