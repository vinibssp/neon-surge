from __future__ import annotations

from game.components.data_components import MovementComponent, StaggeredComponent
from game.core.world import GameWorld
from game.systems.world_queries import ENEMY_BEHAVIOR_QUERY


class StaggerSystem:
    def __init__(self, world: GameWorld) -> None:
        self.world = world

    def update(self, dt: float) -> None:
        for enemy in self.world.query(ENEMY_BEHAVIOR_QUERY):
            stagger = enemy.get_component(StaggeredComponent)
            if stagger is None or stagger.time_left <= 0.0:
                continue

            stagger.time_left = max(0.0, stagger.time_left - dt)
            stagger.pulse_time += dt

            movement = enemy.get_component(MovementComponent)
            if movement is None:
                continue
            movement.velocity *= 0.78
            movement.input_direction.update(0.0, 0.0)
