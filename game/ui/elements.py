from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable

import pygame
from pygame import Vector2

from game.config import UI_BUTTON_COLOR, UI_BUTTON_HOVER_COLOR, UI_LABEL_COLOR, UI_PANEL_COLOR

_FONT_CACHE: dict[int, pygame.font.Font] = {}


def _get_font(size: int) -> pygame.font.Font:
    font = _FONT_CACHE.get(size)
    if font is None:
        font = pygame.font.Font(None, size)
        _FONT_CACHE[size] = font
    return font


def _draw_centered_text(
    screen: pygame.Surface,
    rect: pygame.Rect,
    text: str,
    color: tuple[int, int, int],
    font_size: int,
) -> None:
    if not text:
        return
    font = _get_font(font_size)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(center=rect.center)
    screen.blit(text_surface, text_rect)


@dataclass
class UIElement:
    position: Vector2
    size: Vector2
    margin: float = 8.0
    visible: bool = True
    children: list["UIElement"] = field(default_factory=list)

    def add_child(self, child: "UIElement") -> None:
        self.children.append(child)

    def update(self, dt: float) -> None:
        for child in self.children:
            child.update(dt)

    def handle_input(self, events: list[pygame.event.Event]) -> None:
        for child in self.children:
            child.handle_input(events)

    def render(self, screen: pygame.Surface) -> None:
        if not self.visible:
            return
        for child in self.children:
            child.render(screen)

    def rect(self) -> pygame.Rect:
        return pygame.Rect(self.position.x, self.position.y, self.size.x, self.size.y)


@dataclass
class Label(UIElement):
    text: str = ""
    color: tuple[int, int, int] = UI_LABEL_COLOR
    font_size: int = 28
    draw_panel: bool = True
    panel_color: tuple[int, int, int] = UI_PANEL_COLOR
    border_color: tuple[int, int, int] | None = None

    def render(self, screen: pygame.Surface) -> None:
        if not self.visible:
            return
        rect = self.rect()
        if self.draw_panel:
            pygame.draw.rect(screen, self.panel_color, rect, border_radius=6)
            border_color = self.color if self.border_color is None else self.border_color
            pygame.draw.rect(screen, border_color, rect, width=1, border_radius=6)
        _draw_centered_text(screen, rect, self.text, self.color, font_size=self.font_size)
        super().render(screen)


@dataclass
class Button(UIElement):
    text: str = ""
    callback: Callable[[], None] | None = None
    hovered: bool = False
    base_color: tuple[int, int, int] = UI_BUTTON_COLOR
    hover_color: tuple[int, int, int] = UI_BUTTON_HOVER_COLOR
    border_color: tuple[int, int, int] = UI_LABEL_COLOR
    text_color: tuple[int, int, int] = (245, 245, 255)
    hover_border_color: tuple[int, int, int] | None = None
    hover_text_color: tuple[int, int, int] | None = None
    font_size: int = 30

    def update(self, dt: float) -> None:
        super().update(dt)

    def render(self, screen: pygame.Surface) -> None:
        if not self.visible:
            return
        rect = self.rect()
        fill_color = self.hover_color if self.hovered else self.base_color
        border_color = self.border_color
        text_color = self.text_color
        if self.hovered:
            border_color = self.border_color if self.hover_border_color is None else self.hover_border_color
            text_color = self.text_color if self.hover_text_color is None else self.hover_text_color
        pygame.draw.rect(screen, fill_color, rect, border_radius=8)
        pygame.draw.rect(screen, border_color, rect, width=2, border_radius=8)
        _draw_centered_text(screen, rect, self.text, text_color, font_size=self.font_size)
        super().render(screen)


@dataclass
class Container(UIElement):
    orientation: str = "vertical"
    padding: float = 12.0
    draw_panel: bool = True
    panel_color: tuple[int, int, int] = UI_PANEL_COLOR
    border_color: tuple[int, int, int] = UI_LABEL_COLOR
    border_width: int = 2

    def do_layout(self) -> None:
        cursor_x = self.position.x + self.padding
        cursor_y = self.position.y + self.padding
        for child in self.children:
            child.position = Vector2(cursor_x, cursor_y)
            if self.orientation == "vertical":
                cursor_y += child.size.y + child.margin
            else:
                cursor_x += child.size.x + child.margin

    def update(self, dt: float) -> None:
        self.do_layout()
        super().update(dt)

    def render(self, screen: pygame.Surface) -> None:
        if not self.visible:
            return
        if self.draw_panel:
            pygame.draw.rect(screen, self.panel_color, self.rect(), border_radius=10)
            pygame.draw.rect(screen, self.border_color, self.rect(), width=self.border_width, border_radius=10)
        super().render(screen)
