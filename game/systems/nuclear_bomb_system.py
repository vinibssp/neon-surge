from __future__ import annotations

from game.components.data_components import NuclearBombComponent, TransformComponent
from game.core.events import ExplosionTriggered
from game.core.world import GameWorld


class NuclearBombSystem:
    def __init__(self, world: GameWorld) -> None:
        self.world = world

    def update(self, dt: float) -> None:
        del dt
        player = self.world.player
        if player is None:
            return

        bomb = player.get_component(NuclearBombComponent)
        if bomb is None or not bomb.requested:
            return

        bomb.requested = False
        if bomb.charges <= 0:
            return

        bomb.charges -= 1
        player_transform = player.get_component(TransformComponent)

        for entity in tuple(self.world.entities):
            if entity.has_tag("enemy"):
                self.world.remove_entity(entity)

        self.world.pending_add = [entity for entity in self.world.pending_add if not entity.has_tag("enemy")]
        if player_transform is not None:
            self.world.event_bus.publish(ExplosionTriggered(position=player_transform.position.copy()))
