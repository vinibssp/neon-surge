from __future__ import annotations

from pygame import Vector2

from game.behaviors.behavior import Behavior
from game.components.data_components import MovementComponent, TransformComponent, TurretComponent
from game.ecs.entity import Entity


class LaserMatrixMinibossBehavior(Behavior):
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

        movement.velocity.update(0.0, 0.0)
        movement.input_direction = Vector2()
        movement.max_speed = 0.0

        turret.burst_timer += dt
        turret.shot_timer += dt

        interval = 0.18 if int(turret.burst_timer // 2.2) % 2 else 0.24
        while turret.shot_timer >= interval:
            turret.shot_timer -= interval
            turret.spiral_angle = (turret.spiral_angle + 12.0) % 360.0
            base = turret.spiral_angle
            angles = (base, base + 90.0, base + 180.0, base + 270.0)
            for angle in angles:
                world.spawn_enemy_bullet(
                    transform.position,
                    Vector2(1, 0).rotate(angle),
                    speed=335.0,
                    radius=7.0,
                    color=(255, 78, 108),
                )
            turret.shot_direction = Vector2(1, 0).rotate(base)
            turret.shot_angles = tuple(float(a) for a in angles)

        if int(turret.burst_timer // 3.0) % 2 == 0:
            return

        aim_dir = player_transform.position - transform.position
        if aim_dir.length_squared() <= 0:
            return
        world.spawn_enemy_bullet(
            transform.position,
            aim_dir,
            speed=420.0,
            radius=8.0,
            color=(255, 122, 138),
        )


from game.core.world import GameWorld
