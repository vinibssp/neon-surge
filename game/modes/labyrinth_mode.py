from __future__ import annotations

import random
from typing import TYPE_CHECKING

from pygame import Vector2

from game.components.data_components import MovementComponent, TransformComponent
from game.core.world import GameWorld
from game.factories.enemy_factory import EnemyFactory
from game.factories.labyrinth_factory import LabyrinthFactory
from game.modes.game_mode_strategy import GameModeStrategy
from game.modes.labyrinth_layout import LabyrinthLayout, LabyrinthRuntimeState, LabyrinthSpatialIndex
from game.modes.level_progression_strategy import LabyrinthLevelProgressionStrategy, LevelProgressionStrategy
from game.modes.mode_config import LabyrinthConfig
from game.modes.spawn_strategy import LabyrinthSpawnStrategy, SpawnStrategy
from game.systems.collision_system import CollisionSystem
from game.systems.dash_system import DashSystem
from game.systems.follow_system import FollowSystem
from game.systems.invulnerability_system import InvulnerabilitySystem
from game.systems.labyrinth_ai_system import LabyrinthAISystem
from game.systems.labyrinth_collision_system import LabyrinthCollisionSystem
from game.systems.labyrinth_objective_system import LabyrinthObjectiveSystem
from game.systems.lifetime_system import LifetimeSystem
from game.systems.movement_system import MovementSystem
from game.systems.shoot_system import ShootSystem
from game.systems.system_pipeline import PipelinePhase, SystemSpec

if TYPE_CHECKING:
    from game.scenes.game_scene import GameScene


class LabyrinthMode(GameModeStrategy):
    def __init__(self, config: LabyrinthConfig | None = None, seed: int | None = None) -> None:
        self.config = LabyrinthConfig() if config is None else config
        self._rng = random.Random(seed)
        self._runtime_state: LabyrinthRuntimeState | None = None

    def on_enter(self, scene: "GameScene") -> None:
        scene.setup_level(1)

    def on_player_death(self, scene: "GameScene") -> None:
        death_cause = scene.world.runtime_state.get("last_death_cause")
        scene.open_game_over(
            title="Labirinto - Falha de Sistema",
            subtitle=f"Nivel alcancado: {scene.world.level}",
            retry_strategy_factory=self.create_retry_strategy,
            death_cause=death_cause if isinstance(death_cause, str) else None,
            include_session_summary=True,
        )

    def configure_level(self, scene: "GameScene", level: int) -> None:
        is_boss_level = level % self.config.boss_level_interval == 0
        if is_boss_level:
            self._configure_boss_arena(scene, level)
            return

        difficulty = LabyrinthLayout.difficulty_for_level(level)
        geometry = LabyrinthLayout.geometry_for_bounds(
            screen_width=scene.world.width,
            screen_height=scene.world.height,
            grid_width=difficulty.grid_width,
            grid_height=difficulty.grid_height,
        )
        layout = LabyrinthLayout.generate(
            width=difficulty.grid_width,
            height=difficulty.grid_height,
            geometry=geometry,
            rng=self._rng,
        )
        spatial_index = LabyrinthSpatialIndex.build(layout)
        self._runtime_state = LabyrinthRuntimeState(
            layout=layout,
            spatial_index=spatial_index,
            is_boss_level=False,
            has_key=False,
            exit_unlocked=False,
        )

        self._position_player(scene, level, layout)

        player_cell = self._player_cell(layout, scene)
        key_cell = self._choose_key_cell(layout, player_cell)

        for wall_rect in layout.wall_rects:
            scene.world.add_entity(LabyrinthFactory.create_wall_visual(wall_rect=wall_rect))

        key_position = layout.cell_center(key_cell)
        scene.world.add_entity(LabyrinthFactory.create_key(key_position))

        exit_position = self._border_exit_position(layout)
        scene.world.add_entity(LabyrinthFactory.create_exit(position=exit_position, unlocked=False))

        blocked_cells = {key_cell, layout.border_exit_cell, player_cell}
        for index in range(difficulty.enemy_count):
            spawn_cell = self._choose_enemy_spawn_cell(
                layout=layout,
                blocked_cells=blocked_cells,
                player_cell=player_cell,
                min_cell_distance=3,
            )
            blocked_cells.add(spawn_cell)
            behavior_kind = "chaser" if index % 2 == 0 else "interceptor"
            speed = self.config.base_enemy_speed * difficulty.enemy_speed_multiplier
            virus = LabyrinthFactory.create_virus(
                position=layout.cell_center(spawn_cell),
                behavior_kind=behavior_kind,
                speed=speed,
            )
            scene.world.add_entity(virus)

    def build_level_progression_strategy(self) -> LevelProgressionStrategy:
        return LabyrinthLevelProgressionStrategy()

    def build_spawn_strategy(self) -> SpawnStrategy:
        return LabyrinthSpawnStrategy()

    def build_hud_lines(self, scene: "GameScene") -> list[str]:
        runtime = self._runtime_state
        if runtime is None:
            return [
                "Modo: Labirinto",
                f"Tempo: {scene.elapsed_time:.2f}s",
                f"Nivel: {scene.world.level}",
            ]

        if runtime.is_boss_level:
            remaining_keys = max(0, runtime.boss_keys_required - runtime.boss_keys_collected)
            return [
                "Modo: Labirinto",
                f"Tempo: {scene.elapsed_time:.2f}s",
                f"Nivel: {scene.world.level} (Boss Arena)",
                f"Chaves: {runtime.boss_keys_collected}/{runtime.boss_keys_required}",
                ("Objetivo: colete todas as chaves" if remaining_keys > 0 else "Objetivo: avancando"),
            ]

        key_status = "coletada" if runtime.has_key else "pendente"
        exit_status = "desbloqueada" if runtime.exit_unlocked else "bloqueada"
        return [
            "Modo: Labirinto",
            f"Tempo: {scene.elapsed_time:.2f}s",
            f"Nivel: {scene.world.level}",
            f"Chave: {key_status}",
            f"Saida: {exit_status}",
        ]

    def create_retry_strategy(self) -> GameModeStrategy:
        return LabyrinthMode(config=self.config)

    def build_systems(self, world: GameWorld) -> list[SystemSpec]:
        runtime_provider = self._get_runtime_state
        return [
            SystemSpec(system=DashSystem(world), phase=PipelinePhase.PRE_UPDATE, priority=10),
            SystemSpec(system=InvulnerabilitySystem(world), phase=PipelinePhase.PRE_UPDATE, priority=20),
            SystemSpec(system=FollowSystem(world), phase=PipelinePhase.PRE_UPDATE, priority=30),
            SystemSpec(system=ShootSystem(world), phase=PipelinePhase.PRE_UPDATE, priority=40),
            SystemSpec(system=LifetimeSystem(world), phase=PipelinePhase.PRE_UPDATE, priority=50),
            SystemSpec(system=LabyrinthAISystem(world, runtime_provider), phase=PipelinePhase.PRE_UPDATE, priority=60),
            SystemSpec(system=MovementSystem(world), phase=PipelinePhase.SIMULATION, priority=10),
            SystemSpec(
                system=LabyrinthCollisionSystem(world, runtime_provider),
                phase=PipelinePhase.POST_UPDATE,
                priority=5,
            ),
            SystemSpec(system=CollisionSystem(world), phase=PipelinePhase.POST_UPDATE, priority=10),
            SystemSpec(
                system=LabyrinthObjectiveSystem(world, runtime_provider),
                phase=PipelinePhase.POST_UPDATE,
                priority=20,
            ),
        ]

    def _configure_boss_arena(self, scene: "GameScene", level: int) -> None:
        geometry = LabyrinthLayout.geometry_for_bounds(
            screen_width=scene.world.width,
            screen_height=scene.world.height,
            grid_width=3,
            grid_height=3,
        )
        layout = LabyrinthLayout.generate(width=3, height=3, geometry=geometry, rng=self._rng)
        self._runtime_state = LabyrinthRuntimeState(
            layout=layout,
            spatial_index=LabyrinthSpatialIndex(cell_to_rect_indices={}),
            is_boss_level=True,
            has_key=True,
            exit_unlocked=True,
            boss_keys_required=self.config.boss_keys_required,
            boss_keys_collected=0,
        )
        self._position_player_in_arena(scene)

        boss_kind = EnemyFactory.choose_random_boss_kind()
        boss = EnemyFactory.create_by_kind(boss_kind, Vector2(scene.world.width * 0.5, scene.world.height * 0.5))
        boss_movement = boss.get_component(MovementComponent)
        if boss_movement is not None:
            boss_movement.max_speed *= 0.9 + (level * self.config.boss_speed_gain_per_level)
        scene.world.add_entity(boss)

        for key_position in self._build_boss_key_positions(scene):
            scene.world.add_entity(LabyrinthFactory.create_key(key_position))

        support_count = min(3, 1 + level // 12)
        player_position = Vector2(scene.world.width * 0.8, scene.world.height * 0.8)
        for _ in range(support_count):
            spawn_position = self._choose_arena_enemy_spawn_position(scene, player_position)
            support_enemy = LabyrinthFactory.create_virus(
                position=spawn_position,
                behavior_kind=self._rng.choice(("chaser", "interceptor")),
                speed=self.config.base_enemy_speed * (1.05 + level * 0.015),
                radius=11.0,
            )
            scene.world.add_entity(support_enemy)

    def _position_player(self, scene: "GameScene", level: int, layout: LabyrinthLayout) -> None:
        del level
        player = scene.world.player
        if player is None:
            return
        player_transform = player.get_component(TransformComponent)
        if player_transform is None:
            return

        spawn_cell = (layout.width - 1, layout.height - 1)
        player_transform.position = layout.cell_center(spawn_cell)

    def _player_cell(self, layout: LabyrinthLayout, scene: "GameScene") -> tuple[int, int]:
        player = scene.world.player
        if player is None:
            return (0, 0)
        player_transform = player.get_component(TransformComponent)
        if player_transform is None:
            return (0, 0)
        cell = layout.to_cell(player_transform.position)
        return (0, 0) if cell is None else cell

    @staticmethod
    def _choose_key_cell(layout: LabyrinthLayout, player_cell: tuple[int, int]) -> tuple[int, int]:
        exit_center = layout.cell_center(layout.border_exit_cell)
        player_center = layout.cell_center(player_cell)
        best_cell = layout.key_cell
        best_distance = -1.0
        for y in range(layout.height):
            for x in range(layout.width):
                cell = (x, y)
                if cell == player_cell or cell == layout.border_exit_cell:
                    continue
                center = layout.cell_center(cell)
                distance_sq = (center - exit_center).length_squared() + (center - player_center).length_squared()
                if distance_sq > best_distance:
                    best_distance = distance_sq
                    best_cell = cell
        return best_cell

    @staticmethod
    def _border_exit_position(layout: LabyrinthLayout) -> Vector2:
        cell = layout.border_exit_cell
        center = layout.cell_center(cell)
        x, y = cell
        offset = layout.geometry.cell_size * 0.52
        if y == 0:
            return center + Vector2(0.0, -offset)
        if y == layout.height - 1:
            return center + Vector2(0.0, offset)
        if x == 0:
            return center + Vector2(-offset, 0.0)
        return center + Vector2(offset, 0.0)

    def _position_player_in_arena(self, scene: "GameScene") -> None:
        player = scene.world.player
        if player is None:
            return
        transform = player.get_component(TransformComponent)
        if transform is None:
            return
        transform.position = Vector2(scene.world.width * 0.8, scene.world.height * 0.8)

    def _get_runtime_state(self) -> LabyrinthRuntimeState | None:
        return self._runtime_state

    def _choose_enemy_spawn_cell(
        self,
        layout: LabyrinthLayout,
        blocked_cells: set[tuple[int, int]],
        player_cell: tuple[int, int],
        min_cell_distance: int,
    ) -> tuple[int, int]:
        min_distance_sq = float(min_cell_distance * min_cell_distance)
        candidates: list[tuple[int, int]] = []
        fallback: list[tuple[int, int]] = []
        for y in range(layout.height):
            for x in range(layout.width):
                cell = (x, y)
                if cell in blocked_cells:
                    continue
                fallback.append(cell)
                dx = x - player_cell[0]
                dy = y - player_cell[1]
                if (dx * dx) + (dy * dy) >= min_distance_sq:
                    candidates.append(cell)

        if candidates:
            return self._rng.choice(candidates)
        if fallback:
            return self._rng.choice(fallback)
        return layout.random_open_cell(self._rng, blocked=blocked_cells)

    def _choose_arena_enemy_spawn_position(self, scene: "GameScene", player_position: Vector2) -> Vector2:
        min_distance = 180.0
        min_distance_sq = min_distance * min_distance
        for _ in range(40):
            candidate = Vector2(
                self._rng.uniform(scene.world.width * 0.15, scene.world.width * 0.85),
                self._rng.uniform(scene.world.height * 0.15, scene.world.height * 0.85),
            )
            if (candidate - player_position).length_squared() >= min_distance_sq:
                return candidate
        return Vector2(scene.world.width * 0.2, scene.world.height * 0.2)

    def _build_boss_key_positions(self, scene: "GameScene") -> list[Vector2]:
        keys: list[Vector2] = []
        if self.config.boss_keys_required <= 0:
            return keys

        min_key_distance = 80.0
        min_player_distance = 160.0
        player_position = Vector2(scene.world.width * 0.8, scene.world.height * 0.8)
        min_key_distance_sq = min_key_distance * min_key_distance
        min_player_distance_sq = min_player_distance * min_player_distance

        for _ in range(self.config.boss_keys_required):
            selected: Vector2 | None = None
            for _ in range(120):
                candidate = Vector2(
                    self._rng.uniform(scene.world.width * 0.15, scene.world.width * 0.85),
                    self._rng.uniform(scene.world.height * 0.15, scene.world.height * 0.85),
                )
                if (candidate - player_position).length_squared() < min_player_distance_sq:
                    continue
                if any((candidate - existing).length_squared() < min_key_distance_sq for existing in keys):
                    continue
                selected = candidate
                break

            if selected is None:
                selected = Vector2(
                    self._rng.uniform(scene.world.width * 0.2, scene.world.width * 0.8),
                    self._rng.uniform(scene.world.height * 0.2, scene.world.height * 0.8),
                )
            keys.append(selected)
        return keys
