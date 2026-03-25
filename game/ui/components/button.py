from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, Tuple
import pygame
import pygame_gui

from game.ui.gui_theme import build_component_object_id


@dataclass
class ButtonConfig:
    """Config declarativo para UIButton.

    Variantes via class_id (mapeiam para o tema):
        - None       → estilo padrão (#button)
        - "primary"  → #button.primary
        - "danger"   → #button.danger
        - "ghost"    → #button.ghost
    """
    text: str
    rect: pygame.Rect
    variant: Optional[str] = None          # class_id semântico
    object_id: Optional[str] = None        # override pontual de object_id
    tooltip: Optional[str] = None
    enabled: bool = True
    anchors: dict = field(default_factory=dict)


def create_button(
    config: ButtonConfig,
    manager: pygame_gui.UIManager,
    container: Optional[pygame_gui.core.UIContainer] = None,
) -> pygame_gui.elements.UIButton:
    """Fabrica um UIButton a partir de ButtonConfig."""
    object_id = build_component_object_id(
        element_id="button",
        variant=config.variant,
        object_id=config.object_id,
    )

    btn = pygame_gui.elements.UIButton(
        relative_rect=config.rect,
        text=config.text,
        manager=manager,
        container=container,
        object_id=object_id,
        anchors=config.anchors or None,
        tool_tip_text=config.tooltip,
    )

    if not config.enabled:
        btn.disable()

    return btn
