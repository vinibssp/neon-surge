from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from pygame import Vector2

from game.components.data_components import (
    LabyrinthVirusComponent,
    MovementComponent,
    TransformComponent,
)
from game.core.world import GameWorld
from game.ecs.query import WorldQuery
from game.modes.labyrinth_layout import CellCoord, LabyrinthRuntimeState


MAZE_VIRUS_QUERY = WorldQuery(
    component_types=(TransformComponent, MovementComponent, LabyrinthVirusComponent),
    tags=("maze-virus",),
)


@dataclass
class _PathCacheEntry:
    target_cell: CellCoord
    path: list[CellCoord]


class LabyrinthAISystem:
    def __init__(self, world: GameWorld, runtime_provider: Callable[[], LabyrinthRuntimeState | None]) -> None:
        self.world = world
        self.runtime_provider = runtime_provider
        self._path_cache: dict[int, _PathCacheEntry] = {}

    def update(self, dt: float) -> None:
        runtime = self.runtime_provider()
        if runtime is None or runtime.is_boss_level:
            self._path_cache.clear()
            return

        player = self.world.player
        if player is None:
            return

        player_transform = player.get_component(TransformComponent)
        player_movement = player.get_component(MovementComponent)
        if player_transform is None or player_movement is None:
            return

        active_ids: set[int] = set()
        player_cell = runtime.layout.to_cell(player_transform.position)
        if player_cell is None:
            return

        for entity in self.world.query(MAZE_VIRUS_QUERY):
            active_ids.add(entity.id)
            transform = entity.get_component(TransformComponent)
            movement = entity.get_component(MovementComponent)
            virus = entity.get_component(LabyrinthVirusComponent)
            if transform is None or movement is None or virus is None:
                continue

            virus.retarget_time_left = max(0.0, virus.retarget_time_left - dt)

            start_cell = runtime.layout.to_cell(transform.position)
            if start_cell is None:
                continue

            target_cell = self._target_cell(
                behavior_kind=virus.behavior_kind,
                runtime=runtime,
                player_position=player_transform.position,
                player_velocity=player_movement.velocity,
                fallback_cell=player_cell,
                interception_seconds=virus.interception_seconds,
            )
            if target_cell is None:
                target_cell = player_cell

            cached = self._path_cache.get(entity.id)
            must_repath = virus.retarget_time_left <= 0.0
            if cached is None or cached.target_cell != target_cell or not cached.path:
                must_repath = True

            if must_repath:
                # Replanejamento em janela curta para equilibrar responsividade e custo de CPU.
                new_path = runtime.layout.shortest_path(start=start_cell, target=target_cell)
                self._path_cache[entity.id] = _PathCacheEntry(target_cell=target_cell, path=new_path)
                virus.retarget_time_left = virus.retarget_interval
                cached = self._path_cache[entity.id]

            if cached is None or not cached.path:
                movement.input_direction.update(0, 0)
                continue

            waypoint_cell = cached.path[0] if len(cached.path) == 1 else cached.path[1]
            waypoint = runtime.layout.cell_center(waypoint_cell)
            desired = waypoint - transform.position
            if desired.length_squared() <= 1.0:
                movement.input_direction.update(0, 0)
                continue

            movement.max_speed = virus.base_speed
            movement.input_direction = desired.normalize()

        stale_ids = [entity_id for entity_id in self._path_cache.keys() if entity_id not in active_ids]
        for entity_id in stale_ids:
            del self._path_cache[entity_id]

    @staticmethod
    def _target_cell(
        behavior_kind: str,
        runtime: LabyrinthRuntimeState,
        player_position: Vector2,
        player_velocity: Vector2,
        fallback_cell: CellCoord,
        interception_seconds: float,
    ) -> CellCoord | None:
        if behavior_kind == "interceptor":
            # Interceptor projeta posição futura do player para cortar rota.
            predicted = player_position + (player_velocity * interception_seconds)
            predicted_cell = runtime.layout.to_cell(predicted)
            return fallback_cell if predicted_cell is None else predicted_cell
        return runtime.layout.to_cell(player_position)
