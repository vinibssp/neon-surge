from __future__ import annotations

from pygame import Vector2

from game.behaviors.advanced_helpers import normalized, smoothing_factor
from game.behaviors.behavior import Behavior
from game.components.data_components import MovementComponent, TransformComponent
from game.ecs.entity import Entity


class SuppressorBehavior(Behavior):
    def __init__(self, preferred_distance: float = 230.0) -> None:
        self.preferred_distance = preferred_distance
        self._burst_timer: dict[int, float] = {}

    def update(self, entity: Entity, world: "GameWorld", dt: float) -> None:
        player = world.player
        if player is None:
            return

        transform = entity.get_component(TransformComponent)
        movement = entity.get_component(MovementComponent)
        player_transform = player.get_component(TransformComponent)
        if transform is None or movement is None or player_transform is None:
            return

        to_player = player_transform.position - transform.position
        distance = to_player.length()
        chase_direction = normalized(to_player)
        tangent = Vector2(-chase_direction.y, chase_direction.x)

        if distance > self.preferred_distance + 35.0:
            desired_direction = normalized(chase_direction + tangent * 0.35, chase_direction)
        elif distance < self.preferred_distance - 35.0:
            desired_direction = normalized((-chase_direction) + tangent * 0.25, -chase_direction)
        else:
            desired_direction = normalized(tangent, chase_direction)

        blend = smoothing_factor(0.17, dt)
        current_direction = normalized(movement.input_direction, desired_direction)
        movement.input_direction = normalized(current_direction.lerp(desired_direction, blend), desired_direction)
        movement.max_speed = max(150.0, movement.max_speed)

        entity_id = entity.id
        burst_timer = self._burst_timer.get(entity_id, 0.0) + dt
        self._burst_timer[entity_id] = burst_timer
        if burst_timer < 0.72:
            return

        self._burst_timer[entity_id] = 0.0
        shoot_dir = normalized(player_transform.position - transform.position)
        world.spawn_enemy_bullet(
            transform.position,
            shoot_dir,
            speed=360.0,
            radius=4.0,
            color=(252, 238, 150),
        )
        world.spawn_enemy_bullet(
            transform.position,
            shoot_dir.rotate(8.0),
            speed=340.0,
            radius=4.0,
            color=(252, 238, 150),
        )


from game.core.world import GameWorld
