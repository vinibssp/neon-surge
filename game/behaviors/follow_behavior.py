from __future__ import annotations

from pygame import Vector2

from game.behaviors.behavior import Behavior
from game.components.data_components import FollowComponent, MovementComponent, TransformComponent
from game.ecs.entity import Entity


class FollowBehavior(Behavior):
    def update(self, entity: Entity, world: "GameWorld", dt: float) -> None:
        player = world.player
        if player is None:
            return
        transform = entity.get_component(TransformComponent)
        movement = entity.get_component(MovementComponent)
        follow = entity.get_component(FollowComponent)
        player_transform = player.get_component(TransformComponent)
        if transform is None or movement is None or follow is None or player_transform is None:
            return
        direction = player_transform.position - transform.position
        movement.input_direction = direction.normalize() if direction.length_squared() > 0 else Vector2()
        movement.max_speed = follow.speed


from game.core.world import GameWorld
