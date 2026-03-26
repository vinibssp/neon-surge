from __future__ import annotations

from game.components.data_components import BehaviorComponent, StaggeredComponent
from game.core.world import GameWorld
from game.systems.world_queries import ENEMY_BEHAVIOR_QUERY


class FollowSystem:
    def __init__(self, world: GameWorld) -> None:
        self.world = world

    def update(self, dt: float) -> None:
        for entity in self.world.query(ENEMY_BEHAVIOR_QUERY):
            stagger = entity.get_component(StaggeredComponent)
            if stagger is not None and stagger.time_left > 0.0:
                continue
            behavior_component = entity.get_component(BehaviorComponent)
            if behavior_component is None:
                continue
            self.world.runtime_state["current_enemy_shooter_id"] = entity.id
            try:
                behavior_component.behavior.update(entity, self.world, dt)
            finally:
                self.world.runtime_state.pop("current_enemy_shooter_id", None)
