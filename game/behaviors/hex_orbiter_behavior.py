from __future__ import annotations

from pygame import Vector2

from game.behaviors.advanced_helpers import normalized
from game.behaviors.behavior import Behavior
from game.components.data_components import MovementComponent, TransformComponent, TurretComponent
from game.ecs.entity import Entity


class HexOrbiterBehavior(Behavior):
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

        clockwise = -1.0 if entity.id % 2 == 0 else 1.0
        to_player = player_transform.position - transform.position
        distance = to_player.length()
        forward = normalized(to_player)
        tangent = Vector2(-forward.y, forward.x) * clockwise

        desired = 180.0
        radial = max(-0.6, min(0.6, (distance - desired) / desired))
        move_dir = (tangent * 0.8) + (forward * radial)
        movement.input_direction = normalized(move_dir, tangent)
        movement.max_speed = 165.0

        turret.shot_timer += dt
        if turret.shot_timer < 1.0:
            return

        turret.shot_timer = 0.0
        turret.spiral_angle = (turret.spiral_angle + 24.0) % 360.0
        angles = [turret.spiral_angle + index * 60.0 for index in range(6)]
        for angle in angles:
            direction = Vector2(1, 0).rotate(angle)
            world.spawn_enemy_bullet(
                transform.position,
                direction,
                speed=300.0,
                radius=6.0,
                color=(116, 228, 255),
            )

        turret.is_in_burst = True
        turret.shot_direction = Vector2(1, 0).rotate(turret.spiral_angle)
        turret.shot_angles = tuple(float(angle) for angle in angles)


from game.core.world import GameWorld
