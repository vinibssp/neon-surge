from __future__ import annotations

from pygame import Vector2

from game.behaviors.advanced_helpers import normalized
from game.behaviors.behavior import Behavior
from game.components.data_components import MovementComponent, TransformComponent, TurretComponent
from game.ecs.entity import Entity


class FlamethrowerBehavior(Behavior):
    def __init__(self) -> None:
        self._breath_time_left: dict[int, float] = {}
        self._reposition_time_left: dict[int, float] = {}

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
        forward = normalized(to_player, turret.shot_direction)
        turret.shot_direction = forward

        entity_id = entity.id
        breath_time_left = self._breath_time_left.get(entity_id, 1.1)
        reposition_time_left = self._reposition_time_left.get(entity_id, 0.0)

        if breath_time_left <= 0.0:
            reposition_time_left -= dt
            movement.input_direction = forward.rotate(90.0 if entity_id % 2 == 0 else -90.0)
            movement.max_speed = 160.0
            if reposition_time_left <= 0.0:
                breath_time_left = 1.1
                reposition_time_left = 0.8
            self._breath_time_left[entity_id] = breath_time_left
            self._reposition_time_left[entity_id] = reposition_time_left
            return

        desired_distance = 170.0
        if distance > desired_distance + 40.0:
            movement.input_direction = forward
        elif distance < desired_distance - 40.0:
            movement.input_direction = -forward
        else:
            movement.input_direction = Vector2()
        movement.max_speed = 135.0

        turret.shot_timer += dt
        breath_time_left -= dt
        if turret.shot_timer < 0.12:
            self._breath_time_left[entity_id] = breath_time_left
            self._reposition_time_left[entity_id] = reposition_time_left
            return

        turret.shot_timer = 0.0
        cone = (-24.0, -14.0, -6.0, 6.0, 14.0, 24.0)
        for angle in cone:
            world.spawn_enemy_bullet(
                transform.position,
                forward.rotate(angle),
                speed=220.0,
                radius=5.0,
                color=(255, 132, 62),
            )
        turret.shot_angles = tuple(float(forward.rotate(angle).as_polar()[1]) for angle in cone)
        self._breath_time_left[entity_id] = breath_time_left
        self._reposition_time_left[entity_id] = reposition_time_left


from game.core.world import GameWorld
