from __future__ import annotations

from abc import ABC, abstractmethod

from pygame import Vector2

from game.components.data_components import (
    DashComponent,
    MovementComponent,
    NuclearBombComponent,
    ParryComponent,
    PlayerShootComponent,
    TransformComponent,
)
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


class ShootCommand(Command):
    def __init__(self, screen_position: Vector2) -> None:
        self.screen_position = Vector2(screen_position)

    def execute(self, entity: Entity, world: "GameWorld") -> None:
        shoot = entity.get_component(PlayerShootComponent)
        transform = entity.get_component(TransformComponent)
        if shoot is None or transform is None:
            return

        camera_offset = world.runtime_state.get("camera_offset")
        if isinstance(camera_offset, Vector2):
            world_position = self.screen_position - camera_offset
        else:
            world_position = Vector2(self.screen_position)

        direction = world_position - transform.position
        if direction.length_squared() <= 0.0001:
            return

        shoot.aim_direction = direction.normalize()
        shoot.requested = True


from game.core.world import GameWorld
