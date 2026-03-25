from __future__ import annotations

import math

from pygame import Vector2

from game.behaviors.advanced_helpers import normalized, smoothing_factor
from game.behaviors.behavior import Behavior
from game.components.data_components import MovementComponent, TransformComponent
from game.ecs.entity import Entity


class OrbitShooterBehavior(Behavior):
    def __init__(self, orbit_radius: float = 165.0, angular_speed: float = 1.9) -> None:
        self.orbit_radius = orbit_radius
        self.angular_speed = angular_speed
        self._angle_state: dict[int, float] = {}
        self._shot_timer: dict[int, float] = {}

    def update(self, entity: Entity, world: "GameWorld", dt: float) -> None:
        player = world.player
        if player is None:
            return

        transform = entity.get_component(TransformComponent)
        movement = entity.get_component(MovementComponent)
        player_transform = player.get_component(TransformComponent)
        if transform is None or movement is None or player_transform is None:
            return

        entity_id = entity.id
        to_player = transform.position - player_transform.position
        if to_player.length_squared() <= 0:
            to_player = Vector2(1, 0)

        angle = self._angle_state.get(entity_id, math.atan2(to_player.y, to_player.x))
        angle += self.angular_speed * dt
        self._angle_state[entity_id] = angle

        orbit_offset = Vector2(math.cos(angle), math.sin(angle)) * self.orbit_radius
        desired_position = player_transform.position + orbit_offset
        desired_direction = normalized(desired_position - transform.position)

        blend = smoothing_factor(0.16, dt)
        current_direction = normalized(movement.input_direction, desired_direction)
        movement.input_direction = normalized(current_direction.lerp(desired_direction, blend), desired_direction)

        base_speed = max(120.0, movement.max_speed)
        movement.max_speed = base_speed

        shot_timer = self._shot_timer.get(entity_id, 0.0) + dt
        self._shot_timer[entity_id] = shot_timer
        if shot_timer < 1.15:
            return

        self._shot_timer[entity_id] = 0.0
        center_dir = normalized(player_transform.position - transform.position)
        for angle_offset in (-16.0, 0.0, 16.0):
            world.spawn_enemy_bullet(
                transform.position,
                center_dir.rotate(angle_offset),
                speed=300.0,
                radius=5.0,
                color=(188, 228, 255),
            )


from game.core.world import GameWorld
