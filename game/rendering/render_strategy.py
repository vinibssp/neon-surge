from __future__ import annotations

from typing import Protocol

import pygame


class RenderStrategy(Protocol):
    def render(
        self,
        screen: pygame.Surface,
        entity,
        transform,
    ) -> None:
        ...
