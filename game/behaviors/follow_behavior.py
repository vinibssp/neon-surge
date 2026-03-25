from __future__ import annotations

import random

from pygame import Vector2

from game.behaviors.advanced_helpers import normalized, smoothing_factor
from game.behaviors.behavior import Behavior
from game.components.data_components import FollowComponent, MovementComponent, TransformComponent
from game.ecs.entity import Entity


class FollowBehavior(Behavior):
    def __init__(self, orbit_radius: float = 72.0, turn_responsiveness: float = 0.14) -> None:
        self.orbit_radius = orbit_radius
        self.turn_responsiveness = turn_responsiveness
        self._orbit_clockwise = random.choice((True, False))

    def update(self, entity: Entity, world: "GameWorld", dt: float) -> None:
        player = world.player
        if player is None:
            return
        transform = entity.get_component(TransformComponent)
        movement = entity.get_component(MovementComponent)
        follow = entity.get_component(FollowComponent)
        player_transform = player.get_component(TransformComponent)
        if transform is None or movement is None or follow is None or player_transform is None:
            return

        to_player = player_transform.position - transform.position
        distance = to_player.length()
        if distance <= 0:
            movement.input_direction = Vector2()
            movement.max_speed = follow.speed
            return

        chase_direction = normalized(to_player)
        if distance < self.orbit_radius:
            tangent = Vector2(-chase_direction.y, chase_direction.x)
            if not self._orbit_clockwise:
                tangent *= -1
            close_ratio = 1.0 - (distance / max(1.0, self.orbit_radius))
            pull_out = -chase_direction
            desired_direction = (tangent * (0.65 + close_ratio * 0.35)) + (pull_out * (0.35 + close_ratio * 0.45))
        else:
            desired_direction = chase_direction

        blend = smoothing_factor(self.turn_responsiveness, dt)
        current_direction = normalized(movement.input_direction, desired_direction)
        movement.input_direction = normalized(current_direction.lerp(desired_direction, blend), desired_direction)
        movement.max_speed = follow.speed


from game.core.world import GameWorld
