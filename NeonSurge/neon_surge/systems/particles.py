from __future__ import annotations
from typing import List

from ..entities.particle import Particle


class ParticleSystem:
    """Owns and ticks the global particle pool.

    Entities write into pool directly (via ParticleEmitter.burst);
    this system handles lifecycle and drawing.
    """

    def __init__(self) -> None:
        self.pool: List[Particle] = []

    def update(self) -> None:
        self.pool = [p for p in self.pool if p.alive]
        for p in self.pool:
            p.update()

    def draw(self, surf) -> None:
        for p in self.pool:
            p.draw(surf)

    def clear(self) -> None:
        self.pool.clear()
