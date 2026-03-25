from __future__ import annotations

from pygame import Vector2

from game.behaviors.advanced_helpers import normalized, smoothing_factor
from game.behaviors.behavior import Behavior
from game.components.data_components import MovementComponent, ShootComponent, TransformComponent
from game.ecs.entity import Entity


class LaserShooterBehavior(Behavior):
    def __init__(self) -> None:
        self._burst_count: dict[int, int] = {}

    def update(self, entity: Entity, world: "GameWorld", dt: float) -> None:
        player = world.player
        if player is None:
            return

        shoot = entity.get_component(ShootComponent)
        movement = entity.get_component(MovementComponent)
        transform = entity.get_component(TransformComponent)
        player_transform = player.get_component(TransformComponent)
        if shoot is None or movement is None or transform is None or player_transform is None:
            return

        to_player = player_transform.position - transform.position
        distance = to_player.length()
        target_direction = normalized(to_player, shoot.target_direction)
        shoot.target_direction = normalized(
            shoot.target_direction.lerp(target_direction, smoothing_factor(0.26, dt)),
            target_direction,
        )

        # Strafing keeps laser shooters mobile and less static.
        tangent = Vector2(-target_direction.y, target_direction.x)
        strafe_sign = 1.0 if entity.id % 2 == 0 else -1.0
        desired_distance = 220.0
        radial = max(-0.55, min(0.55, (distance - desired_distance) / desired_distance))
        movement.input_direction = normalized((tangent * strafe_sign * 0.8) + (target_direction * radial), tangent)
        movement.max_speed = 150.0

        shoot.cooldown_left -= dt
        if shoot.cooldown_left > 0.0:
            return

        burst_count = self._burst_count.get(entity.id, 0)
        spread = (-5.0, 0.0, 5.0) if burst_count % 2 == 1 else (0.0,)
        for offset in spread:
            world.spawn_enemy_bullet(
                transform.position,
                shoot.target_direction.rotate(offset),
                speed=shoot.bullet_speed,
                radius=shoot.bullet_radius,
                color=shoot.bullet_color,
            )

        burst_count += 1
        if burst_count >= 4:
            burst_count = 0
            shoot.cooldown_left = shoot.cooldown * 1.7
        else:
            shoot.cooldown_left = shoot.cooldown * 0.7
        self._burst_count[entity.id] = burst_count


from game.core.world import GameWorld
