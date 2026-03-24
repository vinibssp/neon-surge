from __future__ import annotations

from pygame import Vector2

from game.behaviors.advanced_helpers import normalized
from game.behaviors.behavior import Behavior
from game.components.data_components import ChargeComponent, MovementComponent, TransformComponent
from game.ecs.entity import Entity


class ChargeBehavior(Behavior):
    def update(self, entity: Entity, world: "GameWorld", dt: float) -> None:
        player = world.player
        if player is None:
            return

        transform = entity.get_component(TransformComponent)
        movement = entity.get_component(MovementComponent)
        charge = entity.get_component(ChargeComponent)
        player_transform = player.get_component(TransformComponent)
        if transform is None or movement is None or charge is None or player_transform is None:
            return

        if charge.cruise_speed <= 0.0:
            charge.cruise_speed = max(1.0, movement.max_speed)
        if charge.dash_speed <= 0.0:
            charge.dash_speed = max(220.0, charge.cruise_speed * 4.0)

        charge.timer += dt
        if charge.state == "waiting":
            movement.velocity *= 0.9
            movement.input_direction = Vector2()
            movement.max_speed = charge.cruise_speed
            if charge.timer > 1.2:
                charge.state = "aiming"
                charge.timer = 0.0
                charge.is_target_locked = False
            return

        if charge.state == "aiming":
            if charge.timer < 0.5:
                charge.locked_target = Vector2(player_transform.position)
            else:
                charge.is_target_locked = True

            if charge.timer > 0.9:
                dash_direction = charge.locked_target - transform.position
                dash_velocity = normalized(dash_direction) * charge.dash_speed
                movement.velocity = dash_velocity
                movement.input_direction = normalized(dash_velocity)
                movement.max_speed = dash_velocity.length()
                charge.state = "attacking"
                charge.timer = 0.0
            return

        if charge.state == "attacking" and charge.timer > 1.4:
            charge.state = "waiting"
            charge.timer = 0.0
            charge.is_target_locked = False
            movement.velocity *= 0.2
            movement.input_direction = normalized(movement.velocity)
            movement.max_speed = charge.cruise_speed


from game.core.world import GameWorld
