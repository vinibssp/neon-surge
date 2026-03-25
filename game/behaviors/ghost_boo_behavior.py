from __future__ import annotations

from pygame import Vector2

from game.behaviors.advanced_helpers import normalized
from game.behaviors.behavior import Behavior
from game.components.data_components import GhostComponent, MovementComponent, TransformComponent
from game.ecs.entity import Entity


class GhostBooBehavior(Behavior):
    def __init__(self) -> None:
        self._visible_cooldown: dict[int, float] = {}

    def update(self, entity: Entity, world: "GameWorld", dt: float) -> None:
        player = world.player
        if player is None:
            return

        transform = entity.get_component(TransformComponent)
        movement = entity.get_component(MovementComponent)
        ghost = entity.get_component(GhostComponent)
        player_transform = player.get_component(TransformComponent)
        if transform is None or movement is None or ghost is None or player_transform is None:
            return

        ghost.timer += dt
        to_player = player_transform.position - transform.position
        distance = to_player.length()
        visible_cd = self._visible_cooldown.get(entity.id, 0.0)
        visible_cd = max(0.0, visible_cd - dt)
        self._visible_cooldown[entity.id] = visible_cd

        if not ghost.is_visible:
            movement.input_direction = normalized(to_player, movement.input_direction)
            movement.max_speed = ghost.hidden_speed
            if distance <= ghost.reveal_distance and ghost.timer >= ghost.hidden_duration and visible_cd <= 0.0:
                ghost.is_visible = True
                ghost.timer = 0.0
                movement.input_direction = Vector2()
                movement.velocity.update(0.0, 0.0)
                movement.max_speed = 0.0
            return

        movement.input_direction = Vector2()
        movement.velocity.update(0.0, 0.0)
        movement.max_speed = 0.0
        if ghost.timer >= ghost.visible_duration:
            ghost.is_visible = False
            ghost.timer = 0.0
            self._visible_cooldown[entity.id] = 0.55


from game.core.world import GameWorld
