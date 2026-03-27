from __future__ import annotations

from typing import TYPE_CHECKING

from game.core.enemy_names import format_enemy_name
from game.core.world import GameWorld
from game.factories.enemy_factory import EnemyFactory
from game.modes.game_mode_strategy import GameModeStrategy
from game.modes.level_progression_strategy import LevelProgressionStrategy, OneVsOneLevelProgressionStrategy
from game.modes.spawn_strategy import OneVsOneSpawnStrategy, SpawnStrategy
from game.systems.collision_system import CollisionSystem
from game.systems.dash_system import DashSystem
from game.systems.follow_system import FollowSystem
from game.systems.invulnerability_system import InvulnerabilitySystem
from game.systems.lifetime_system import LifetimeSystem
from game.systems.movement_system import MovementSystem
from game.systems.shoot_system import ShootSystem
from game.systems.system_pipeline import PipelinePhase, SystemSpec

if TYPE_CHECKING:
    from game.core.session_stats import GameSessionStats
    from game.scenes.game_scene import GameScene


class OneVsOneMode(GameModeStrategy):
    def __init__(self, enemy_kinds: list[str] | None = None) -> None:
        registered_kinds = EnemyFactory.registered_all_kinds()
        self.enemy_kinds = registered_kinds if enemy_kinds is None else enemy_kinds
        self._progression: OneVsOneLevelProgressionStrategy | None = None

    def on_enter(self, scene: "GameScene") -> None:
        scene.setup_level(1)

    def on_player_death(self, scene: "GameScene") -> None:
        elapsed_time = float(scene.elapsed_time)
        reached_level = int(scene.world.level)
        score = self.calcular_ranking(elapsed_time, reached_level, scene.session_stats)
        defeated_count = 0
        if self._progression is not None:
            defeated_count = max(0, self._progression.current_enemy_index)
        death_cause = scene.world.runtime_state.get("last_death_cause")
        scene.open_game_over(
            title="GAME OVER",
            subtitle=f"Rounds completos: {defeated_count}/{len(self.enemy_kinds)}",
            retry_strategy_factory=self.create_retry_strategy,
            death_cause=death_cause if isinstance(death_cause, str) else None,
            include_session_summary=True,
            final_score=score,
        )

    def mode_key(self) -> str:
        return "OneVsOne"

    def calcular_ranking(self, elapsed_time: float, reached_level: int, session_stats: "GameSessionStats") -> float:
        return round(sum(points for _, points in self.score_breakdown(elapsed_time, reached_level, session_stats)), 2)

    def score_breakdown(
        self,
        elapsed_time: float,
        reached_level: int,
        session_stats: "GameSessionStats",
    ) -> list[tuple[str, float]]:
        del reached_level
        portal_count = session_stats.spawn_portal_destroyed_total
        parry_count = session_stats.parry_landed_total
        return [
            (f"Tempo ({elapsed_time:.1f}s)", elapsed_time),
            (f"Portais ({portal_count}x5)", portal_count * 5.0),
            (f"Parry ({parry_count}x5)", parry_count * 5.0),
        ]

    def configure_level(self, scene: "GameScene", level: int) -> None:
        del scene, level

    def build_level_progression_strategy(self) -> LevelProgressionStrategy:
        progression = OneVsOneLevelProgressionStrategy(enemy_kinds=list(self.enemy_kinds))
        self._progression = progression
        return progression

    def build_spawn_strategy(self) -> SpawnStrategy:
        return OneVsOneSpawnStrategy()

    def build_hud_lines(self, scene: "GameScene") -> list[str]:
        total = len(self.enemy_kinds)
        current_name = "-"
        current_round = scene.world.level
        time_left = 0.0
        if self._progression is not None:
            enemy_kind = self._progression.current_enemy_kind
            if enemy_kind is not None:
                current_name = format_enemy_name(enemy_kind)
            current_round = max(1, min(self._progression.current_enemy_index + 1, total if total > 0 else 1))
            time_left = self._progression.round_time_left

        objective_line = (
            "Objetivo: entre no portal"
            if self._progression is not None and self._progression.awaiting_portal
            else f"Sobreviva: {time_left:.1f}s"
        )

        return [
            "Modo: 1v1",
            f"Tempo: {scene.elapsed_time:.2f}s",
            f"Round: {current_round}/{max(1, total)}",
            f"Inimigo: {current_name}",
            objective_line,
        ]

    def create_retry_strategy(self) -> GameModeStrategy:
        return OneVsOneMode(enemy_kinds=list(self.enemy_kinds))

    def build_systems(self, world: GameWorld) -> list[SystemSpec]:
        return [
            SystemSpec(system=DashSystem(world), phase=PipelinePhase.PRE_UPDATE, priority=10),
            SystemSpec(system=InvulnerabilitySystem(world), phase=PipelinePhase.PRE_UPDATE, priority=20),
            SystemSpec(system=FollowSystem(world), phase=PipelinePhase.PRE_UPDATE, priority=30),
            SystemSpec(system=ShootSystem(world), phase=PipelinePhase.PRE_UPDATE, priority=40),
            SystemSpec(system=LifetimeSystem(world), phase=PipelinePhase.PRE_UPDATE, priority=50),
            SystemSpec(system=MovementSystem(world), phase=PipelinePhase.SIMULATION, priority=10),
            SystemSpec(system=CollisionSystem(world), phase=PipelinePhase.POST_UPDATE, priority=10),
        ]

