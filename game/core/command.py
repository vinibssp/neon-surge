from __future__ import annotations

from abc import ABC, abstractmethod

from pygame import Vector2

from game.components.data_components import DashComponent, MovementComponent
from game.ecs.entity import Entity


class Command(ABC):
    @abstractmethod
    def execute(self, entity: Entity, world: "GameWorld") -> None:
        ...


class MoveCommand(Command):
    def __init__(self, direction: Vector2) -> None:
        self.direction = direction

    def execute(self, entity: Entity, world: "GameWorld") -> None:
        movement = entity.get_component(MovementComponent)
        if movement is None:
            return
        if self.direction.length_squared() > 0:
            movement.input_direction = self.direction.normalize()
        else:
            movement.input_direction = Vector2()


class DashCommand(Command):
    def execute(self, entity: Entity, world: "GameWorld") -> None:
        dash = entity.get_component(DashComponent)
        if dash is None:
            return
        dash.requested = True


from game.core.world import GameWorld
