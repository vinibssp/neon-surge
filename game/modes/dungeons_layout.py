from __future__ import annotations

from dataclasses import dataclass
import math
import random
from typing import Iterable

from pygame import Rect
from pygame import Vector2


CellCoord = tuple[int, int]


@dataclass(frozen=True)
class DungeonGeometry:
    origin: Vector2
    cell_size: float


@dataclass(frozen=True)
class DungeonRoom:
    x: int
    y: int
    width: int
    height: int

    def center_cell(self) -> CellCoord:
        return (self.x + self.width // 2, self.y + self.height // 2)

    def rect(self) -> Rect:
        return Rect(self.x, self.y, self.width, self.height)


@dataclass
class DungeonLayout:
    width: int
    height: int
    geometry: DungeonGeometry
    grid: list[list[bool]]
    rooms: list[DungeonRoom]
    spawn_room_index: int
    boss_room_index: int
    wall_rects: list[Rect]

    @classmethod
    def generate(
        cls,
        width: int,
        height: int,
        cell_size: float,
        rng: random.Random,
        room_attempts: int,
        room_min_size: int,
        room_max_size: int,
        corridor_width: int,
    ) -> "DungeonLayout":
        grid = [[False for _ in range(width)] for _ in range(height)]
        rooms: list[DungeonRoom] = []

        for _ in range(room_attempts):
            room_width = rng.randint(room_min_size, room_max_size)
            room_height = rng.randint(room_min_size, room_max_size)
            x = rng.randint(1, max(1, width - room_width - 1))
            y = rng.randint(1, max(1, height - room_height - 1))
            candidate = DungeonRoom(x=x, y=y, width=room_width, height=room_height)
            if cls._overlaps_existing(candidate, rooms, padding=1):
                continue
            rooms.append(candidate)
            cls._carve_room(grid, candidate)

        if not rooms:
            fallback = DungeonRoom(
                x=max(1, width // 2 - 3),
                y=max(1, height // 2 - 3),
                width=min(width - 2, 7),
                height=min(height - 2, 7),
            )
            rooms.append(fallback)
            cls._carve_room(grid, fallback)

        cls._connect_rooms(grid, rooms, rng, corridor_width)
        cls._ensure_connectivity(grid, rooms, rng, corridor_width)

        spawn_room_index = rng.randrange(len(rooms))
        boss_room_index = cls._choose_farthest_room(rooms, spawn_room_index)

        geometry = DungeonGeometry(origin=Vector2(0, 0), cell_size=cell_size)
        wall_rects = cls._build_wall_rects(grid, geometry)

        return cls(
            width=width,
            height=height,
            geometry=geometry,
            grid=grid,
            rooms=rooms,
            spawn_room_index=spawn_room_index,
            boss_room_index=boss_room_index,
            wall_rects=wall_rects,
        )

    @staticmethod
    def _overlaps_existing(room: DungeonRoom, rooms: list[DungeonRoom], padding: int) -> bool:
        candidate = Rect(
            room.x - padding,
            room.y - padding,
            room.width + padding * 2,
            room.height + padding * 2,
        )
        return any(candidate.colliderect(existing.rect()) for existing in rooms)

    @staticmethod
    def _carve_room(grid: list[list[bool]], room: DungeonRoom) -> None:
        for y in range(room.y, room.y + room.height):
            for x in range(room.x, room.x + room.width):
                if 0 <= y < len(grid) and 0 <= x < len(grid[0]):
                    grid[y][x] = True

    @classmethod
    def _connect_rooms(
        cls,
        grid: list[list[bool]],
        rooms: list[DungeonRoom],
        rng: random.Random,
        corridor_width: int,
    ) -> None:
        if len(rooms) <= 1:
            return

        for index in range(1, len(rooms)):
            room = rooms[index]
            nearest_index = cls._nearest_room_index(room, rooms[:index])
            target = rooms[nearest_index]
            cls._carve_corridor(grid, room.center_cell(), target.center_cell(), rng, corridor_width)

    @staticmethod
    def _nearest_room_index(room: DungeonRoom, rooms: list[DungeonRoom]) -> int:
        cx, cy = room.center_cell()
        best_index = 0
        best_distance = float("inf")
        for index, candidate in enumerate(rooms):
            tx, ty = candidate.center_cell()
            distance = (tx - cx) * (tx - cx) + (ty - cy) * (ty - cy)
            if distance < best_distance:
                best_distance = distance
                best_index = index
        return best_index

    @classmethod
    def _carve_corridor(
        cls,
        grid: list[list[bool]],
        start: CellCoord,
        end: CellCoord,
        rng: random.Random,
        corridor_width: int,
    ) -> None:
        sx, sy = start
        ex, ey = end
        if rng.random() < 0.5:
            cls._carve_h(grid, sx, ex, sy, corridor_width)
            cls._carve_v(grid, sy, ey, ex, corridor_width)
        else:
            cls._carve_v(grid, sy, ey, sx, corridor_width)
            cls._carve_h(grid, sx, ex, ey, corridor_width)

    @staticmethod
    def _carve_h(grid: list[list[bool]], x1: int, x2: int, y: int, corridor_width: int) -> None:
        if x2 < x1:
            x1, x2 = x2, x1
        for x in range(x1, x2 + 1):
            for offset in range(-corridor_width // 2, corridor_width // 2 + 1):
                ny = y + offset
                if 0 <= ny < len(grid) and 0 <= x < len(grid[0]):
                    grid[ny][x] = True

    @staticmethod
    def _carve_v(grid: list[list[bool]], y1: int, y2: int, x: int, corridor_width: int) -> None:
        if y2 < y1:
            y1, y2 = y2, y1
        for y in range(y1, y2 + 1):
            for offset in range(-corridor_width // 2, corridor_width // 2 + 1):
                nx = x + offset
                if 0 <= y < len(grid) and 0 <= nx < len(grid[0]):
                    grid[y][nx] = True

    @classmethod
    def _ensure_connectivity(
        cls,
        grid: list[list[bool]],
        rooms: list[DungeonRoom],
        rng: random.Random,
        corridor_width: int,
    ) -> None:
        if len(rooms) <= 1:
            return

        reachable = cls._reachable_cells(grid, rooms[0].center_cell())
        unreachable = [room for room in rooms if room.center_cell() not in reachable]
        while unreachable:
            room = unreachable.pop(0)
            reachable_rooms = [r for r in rooms if r.center_cell() in reachable]
            if not reachable_rooms:
                break
            target = reachable_rooms[rng.randrange(len(reachable_rooms))]
            cls._carve_corridor(grid, room.center_cell(), target.center_cell(), rng, corridor_width)
            reachable = cls._reachable_cells(grid, rooms[0].center_cell())
            unreachable = [r for r in rooms if r.center_cell() not in reachable]

    @staticmethod
    def _reachable_cells(grid: list[list[bool]], start: CellCoord) -> set[CellCoord]:
        if not grid:
            return set()
        width = len(grid[0])
        height = len(grid)
        if not (0 <= start[0] < width and 0 <= start[1] < height):
            return set()
        if not grid[start[1]][start[0]]:
            return set()

        visited = {start}
        queue = [start]
        while queue:
            x, y = queue.pop(0)
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nx = x + dx
                ny = y + dy
                if nx < 0 or ny < 0 or nx >= width or ny >= height:
                    continue
                if not grid[ny][nx]:
                    continue
                cell = (nx, ny)
                if cell in visited:
                    continue
                visited.add(cell)
                queue.append(cell)
        return visited

    @staticmethod
    def _choose_farthest_room(rooms: list[DungeonRoom], spawn_index: int) -> int:
        sx, sy = rooms[spawn_index].center_cell()
        best_index = spawn_index
        best_distance = -1.0
        for index, room in enumerate(rooms):
            cx, cy = room.center_cell()
            dx = cx - sx
            dy = cy - sy
            distance = dx * dx + dy * dy
            if distance > best_distance:
                best_distance = distance
                best_index = index
        return best_index

    @classmethod
    def _build_wall_rects(cls, grid: list[list[bool]], geometry: DungeonGeometry) -> list[Rect]:
        wall_rects: list[Rect] = []
        for y, row in enumerate(grid):
            for x, is_floor in enumerate(row):
                if is_floor:
                    continue
                rect = Rect(
                    int(geometry.origin.x + x * geometry.cell_size),
                    int(geometry.origin.y + y * geometry.cell_size),
                    int(geometry.cell_size),
                    int(geometry.cell_size),
                )
                wall_rects.append(rect)
        return wall_rects

    def cell_center(self, cell: CellCoord) -> Vector2:
        x, y = cell
        center_x = self.geometry.origin.x + (x + 0.5) * self.geometry.cell_size
        center_y = self.geometry.origin.y + (y + 0.5) * self.geometry.cell_size
        return Vector2(center_x, center_y)

    def to_cell(self, position: Vector2) -> CellCoord | None:
        relative = position - self.geometry.origin
        if relative.x < 0 or relative.y < 0:
            return None
        x = int(relative.x // self.geometry.cell_size)
        y = int(relative.y // self.geometry.cell_size)
        if x < 0 or y < 0 or x >= self.width or y >= self.height:
            return None
        return (x, y)

    def is_floor(self, cell: CellCoord) -> bool:
        x, y = cell
        if x < 0 or y < 0 or x >= self.width or y >= self.height:
            return False
        return self.grid[y][x]

    def room(self, index: int) -> DungeonRoom:
        return self.rooms[index]

    def room_center(self, index: int) -> Vector2:
        return self.cell_center(self.room(index).center_cell())

    def random_floor_cell(self, rng: random.Random, blocked: Iterable[CellCoord] = ()) -> CellCoord:
        blocked_set = set(blocked)
        candidates: list[CellCoord] = [
            (x, y)
            for y in range(self.height)
            for x in range(self.width)
            if self.grid[y][x] and (x, y) not in blocked_set
        ]
        if not candidates:
            return self.room(self.spawn_room_index).center_cell()
        return rng.choice(candidates)


@dataclass
class DungeonSpatialIndex:
    cell_to_rect_indices: dict[CellCoord, list[int]]

    @classmethod
    def build(cls, layout: DungeonLayout) -> "DungeonSpatialIndex":
        mapping: dict[CellCoord, list[int]] = {}
        for rect_index, rect in enumerate(layout.wall_rects):
            cell = layout.to_cell(Vector2(rect.centerx, rect.centery))
            if cell is None:
                continue
            mapping.setdefault(cell, []).append(rect_index)
        return cls(cell_to_rect_indices=mapping)

    def nearby_rect_indices(self, cell: CellCoord) -> list[int]:
        return self.cell_to_rect_indices.get(cell, [])


@dataclass
class DungeonRuntimeState:
    layout: DungeonLayout
    spatial_index: DungeonSpatialIndex
    revealed_cells: set[CellCoord]
    visible_cells: set[CellCoord]
    boss_defeated: bool = False
    exit_portal_spawned: bool = False
