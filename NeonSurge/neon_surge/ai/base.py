from __future__ import annotations
from abc import ABC, abstractmethod

import pygame

from ..constants import SCREEN_W, SCREEN_H, HUD_H
from ..components.transform import TransformComponent


class AIBehaviour(ABC):
    """Abstract Strategy — inject a concrete subclass into Enemy."""

    @abstractmethod
    def update(
        self,
        transform: TransformComponent,
        player_pos: pygame.math.Vector2,
        peers: list,
        dt: float,
        particle_pool: list,
    ) -> None: ...

    @staticmethod
    def _clamp_pos(pos: pygame.math.Vector2, r: float) -> None:
        pos.x = max(r, min(SCREEN_W - r, pos.x))
        pos.y = max(HUD_H + r, min(SCREEN_H - r, pos.y))
