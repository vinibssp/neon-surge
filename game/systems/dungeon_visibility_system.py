from __future__ import annotations

import math
from typing import Callable

from pygame import Vector2

from game.components.data_components import DormantComponent, TransformComponent
from game.core.world import GameWorld
from game.ecs.query import WorldQuery
from game.modes.dungeons_layout import CellCoord, DungeonRuntimeState


DUNGEON_ENEMY_QUERY = WorldQuery(
    component_types=(TransformComponent, DormantComponent),
    tags=("enemy",),
)


class DungeonVisibilitySystem:
    def __init__(
        self,
        world: GameWorld,
        runtime_provider: Callable[[], DungeonRuntimeState | None],
        vision_radius: float,
        update_interval: float = 0.0,
    ) -> None:
        self.world = world
        self.runtime_provider = runtime_provider
        self.vision_radius = vision_radius
        self.update_interval = max(0.0, update_interval)
        self._time_since_update = 0.0
        self._last_player_cell: CellCoord | None = None

    def update(self, dt: float) -> None:
        if self.update_interval > 0.0:
            self._time_since_update += dt
            if self._time_since_update < self.update_interval:
                return
            self._time_since_update = 0.0
        runtime = self.runtime_provider()
        if runtime is None:
            return

        player = self.world.player
        if player is None:
            return

        player_transform = player.get_component(TransformComponent)
        if player_transform is None:
            return

        layout = runtime.layout
        player_cell = layout.to_cell(player_transform.position)
        if player_cell is None:
            return

        if self._last_player_cell == player_cell and runtime.visible_cells:
            if self.update_interval > 0.0 and self._time_since_update > 0.0:
                return

        visible_cells = self._compute_visible_cells(layout, player_cell, player_transform.position)
        runtime.visible_cells = visible_cells
        revealed_before = len(runtime.revealed_cells)
        runtime.revealed_cells |= visible_cells
        if len(runtime.revealed_cells) != revealed_before:
            runtime.minimap_dirty = True
        runtime.fog_dirty = True
        self._last_player_cell = player_cell

        for enemy in self.world.query(DUNGEON_ENEMY_QUERY):
            dormant = enemy.get_component(DormantComponent)
            if dormant is None or dormant.active:
                continue
            transform = enemy.get_component(TransformComponent)
            if transform is None:
                continue
            enemy_cell = layout.to_cell(transform.position)
            if enemy_cell is None:
                continue
            if enemy_cell in runtime.revealed_cells:
                dormant.active = True

    def _compute_visible_cells(
        self,
        layout,
        player_cell: CellCoord,
        player_position: Vector2,
    ) -> set[CellCoord]:
        radius_cells = max(1, int(math.ceil(self.vision_radius / max(1.0, layout.geometry.cell_size))))
        max_distance_sq = self.vision_radius * self.vision_radius
        visible: set[CellCoord] = set()
        px, py = player_cell
        for y in range(py - radius_cells, py + radius_cells + 1):
            for x in range(px - radius_cells, px + radius_cells + 1):
                if x < 0 or y < 0 or x >= layout.width or y >= layout.height:
                    continue
                cell = (x, y)
                if not layout.is_floor(cell):
                    continue
                center = layout.cell_center(cell)
                if (center - player_position).length_squared() > max_distance_sq:
                    continue
                if not self._has_line_of_sight(layout, player_cell, cell):
                    continue
                visible.add(cell)
        return visible

    @staticmethod
    def _has_line_of_sight(layout, start: CellCoord, end: CellCoord) -> bool:
        if start == end:
            return True

        x0, y0 = start
        x1, y1 = end
        dx = abs(x1 - x0)
        dy = abs(y1 - y0)
        x = x0
        y = y0
        n = 1 + dx + dy
        x_inc = 1 if x1 > x0 else -1
        y_inc = 1 if y1 > y0 else -1
        error = dx - dy
        dx *= 2
        dy *= 2

        for _ in range(n):
            if not layout.is_floor((x, y)):
                return False
            if error > 0:
                x += x_inc
                error -= dy
            else:
                y += y_inc
                error += dx
        return True
