from __future__ import annotations

from pygame import Vector2

from game.behaviors.advanced_helpers import normalized, predict_intercept_position, smoothing_factor
from game.behaviors.behavior import Behavior
from game.components.data_components import MovementComponent, ShootComponent, TransformComponent
from game.ecs.entity import Entity


class ShootBehavior(Behavior):
    MIN_AIM_TIME = 0.25
    MAX_AIM_EXTENSION_FACTOR = 1.6
    TRACKING_RESPONSIVENESS = 0.22

    def update(self, entity: Entity, world: "GameWorld", dt: float) -> None:
        player = world.player
        if player is None:
            return
        shoot = entity.get_component(ShootComponent)
        transform = entity.get_component(TransformComponent)
        player_transform = player.get_component(TransformComponent)
        player_movement = player.get_component(MovementComponent)
        if shoot is None or transform is None or player_transform is None:
            return

        player_velocity = Vector2() if player_movement is None else Vector2(player_movement.velocity)
        target_position = predict_intercept_position(
            origin=transform.position,
            target_position=player_transform.position,
            target_velocity=player_velocity,
            projectile_speed=shoot.bullet_speed,
            max_lead_time=0.75,
        )
        target_direction = normalized(target_position - transform.position, shoot.target_direction)
        distance_to_player = (player_transform.position - transform.position).length()
        player_speed = player_velocity.length()
        distance_term = 0.3 + (distance_to_player / 560.0)
        speed_term = min(0.35, player_speed / 950.0)
        dynamic_aim_time = max(self.MIN_AIM_TIME, min(shoot.aim_time, distance_term + speed_term))

        if shoot.is_aiming:
            aim_blend = smoothing_factor(self.TRACKING_RESPONSIVENESS, dt)
            tracked = shoot.target_direction.lerp(target_direction, aim_blend)
            shoot.target_direction = normalized(tracked, target_direction)

            angle_error = abs(shoot.target_direction.angle_to(target_direction))
            if angle_error > 35.0:
                shoot.aim_left += min(0.18, dt * 0.9)
                max_aim_time = dynamic_aim_time * self.MAX_AIM_EXTENSION_FACTOR
                shoot.aim_left = min(shoot.aim_left, max_aim_time)

            shoot.aim_left -= dt
            if shoot.aim_left <= 0:
                world.spawn_enemy_bullet(
                    transform.position,
                    shoot.target_direction,
                    shoot.bullet_speed,
                    shoot.bullet_radius,
                    color=shoot.bullet_color,
                )
                shoot.is_aiming = False
                shoot.cooldown_left = shoot.cooldown
            return

        shoot.cooldown_left -= dt
        if shoot.cooldown_left > 0:
            return
        shoot.is_aiming = True
        shoot.target_direction = target_direction
        shoot.aim_left = dynamic_aim_time


from game.core.world import GameWorld
