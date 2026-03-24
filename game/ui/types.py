from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, TypeAlias

import pygame
from pygame_gui.core.interfaces import IContainerLikeInterface
from pygame_gui.elements import UILabel, UIPanel, UITextBox


class UIControlProtocol(Protocol):
    rect: pygame.Rect

    def select(self) -> None: ...

    def unselect(self) -> None: ...

    def set_text(self, text: str) -> None: ...


UIControl: TypeAlias = UIControlProtocol


@dataclass(frozen=True)
class PanelConfig:
    size: tuple[int, int]
    object_id: str
    container: IContainerLikeInterface | None = None


@dataclass(frozen=True)
class TitleConfig:
    text: str
    rect: pygame.Rect
    object_id: str = "#menu_title_label"


@dataclass(frozen=True)
class ButtonConfig:
    text: str
    rect: pygame.Rect
    object_id: str


@dataclass(frozen=True)
class TextBoxConfig:
    html_text: str
    rect: pygame.Rect
    object_id: str


@dataclass(frozen=True)
class TabBarConfig:
    labels: tuple[str, ...]
    object_ids: tuple[str, ...]
    top_left: tuple[int, int]
    button_size: tuple[int, int]
    gap: int = 8


@dataclass(frozen=True)
class OverlayMenuConfig:
    title: str
    panel_object_id: str
    panel_size: tuple[int, int] = (560, 320)
    close_button_text: str = "X"


@dataclass(frozen=True)
class OverlayMenuWidgets:
    panel: UIPanel
    title: UILabel
    close_button: UIControl


@dataclass(frozen=True)
class OverlayActionConfig:
    key: str
    text: str
    rect: pygame.Rect
    object_id: str = "#menu_action_button"


@dataclass(frozen=True)
class StandardOverlayLayoutSpec:
    title: str
    panel_object_id: str
    panel_size: tuple[int, int] = (560, 320)
    title_rect: pygame.Rect | None = None
    body_text: str | None = None
    body_rect: pygame.Rect | None = None
    actions: tuple[OverlayActionConfig, ...] = ()


@dataclass(frozen=True)
class StandardOverlayWidgets:
    panel: UIPanel
    title: UILabel
    body: UITextBox | None
    actions: dict[str, UIControl]
