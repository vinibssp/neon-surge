from __future__ import annotations

import math

from pygame import Vector2

from game.behaviors.advanced_helpers import normalized
from game.behaviors.behavior import Behavior
from game.components.data_components import (
    MovementComponent,
    OrbitComponent,
    TransformComponent,
    TurretComponent,
)
from game.config import ENEMY_SHIELD_BULLET_COLOR
from game.ecs.entity import Entity


class ShieldMinibossBehavior(Behavior):
    def update(self, entity: Entity, world: "GameWorld", dt: float) -> None:
        player = world.player
        if player is None:
            return

        transform = entity.get_component(TransformComponent)
        movement = entity.get_component(MovementComponent)
        turret = entity.get_component(TurretComponent)
        orbit = entity.get_component(OrbitComponent)
        player_transform = player.get_component(TransformComponent)
        if (
            transform is None
            or movement is None
            or turret is None
            or orbit is None
            or player_transform is None
        ):
            return

        turret.shot_timer += dt
        turret.burst_timer += dt
        orbit.angle += dt * orbit.angular_speed

        orbit_target = player_transform.position + Vector2(math.cos(orbit.angle), math.sin(orbit.angle)) * orbit.radius
        to_target = orbit_target - transform.position
        desired_velocity = normalized(to_target) * (movement.max_speed * 1.2)
        smoothing = max(0.0, min(1.0, 0.14 * 60.0 * dt))
        movement.velocity = movement.velocity.lerp(desired_velocity, smoothing)
        movement.input_direction = normalized(movement.velocity)
        movement.max_speed = max(1.0, movement.velocity.length())

        if turret.shot_timer < 1.45:
            return
        turret.shot_timer = 0.0

        world.spawn_enemy_bullet(
            transform.position,
            normalized(player_transform.position - transform.position),
            speed=280.0,
            radius=7.0,
            color=ENEMY_SHIELD_BULLET_COLOR,
        )


from game.core.world import GameWorld
