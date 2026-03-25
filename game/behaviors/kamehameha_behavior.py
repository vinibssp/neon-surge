from __future__ import annotations

import math

from pygame import Vector2

from game.behaviors.advanced_helpers import normalized
from game.behaviors.behavior import Behavior
from game.components.data_components import KamehamehaComponent, MovementComponent, TransformComponent
from game.ecs.entity import Entity


class KamehamehaBehavior(Behavior):
    def update(self, entity: Entity, world: "GameWorld", dt: float) -> None:
        player = world.player
        if player is None:
            return

        transform = entity.get_component(TransformComponent)
        movement = entity.get_component(MovementComponent)
        kame = entity.get_component(KamehamehaComponent)
        player_transform = player.get_component(TransformComponent)
        if transform is None or movement is None or kame is None or player_transform is None:
            return

        movement.velocity.update(0.0, 0.0)
        movement.input_direction = Vector2()
        movement.max_speed = 0.0

        to_player = player_transform.position - transform.position
        if kame.state == "cooldown":
            retreat = normalized(-to_player, kame.locked_direction)
            movement.input_direction = retreat
            movement.max_speed = 95.0
            kame.timer += dt
            if kame.timer >= kame.cooldown_duration:
                kame.state = "charging"
                kame.timer = 0.0
            return

        if kame.state == "charging":
            kame.locked_direction = normalized(to_player, kame.locked_direction)
            # Slow drift while charging keeps telegraph readable but not static.
            movement.input_direction = kame.locked_direction.rotate(90.0 if entity.id % 2 == 0 else -90.0)
            movement.max_speed = 60.0
            kame.timer += dt
            if kame.timer >= kame.charge_duration:
                kame.state = "firing"
                kame.timer = 0.0
                kame.tick_timer = 0.0
            return

        kame.timer += dt
        kame.tick_timer += dt
        sweep = math.sin(kame.timer * 5.0) * 7.0
        while kame.tick_timer >= kame.fire_tick:
            kame.tick_timer -= kame.fire_tick
            forward = normalized(kame.locked_direction).rotate(sweep)
            side = Vector2(-forward.y, forward.x)
            for lateral in (-7.0, 0.0, 7.0):
                origin = transform.position + side * lateral
                world.spawn_enemy_bullet(
                    origin,
                    forward,
                    speed=430.0,
                    radius=6.0,
                    color=kame.beam_color,
                )

        if kame.timer >= kame.fire_duration:
            kame.state = "cooldown"
            kame.timer = 0.0


from game.core.world import GameWorld
