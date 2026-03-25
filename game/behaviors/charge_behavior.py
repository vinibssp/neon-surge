from __future__ import annotations

from pygame import Vector2

from game.behaviors.advanced_helpers import normalized, smoothing_factor
from game.behaviors.behavior import Behavior
from game.components.data_components import ChargeComponent, MovementComponent, TransformComponent
from game.ecs.entity import Entity


class ChargeBehavior(Behavior):
    WAIT_DURATION = 0.85
    AIM_DURATION = 0.55
    ATTACK_DURATION = 1.05
    APPROACH_DISTANCE = 180.0
    MIN_DASH_TRIGGER_DISTANCE = 70.0
    MAX_DASH_TRIGGER_DISTANCE = 440.0
    MAX_AIM_OVERHOLD = 0.45

    @staticmethod
    def _apply_steering(movement: MovementComponent, direction: Vector2, target_speed: float, blend: float) -> None:
        current_direction = normalized(movement.input_direction, direction)
        next_direction = normalized(current_direction.lerp(direction, blend), direction)
        movement.input_direction = next_direction
        movement.max_speed = target_speed

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

        to_player = player_transform.position - transform.position
        distance_to_player = to_player.length()
        chase_direction = normalized(to_player)

        charge.timer += dt
        if charge.state == "waiting":
            strafe_sign = 1.0 if entity.id % 2 == 0 else -1.0
            strafe_direction = Vector2(-chase_direction.y, chase_direction.x) * strafe_sign
            if distance_to_player > self.APPROACH_DISTANCE:
                desired_direction = chase_direction
                desired_speed = charge.cruise_speed * 0.82
            else:
                desired_direction = normalized(strafe_direction + (chase_direction * 0.2), chase_direction)
                desired_speed = charge.cruise_speed * 0.68
            self._apply_steering(
                movement,
                direction=desired_direction,
                target_speed=desired_speed,
                blend=smoothing_factor(0.14, dt),
            )
            charge.is_target_locked = False
            if charge.timer >= self.WAIT_DURATION:
                charge.state = "aiming"
                charge.timer = 0.0
            return

        if charge.state == "aiming":
            charge.locked_target = Vector2(player_transform.position)
            charge.is_target_locked = True
            aim_direction = normalized(charge.locked_target - transform.position, chase_direction)
            self._apply_steering(
                movement,
                direction=aim_direction,
                target_speed=charge.cruise_speed * 0.42,
                blend=smoothing_factor(0.2, dt),
            )

            can_dash_now = (
                self.MIN_DASH_TRIGGER_DISTANCE <= distance_to_player <= self.MAX_DASH_TRIGGER_DISTANCE
            )
            aim_expired = charge.timer >= self.AIM_DURATION
            force_dash = charge.timer >= self.AIM_DURATION + self.MAX_AIM_OVERHOLD
            if (aim_expired and can_dash_now) or force_dash:
                dash_velocity = aim_direction * charge.dash_speed
                movement.velocity = dash_velocity
                movement.input_direction = aim_direction
                movement.max_speed = charge.dash_speed
                charge.state = "attacking"
                charge.timer = 0.0
            return

        if charge.state == "attacking":
            movement.input_direction = normalized(movement.velocity, movement.input_direction)
            movement.max_speed = charge.dash_speed
            near_border = (
                transform.position.x < 20.0
                or transform.position.x > world.width - 20.0
                or transform.position.y < 20.0
                or transform.position.y > world.height - 20.0
            )
            if charge.timer >= self.ATTACK_DURATION or near_border:
                charge.state = "waiting"
                charge.timer = 0.0
                charge.is_target_locked = False
                movement.velocity *= 0.25
                movement.input_direction = normalized(movement.velocity, chase_direction)
                movement.max_speed = charge.cruise_speed


from game.core.world import GameWorld
