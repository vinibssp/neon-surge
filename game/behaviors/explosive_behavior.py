from __future__ import annotations

from game.behaviors.advanced_helpers import normalized
from game.behaviors.behavior import Behavior
from game.components.data_components import (
    CollisionComponent,
    ExplosiveComponent,
    MovementComponent,
    TransformComponent,
)
from game.ecs.entity import Entity


class ExplosiveBehavior(Behavior):
    def update(self, entity: Entity, world: "GameWorld", dt: float) -> None:
        player = world.player
        if player is None:
            return

        explosive = entity.get_component(ExplosiveComponent)
        transform = entity.get_component(TransformComponent)
        movement = entity.get_component(MovementComponent)
        collision = entity.get_component(CollisionComponent)
        player_transform = player.get_component(TransformComponent)
        if (
            explosive is None
            or transform is None
            or movement is None
            or collision is None
            or player_transform is None
        ):
            return

        explosive.timer += dt
        if explosive.timer < explosive.chase_time:
            target_vector = player_transform.position - transform.position
            desired_velocity = normalized(target_vector) * (movement.max_speed * 1.05)
            smoothing = max(0.0, min(1.0, 0.09 * 60.0 * dt))
            movement.velocity = movement.velocity.lerp(desired_velocity, smoothing)
            movement.input_direction = normalized(movement.velocity)
            movement.max_speed = max(1.0, movement.velocity.length())
            return

        movement.velocity *= 0.9
        movement.input_direction = normalized(movement.velocity)
        if explosive.timer > 3.5:
            collision.radius = min(80.0, 12.0 + (explosive.timer - 3.5) * 80.0)

        if explosive.timer >= explosive.detonate_time:
            explosive.exploded = True
            world.remove_entity(entity)


from game.core.world import GameWorld
