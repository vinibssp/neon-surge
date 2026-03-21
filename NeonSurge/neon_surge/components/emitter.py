from __future__ import annotations


class ParticleEmitter:
    """Spawns a burst of Particle objects into a shared pool.

    Inject into any entity that needs visual particle effects.
    Import Particle lazily to avoid circular deps with entities/.
    """

    def __init__(self, color: tuple) -> None:
        self.color = color

    def burst(self, x: float, y: float, pool: list, count: int = 10) -> None:
        from neon_surge.entities.particle import Particle  # lazy import
        for _ in range(count):
            pool.append(Particle(x, y, self.color))
