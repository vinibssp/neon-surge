from __future__ import annotations

from game.behaviors.advanced_helpers import normalized, smoothing_factor
from game.behaviors.behavior import Behavior
from game.components.data_components import (
    CollisionComponent,
    ExplosiveComponent,
    MovementComponent,
    TransformComponent,
)
from game.ecs.entity import Entity


class ExplosiveBehavior(Behavior):
    BASE_RADIUS = 12.0
    DIRECT_CHASE_SPEED = 168.0
    CHASE_RESPONSIVENESS = 0.18
    ARMING_DISTANCE = 110.0
    BLAST_MAX_RADIUS = 96.0
    BLAST_GROWTH_RATE = 130.0

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
        to_player = player_transform.position - transform.position
        distance_to_player = to_player.length()

        if explosive.timer < explosive.chase_time and distance_to_player > self.ARMING_DISTANCE:
            desired_direction = normalized(to_player)
            desired_velocity = desired_direction * self.DIRECT_CHASE_SPEED
            movement.velocity = movement.velocity.lerp(
                desired_velocity,
                smoothing_factor(self.CHASE_RESPONSIVENESS, dt),
            )
            movement.input_direction = desired_direction
            movement.max_speed = self.DIRECT_CHASE_SPEED
            collision.radius = self.BASE_RADIUS
            return

        slowdown = 0.82 if distance_to_player <= self.ARMING_DISTANCE else 0.9
        movement.velocity *= slowdown
        movement.input_direction = normalized(movement.velocity, normalized(to_player))

        arm_time_boost = 0.0
        if distance_to_player <= self.ARMING_DISTANCE:
            arm_time_boost += dt * 1.35
        if distance_to_player <= self.ARMING_DISTANCE * 0.6:
            arm_time_boost += dt * 1.15
        explosive.timer += arm_time_boost

        arm_start_time = min(explosive.chase_time, explosive.detonate_time * 0.68)
        if explosive.timer >= arm_start_time:
            growth_time = explosive.timer - arm_start_time
            collision.radius = min(self.BLAST_MAX_RADIUS, self.BASE_RADIUS + growth_time * self.BLAST_GROWTH_RATE)

        if explosive.timer >= explosive.detonate_time:
            explosive.exploded = True
            world.remove_entity(entity)


from game.core.world import GameWorld
