from __future__ import annotations

import pygame
from pygame_gui import UIManager
from pygame_gui.core.interfaces import IContainerLikeInterface
from pygame_gui.elements import UIButton, UILabel, UIPanel, UITextBox

from game.ui.types import ButtonConfig, PanelConfig, TextBoxConfig, TitleConfig


def create_centered_panel(
    manager: UIManager,
    screen_size: tuple[int, int],
    config: PanelConfig,
) -> UIPanel:
    width, height = config.size
    screen_width, screen_height = screen_size
    panel_rect = pygame.Rect((screen_width - width) // 2, (screen_height - height) // 2, width, height)
    return UIPanel(
        relative_rect=panel_rect,
        manager=manager,
        container=config.container,
        object_id=config.object_id,
    )


def create_title(manager: UIManager, container: IContainerLikeInterface | None, config: TitleConfig) -> UILabel:
    return UILabel(
        relative_rect=config.rect,
        text=config.text,
        manager=manager,
        container=container,
        object_id=config.object_id,
    )


def create_button(manager: UIManager, container: IContainerLikeInterface | None, config: ButtonConfig) -> UIButton:
    return UIButton(
        relative_rect=config.rect,
        text=config.text,
        manager=manager,
        container=container,
        object_id=config.object_id,
    )


def create_text_box(manager: UIManager, container: IContainerLikeInterface | None, config: TextBoxConfig) -> UITextBox:
    return UITextBox(
        html_text=config.html_text,
        relative_rect=config.rect,
        manager=manager,
        container=container,
        object_id=config.object_id,
    )
