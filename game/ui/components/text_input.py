from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional
import re
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
    regex_pattern: Optional[str] = None
    length_limit: int = 15
    anchors: dict = field(default_factory=dict)

class SanitizedTextEntryLine(pygame_gui.elements.UITextEntryLine):
    def __init__(self, regex_pattern: Optional[str] = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.regex_pattern = regex_pattern
        self.compiled_regex = re.compile(self.regex_pattern) if self.regex_pattern else None

    def process_event(self, event: pygame.event.Event) -> bool:
        if self.is_enabled and self.is_focused and self.compiled_regex:
            if event.type == pygame.KEYDOWN:
                allowed_controls = {
                    pygame.K_BACKSPACE, pygame.K_RETURN, pygame.K_ESCAPE,
                    pygame.K_LEFT, pygame.K_RIGHT, pygame.K_DELETE,
                    pygame.K_HOME, pygame.K_END, pygame.K_TAB
                }
                if event.key not in allowed_controls and event.unicode:
                    if not self.compiled_regex.match(event.unicode):
                        return True  # Consome o evento, bloqueando-o

            elif event.type == pygame.TEXTINPUT:
                if not self.compiled_regex.match(event.text):
                    return True  # Consome o evento TEXTINPUT
                    
        return super().process_event(event)

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

    entry = SanitizedTextEntryLine(
        regex_pattern=config.regex_pattern,
        relative_rect=config.rect,
        manager=manager,
        container=container,
        object_id=object_id,
        placeholder_text=config.placeholder,
        initial_text=config.initial_text,
        anchors=config.anchors or None,
    )

    if config.allowed_characters is not None:
        entry.set_allowed_characters(config.allowed_characters)
    if config.forbidden_characters is not None:
        entry.set_forbidden_characters(config.forbidden_characters)

    entry.set_text_length_limit(config.length_limit)

    if not config.enabled:
        entry.disable()

    return entry
