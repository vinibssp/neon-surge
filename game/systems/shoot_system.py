from __future__ import annotations

from game.components.data_components import BulletComponent, CollisionComponent, TransformComponent
from game.core.events import BulletExpired
from game.core.world import GameWorld
from game.systems.world_queries import BULLET_QUERY


class ShootSystem:
    def __init__(self, world: GameWorld) -> None:
        self.world = world

    def update(self, dt: float) -> None:
        for bullet_entity in self.world.query(BULLET_QUERY):
            bullet = bullet_entity.get_component(BulletComponent)
            transform = bullet_entity.get_component(TransformComponent)
            collision = bullet_entity.get_component(CollisionComponent)
            if bullet is None:
                continue

            if transform is not None:
                radius = 0.0 if collision is None else collision.radius
                touches_border = (
                    transform.position.x <= radius
                    or transform.position.x >= self.world.width - radius
                    or transform.position.y <= radius
                    or transform.position.y >= self.world.height - radius
                )
                out_of_bounds = (
                    transform.position.x < -radius
                    or transform.position.x > self.world.width + radius
                    or transform.position.y < -radius
                    or transform.position.y > self.world.height + radius
                )
                if touches_border or out_of_bounds:
                    self.world.event_bus.publish(BulletExpired(owner_tag=bullet.owner_tag))
                    self.world.remove_entity(bullet_entity)
                    continue

            bullet.lifetime -= dt
            if bullet.lifetime <= 0:
                self.world.event_bus.publish(BulletExpired(owner_tag=bullet.owner_tag))
                self.world.remove_entity(bullet_entity)
