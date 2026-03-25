from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional
import pygame
import pygame_gui

from game.ui.gui_theme import build_component_object_id


@dataclass
class CheckboxConfig:
    """Config declarativo para UICheckBox (pygame_gui >= 0.6.x).

    pygame_gui representa checkbox como UIButton com #check_box element_id.
    """
    text: str
    rect: pygame.Rect
    checked: bool = False
    object_id: Optional[str] = None
    enabled: bool = True
    anchors: dict = field(default_factory=dict)


def create_checkbox(
    config: CheckboxConfig,
    manager: pygame_gui.UIManager,
    container: Optional[pygame_gui.core.UIContainer] = None,
) -> pygame_gui.elements.UICheckBox:
    """Fabrica um UICheckBox a partir de CheckboxConfig."""
    object_id = build_component_object_id(
        element_id="check_box",
        object_id=config.object_id,
    )

    cb = pygame_gui.elements.UICheckBox(
        relative_rect=config.rect,
        text=config.text,
        manager=manager,
        container=container,
        object_id=object_id,
        anchors=config.anchors or None,
    )

    if config.checked:
        cb.check()

    if not config.enabled:
        cb.disable()

    return cb
