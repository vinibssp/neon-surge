from __future__ import annotations

from typing import TYPE_CHECKING

from game.core.world import GameWorld
from game.factories.collectible_factory import CollectibleFactory
from game.modes.game_mode_strategy import GameModeStrategy
from game.modes.level_progression_strategy import LevelProgressionStrategy, RaceLevelProgressionStrategy
from game.modes.mode_config import RaceConfig
from game.modes.spawn_strategy import RaceSpawnStrategy, SpawnStrategy
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
    from game.core.session_stats import GameSessionStats
    from game.scenes.game_scene import GameScene


class RaceMode(GameModeStrategy):
    def __init__(self, config: RaceConfig | None = None) -> None:
        self.config = RaceConfig() if config is None else config

    def on_enter(self, scene: "GameScene") -> None:
        scene.setup_level(1)

    def on_player_death(self, scene: "GameScene") -> None:
        elapsed_time = float(scene.elapsed_time)
        reached_level = int(scene.world.level)
        score = self.calcular_ranking(elapsed_time, reached_level, scene.session_stats)
        death_cause = scene.world.runtime_state.get("last_death_cause")
        scene.open_game_over(
            title="GAME OVER",
            subtitle=f"Tempo: {scene.elapsed_time:.2f}s",
            retry_strategy_factory=self.create_retry_strategy,
            death_cause=death_cause if isinstance(death_cause, str) else None,
            include_session_summary=True,
            final_score=score,
        )

    def mode_key(self) -> str:
        return "Race"

    def calcular_ranking(self, elapsed_time: float, reached_level: int, session_stats: "GameSessionStats") -> float:
        return round(sum(points for _, points in self.score_breakdown(elapsed_time, reached_level, session_stats)), 2)

    def score_breakdown(
        self,
        elapsed_time: float,
        reached_level: int,
        session_stats: "GameSessionStats",
    ) -> list[tuple[str, float]]:
        portal_count = session_stats.spawn_portal_destroyed_total
        parry_count = session_stats.parry_landed_total
        return [
            (f"Nivel ({reached_level}x100)", reached_level * 100.0),
            (f"Tempo (-{elapsed_time:.1f}s)", -elapsed_time),
            (f"Portais ({portal_count}x5)", portal_count * 5.0),
            (f"Parry ({parry_count}x5)", parry_count * 5.0),
        ]

    def configure_level(self, scene: "GameScene", level: int) -> None:
        growth_steps = max(0, (level - 1) // max(1, self.config.collectible_growth_every))
        collectible_count = self.config.collectible_base + growth_steps * self.config.collectible_growth_step
        for _ in range(collectible_count):
            scene.world.add_entity(CollectibleFactory.create(scene.random_play_area_position()))

    def build_level_progression_strategy(self) -> LevelProgressionStrategy:
        return RaceLevelProgressionStrategy(config=self.config)

    def build_spawn_strategy(self) -> SpawnStrategy:
        return RaceSpawnStrategy(config=self.config)

    def build_hud_lines(self, scene: "GameScene") -> list[str]:
        return [
            "Modo: Corrida",
            f"Tempo: {scene.elapsed_time:.2f}s",
            f"Nivel: {scene.world.level}/{self.config.total_levels}",
        ]

    def create_retry_strategy(self) -> GameModeStrategy:
        return RaceMode(config=self.config)

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
