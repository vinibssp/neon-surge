from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from game.core.events import PortalActivated
from game.factories.portal_factory import PortalFactory
from game.factories.enemy_factory import EnemyFactory
from game.modes.spawn_strategy import TrainingSpawnStrategy
from game.modes.mode_config import RaceConfig, SurvivalConfig
from game.systems.world_queries import PORTAL_SPAWN_QUERY

if TYPE_CHECKING:
    from game.scenes.game_scene import GameScene


class LevelProgressionStrategy(ABC):
    @abstractmethod
    def update(self, scene: "GameScene", dt: float) -> None:
        ...

    @abstractmethod
    def on_level_portal_crossed(self, scene: "GameScene") -> None:
        ...


class RaceLevelProgressionStrategy(LevelProgressionStrategy):
    def __init__(self, config: RaceConfig) -> None:
        self.config = config

    def update(self, scene: "GameScene", dt: float) -> None:
        del dt
        if scene.world.count_by_tag("collectible") == 0 and not scene.level_portal_spawned:
            scene.world.add_entity(PortalFactory.create_level_portal(scene.random_play_area_position()))
            scene.world.event_bus.publish(PortalActivated(portal_kind="level"))
            scene.level_portal_spawned = True

    def on_level_portal_crossed(self, scene: "GameScene") -> None:
        if not self.config.infinite and scene.world.level >= self.config.total_levels:
            final_score = scene.mode.calcular_ranking(scene.elapsed_time, scene.world.level, scene.session_stats)
            scene.open_game_over(
                title="Corrida Completa",
                subtitle=f"Tempo: {scene.elapsed_time:.2f}s",
                retry_strategy_factory=scene.mode.create_retry_strategy,
                final_score=final_score,
            )
            return
        scene.setup_level(scene.world.level + 1)


class SurvivalLevelProgressionStrategy(LevelProgressionStrategy):
    def __init__(self, config: SurvivalConfig) -> None:
        self.config = config

    def update(self, scene: "GameScene", dt: float) -> None:
        del dt
        target_level = int(scene.elapsed_time // self.config.level_duration) + 1
        if target_level > scene.world.level:
            scene.world.level = target_level

    def on_level_portal_crossed(self, scene: "GameScene") -> None:
        del scene


class OneVsOneLevelProgressionStrategy(LevelProgressionStrategy):
    def __init__(self, enemy_kinds: list[str], round_duration: float = 1.0) -> None:
        self.enemy_kinds = enemy_kinds
        self.round_duration = round_duration
        self.current_enemy_index = -1
        self.current_enemy_kind: str | None = None
        self.round_time_left = round_duration
        self.awaiting_portal = False
        self._completed = False

    @property
    def total_enemies(self) -> int:
        return len(self.enemy_kinds)

    def update(self, scene: "GameScene", dt: float) -> None:
        if self._completed:
            return

        if self.current_enemy_kind is None:
            self._start_next_round(scene)
            return

        if self.awaiting_portal:
            if not scene.level_portal_spawned:
                scene.world.add_entity(PortalFactory.create_level_portal(scene.random_play_area_position()))
                scene.world.event_bus.publish(PortalActivated(portal_kind="level"))
                scene.level_portal_spawned = True
            return

        self.round_time_left = max(0.0, self.round_time_left - dt)
        if self.round_time_left > 0.0:
            return

        self.awaiting_portal = True
        if not scene.level_portal_spawned:
            scene.world.add_entity(PortalFactory.create_level_portal(scene.random_play_area_position()))
            scene.world.event_bus.publish(PortalActivated(portal_kind="level"))
            scene.level_portal_spawned = True

    def on_level_portal_crossed(self, scene: "GameScene") -> None:
        if self._completed:
            return
        if self.current_enemy_index >= self.total_enemies - 1:
            self._completed = True
            final_score = scene.mode.calcular_ranking(scene.elapsed_time, scene.world.level, scene.session_stats)
            scene.open_game_over(
                title="1v1 Completo",
                subtitle=f"Sobreviveu a {self.total_enemies} inimigos",
                retry_strategy_factory=scene.mode.create_retry_strategy,
                final_score=final_score,
            )
            return

        self.current_enemy_kind = None
        self.awaiting_portal = False
        scene.setup_level(scene.world.level + 1)

    def _start_next_round(self, scene: "GameScene") -> None:
        next_index = self.current_enemy_index + 1
        if next_index >= self.total_enemies:
            self._completed = True
            final_score = scene.mode.calcular_ranking(scene.elapsed_time, scene.world.level, scene.session_stats)
            scene.open_game_over(
                title="1v1 Completo",
                subtitle=f"Sobreviveu a {self.total_enemies} inimigos",
                retry_strategy_factory=scene.mode.create_retry_strategy,
                final_score=final_score,
            )
            return

        enemy_kind = self.enemy_kinds[next_index]
        self.current_enemy_index = next_index
        self.current_enemy_kind = enemy_kind
        self.round_time_left = self.round_duration
        self.awaiting_portal = False
        scene.world.level = next_index + 1
        scene.world.add_entity(EnemyFactory.create_by_kind(enemy_kind, scene.random_play_area_position()))


class LabyrinthLevelProgressionStrategy(LevelProgressionStrategy):
    def update(self, scene: "GameScene", dt: float) -> None:
        del scene, dt

    def on_level_portal_crossed(self, scene: "GameScene") -> None:
        scene.setup_level(scene.world.level + 1)


class TrainingLevelProgressionStrategy(LevelProgressionStrategy):
    def __init__(self, spawn_strategy: TrainingSpawnStrategy) -> None:
        self._spawn_strategy = spawn_strategy
        self._completed = False

    def update(self, scene: "GameScene", dt: float) -> None:
        del dt
        if self._completed:
            return
        if self._spawn_strategy.remaining_to_spawn > 0:
            return
        if scene.world.count_by_tag("enemy") > 0:
            return
        if scene.world.query(PORTAL_SPAWN_QUERY):
            return

        self._completed = True
        final_score = scene.mode.calcular_ranking(scene.elapsed_time, scene.world.level, scene.session_stats)
        scene.open_game_over(
            title="Treino Completo",
            subtitle=f"Derrotou {self._spawn_strategy.total_planned} inimigos selecionados",
            retry_strategy_factory=scene.mode.create_retry_strategy,
            include_session_summary=True,
            final_score=final_score,
        )

    def on_level_portal_crossed(self, scene: "GameScene") -> None:
        del scene

