from __future__ import annotations

import random

from pygame import Vector2

from game.behaviors.advanced_helpers import normalized
from game.behaviors.behavior import Behavior
from game.components.data_components import MovementComponent, StaggeredComponent, TransformComponent
from game.ecs.entity import Entity


class BlinkStrikerBehavior(Behavior):
    POST_BLINK_GRACE = 0.32
    POST_BLINK_MIN_DISTANCE = 86.0

    def __init__(self, blink_interval: float = 2.4, blink_distance: float = 180.0) -> None:
        self.blink_interval = blink_interval
        self.blink_distance = blink_distance
        self._timer: dict[int, float] = {}

    def update(self, entity: Entity, world: "GameWorld", dt: float) -> None:
        player = world.player
        if player is None:
            return

        transform = entity.get_component(TransformComponent)
        movement = entity.get_component(MovementComponent)
        player_transform = player.get_component(TransformComponent)
        if transform is None or movement is None or player_transform is None:
            return

        movement.velocity.update(0.0, 0.0)
        movement.input_direction = Vector2()
        movement.max_speed = 0.0

        entity_id = entity.id
        timer = self._timer.get(entity_id, random.uniform(0.0, self.blink_interval * 0.75)) + dt
        self._timer[entity_id] = timer
        if timer < self.blink_interval:
            return

        self._timer[entity_id] = 0.0
        angle = random.uniform(0.0, 360.0)
        target_position = player_transform.position + Vector2(self.blink_distance, 0.0).rotate(angle)
        target_position = world.clamp_to_bounds(target_position, radius=16.0)
        to_player_after_blink = target_position - player_transform.position
        if to_player_after_blink.length_squared() < self.POST_BLINK_MIN_DISTANCE * self.POST_BLINK_MIN_DISTANCE:
            push_dir = normalized(to_player_after_blink, Vector2(1, 0).rotate(random.uniform(0.0, 360.0)))
            target_position = world.clamp_to_bounds(
                player_transform.position + (push_dir * self.POST_BLINK_MIN_DISTANCE),
                radius=16.0,
            )
        transform.position = target_position

        stagger = entity.get_component(StaggeredComponent)
        if stagger is None:
            entity.add_component(StaggeredComponent(time_left=self.POST_BLINK_GRACE, pulse_time=0.0))
        else:
            stagger.time_left = max(stagger.time_left, self.POST_BLINK_GRACE)

        shot_dir = normalized(player_transform.position - transform.position)
        for offset in (-28.0, 0.0, 28.0):
            world.spawn_enemy_bullet(
                transform.position,
                shot_dir.rotate(offset),
                speed=335.0,
                radius=5.0,
                color=(226, 206, 255),
            )


from game.core.world import GameWorld
