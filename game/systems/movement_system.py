from __future__ import annotations

from game.components.data_components import DashComponent, DormantComponent, MovementComponent, TransformComponent
from game.core.world import GameWorld
from game.systems.world_queries import MOVABLE_QUERY


class MovementSystem:
    def __init__(self, world: GameWorld) -> None:
        self.world = world

    def update(self, dt: float) -> None:
        for entity in self.world.query(MOVABLE_QUERY):
            transform = entity.get_component(TransformComponent)
            movement = entity.get_component(MovementComponent)
            if transform is None or movement is None:
                continue

            dormant = entity.get_component(DormantComponent)
            if dormant is not None and not dormant.active:
                movement.velocity.update(0, 0)
                movement.input_direction.update(0, 0)
                continue

            dash = entity.get_component(DashComponent)
            if dash is None or dash.active_time_left <= 0:
                if movement.input_direction.length_squared() > 0:
                    movement.velocity = movement.input_direction.normalize() * movement.max_speed
                else:
                    movement.velocity.update(0, 0)

            transform.position += movement.velocity * dt
            radius = self.world.get_collision_radius(entity)
            transform.position = self.world.clamp_to_bounds(transform.position, radius)
