from __future__ import annotations

from pygame import Vector2

from game.behaviors.advanced_helpers import smoothing_factor
from game.behaviors.behavior import Behavior
from game.components.data_components import MovementComponent, SniperComponent, TransformComponent
from game.config import ENEMY_SNIPER_BULLET_COLOR
from game.ecs.entity import Entity


class SniperMinibossBehavior(Behavior):
    AIM_TRACKING_RESPONSIVENESS = 0.2

    def update(self, entity: Entity, world: "GameWorld", dt: float) -> None:
        player = world.player
        if player is None:
            return

        transform = entity.get_component(TransformComponent)
        movement = entity.get_component(MovementComponent)
        sniper = entity.get_component(SniperComponent)
        player_transform = player.get_component(TransformComponent)
        if transform is None or movement is None or sniper is None or player_transform is None:
            return

        movement.velocity.update(0.0, 0.0)
        movement.input_direction = Vector2()
        movement.max_speed = 0.0

        sniper.shot_timer += dt
        if sniper.state == "aiming":
            target_position = Vector2(player_transform.position)
            blend = smoothing_factor(self.AIM_TRACKING_RESPONSIVENESS, dt)
            sniper.aim_target = sniper.aim_target.lerp(target_position, blend)
            if sniper.shot_timer >= 1.15:
                sniper.state = "shooting"
                sniper.shot_timer = 0.0
            return

        direction = sniper.aim_target - transform.position
        world.spawn_enemy_bullet(
            transform.position,
            direction,
            speed=430.0,
            radius=9.0,
            color=ENEMY_SNIPER_BULLET_COLOR,
        )
        sniper.state = "aiming"
        sniper.shot_timer = 0.0


from game.core.world import GameWorld
