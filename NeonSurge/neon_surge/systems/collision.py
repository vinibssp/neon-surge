from __future__ import annotations
from typing import List, Optional

from ..entities.player      import Player
from ..entities.enemy       import Enemy
from ..entities.collectible import Collectible
from ..entities.portal      import Portal


class CollisionSystem:
    """
    Pure-function collision queries — no mutable state.

    Kept as a class so a future broad-phase optimisation (spatial hash,
    quadtree) can be slotted in here without touching entities or Level.
    """

    @staticmethod
    def player_vs_enemies(player: Player, enemies: List[Enemy]) -> bool:
        if player.invincible:
            return False
        for e in enemies:
            if player.pos.distance_to(e.pos) < (e.radius + player.size // 2 - 2):
                return True
        return False

    @staticmethod
    def player_vs_collectible(
        player: Player, collectibles: List[Collectible]
    ) -> Optional[Collectible]:
        for c in collectibles:
            if player.pos.distance_to(c.pos) < c.collider.radius:
                return c
        return None

    @staticmethod
    def player_vs_portal(player: Player, portal: Optional[Portal]) -> bool:
        if portal is None:
            return False
        return player.pos.distance_to(portal.pos) < portal.collider.radius
