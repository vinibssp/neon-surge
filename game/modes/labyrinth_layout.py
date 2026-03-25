from __future__ import annotations

from dataclasses import dataclass
import math
import random
from typing import Iterable

from pygame import Rect
from pygame import Vector2


NORTH = 1
EAST = 2
SOUTH = 4
WEST = 8

_DIRECTION_ORDER: tuple[int, ...] = (NORTH, EAST, SOUTH, WEST)
_DIRECTION_TO_OFFSET: dict[int, tuple[int, int]] = {
    NORTH: (0, -1),
    EAST: (1, 0),
    SOUTH: (0, 1),
    WEST: (-1, 0),
}
_OPPOSITE_DIRECTION: dict[int, int] = {
    NORTH: SOUTH,
    EAST: WEST,
    SOUTH: NORTH,
    WEST: EAST,
}


CellCoord = tuple[int, int]


@dataclass(frozen=True)
class LabyrinthDifficulty:
    grid_width: int
    grid_height: int
    enemy_speed_multiplier: float
    enemy_count: int


@dataclass(frozen=True)
class LabyrinthGeometry:
    origin: Vector2
    cell_size: float
    wall_thickness: float


@dataclass
class LabyrinthLayout:
    width: int
    height: int
    geometry: LabyrinthGeometry
    passages: list[list[int]]
    wall_rects: list[Rect]
    border_exit_cell: CellCoord
    key_cell: CellCoord

    @classmethod
    def generate(
        cls,
        width: int,
        height: int,
        geometry: LabyrinthGeometry,
        rng: random.Random,
    ) -> LabyrinthLayout:
        # Backtracking recursivo iterativo: gera um labirinto perfeito (conexo e sem ilhas).
        passages = [[0 for _ in range(width)] for _ in range(height)]
        visited = [[False for _ in range(width)] for _ in range(height)]

        start_x = rng.randrange(width)
        start_y = rng.randrange(height)
        stack: list[CellCoord] = [(start_x, start_y)]
        visited[start_y][start_x] = True

        while stack:
            x, y = stack[-1]
            unvisited_neighbors: list[tuple[int, int, int]] = []
            for direction in _DIRECTION_ORDER:
                offset_x, offset_y = _DIRECTION_TO_OFFSET[direction]
                nx = x + offset_x
                ny = y + offset_y
                if nx < 0 or nx >= width or ny < 0 or ny >= height:
                    continue
                if visited[ny][nx]:
                    continue
                unvisited_neighbors.append((direction, nx, ny))

            if not unvisited_neighbors:
                stack.pop()
                continue

            direction, nx, ny = rng.choice(unvisited_neighbors)
            passages[y][x] |= direction
            passages[ny][nx] |= _OPPOSITE_DIRECTION[direction]
            visited[ny][nx] = True
            stack.append((nx, ny))

        border_exit_cell = cls._choose_border_cell(width=width, height=height, rng=rng)
        key_cell = cls._choose_farthest_key_cell(
            width=width,
            height=height,
            geometry=geometry,
            exit_cell=border_exit_cell,
        )
        wall_rects = cls._build_wall_rects(
            width=width,
            height=height,
            passages=passages,
            geometry=geometry,
            border_exit_cell=border_exit_cell,
        )
        return cls(
            width=width,
            height=height,
            geometry=geometry,
            passages=passages,
            wall_rects=wall_rects,
            border_exit_cell=border_exit_cell,
            key_cell=key_cell,
        )

    @staticmethod
    def difficulty_for_level(level: int) -> LabyrinthDifficulty:
        normalized_level = max(1, level)
        tier = min(8, (normalized_level - 1) // 3)
        grid_width = 10 + tier
        grid_height = 6 + tier
        enemy_count = 1 + min(9, (normalized_level - 1) // 3)
        speed_multiplier = 0.9 + min(0.75, (normalized_level - 1) * 0.03)
        return LabyrinthDifficulty(
            grid_width=grid_width,
            grid_height=grid_height,
            enemy_speed_multiplier=speed_multiplier,
            enemy_count=enemy_count,
        )

    @staticmethod
    def geometry_for_bounds(screen_width: int, screen_height: int, grid_width: int, grid_height: int) -> LabyrinthGeometry:
        usable_width = screen_width * 0.88
        usable_height = screen_height * 0.78
        cell_size = min(usable_width / max(1, grid_width), usable_height / max(1, grid_height))
        labyrinth_width = grid_width * cell_size
        labyrinth_height = grid_height * cell_size
        origin_x = (screen_width - labyrinth_width) * 0.5
        origin_y = (screen_height - labyrinth_height) * 0.5
        wall_thickness = max(5.0, cell_size * 0.13)
        return LabyrinthGeometry(
            origin=Vector2(origin_x, origin_y),
            cell_size=cell_size,
            wall_thickness=wall_thickness,
        )

    @staticmethod
    def _choose_border_cell(width: int, height: int, rng: random.Random) -> CellCoord:
        side = rng.choice(("top", "right", "bottom", "left"))
        if side == "top":
            return (rng.randrange(width), 0)
        if side == "bottom":
            return (rng.randrange(width), height - 1)
        if side == "left":
            return (0, rng.randrange(height))
        return (width - 1, rng.randrange(height))

    @classmethod
    def _choose_farthest_key_cell(
        cls,
        width: int,
        height: int,
        geometry: LabyrinthGeometry,
        exit_cell: CellCoord,
    ) -> CellCoord:
        # Critério de objetivo: escolher a célula de chave com maior distância Euclidiana até a saída.
        exit_center = cls._cell_center_static(exit_cell, geometry)
        farthest_cell = (0, 0)
        farthest_distance_sq = -1.0
        for y in range(height):
            for x in range(width):
                candidate = (x, y)
                candidate_center = cls._cell_center_static(candidate, geometry)
                dx = candidate_center.x - exit_center.x
                dy = candidate_center.y - exit_center.y
                distance_sq = dx * dx + dy * dy
                if distance_sq > farthest_distance_sq:
                    farthest_distance_sq = distance_sq
                    farthest_cell = candidate
        return farthest_cell

    @classmethod
    def _build_wall_rects(
        cls,
        width: int,
        height: int,
        passages: list[list[int]],
        geometry: LabyrinthGeometry,
        border_exit_cell: CellCoord,
    ) -> list[Rect]:
        wall_rects: list[Rect] = []
        layout_bounds = Rect(
            int(geometry.origin.x),
            int(geometry.origin.y),
            int(width * geometry.cell_size),
            int(height * geometry.cell_size),
        )
        opened_border_direction = cls._border_open_direction(border_exit_cell, width, height)

        for y in range(height):
            for x in range(width):
                cell = (x, y)
                center = cls._cell_center_static(cell, geometry)
                left = center.x - geometry.cell_size * 0.5
                top = center.y - geometry.cell_size * 0.5
                right = center.x + geometry.cell_size * 0.5
                bottom = center.y + geometry.cell_size * 0.5
                mask = passages[y][x]

                if not (mask & NORTH) and not (cell == border_exit_cell and opened_border_direction == NORTH):
                    wall_rects.append(
                        Rect(
                            int(left - geometry.wall_thickness * 0.5),
                            int(top - geometry.wall_thickness * 0.5),
                            int(geometry.cell_size + geometry.wall_thickness),
                            int(geometry.wall_thickness),
                        )
                    )
                if not (mask & WEST) and not (cell == border_exit_cell and opened_border_direction == WEST):
                    wall_rects.append(
                        Rect(
                            int(left - geometry.wall_thickness * 0.5),
                            int(top - geometry.wall_thickness * 0.5),
                            int(geometry.wall_thickness),
                            int(geometry.cell_size + geometry.wall_thickness),
                        )
                    )

                if y == height - 1 and not (mask & SOUTH) and not (
                    cell == border_exit_cell and opened_border_direction == SOUTH
                ):
                    wall_rects.append(
                        Rect(
                            int(left - geometry.wall_thickness * 0.5),
                            int(bottom - geometry.wall_thickness * 0.5),
                            int(geometry.cell_size + geometry.wall_thickness),
                            int(geometry.wall_thickness),
                        )
                    )
                if x == width - 1 and not (mask & EAST) and not (
                    cell == border_exit_cell and opened_border_direction == EAST
                ):
                    wall_rects.append(
                        Rect(
                            int(right - geometry.wall_thickness * 0.5),
                            int(top - geometry.wall_thickness * 0.5),
                            int(geometry.wall_thickness),
                            int(geometry.cell_size + geometry.wall_thickness),
                        )
                    )

        normalized_rects: list[Rect] = []
        for wall_rect in wall_rects:
            clipped = wall_rect.clip(layout_bounds)
            if clipped.width <= 0 or clipped.height <= 0:
                continue
            normalized_rects.append(clipped)

        return _dedupe_rects(normalized_rects)

    @staticmethod
    def _border_open_direction(cell: CellCoord, width: int, height: int) -> int:
        x, y = cell
        if y == 0:
            return NORTH
        if y == height - 1:
            return SOUTH
        if x == 0:
            return WEST
        return EAST

    @staticmethod
    def _cell_center_static(cell: CellCoord, geometry: LabyrinthGeometry) -> Vector2:
        x, y = cell
        center_x = geometry.origin.x + (x + 0.5) * geometry.cell_size
        center_y = geometry.origin.y + (y + 0.5) * geometry.cell_size
        return Vector2(center_x, center_y)

    def cell_center(self, cell: CellCoord) -> Vector2:
        return self._cell_center_static(cell, self.geometry)

    def to_cell(self, position: Vector2) -> CellCoord | None:
        relative = position - self.geometry.origin
        if relative.x < 0 or relative.y < 0:
            return None

        x = int(relative.x // self.geometry.cell_size)
        y = int(relative.y // self.geometry.cell_size)
        if x < 0 or y < 0 or x >= self.width or y >= self.height:
            return None
        return (x, y)

    def is_adjacent(self, source: CellCoord, target: CellCoord) -> bool:
        sx, sy = source
        tx, ty = target
        dx = tx - sx
        dy = ty - sy
        if abs(dx) + abs(dy) != 1:
            return False
        if dx == 1:
            return (self.passages[sy][sx] & EAST) != 0
        if dx == -1:
            return (self.passages[sy][sx] & WEST) != 0
        if dy == 1:
            return (self.passages[sy][sx] & SOUTH) != 0
        return (self.passages[sy][sx] & NORTH) != 0

    def connected_neighbors(self, cell: CellCoord) -> list[CellCoord]:
        x, y = cell
        mask = self.passages[y][x]
        neighbors: list[CellCoord] = []
        for direction in _DIRECTION_ORDER:
            if (mask & direction) == 0:
                continue
            offset_x, offset_y = _DIRECTION_TO_OFFSET[direction]
            nx = x + offset_x
            ny = y + offset_y
            if nx < 0 or ny < 0 or nx >= self.width or ny >= self.height:
                continue
            neighbors.append((nx, ny))
        return neighbors

    def shortest_path(self, start: CellCoord, target: CellCoord) -> list[CellCoord]:
        # BFS em grade não ponderada: robusto e previsível para inimigos em tempo real.
        if start == target:
            return [start]

        queue: list[CellCoord] = [start]
        visited = {start}
        previous: dict[CellCoord, CellCoord | None] = {start: None}
        index = 0

        while index < len(queue):
            cell = queue[index]
            index += 1
            if cell == target:
                break

            for neighbor in self.connected_neighbors(cell):
                if neighbor in visited:
                    continue
                visited.add(neighbor)
                previous[neighbor] = cell
                queue.append(neighbor)

        if target not in previous:
            return [start]

        path: list[CellCoord] = []
        current: CellCoord | None = target
        while current is not None:
            path.append(current)
            current = previous[current]
        path.reverse()
        return path

    def random_open_cell(self, rng: random.Random, blocked: Iterable[CellCoord] = ()) -> CellCoord:
        blocked_set = set(blocked)
        candidates: list[CellCoord] = [
            (x, y)
            for y in range(self.height)
            for x in range(self.width)
            if (x, y) not in blocked_set
        ]
        if not candidates:
            return (0, 0)
        return rng.choice(candidates)


@dataclass
class LabyrinthSpatialIndex:
    cell_to_rect_indices: dict[CellCoord, list[int]]

    @classmethod
    def build(cls, layout: LabyrinthLayout) -> LabyrinthSpatialIndex:
        # Índice espacial por célula: reduz colisão parede-entidade para vizinhança local.
        mapping: dict[CellCoord, list[int]] = {}
        for rect_index, rect in enumerate(layout.wall_rects):
            min_cell = layout.to_cell(Vector2(rect.left, rect.top))
            max_cell = layout.to_cell(Vector2(rect.right, rect.bottom))
            if min_cell is None and max_cell is None:
                continue

            min_x = 0 if min_cell is None else min_cell[0]
            min_y = 0 if min_cell is None else min_cell[1]
            max_x = layout.width - 1 if max_cell is None else max_cell[0]
            max_y = layout.height - 1 if max_cell is None else max_cell[1]
            for y in range(max(0, min_y - 1), min(layout.height - 1, max_y + 1) + 1):
                for x in range(max(0, min_x - 1), min(layout.width - 1, max_x + 1) + 1):
                    mapping.setdefault((x, y), []).append(rect_index)
        return cls(cell_to_rect_indices=mapping)

    def nearby_rect_indices(self, cell: CellCoord) -> list[int]:
        return self.cell_to_rect_indices.get(cell, [])


@dataclass
class LabyrinthRuntimeState:
    layout: LabyrinthLayout
    spatial_index: LabyrinthSpatialIndex
    is_boss_level: bool
    has_key: bool = False
    exit_unlocked: bool = False
    boss_keys_required: int = 0
    boss_keys_collected: int = 0


def circle_rect_overlap(circle_position: Vector2, radius: float, rect: Rect) -> tuple[bool, Vector2, float]:
    nearest_x = max(rect.left, min(circle_position.x, rect.right))
    nearest_y = max(rect.top, min(circle_position.y, rect.bottom))
    delta = Vector2(circle_position.x - nearest_x, circle_position.y - nearest_y)
    distance_sq = delta.length_squared()
    if distance_sq > radius * radius:
        return (False, Vector2(), 0.0)

    if distance_sq <= 0.0001:
        distances = [
            (Vector2(-1, 0), abs(circle_position.x - rect.left)),
            (Vector2(1, 0), abs(rect.right - circle_position.x)),
            (Vector2(0, -1), abs(circle_position.y - rect.top)),
            (Vector2(0, 1), abs(rect.bottom - circle_position.y)),
        ]
        normal, min_distance = min(distances, key=lambda item: item[1])
        penetration = radius + min_distance
        return (True, normal, penetration)

    distance = math.sqrt(distance_sq)
    normal = delta / distance
    penetration = radius - distance
    return (True, normal, penetration)


def _dedupe_rects(rects: list[Rect]) -> list[Rect]:
    unique: dict[tuple[int, int, int, int], Rect] = {}
    for rect in rects:
        key = (rect.left, rect.top, rect.width, rect.height)
        unique[key] = rect
    return list(unique.values())
