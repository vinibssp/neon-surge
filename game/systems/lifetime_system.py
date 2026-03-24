from __future__ import annotations

from game.components.data_components import LifetimeComponent
from game.core.events import LifetimeExpired
from game.core.world import GameWorld
from game.systems.world_queries import LIFETIME_QUERY


class LifetimeSystem:
    def __init__(self, world: GameWorld) -> None:
        self.world = world

    def update(self, dt: float) -> None:
        for entity in self.world.query(LIFETIME_QUERY):
            lifetime = entity.get_component(LifetimeComponent)
            if lifetime is None:
                continue
            lifetime.time_left -= dt
            if lifetime.time_left <= 0:
                self.world.event_bus.publish(
                    LifetimeExpired(entity_id=entity.id, tags=tuple(sorted(entity.tags)))
                )
                self.world.remove_entity(entity)
