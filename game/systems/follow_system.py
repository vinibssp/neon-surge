from __future__ import annotations

from game.components.data_components import BehaviorComponent
from game.core.world import GameWorld
from game.systems.world_queries import ENEMY_BEHAVIOR_QUERY


class FollowSystem:
    def __init__(self, world: GameWorld) -> None:
        self.world = world

    def update(self, dt: float) -> None:
        for entity in self.world.query(ENEMY_BEHAVIOR_QUERY):
            behavior_component = entity.get_component(BehaviorComponent)
            if behavior_component is None:
                continue
            behavior_component.behavior.update(entity, self.world, dt)
