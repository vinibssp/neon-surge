from __future__ import annotations

from pygame import Vector2

from game.behaviors.behavior import Behavior
from game.components.data_components import MovementComponent, SniperComponent, TransformComponent
from game.config import ENEMY_SNIPER_BULLET_COLOR
from game.ecs.entity import Entity


class SniperMinibossBehavior(Behavior):
    def __init__(self) -> None:
        self._double_shot_toggle: dict[int, bool] = {}

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
            sniper.aim_target = Vector2(player_transform.position)
            if sniper.shot_timer >= 1.15:
                sniper.state = "shooting"
                sniper.shot_timer = 0.0
            return

        sniper.aim_target = Vector2(player_transform.position)
        direction = sniper.aim_target - transform.position
        base_direction = direction.normalize() if direction.length_squared() > 0 else Vector2(1, 0)
        double_shot = self._double_shot_toggle.get(entity.id, False)
        self._double_shot_toggle[entity.id] = not double_shot
        spreads = (-4.0, 4.0) if double_shot else (0.0,)
        for spread in spreads:
            world.spawn_enemy_bullet(
                transform.position,
                base_direction.rotate(spread),
                speed=430.0,
                radius=9.0,
                color=ENEMY_SNIPER_BULLET_COLOR,
            )
        sniper.state = "aiming"
        sniper.shot_timer = 0.0


from game.core.world import GameWorld
