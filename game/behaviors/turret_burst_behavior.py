from __future__ import annotations

from pygame import Vector2

from game.behaviors.advanced_helpers import shoot_radial
from game.behaviors.behavior import Behavior
from game.components.data_components import MovementComponent, TransformComponent, TurretComponent
from game.config import ENEMY_TURRET_BULLET_COLOR
from game.ecs.entity import Entity


class TurretBurstBehavior(Behavior):
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
        if turret.shot_pattern == 0:
            turret.is_in_burst = True
            interval = 0.64
            while turret.shot_timer >= interval:
                turret.shot_timer -= interval
                shoot_radial(
                    world,
                    transform.position,
                    speed=310.0,
                    radius=8.0,
                    step_degrees=45,
                    color=ENEMY_TURRET_BULLET_COLOR,
                )
                turret.shot_direction = Vector2(1, 0)
                turret.shot_angles = tuple(float(angle) for angle in range(0, 360, 45))
            return

        turret.is_in_burst = False
        interval = 0.26
        while turret.shot_timer >= interval:
            turret.shot_timer -= interval
            phase_offset = 45.0 if int(turret.burst_timer * 8.0) % 2 else 0.0
            shot_angles = (
                phase_offset,
                phase_offset + 90.0,
                phase_offset + 180.0,
                phase_offset + 270.0,
            )
            for angle in shot_angles:
                direction = Vector2(1, 0).rotate(angle)
                world.spawn_enemy_bullet(
                    transform.position,
                    direction,
                    speed=320.0,
                    radius=8.0,
                    color=ENEMY_TURRET_BULLET_COLOR,
                )
            turret.shot_direction = Vector2(1, 0).rotate(phase_offset)
            turret.shot_angles = tuple(shot_angles)


from game.core.world import GameWorld
