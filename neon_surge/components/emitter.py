from __future__ import annotations


class ParticleEmitter:
    """Spawns a burst of Particle objects into a shared pool.

    Inject into any entity that needs visual particle effects.
    Import Particle lazily to avoid circular deps with entities/.
    """

    def __init__(self, color: tuple) -> None:
        self.color = color

    def burst(self, x: float, y: float, pool: list, count: int = 10) -> None:
        from ..entities.particle import Particula  # lazy import
        for _ in range(count):
            pool.append(Particula(x, y, self.color))
