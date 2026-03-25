from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional
import pygame
import pygame_gui


@dataclass
class ProgressBarConfig:
    """Config declarativo para UIProgressBar.

    Nota: pygame_gui não expõe class_id direto no ProgressBar —
    use object_id para override de tema pontual quando necessário.
    """
    rect: pygame.Rect
    value: float = 1.0          # 0.0 – 1.0
    status_text: str = ""       # texto sobreposto à barra; "" = percentual automático
    object_id: Optional[str] = None
    anchors: dict = field(default_factory=dict)


def create_progress_bar(
    config: ProgressBarConfig,
    manager: pygame_gui.UIManager,
    container: Optional[pygame_gui.core.UIContainer] = None,
) -> pygame_gui.elements.UIProgressBar:
    """Fabrica um UIProgressBar a partir de ProgressBarConfig."""
    object_id = pygame_gui.core.ObjectID(
        object_id=config.object_id,
    )

    bar = pygame_gui.elements.UIProgressBar(
        relative_rect=config.rect,
        manager=manager,
        container=container,
        object_id=object_id,
        anchors=config.anchors or None,
    )

    bar.set_current_progress(max(0.0, min(1.0, config.value)) * 100)

    if config.status_text:
        bar.status_text = lambda: config.status_text

    return bar
