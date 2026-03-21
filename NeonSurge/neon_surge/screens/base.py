from __future__ import annotations
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Optional

import pygame

from ..constants import C_DARK_GRAY, C_WHITE
from ..utils     import draw_text, draw_dynamic_button

if TYPE_CHECKING:
    from ..game import Game


class Screen(ABC):
    """
    Base class for every state-machine node (screen).

    Contract
    --------
    handle_event(event) → Optional[str]   next-state key, or None to stay
    update(dt)          → Optional[str]   same
    draw(surface)       → None

    Shared helpers (_back_button, _nav_keys, _hover_sel, _draw_vol) are
    available to all subclasses to avoid duplication.
    """

    def __init__(self, game: "Game") -> None:
        self.game = game

    @abstractmethod
    def handle_event(self, event) -> Optional[str]: ...

    @abstractmethod
    def update(self, dt: float) -> Optional[str]: ...

    @abstractmethod
    def draw(self, surf) -> None: ...

    # ── shared helpers ────────────────────────────────────────────────────────

    def _back_button(self, surf) -> None:
        pygame.draw.rect(surf, C_DARK_GRAY, (20, 20, 140, 40), border_radius=5)
        draw_text(surf, "< ESC VOLTAR", self.game.fonts["text"], C_WHITE, 90, 40)

    def _nav_keys(self, event, sel: int, n: int) -> int:
        if event.key in (pygame.K_UP, pygame.K_w, pygame.K_LEFT, pygame.K_a):
            return (sel - 1) % n
        if event.key in (pygame.K_DOWN, pygame.K_s, pygame.K_RIGHT, pygame.K_d):
            return (sel + 1) % n
        return sel

    def _hover_sel(self, hitboxes: list) -> Optional[int]:
        mx, my = self.game.mouse_pos()
        for i, r in enumerate(hitboxes):
            if r.collidepoint(mx, my):
                return i
        return None

    def _draw_vol(self, surf) -> None:
        self.game.volume_widget.draw(
            surf, self.game.fonts, self.game.audio, *self.game.mouse_pos()
        )
