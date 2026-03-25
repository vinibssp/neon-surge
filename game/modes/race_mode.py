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
from game.systems.shoot_system import ShootSystem
from game.systems.system_pipeline import PipelinePhase, SystemSpec

if TYPE_CHECKING:
    from game.scenes.game_scene import GameScene


class RaceMode(GameModeStrategy):
    def __init__(self, config: RaceConfig | None = None) -> None:
        self.config = RaceConfig() if config is None else config

    def on_enter(self, scene: "GameScene") -> None:
        scene.setup_level(1)

    def on_player_death(self, scene: "GameScene") -> None:
        scene.setup_level(scene.world.level)

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
            SystemSpec(system=InvulnerabilitySystem(world), phase=PipelinePhase.PRE_UPDATE, priority=20),
            SystemSpec(system=FollowSystem(world), phase=PipelinePhase.PRE_UPDATE, priority=30),
            SystemSpec(system=ShootSystem(world), phase=PipelinePhase.PRE_UPDATE, priority=40),
            SystemSpec(system=LifetimeSystem(world), phase=PipelinePhase.PRE_UPDATE, priority=50),
            SystemSpec(system=MovementSystem(world), phase=PipelinePhase.SIMULATION, priority=10),
            SystemSpec(system=CollisionSystem(world), phase=PipelinePhase.POST_UPDATE, priority=10),
        ]
