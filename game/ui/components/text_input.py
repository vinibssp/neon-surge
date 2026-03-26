from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional
import pygame
import pygame_gui

from game.ui.gui_theme import build_component_object_id


@dataclass
class TextInputConfig:
    """Config declarativo para UITextEntryLine."""
    rect: pygame.Rect
    placeholder: str = ""
    initial_text: str = ""
    object_id: Optional[str] = None
    enabled: bool = True
    forbidden_characters: Optional[list[str]] = None
    allowed_characters: Optional[list[str]] = None
    anchors: dict = field(default_factory=dict)


def create_text_input(
    config: TextInputConfig,
    manager: pygame_gui.UIManager,
    container: Optional[pygame_gui.core.UIContainer] = None,
) -> pygame_gui.elements.UITextEntryLine:
    """Fabrica um UITextEntryLine a partir de TextInputConfig."""
    object_id = build_component_object_id(
        element_id="text_entry_line",
        object_id=config.object_id,
    )

    kwargs = {
        "relative_rect": config.rect,
        "manager": manager,
        "container": container,
        "object_id": object_id,
        "initial_text": config.initial_text,
    }
    if config.placeholder:
        kwargs["placeholder_text"] = config.placeholder
    if config.anchors:
        kwargs["anchors"] = config.anchors

    entry = pygame_gui.elements.UITextEntryLine(**kwargs)

    if config.allowed_characters is not None:
        entry.set_allowed_characters(config.allowed_characters)
    if config.forbidden_characters is not None:
        entry.set_forbidden_characters(config.forbidden_characters)

    if not config.enabled:
        entry.disable()

    return entry
