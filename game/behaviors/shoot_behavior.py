from __future__ import annotations

from game.behaviors.advanced_helpers import normalized, smoothing_factor
from game.behaviors.behavior import Behavior
from game.components.data_components import ShootComponent, TransformComponent
from game.ecs.entity import Entity


class ShootBehavior(Behavior):
    MIN_AIM_TIME = 0.25
    MAX_AIM_EXTENSION_FACTOR = 1.6
    AIM_TRACKING_RESPONSIVENESS = 0.22
    IDLE_TRACKING_RESPONSIVENESS = 0.14

    def update(self, entity: Entity, world: "GameWorld", dt: float) -> None:
        player = world.player
        if player is None:
            return
        shoot = entity.get_component(ShootComponent)
        transform = entity.get_component(TransformComponent)
        player_transform = player.get_component(TransformComponent)
        if shoot is None or transform is None or player_transform is None:
            return

        target_direction = normalized(player_transform.position - transform.position, shoot.target_direction)
        distance_to_player = (player_transform.position - transform.position).length()
        distance_term = 0.3 + (distance_to_player / 560.0)
        dynamic_aim_time = max(self.MIN_AIM_TIME, min(shoot.aim_time, distance_term))
        idle_blend = smoothing_factor(self.IDLE_TRACKING_RESPONSIVENESS, dt)
        idle_tracked = shoot.target_direction.lerp(target_direction, idle_blend)
        shoot.target_direction = normalized(idle_tracked, target_direction)

        if shoot.is_aiming:
            aim_blend = smoothing_factor(self.AIM_TRACKING_RESPONSIVENESS, dt)
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
        shoot.aim_left = dynamic_aim_time


from game.core.world import GameWorld
