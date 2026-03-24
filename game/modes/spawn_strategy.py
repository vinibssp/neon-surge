from __future__ import annotations

from abc import ABC, abstractmethod
import random

from game.components.data_components import LifetimeComponent
from game.core.world import GameWorld
from game.ecs.entity import Entity
from game.factories.enemy_factory import EnemyFactory
from game.modes.mode_config import RaceConfig, SurvivalConfig


class SpawnStrategy(ABC):
    @abstractmethod
    def initial_timer(self, world: GameWorld, elapsed_time: float) -> float:
        ...

    @abstractmethod
    def next_interval(self, world: GameWorld, elapsed_time: float) -> float:
        ...

    @abstractmethod
    def choose_enemy_kind(self, world: GameWorld, elapsed_time: float) -> str:
        ...

    @abstractmethod
    def portals_per_cycle(self, world: GameWorld, elapsed_time: float) -> int:
        ...

    @abstractmethod
    def on_enemy_spawned(self, world: GameWorld, enemy: Entity) -> None:
        ...


class RaceSpawnStrategy(SpawnStrategy):
    def __init__(self, config: RaceConfig) -> None:
        self.config = config

    def initial_timer(self, world: GameWorld, elapsed_time: float) -> float:
        return min(self.config.initial_spawn_cap, self.next_interval(world, elapsed_time))

    def next_interval(self, world: GameWorld, elapsed_time: float) -> float:
        del elapsed_time
        return max(
            self.config.spawn_interval_min,
            self.config.spawn_interval_base - world.level * self.config.spawn_interval_level_step,
        )

    def choose_enemy_kind(self, world: GameWorld, elapsed_time: float) -> str:
        del elapsed_time
        category = self._choose_spawn_category(world.level)
        if category == "boss":
            return EnemyFactory.choose_random_boss_kind()
        if category == "miniboss":
            return EnemyFactory.choose_random_miniboss_kind()
        return EnemyFactory.choose_random_enemy_kind()

    def _choose_spawn_category(self, level: int) -> str:
        if level < self.config.miniboss_start_level:
            return "enemy"

        if level < self.config.boss_start_level:
            return "miniboss" if random.random() < self.config.miniboss_spawn_chance else "enemy"

        roll = random.random()
        if roll < self.config.boss_spawn_chance:
            return "boss"
        if roll < self.config.boss_spawn_chance + self.config.miniboss_spawn_chance:
            return "miniboss"
        return "enemy"

    def portals_per_cycle(self, world: GameWorld, elapsed_time: float) -> int:
        del elapsed_time
        return max(1, world.level)

    def on_enemy_spawned(self, world: GameWorld, enemy: Entity) -> None:
        del world, enemy


class SurvivalSpawnStrategy(SpawnStrategy):
    def __init__(self, config: SurvivalConfig) -> None:
        self.config = config

    def initial_timer(self, world: GameWorld, elapsed_time: float) -> float:
        return min(self.config.initial_spawn_cap, self.next_interval(world, elapsed_time))

    def next_interval(self, world: GameWorld, elapsed_time: float) -> float:
        del elapsed_time
        level_offset = max(0, world.level - 1)
        return max(
            self.config.spawn_interval_min,
            self.config.spawn_interval_base - level_offset * self.config.spawn_interval_level_step,
        )

    def choose_enemy_kind(self, world: GameWorld, elapsed_time: float) -> str:
        del world
        category = self._choose_spawn_category(elapsed_time)
        if category == "boss":
            return EnemyFactory.choose_random_boss_kind()
        if category == "miniboss":
            return EnemyFactory.choose_random_miniboss_kind()
        return EnemyFactory.choose_random_enemy_kind()

    def _choose_spawn_category(self, elapsed_time: float) -> str:
        if elapsed_time < self.config.miniboss_start_time:
            return "enemy"

        if elapsed_time < self.config.boss_start_time:
            return "miniboss" if random.random() < self.config.miniboss_spawn_chance else "enemy"

        roll = random.random()
        if roll < self.config.boss_spawn_chance:
            return "boss"
        if roll < self.config.boss_spawn_chance + self.config.miniboss_spawn_chance:
            return "miniboss"
        return "enemy"

    def portals_per_cycle(self, world: GameWorld, elapsed_time: float) -> int:
        del world
        return max(1, int(elapsed_time // self.config.level_duration) + 1)

    def on_enemy_spawned(self, world: GameWorld, enemy: Entity) -> None:
        del world
        enemy.add_component(LifetimeComponent(time_left=self.config.enemy_lifetime))


class OneVsOneSpawnStrategy(SpawnStrategy):
    def initial_timer(self, world: GameWorld, elapsed_time: float) -> float:
        del world, elapsed_time
        return 999_999.0

    def next_interval(self, world: GameWorld, elapsed_time: float) -> float:
        del world, elapsed_time
        return 999_999.0

    def choose_enemy_kind(self, world: GameWorld, elapsed_time: float) -> str:
        del world, elapsed_time
        return EnemyFactory.registered_all_kinds()[0]

    def portals_per_cycle(self, world: GameWorld, elapsed_time: float) -> int:
        del world, elapsed_time
        return 0

    def on_enemy_spawned(self, world: GameWorld, enemy: Entity) -> None:
        del world, enemy
