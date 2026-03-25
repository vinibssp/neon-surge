from __future__ import annotations

from pygame import Vector2

from game.behaviors.advanced_helpers import normalized
from game.behaviors.behavior import Behavior
from game.components.data_components import MovementComponent, TransformComponent, TurretComponent
from game.ecs.entity import Entity


class ShotgunAmbusherBehavior(Behavior):
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

        if distance > 190.0:
            movement.input_direction = forward
        elif distance < 130.0:
            movement.input_direction = -forward
        else:
            movement.input_direction = Vector2()
        movement.max_speed = 145.0

        turret.shot_timer += dt
        if turret.shot_timer < 1.4:
            return

        turret.shot_timer = 0.0
        spread_angles = (-26.0, -13.0, 0.0, 13.0, 26.0)
        fired_angles: list[float] = []
        for offset in spread_angles:
            direction = forward.rotate(offset)
            world.spawn_enemy_bullet(
                transform.position,
                direction,
                speed=255.0,
                radius=6.0,
                color=(244, 126, 74),
            )
            fired_angles.append(float(direction.as_polar()[1]))

        turret.is_in_burst = True
        turret.shot_direction = forward
        turret.shot_angles = tuple(fired_angles)


from game.core.world import GameWorld
