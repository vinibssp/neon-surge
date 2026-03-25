from __future__ import annotations

from pygame import Vector2

from game.behaviors.behavior import Behavior
from game.components.data_components import MovementComponent, TransformComponent, TurretComponent
from game.config import ENEMY_TURRET_BULLET_COLOR
from game.ecs.entity import Entity


class SpiralTurretBehavior(Behavior):
    def update(self, entity: Entity, world: "GameWorld", dt: float) -> None:
        transform = entity.get_component(TransformComponent)
        movement = entity.get_component(MovementComponent)
        turret = entity.get_component(TurretComponent)
        if transform is None or movement is None or turret is None:
            return

        movement.velocity.update(0.0, 0.0)
        movement.input_direction = Vector2()
        movement.max_speed = 0.0

        turret.burst_timer += dt
        turret.shot_timer += dt
        fast_phase = int(turret.burst_timer // 2.2) % 2 == 1
        interval = 0.10 if fast_phase else 0.14
        angle_step = 22.0 if fast_phase else 16.0
        while turret.shot_timer >= interval:
            turret.shot_timer -= interval
            turret.spiral_angle = (turret.spiral_angle + angle_step) % 360.0
            angle_a = turret.spiral_angle
            angle_b = turret.spiral_angle + 180.0
            direction_a = Vector2(1, 0).rotate(angle_a)
            direction_b = Vector2(1, 0).rotate(angle_b)
            world.spawn_enemy_bullet(
                transform.position,
                direction_a,
                speed=330.0,
                radius=9.0,
                color=ENEMY_TURRET_BULLET_COLOR,
            )
            world.spawn_enemy_bullet(
                transform.position,
                direction_b,
                speed=330.0,
                radius=9.0,
                color=ENEMY_TURRET_BULLET_COLOR,
            )
            turret.shot_direction = direction_a
            turret.shot_angles = (angle_a, angle_b)


from game.core.world import GameWorld
