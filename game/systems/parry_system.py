from __future__ import annotations

from game.components.data_components import ParryComponent, StaggeredComponent, TransformComponent
from game.core.world import GameWorld
from game.systems.world_queries import ENEMY_TRANSFORM_QUERY, PLAYER_PARRY_QUERY


class ParrySystem:
    def __init__(self, world: GameWorld) -> None:
        self.world = world

    def update(self, dt: float) -> None:
        for player in self.world.query(PLAYER_PARRY_QUERY):
            parry = player.get_component(ParryComponent)
            transform = player.get_component(TransformComponent)
            if parry is None or transform is None:
                continue

            parry.cooldown_left = max(0.0, parry.cooldown_left - dt)

            should_start = parry.requested and parry.cooldown_left <= 0.0
            parry.requested = False
            if should_start:
                parry.active_time_left = parry.duration
                parry.cooldown_left = parry.cooldown

            if parry.active_time_left <= 0.0:
                continue

            parry.active_time_left = max(0.0, parry.active_time_left - dt)
            self._apply_parry_stagger(transform.position, parry.radius, parry.stagger_duration)

    def _apply_parry_stagger(self, center, radius: float, duration: float) -> None:
        radius_sq = radius * radius
        for enemy in self.world.query(ENEMY_TRANSFORM_QUERY):
            enemy_transform = enemy.get_component(TransformComponent)
            if enemy_transform is None:
                continue
            if (enemy_transform.position - center).length_squared() > radius_sq:
                continue

            stagger = enemy.get_component(StaggeredComponent)
            if stagger is None:
                enemy.add_component(StaggeredComponent(time_left=duration, pulse_time=0.0))
                continue

            stagger.time_left = max(stagger.time_left, duration)
