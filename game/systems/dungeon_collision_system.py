from __future__ import annotations

import math
from typing import Callable

from pygame import Vector2

from game.components.data_components import CollisionComponent, MovementComponent, TransformComponent
from game.core.world import GameWorld
from game.ecs.query import WorldQuery
from game.modes.dungeons_layout import DungeonRuntimeState
from game.modes.labyrinth_layout import circle_rect_overlap


DUNGEON_COLLISION_QUERY = WorldQuery(
    component_types=(TransformComponent, CollisionComponent),
    tags=(),
)


class DungeonCollisionSystem:
    def __init__(self, world: GameWorld, runtime_provider: Callable[[], DungeonRuntimeState | None]) -> None:
        self.world = world
        self.runtime_provider = runtime_provider

    def update(self, dt: float) -> None:
        runtime = self.runtime_provider()
        if runtime is None:
            return

        for entity in self.world.query(DUNGEON_COLLISION_QUERY):
            if not (entity.has_tag("player") or entity.has_tag("enemy") or entity.has_tag("bullet")):
                continue

            transform = entity.get_component(TransformComponent)
            collision = entity.get_component(CollisionComponent)
            movement = entity.get_component(MovementComponent)
            if transform is None or collision is None:
                continue

            collided_with_wall = False
            if movement is None or dt <= 0.0:
                collided_with_wall = self._resolve_wall_overlap(runtime, transform, collision, movement)
            else:
                end_position = Vector2(transform.position)
                start_position = end_position - (movement.velocity * dt)
                travel = end_position - start_position
                distance = travel.length()
                max_step = max(0.5, min(collision.radius * 0.33, runtime.layout.geometry.cell_size * 0.33))
                step_count = max(1, int(math.ceil(distance / max_step)))
                step_delta = Vector2() if step_count <= 0 else (travel / step_count)

                sweep_position = Vector2(start_position)
                for _ in range(step_count):
                    sweep_position += step_delta
                    transform.position = Vector2(sweep_position)
                    collided = self._resolve_wall_overlap(runtime, transform, collision, movement)
                    if collided:
                        collided_with_wall = True
                    sweep_position = Vector2(transform.position)

            if collided_with_wall and entity.has_tag("bullet"):
                self.world.remove_entity(entity)
                continue

            if entity.has_tag("player"):
                self._clamp_entity_inside_layout(runtime, transform, collision)

    def _resolve_wall_overlap(
        self,
        runtime: DungeonRuntimeState,
        transform: TransformComponent,
        collision: CollisionComponent,
        movement: MovementComponent | None,
    ) -> bool:
        current_cell = runtime.layout.to_cell(transform.position)
        if current_cell is None:
            current_cell = self._closest_cell(runtime, transform.position)

        rect_indices = self._rect_indices_near_cell(runtime, current_cell)
        if not rect_indices:
            return False

        collided_with_wall = False
        for _ in range(3):
            resolved = False
            for rect_index in rect_indices:
                if rect_index < 0 or rect_index >= len(runtime.layout.wall_rects):
                    continue
                wall_rect = runtime.layout.wall_rects[rect_index]
                overlapped, normal, penetration = circle_rect_overlap(transform.position, collision.radius, wall_rect)
                if not overlapped:
                    continue

                resolved = True
                collided_with_wall = True
                transform.position += normal * penetration
                if movement is not None and normal.length_squared() > 0:
                    if abs(normal.x) > 0.5:
                        movement.velocity.x = 0.0
                    if abs(normal.y) > 0.5:
                        movement.velocity.y = 0.0
            if not resolved:
                break
        return collided_with_wall

    @staticmethod
    def _closest_cell(runtime: DungeonRuntimeState, position: Vector2) -> tuple[int, int]:
        origin = runtime.layout.geometry.origin
        cell_size = runtime.layout.geometry.cell_size
        local_x = (position.x - origin.x) / max(1.0, cell_size)
        local_y = (position.y - origin.y) / max(1.0, cell_size)
        x = int(max(0, min(runtime.layout.width - 1, math.floor(local_x))))
        y = int(max(0, min(runtime.layout.height - 1, math.floor(local_y))))
        return (x, y)

    @staticmethod
    def _rect_indices_near_cell(runtime: DungeonRuntimeState, cell: tuple[int, int]) -> list[int]:
        seen: set[int] = set()
        x, y = cell
        for offset_y in (-1, 0, 1):
            for offset_x in (-1, 0, 1):
                nx = x + offset_x
                ny = y + offset_y
                if nx < 0 or ny < 0 or nx >= runtime.layout.width or ny >= runtime.layout.height:
                    continue
                for rect_index in runtime.spatial_index.nearby_rect_indices((nx, ny)):
                    seen.add(rect_index)
        return list(seen)

    @staticmethod
    def _clamp_entity_inside_layout(
        runtime: DungeonRuntimeState,
        transform: TransformComponent,
        collision: CollisionComponent,
    ) -> None:
        origin = runtime.layout.geometry.origin
        width_px = runtime.layout.width * runtime.layout.geometry.cell_size
        height_px = runtime.layout.height * runtime.layout.geometry.cell_size
        min_x = origin.x + collision.radius
        min_y = origin.y + collision.radius
        max_x = origin.x + width_px - collision.radius
        max_y = origin.y + height_px - collision.radius
        transform.position.x = max(min_x, min(max_x, transform.position.x))
        transform.position.y = max(min_y, min(max_y, transform.position.y))
