from __future__ import annotations

from abc import ABC, abstractmethod

from pygame import Vector2

from game.components.data_components import DashComponent, MovementComponent, NuclearBombComponent, ParryComponent
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


class ParryCommand(Command):
    def execute(self, entity: Entity, world: "GameWorld") -> None:
        parry = entity.get_component(ParryComponent)
        if parry is None:
            return
        parry.requested = True


class NuclearBombCommand(Command):
    def execute(self, entity: Entity, world: "GameWorld") -> None:
        bomb = entity.get_component(NuclearBombComponent)
        if bomb is None:
            return
        bomb.requested = True


from game.core.world import GameWorld
