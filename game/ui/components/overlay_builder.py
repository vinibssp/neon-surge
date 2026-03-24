from __future__ import annotations

import pygame
from pygame_gui import UIManager
from pygame_gui.elements import UITextBox

from game.ui.components.base_widgets import create_button, create_centered_panel, create_text_box, create_title
from game.ui.types import (
    ButtonConfig,
    OverlayActionConfig,
    OverlayMenuConfig,
    OverlayMenuWidgets,
    PanelConfig,
    StandardOverlayLayoutSpec,
    StandardOverlayWidgets,
    TextBoxConfig,
    TitleConfig,
    UIControl,
)


def create_standard_overlay(
    manager: UIManager,
    screen_size: tuple[int, int],
    layout: StandardOverlayLayoutSpec,
) -> StandardOverlayWidgets:
    panel = create_centered_panel(
        manager=manager,
        screen_size=screen_size,
        config=PanelConfig(size=layout.panel_size, object_id=layout.panel_object_id),
    )
    title_rect = layout.title_rect or pygame.Rect(14, 14, layout.panel_size[0] - 28, 54)
    title = create_title(
        manager=manager,
        container=panel,
        config=TitleConfig(text=layout.title, rect=title_rect),
    )

    body: UITextBox | None = None
    if layout.body_text is not None:
        body_rect = layout.body_rect or pygame.Rect(14, 78, layout.panel_size[0] - 28, layout.panel_size[1] - 150)
        body = create_text_box(
            manager=manager,
            container=panel,
            config=TextBoxConfig(html_text=layout.body_text, rect=body_rect, object_id="#menu_body_label"),
        )

    actions: dict[str, UIControl] = {}
    for action in layout.actions:
        actions[action.key] = create_button(
            manager=manager,
            container=panel,
            config=ButtonConfig(text=action.text, rect=action.rect, object_id=action.object_id),
        )

    return StandardOverlayWidgets(panel=panel, title=title, body=body, actions=actions)


def create_overlay_menu(
    manager: UIManager,
    screen_size: tuple[int, int],
    config: OverlayMenuConfig,
) -> OverlayMenuWidgets:
    standard_overlay = create_standard_overlay(
        manager=manager,
        screen_size=screen_size,
        layout=StandardOverlayLayoutSpec(
            title=config.title,
            panel_object_id=config.panel_object_id,
            panel_size=config.panel_size,
            actions=(
                OverlayActionConfig(
                    key="close",
                    text=config.close_button_text,
                    rect=pygame.Rect(14, config.panel_size[1] - 72, config.panel_size[0] - 28, 58),
                    object_id="#overlay_close_button",
                ),
            ),
        ),
    )
    return OverlayMenuWidgets(
        panel=standard_overlay.panel,
        title=standard_overlay.title,
        close_button=standard_overlay.actions["close"],
    )


def draw_overlay_backdrop(
    screen: pygame.Surface,
    screen_size: tuple[int, int],
    color: tuple[int, int, int],
    alpha: int = 140,
) -> None:
    overlay = pygame.Surface(screen_size)
    overlay.set_alpha(alpha)
    overlay.fill(color)
    screen.blit(overlay, (0, 0))
