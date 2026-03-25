from __future__ import annotations

from pygame import Vector2

from game.behaviors.advanced_helpers import normalized
from game.behaviors.behavior import Behavior
from game.components.data_components import ChargeComponent, MovementComponent, TransformComponent
from game.ecs.entity import Entity


class ShadowPouncerBehavior(Behavior):
    def update(self, entity: Entity, world: "GameWorld", dt: float) -> None:
        player = world.player
        if player is None:
            return

        transform = entity.get_component(TransformComponent)
        movement = entity.get_component(MovementComponent)
        charge = entity.get_component(ChargeComponent)
        player_transform = player.get_component(TransformComponent)
        if transform is None or movement is None or charge is None or player_transform is None:
            return

        if charge.state not in {"stalking", "pouncing", "recover"}:
            charge.state = "stalking"
            charge.timer = 1.2

        to_player = player_transform.position - transform.position
        forward = normalized(to_player)

        if charge.state == "stalking":
            movement.max_speed = 170.0
            movement.input_direction = forward
            charge.timer -= dt
            if charge.timer > 0.0:
                return

            charge.state = "pouncing"
            charge.timer = 0.30
            charge.locked_target = Vector2(forward)
            for spread in (-10.0, 0.0, 10.0):
                world.spawn_enemy_bullet(
                    transform.position,
                    charge.locked_target.rotate(spread),
                    speed=290.0,
                    radius=5.0,
                    color=(188, 82, 240),
                )
            return

        if charge.state == "pouncing":
            movement.input_direction = Vector2(charge.locked_target)
            movement.max_speed = 420.0
            movement.velocity = movement.input_direction * movement.max_speed
            charge.timer -= dt
            if charge.timer > 0.0:
                return

            charge.state = "recover"
            charge.timer = 0.72
            movement.input_direction = Vector2()
            movement.velocity.update(0.0, 0.0)
            movement.max_speed = 0.0
            return

        movement.input_direction = Vector2()
        movement.velocity.update(0.0, 0.0)
        movement.max_speed = 0.0
        charge.timer -= dt
        if charge.timer <= 0.0:
            charge.state = "stalking"
            charge.timer = 1.2


from game.core.world import GameWorld
