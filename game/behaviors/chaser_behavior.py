from __future__ import annotations

from pygame import Vector2

from game.behaviors.advanced_helpers import normalized
from game.behaviors.behavior import Behavior
from game.components.data_components import MovementComponent, TransformComponent
from game.ecs.entity import Entity


class ChaserBehavior(Behavior):
    def __init__(self, prediction_factor: float = 12.0, speed_multiplier: float = 1.0, lerp_speed: float = 0.08) -> None:
        self.prediction_factor = prediction_factor
        self.speed_multiplier = speed_multiplier
        self.lerp_speed = lerp_speed

    def update(self, entity: Entity, world: "GameWorld", dt: float) -> None:
        player = world.player
        if player is None:
            return

        transform = entity.get_component(TransformComponent)
        movement = entity.get_component(MovementComponent)
        player_transform = player.get_component(TransformComponent)
        player_movement = player.get_component(MovementComponent)
        if transform is None or movement is None or player_transform is None:
            return

        player_velocity = Vector2() if player_movement is None else Vector2(player_movement.velocity)
        predicted_position = player_transform.position + (player_velocity * self.prediction_factor)
        target_vector = predicted_position - transform.position

        desired_velocity = normalized(target_vector) * (movement.max_speed * self.speed_multiplier)
        smoothing = max(0.0, min(1.0, self.lerp_speed * 60.0 * dt))
        movement.velocity = movement.velocity.lerp(desired_velocity, smoothing)
        movement.input_direction = normalized(movement.velocity)
        movement.max_speed = max(1.0, movement.velocity.length())


from game.core.world import GameWorld
