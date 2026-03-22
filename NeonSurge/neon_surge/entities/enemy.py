from __future__ import annotations
from typing import Dict

import pygame

from ..constants  import C_NEON_PNK, C_BLOOD_RED, C_NEON_ORG, C_WHITE
from ..utils      import draw_neon_glow
from ..components import TransformComponent, ColliderComponent
from ..ai         import AIBehaviour, BounceAI, ChaserAI, ChargeAI


class Enemy:
    """
    Enemy drone.

    Composition
    -----------
    TransformComponent   pos / vel
    ColliderComponent    circle hitbox
    AIBehaviour          injected strategy — BounceAI | ChaserAI | ChargeAI

    To add a new enemy type: write an AIBehaviour subclass and register it in
    _REGISTRY.  No changes needed here.
    """

    # kind → (AI factory, neon colour)
    _REGISTRY: Dict[str, tuple] = {
        "quique":      (lambda v: BounceAI(v),  C_NEON_PNK),
        "perseguidor": (lambda v: ChaserAI(v),  C_BLOOD_RED),
        "investida":   (lambda v: ChargeAI(v),  C_NEON_ORG),
    }

    def __init__(self, x: float, y: float, kind: str, speed: float) -> None:
        factory, color  = self._REGISTRY[kind]
        self.transform  = TransformComponent(x, y)
        self.collider   = ColliderComponent(12)
        self.kind       = kind
        self.ai: AIBehaviour = factory(speed)
        self.color      = color

    @property
    def pos(self) -> pygame.math.Vector2:
        return self.transform.pos

    @property
    def radius(self) -> float:
        return self.collider.radius

    def update(self, player_pos, peers: list, dt: float, particle_pool: list, sound_manager) -> None:
        self.ai.update(self.transform, player_pos, peers, dt, particle_pool, sound_manager)
        self._apply_separation(peers)

    def _apply_separation(self, peers: list) -> None:
        """Soft repulsion — prevents enemies from stacking on top of each other."""
        force = pygame.math.Vector2(0, 0)
        for other in peers:
            if other is self:
                continue
            d     = self.pos.distance_to(other.pos)
            min_d = self.radius + other.radius + 5
            if 0 < d < min_d:
                force += (self.pos - other.pos).normalize() * (min_d - d) * 0.1
        self.transform.pos += force

    def draw(self, surf) -> None:
        # Aim-line only for ChargeAI in the AIM state
        if self.kind == "investida" and isinstance(self.ai, ChargeAI):
            if self.ai.state == ChargeAI.AIM:
                col = C_BLOOD_RED if not self.ai.locked else C_WHITE
                thk = 2           if not self.ai.locked else 4
                pygame.draw.line(surf, col, self.pos, self.ai.target, thk)

        draw_neon_glow(surf, self.color, self.pos.x, self.pos.y, self.radius, 3)
        pygame.draw.circle(surf, self.color, (int(self.pos.x), int(self.pos.y)), int(self.radius))
        pygame.draw.circle(surf, C_WHITE,    (int(self.pos.x), int(self.pos.y)), int(self.radius // 3))
