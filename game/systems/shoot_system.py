from __future__ import annotations

from game.components.data_components import BulletComponent
from game.core.events import BulletExpired
from game.core.world import GameWorld
from game.systems.world_queries import BULLET_QUERY


class ShootSystem:
    def __init__(self, world: GameWorld) -> None:
        self.world = world

    def update(self, dt: float) -> None:
        for bullet_entity in self.world.query(BULLET_QUERY):
            bullet = bullet_entity.get_component(BulletComponent)
            if bullet is None:
                continue
            bullet.lifetime -= dt
            if bullet.lifetime <= 0:
                self.world.event_bus.publish(BulletExpired(owner_tag=bullet.owner_tag))
                self.world.remove_entity(bullet_entity)
