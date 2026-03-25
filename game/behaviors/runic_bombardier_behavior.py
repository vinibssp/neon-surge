from __future__ import annotations

from pygame import Vector2

from game.behaviors.advanced_helpers import normalized
from game.behaviors.behavior import Behavior
from game.components.data_components import MovementComponent, TransformComponent, TurretComponent
from game.ecs.entity import Entity


class RunicBombardierBehavior(Behavior):
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
        distance = to_player.length()
        forward = normalized(to_player)
        tangent = Vector2(-forward.y, forward.x)

        if distance < 230.0:
            movement.input_direction = normalized((-forward * 0.8) + (tangent * 0.5), -forward)
        else:
            movement.input_direction = normalized((forward * 0.25) + (tangent * 0.75), tangent)
        movement.max_speed = 145.0

        turret.shot_timer += dt
        if turret.shot_timer < 1.85:
            return
        turret.shot_timer = 0.0

        base_angle = forward.as_polar()[1]
        fan_angles = (base_angle - 18.0, base_angle, base_angle + 18.0)
        for angle in fan_angles:
            world.spawn_enemy_bullet(
                transform.position,
                Vector2(1, 0).rotate(angle),
                speed=235.0,
                radius=7.0,
                color=(250, 184, 74),
            )

        radial_angles = tuple(float(index * 45.0) for index in range(8))
        for angle in radial_angles:
            world.spawn_enemy_bullet(
                transform.position,
                Vector2(1, 0).rotate(angle),
                speed=155.0,
                radius=5.0,
                color=(250, 228, 84),
            )

        turret.is_in_burst = True
        turret.shot_direction = forward
        turret.shot_angles = radial_angles


from game.core.world import GameWorld
