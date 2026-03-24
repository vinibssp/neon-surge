from __future__ import annotations

from typing import Protocol

from game.ecs.entity import Entity


class Behavior(Protocol):
    def update(self, entity: Entity, world: "GameWorld", dt: float) -> None:
        ...


from game.core.world import GameWorld
