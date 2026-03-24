from __future__ import annotations

from pygame import Vector2

from game.behaviors.behavior import Behavior
from game.components.data_components import ShootComponent, TransformComponent
from game.ecs.entity import Entity


class ShootBehavior(Behavior):
    def update(self, entity: Entity, world: "GameWorld", dt: float) -> None:
        player = world.player
        if player is None:
            return
        shoot = entity.get_component(ShootComponent)
        transform = entity.get_component(TransformComponent)
        player_transform = player.get_component(TransformComponent)
        if shoot is None or transform is None or player_transform is None:
            return

        if shoot.is_aiming:
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

        direction = player_transform.position - transform.position
        shoot.target_direction = direction.normalize() if direction.length_squared() > 0 else Vector2(1, 0)
        shoot.is_aiming = True
        shoot.aim_left = shoot.aim_time


from game.core.world import GameWorld
