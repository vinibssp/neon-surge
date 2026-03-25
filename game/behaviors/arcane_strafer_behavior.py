from __future__ import annotations

from pygame import Vector2

from game.behaviors.advanced_helpers import normalized, smoothing_factor
from game.behaviors.behavior import Behavior
from game.components.data_components import MovementComponent, ShootComponent, TransformComponent
from game.ecs.entity import Entity


class ArcaneStraferBehavior(Behavior):
    def __init__(self) -> None:
        self._strafe_dir: dict[int, float] = {}
        self._flip_time_left: dict[int, float] = {}

    def update(self, entity: Entity, world: "GameWorld", dt: float) -> None:
        player = world.player
        if player is None:
            return

        transform = entity.get_component(TransformComponent)
        movement = entity.get_component(MovementComponent)
        shoot = entity.get_component(ShootComponent)
        player_transform = player.get_component(TransformComponent)
        if transform is None or movement is None or shoot is None or player_transform is None:
            return

        entity_id = entity.id
        strafe_dir = self._strafe_dir.get(entity_id, 1.0)
        flip_time_left = self._flip_time_left.get(entity_id, 2.1)
        flip_time_left -= dt
        if flip_time_left <= 0.0:
            strafe_dir *= -1.0
            flip_time_left = 2.1
        self._strafe_dir[entity_id] = strafe_dir
        self._flip_time_left[entity_id] = flip_time_left

        to_player = player_transform.position - transform.position
        distance = to_player.length()
        forward = normalized(to_player)
        tangent = Vector2(-forward.y, forward.x) * strafe_dir

        desired_distance = 220.0
        radial_weight = (distance - desired_distance) / max(1.0, desired_distance)
        radial_weight = max(-0.65, min(0.65, radial_weight))

        move_dir = (tangent * 0.86) + (forward * radial_weight)
        movement.input_direction = normalized(move_dir, tangent)
        movement.max_speed = 190.0

        target_direction = normalized(to_player, shoot.target_direction)
        blend = smoothing_factor(0.22, dt)
        shoot.target_direction = normalized(shoot.target_direction.lerp(target_direction, blend), target_direction)

        shoot.cooldown_left -= dt
        if shoot.cooldown_left > 0.0:
            return

        world.spawn_enemy_bullet(
            transform.position,
            shoot.target_direction,
            speed=shoot.bullet_speed,
            radius=shoot.bullet_radius,
            color=shoot.bullet_color,
        )
        shoot.cooldown_left = shoot.cooldown


from game.core.world import GameWorld
