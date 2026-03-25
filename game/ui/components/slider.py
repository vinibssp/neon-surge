from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, Tuple
import pygame
import pygame_gui

from game.ui.gui_theme import build_component_object_id


@dataclass
class SliderConfig:
    """Config declarativo para UIHorizontalSlider."""
    rect: pygame.Rect
    value: float = 0.5
    value_range: Tuple[float, float] = (0.0, 1.0)
    click_increment: float = 0.05
    object_id: Optional[str] = None
    enabled: bool = True
    anchors: dict = field(default_factory=dict)


def create_slider(
    config: SliderConfig,
    manager: pygame_gui.UIManager,
    container: Optional[pygame_gui.core.UIContainer] = None,
) -> pygame_gui.elements.UIHorizontalSlider:
    """Fabrica um UIHorizontalSlider a partir de SliderConfig."""
    object_id = build_component_object_id(
        element_id="horizontal_slider",
        object_id=config.object_id,
    )

    slider = pygame_gui.elements.UIHorizontalSlider(
        relative_rect=config.rect,
        start_value=config.value,
        value_range=config.value_range,
        manager=manager,
        container=container,
        object_id=object_id,
        click_increment=config.click_increment,
        anchors=config.anchors or None,
    )

    if not config.enabled:
        slider.disable()

    return slider
