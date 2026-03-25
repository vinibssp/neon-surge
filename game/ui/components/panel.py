from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional
import pygame
import pygame_gui

from game.ui.gui_theme import build_component_object_id


@dataclass
class PanelConfig:
    """Config declarativo para UIPanel.

    Variantes via class_id (mapeiam para o tema):
        - None    → estilo padrão (#panel)
        - "card"  → #panel.card   (borda neon sólida)
        - "hud"   → #panel.hud    (semi-transparente, borda cyan tênue)
    """
    rect: pygame.Rect
    variant: Optional[str] = None
    object_id: Optional[str] = None
    starting_layer_height: int = 1
    anchors: dict = field(default_factory=dict)


def create_panel(
    config: PanelConfig,
    manager: pygame_gui.UIManager,
    container: Optional[pygame_gui.core.UIContainer] = None,
) -> pygame_gui.elements.UIPanel:
    """Fabrica um UIPanel a partir de PanelConfig."""
    object_id = build_component_object_id(
        element_id="panel",
        variant=config.variant,
        object_id=config.object_id,
    )

    return pygame_gui.elements.UIPanel(
        relative_rect=config.rect,
        starting_height=config.starting_layer_height,
        manager=manager,
        container=container,
        object_id=object_id,
        anchors=config.anchors or None,
    )
