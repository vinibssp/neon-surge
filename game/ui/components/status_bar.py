from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional
import pygame
import pygame_gui

from game.ui.gui_theme import build_component_object_id


@dataclass
class StatusBarConfig:
    """Config declarativo para UIStatusBar.

    Variantes via class_id (mapeiam para o tema):
        - None      → #status_bar         (neon roxo, genérico)
        - "health"  → #status_bar.health  (rosa/vermelho)
        - "energy"  → #status_bar.energy  (cyan)
        - "xp"      → #status_bar.xp      (amarelo)
    """
    rect: pygame.Rect
    value: float = 1.0              # 0.0 – 1.0
    variant: Optional[str] = None
    object_id: Optional[str] = None
    status_text: str = ""
    anchors: dict = field(default_factory=dict)


def create_status_bar(
    config: StatusBarConfig,
    manager: pygame_gui.UIManager,
    container: Optional[pygame_gui.core.UIContainer] = None,
) -> pygame_gui.elements.UIStatusBar:
    """Fabrica um UIStatusBar a partir de StatusBarConfig."""
    object_id = build_component_object_id(
        element_id="status_bar",
        variant=config.variant,
        object_id=config.object_id,
    )

    bar = pygame_gui.elements.UIStatusBar(
        relative_rect=config.rect,
        manager=manager,
        container=container,
        object_id=object_id,
        anchors=config.anchors or None,
    )

    bar.set_display_text(config.status_text)
    bar.status_percentage = max(0.0, min(1.0, config.value))

    return bar
