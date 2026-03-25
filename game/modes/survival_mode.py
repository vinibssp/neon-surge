from __future__ import annotations

from typing import TYPE_CHECKING

from game.components.data_components import NuclearBombComponent
from game.core.world import GameWorld
from game.modes.game_mode_strategy import GameModeStrategy
from game.modes.level_progression_strategy import LevelProgressionStrategy, SurvivalLevelProgressionStrategy
from game.modes.mode_config import SurvivalConfig
from game.modes.spawn_strategy import SpawnStrategy, SurvivalSpawnStrategy
from game.systems.collision_system import CollisionSystem
from game.systems.dash_system import DashSystem
from game.systems.environment_event_system import EnvironmentEventSystem
from game.systems.follow_system import FollowSystem
from game.systems.invulnerability_system import InvulnerabilitySystem
from game.systems.lifetime_system import LifetimeSystem
from game.systems.movement_system import MovementSystem
from game.systems.nuclear_bomb_system import NuclearBombSystem
from game.systems.parry_system import ParrySystem
from game.systems.shoot_system import ShootSystem
from game.systems.stagger_system import StaggerSystem
from game.systems.survival_collectible_system import SurvivalCollectibleSystem
from game.systems.system_pipeline import PipelinePhase, SystemSpec

if TYPE_CHECKING:
    from game.scenes.game_scene import GameScene


class SurvivalMode(GameModeStrategy):
    def __init__(self, config: SurvivalConfig | None = None) -> None:
        self.config = SurvivalConfig() if config is None else config

    def on_enter(self, scene: "GameScene") -> None:
        scene.setup_level(1)
        player = scene.world.player
        if player is not None and player.get_component(NuclearBombComponent) is None:
            player.add_component(NuclearBombComponent())

    def on_player_death(self, scene: "GameScene") -> None:
        death_cause = scene.world.runtime_state.get("last_death_cause")
        scene.open_game_over(
            title="Game Over",
            subtitle=f"Sobreviveu: {scene.elapsed_time:.2f}s",
            retry_strategy_factory=self.create_retry_strategy,
            death_cause=death_cause if isinstance(death_cause, str) else None,
            include_session_summary=True,
        )

    def configure_level(self, scene: "GameScene", level: int) -> None:
        del scene, level

    def build_level_progression_strategy(self) -> LevelProgressionStrategy:
        return SurvivalLevelProgressionStrategy(config=self.config)

    def build_spawn_strategy(self) -> SpawnStrategy:
        return SurvivalSpawnStrategy(config=self.config)

    def build_hud_lines(self, scene: "GameScene") -> list[str]:
        bomb_charges = 0
        player = scene.world.player
        if player is not None:
            bomb = player.get_component(NuclearBombComponent)
            if bomb is not None:
                bomb_charges = bomb.charges

        return [
            f"Tempo vivo: {scene.elapsed_time:.1f}s",
            f"Moedas: {scene.session_stats.collectible_collected_total}",
            f"Bomba [I]: {bomb_charges} carga(s)",
        ]

    def create_retry_strategy(self) -> GameModeStrategy:
        return SurvivalMode(config=self.config)

    def build_systems(self, world: GameWorld) -> list[SystemSpec]:
        return [
            SystemSpec(system=DashSystem(world), phase=PipelinePhase.PRE_UPDATE, priority=10),
            SystemSpec(system=ParrySystem(world), phase=PipelinePhase.PRE_UPDATE, priority=15),
            SystemSpec(system=InvulnerabilitySystem(world), phase=PipelinePhase.PRE_UPDATE, priority=20),
            SystemSpec(system=NuclearBombSystem(world), phase=PipelinePhase.PRE_UPDATE, priority=22),
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
                ),
                phase=PipelinePhase.PRE_UPDATE,
                priority=25,
            ),
            SystemSpec(
                system=SurvivalCollectibleSystem(
                    world=world,
                    spawn_interval=self.config.collectible_spawn_interval,
                    spawn_cap=self.config.collectible_spawn_cap,
                ),
                phase=PipelinePhase.PRE_UPDATE,
                priority=28,
            ),
            SystemSpec(system=FollowSystem(world), phase=PipelinePhase.PRE_UPDATE, priority=30),
            SystemSpec(system=ShootSystem(world), phase=PipelinePhase.PRE_UPDATE, priority=40),
            SystemSpec(system=LifetimeSystem(world), phase=PipelinePhase.PRE_UPDATE, priority=50),
            SystemSpec(system=StaggerSystem(world), phase=PipelinePhase.PRE_UPDATE, priority=55),
            SystemSpec(system=MovementSystem(world), phase=PipelinePhase.SIMULATION, priority=10),
            SystemSpec(system=CollisionSystem(world), phase=PipelinePhase.POST_UPDATE, priority=10),
        ]
