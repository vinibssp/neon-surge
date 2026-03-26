from __future__ import annotations

from typing import TYPE_CHECKING

from game.core.world import GameWorld
from game.factories.enemy_factory import EnemyFactory
from game.modes.game_mode_strategy import GameModeStrategy
from game.modes.level_progression_strategy import LevelProgressionStrategy, TrainingLevelProgressionStrategy
from game.modes.mode_config import TrainingConfig
from game.modes.spawn_strategy import SpawnStrategy, TrainingSpawnStrategy
from game.systems.collision_system import CollisionSystem
from game.systems.dash_system import DashSystem
from game.systems.follow_system import FollowSystem
from game.systems.invulnerability_system import InvulnerabilitySystem
from game.systems.lifetime_system import LifetimeSystem
from game.systems.movement_system import MovementSystem
from game.systems.parry_system import ParrySystem
from game.systems.shoot_system import ShootSystem
from game.systems.stagger_system import StaggerSystem
from game.systems.system_pipeline import PipelinePhase, SystemSpec

if TYPE_CHECKING:
    from game.scenes.game_scene import GameScene


class TrainingMode(GameModeStrategy):
    def __init__(self, spawn_plan: dict[str, int], config: TrainingConfig | None = None) -> None:
        self.config = TrainingConfig() if config is None else config
        self.spawn_plan = self._sanitize_spawn_plan(spawn_plan)
        self._spawn_strategy: TrainingSpawnStrategy | None = None

    def on_enter(self, scene: "GameScene") -> None:
        scene.setup_level(1)

    def on_player_death(self, scene: "GameScene") -> None:
        elapsed_time = float(scene.elapsed_time)
        reached_level = int(scene.world.level)
        score = self.calcular_ranking(elapsed_time, reached_level)
        death_cause = scene.world.runtime_state.get("last_death_cause")
        total_planned = sum(self.spawn_plan.values())
        remaining_to_spawn = self._spawn_strategy.remaining_to_spawn if self._spawn_strategy is not None else 0
        active_enemies = scene.world.count_by_tag("enemy")
        spawned = total_planned - remaining_to_spawn
        defeated = max(0, spawned - active_enemies)
        scene.open_game_over(
            title="Treino - Derrota",
            subtitle=f"Derrotados: {defeated}/{total_planned}",
            retry_strategy_factory=self.create_retry_strategy,
            death_cause=death_cause if isinstance(death_cause, str) else None,
            include_session_summary=True,
            final_score=score,
        )

    def calcular_ranking(self, elapsed_time: float, reached_level: int) -> float:
        del reached_level
        return round(elapsed_time, 2)

    def configure_level(self, scene: "GameScene", level: int) -> None:
        del scene, level

    def build_level_progression_strategy(self) -> LevelProgressionStrategy:
        if self._spawn_strategy is None:
            self._spawn_strategy = TrainingSpawnStrategy(self.spawn_plan, self.config)
        return TrainingLevelProgressionStrategy(self._spawn_strategy)

    def build_spawn_strategy(self) -> SpawnStrategy:
        self._spawn_strategy = TrainingSpawnStrategy(self.spawn_plan, self.config)
        return self._spawn_strategy

    def build_hud_lines(self, scene: "GameScene") -> list[str]:
        total_planned = sum(self.spawn_plan.values())
        remaining_to_spawn = self._spawn_strategy.remaining_to_spawn if self._spawn_strategy is not None else 0
        active_enemies = scene.world.count_by_tag("enemy")
        spawned = total_planned - remaining_to_spawn
        defeated = max(0, spawned - active_enemies)
        return [
            "Modo: Treino",
            f"Tempo: {scene.elapsed_time:.2f}s",
            f"Planejados: {total_planned}",
            f"Derrotados: {defeated}/{total_planned}",
            f"Restando no campo: {active_enemies}",
        ]

    def create_retry_strategy(self) -> GameModeStrategy:
        return TrainingMode(spawn_plan=dict(self.spawn_plan), config=self.config)

    def build_systems(self, world: GameWorld) -> list[SystemSpec]:
        return [
            SystemSpec(system=DashSystem(world), phase=PipelinePhase.PRE_UPDATE, priority=10),
            SystemSpec(system=ParrySystem(world), phase=PipelinePhase.PRE_UPDATE, priority=15),
            SystemSpec(system=InvulnerabilitySystem(world), phase=PipelinePhase.PRE_UPDATE, priority=20),
            SystemSpec(system=FollowSystem(world), phase=PipelinePhase.PRE_UPDATE, priority=30),
            SystemSpec(system=ShootSystem(world), phase=PipelinePhase.PRE_UPDATE, priority=40),
            SystemSpec(system=LifetimeSystem(world), phase=PipelinePhase.PRE_UPDATE, priority=50),
            SystemSpec(system=StaggerSystem(world), phase=PipelinePhase.PRE_UPDATE, priority=55),
            SystemSpec(system=MovementSystem(world), phase=PipelinePhase.SIMULATION, priority=10),
            SystemSpec(system=CollisionSystem(world), phase=PipelinePhase.POST_UPDATE, priority=10),
        ]

    @staticmethod
    def _sanitize_spawn_plan(spawn_plan: dict[str, int]) -> dict[str, int]:
        registered = set(EnemyFactory.registered_all_kinds())
        sanitized: dict[str, int] = {}
        for kind, count in spawn_plan.items():
            if kind not in registered:
                continue
            sanitized_count = max(0, int(count))
            if sanitized_count > 0:
                sanitized[kind] = sanitized_count
        if sanitized:
            return sanitized
        fallback_kind = EnemyFactory.registered_enemy_kinds()[0]
        return {fallback_kind: 1}
