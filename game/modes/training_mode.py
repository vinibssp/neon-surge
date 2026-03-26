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
from game.systems.environment_event_system import EnvironmentEventSystem
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
        )

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
            SystemSpec(
                system=EnvironmentEventSystem(
                    world=world,
                    interval=self.config.env_event_interval,
                    duration=self.config.env_event_duration,
                    snow_drag_multiplier=self.config.snow_drag_multiplier,
                    snow_turn_response=self.config.snow_turn_response,
                    water_pirate_count=self.config.water_pirate_count,
                    bullet_cloud_fire_interval=self.config.bullet_cloud_fire_interval,
                    black_hole_pull_radius=self.config.black_hole_pull_radius,
                    black_hole_pull_strength=self.config.black_hole_pull_strength,
                    black_hole_speed=self.config.black_hole_speed,
                    black_hole_consume_radius=self.config.black_hole_consume_radius,
                    lava_warning_duration=self.config.lava_warning_duration,
                    lava_active_duration=self.config.lava_active_duration,
                    lava_blink_duration=self.config.lava_blink_duration,
                    lava_height_ratio=self.config.lava_height_ratio,
                    forced_event=self.config.forced_environment_event,
                ),
                phase=PipelinePhase.PRE_UPDATE,
                priority=45,
            ),
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
