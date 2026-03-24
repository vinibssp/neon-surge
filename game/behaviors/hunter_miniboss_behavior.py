from __future__ import annotations

from game.behaviors.advanced_helpers import normalized
from game.behaviors.behavior import Behavior
from game.components.data_components import MovementComponent, TransformComponent, TurretComponent
from game.config import ENEMY_HUNTER_BULLET_COLOR
from game.ecs.entity import Entity


class HunterMinibossBehavior(Behavior):
    def update(self, entity: Entity, world: "GameWorld", dt: float) -> None:
        player = world.player
        if player is None:
            return

        transform = entity.get_component(TransformComponent)
        movement = entity.get_component(MovementComponent)
        turret = entity.get_component(TurretComponent)
        player_transform = player.get_component(TransformComponent)
        if transform is None or movement is None or turret is None or player_transform is None:
            return

        to_player = player_transform.position - transform.position
        desired_velocity = normalized(to_player) * (movement.max_speed * 1.08)
        smoothing = max(0.0, min(1.0, 0.08 * 60.0 * dt))
        movement.velocity = movement.velocity.lerp(desired_velocity, smoothing)
        movement.input_direction = normalized(movement.velocity)
        movement.max_speed = max(1.0, movement.velocity.length())

        turret.shot_timer += dt
        if turret.shot_timer < 1.1:
            return
        turret.shot_timer = 0.0

        base_direction = normalized(to_player)
        for offset in (-14.0, 0.0, 14.0):
            world.spawn_enemy_bullet(
                transform.position,
                base_direction.rotate(offset),
                speed=305.0,
                radius=8.0,
                color=ENEMY_HUNTER_BULLET_COLOR,
            )


from game.core.world import GameWorld
