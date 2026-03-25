from __future__ import annotations

import random

from pygame import Vector2

from game.core.world import GameWorld
from game.factories.collectible_factory import CollectibleFactory


class SurvivalCollectibleSystem:
    def __init__(self, world: GameWorld, spawn_interval: float, spawn_cap: int) -> None:
        self.world = world
        self.spawn_interval = max(0.6, spawn_interval)
        self.spawn_cap = max(1, spawn_cap)
        self._time_left = self.spawn_interval

    def update(self, dt: float) -> None:
        self._time_left = max(0.0, self._time_left - dt)
        if self._time_left > 0.0:
            return
        self._time_left = self.spawn_interval

        if self.world.count_by_tag("collectible") >= self.spawn_cap:
            return

        padding = 58.0
        position = Vector2(
            random.uniform(padding, self.world.width - padding),
            random.uniform(padding, self.world.height - padding),
        )
        self.world.add_entity(CollectibleFactory.create(position))
