from __future__ import annotations

from typing import Mapping, Optional

import pygame_gui
from pygame_gui.core import ObjectID

from .theme.retrowave_theme import THEME_DATA

def create_ui_manager(window_size: tuple[int, int]) -> pygame_gui.UIManager:
    manager = pygame_gui.UIManager(window_size, THEME_DATA)
    manager.preload_fonts(
        [
            {
                "name": "noto_sans",
                "point_size": 14,
                "style": "italic",
                "antialiased": "1",
            }
        ]
    )

    return manager


def resolve_component_class_id(element_id: str, variant: Optional[str]) -> Optional[str]:
    if variant is None or variant == "":
        return None
    if "." in variant:
        return variant
    return f"{element_id}.{variant}"


def resolve_component_object_id(object_id: Optional[str]) -> Optional[str]:
    if object_id is None:
        return None
    object_id = object_id.strip()
    if object_id == "":
        return None
    if object_id.startswith("#"):
        return object_id
    return f"#{object_id}"

def build_component_object_id(
    element_id: str,
    variant: Optional[str] = None,
    object_id: Optional[str] = None,
) -> ObjectID:
    return ObjectID(
        class_id=resolve_component_class_id(element_id, variant),
        object_id=resolve_component_object_id(object_id),
    )


def register_custom_element_themes(
    ui_manager: pygame_gui.UIManager,
    element_themes: Mapping[str, dict],
    rebuild_all: bool = True,
) -> None:
    theme = ui_manager.get_theme()
    resolved_theme_data: dict[str, dict] = {}
    for element_name, theme_data in element_themes.items():
        resolved_name = resolve_component_object_id(element_name) or element_name
        resolved_theme_data[resolved_name] = theme_data

    theme.update_theming(resolved_theme_data, rebuild_all=False)

    if rebuild_all:
        ui_manager.rebuild_all_from_changed_theme_data()
