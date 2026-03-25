from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional
import pygame
import pygame_gui

from game.ui.gui_theme import build_component_object_id


@dataclass
class LabelConfig:
    """Config declarativo para UILabel.

    Variantes via class_id (mapeiam para o tema):
        - None       → estilo padrão (`label`)
        - "title"    → `label.title`
        - "subtitle" → `label.subtitle`
        - "muted"    → `label.muted`
        - "value"    → `label.value` (números/stats, mono cyan bold)
    """
    text: str
    rect: pygame.Rect
    variant: Optional[str] = None
    object_id: Optional[str] = None
    anchors: dict = field(default_factory=dict)


def create_label(
    config: LabelConfig,
    manager: pygame_gui.UIManager,
    container: Optional[pygame_gui.core.UIContainer] = None,
) -> pygame_gui.elements.UILabel:
    """Fabrica um UILabel a partir de LabelConfig."""
    object_id = build_component_object_id(
        element_id="label",
        variant=config.variant,
        object_id=config.object_id,
    )

    return pygame_gui.elements.UILabel(
        relative_rect=config.rect,
        text=config.text,
        manager=manager,
        container=container,
        object_id=object_id,
        anchors=config.anchors or None,
    )
