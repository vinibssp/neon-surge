from __future__ import annotations

from typing import TYPE_CHECKING

from game.core.world import GameWorld
from game.modes.game_mode_strategy import GameModeStrategy
from game.modes.level_progression_strategy import LevelProgressionStrategy, SurvivalLevelProgressionStrategy
from game.modes.mode_config import SurvivalConfig
from game.modes.spawn_strategy import SpawnStrategy, SurvivalSpawnStrategy
from game.systems.collision_system import CollisionSystem
from game.systems.dash_system import DashSystem
from game.systems.follow_system import FollowSystem
from game.systems.invulnerability_system import InvulnerabilitySystem
from game.systems.lifetime_system import LifetimeSystem
from game.systems.movement_system import MovementSystem
from game.systems.shoot_system import ShootSystem
from game.systems.system_pipeline import PipelinePhase, SystemSpec

if TYPE_CHECKING:
    from game.scenes.game_scene import GameScene


class SurvivalMode(GameModeStrategy):
    def __init__(self, config: SurvivalConfig | None = None) -> None:
        self.config = SurvivalConfig() if config is None else config

    def on_enter(self, scene: "GameScene") -> None:
        scene.setup_level(1)

    def on_player_death(self, scene: "GameScene") -> None:
        scene.open_game_over(
            title="Game Over",
            subtitle=f"Sobreviveu: {scene.elapsed_time:.2f}s",
            retry_strategy_factory=self.create_retry_strategy,
        )

    def configure_level(self, scene: "GameScene", level: int) -> None:
        del scene, level

    def build_level_progression_strategy(self) -> LevelProgressionStrategy:
        return SurvivalLevelProgressionStrategy(config=self.config)

    def build_spawn_strategy(self) -> SpawnStrategy:
        return SurvivalSpawnStrategy(config=self.config)

    def build_hud_lines(self, scene: "GameScene") -> list[str]:
        return [
            "Modo: Sobrevivencia",
            f"Tempo: {scene.elapsed_time:.2f}s",
            f"Nivel: {scene.world.level}",
        ]

    def create_retry_strategy(self) -> GameModeStrategy:
        return SurvivalMode(config=self.config)

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
