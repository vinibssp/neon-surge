from __future__ import annotations

from abc import ABC, abstractmethod
import random

from game.components.data_components import LifetimeComponent
from game.core.world import GameWorld
from game.ecs.entity import Entity
from game.factories.enemy_factory import EnemyFactory
from game.modes.mode_config import RaceConfig, SurvivalConfig


EARLY_ENEMY_KINDS: tuple[str, ...] = (
    "follower",
    "shooter",
    "quique",
    "investida",
    "explosivo",
)

MID_ENEMY_KINDS: tuple[str, ...] = (
    *EARLY_ENEMY_KINDS,
    "bandido_arcano",
    "mago_hobbit",
    "escorpiao_rainha",
    "abominacao_limo",
    "olho_orbitante",
    "vigia_supressor",
    "xama_mineiro",
    "algoz_faseado",
    "cavaleiro_voraz",
    "caotico_estilha",
    "metralhadora",
    "morteiro",
    "estrafador_arcano",
    "emboscador_escopeta",
    "orbitador_hex",
    "sombra_investida",
)

LATE_ENEMY_KINDS: tuple[str, ...] = (
    *MID_ENEMY_KINDS,
    "bombardeiro_runa",
    "atirador_laser",
    "kamehameha",
    "lanca_chamas",
    "fantasma",
    "buffer",
    "sapo",
    "gazer_vazio",
    "assassino_crepuscular",
    "sentinela_estelar",
    "necrolorde_orbital",
    "horror_igneo",
    "espectro_lancante",
    "aracnideo_venenoso",
    "bombardeiro_abyssal",
    "guardiao_cosmico",
    "fuzileiro_runico",
    "necromante_torre",
    "aranha_laser",
)

EARLY_MINIBOSS_KINDS: tuple[str, ...] = (
    "miniboss_espiral",
    "miniboss_cacador",
)

MID_MINIBOSS_KINDS: tuple[str, ...] = (
    *EARLY_MINIBOSS_KINDS,
    "miniboss_escudo",
    "miniboss_sniper",
    "miniboss_laser_matrix",
)

LATE_MINIBOSS_KINDS: tuple[str, ...] = (
    *MID_MINIBOSS_KINDS,
    "miniboss_oraculo_kame",
    "miniboss_piro_hidra",
    "miniboss_fantasma_senhor",
    "miniboss_alquimista",
)

EARLY_BOSS_KINDS: tuple[str, ...] = (
    "boss",
    "boss_artilharia",
)

MID_BOSS_KINDS: tuple[str, ...] = (
    *EARLY_BOSS_KINDS,
    "boss_caotico",
)

LATE_BOSS_KINDS: tuple[str, ...] = (
    *MID_BOSS_KINDS,
    "boss_colosso_laser",
    "boss_druida_toxico",
    "boss_soberano_espectral",
)


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
            return EnemyFactory.choose_random_boss_kind_from(self._boss_pool_for_level(world.level))
        if category == "miniboss":
            return EnemyFactory.choose_random_miniboss_kind_from(self._miniboss_pool_for_level(world.level))
        return EnemyFactory.choose_random_enemy_kind_from(self._enemy_pool_for_level(world.level))

    def _enemy_pool_for_level(self, level: int) -> list[str]:
        if level <= 3:
            return list(EARLY_ENEMY_KINDS)
        if level <= 7:
            return list(MID_ENEMY_KINDS)
        return list(LATE_ENEMY_KINDS)

    def _miniboss_pool_for_level(self, level: int) -> list[str]:
        if level <= 6:
            return list(EARLY_MINIBOSS_KINDS)
        if level <= 10:
            return list(MID_MINIBOSS_KINDS)
        return list(LATE_MINIBOSS_KINDS)

    def _boss_pool_for_level(self, level: int) -> list[str]:
        if level <= 10:
            return list(EARLY_BOSS_KINDS)
        if level <= 15:
            return list(MID_BOSS_KINDS)
        return list(LATE_BOSS_KINDS)

    def _choose_spawn_category(self, level: int) -> str:
        if level < self.config.miniboss_start_level:
            return "enemy"

        if level < self.config.boss_start_level:
            level_offset = level - self.config.miniboss_start_level
            miniboss_chance = min(
                0.85,
                self.config.miniboss_spawn_chance
                + level_offset * self.config.miniboss_spawn_chance_gain_per_level,
            )
            return "miniboss" if random.random() < miniboss_chance else "enemy"

        level_offset = level - self.config.boss_start_level
        boss_chance = min(
            0.45,
            self.config.boss_spawn_chance
            + level_offset * self.config.boss_spawn_chance_gain_per_level,
        )
        miniboss_chance = min(
            0.75,
            self.config.miniboss_spawn_chance
            + level_offset * self.config.miniboss_spawn_chance_gain_per_level,
        )
        roll = random.random()
        if roll < boss_chance:
            return "boss"
        if roll < boss_chance + miniboss_chance:
            return "miniboss"
        return "enemy"

    def portals_per_cycle(self, world: GameWorld, elapsed_time: float) -> int:
        del elapsed_time
        levels_per_step = max(1, self.config.portal_growth_levels)
        return min(self.config.max_portals_per_cycle, 1 + (max(0, world.level - 1) // levels_per_step))

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
            return EnemyFactory.choose_random_boss_kind_from(self._boss_pool_for_time(elapsed_time))
        if category == "miniboss":
            return EnemyFactory.choose_random_miniboss_kind_from(self._miniboss_pool_for_time(elapsed_time))
        return EnemyFactory.choose_random_enemy_kind_from(self._enemy_pool_for_time(elapsed_time))

    def _enemy_pool_for_time(self, elapsed_time: float) -> list[str]:
        if elapsed_time < 50.0:
            return list(EARLY_ENEMY_KINDS)
        if elapsed_time < 120.0:
            return list(MID_ENEMY_KINDS)
        return list(LATE_ENEMY_KINDS)

    def _miniboss_pool_for_time(self, elapsed_time: float) -> list[str]:
        if elapsed_time < 100.0:
            return list(EARLY_MINIBOSS_KINDS)
        if elapsed_time < 180.0:
            return list(MID_MINIBOSS_KINDS)
        return list(LATE_MINIBOSS_KINDS)

    def _boss_pool_for_time(self, elapsed_time: float) -> list[str]:
        if elapsed_time < 150.0:
            return list(EARLY_BOSS_KINDS)
        if elapsed_time < 240.0:
            return list(MID_BOSS_KINDS)
        return list(LATE_BOSS_KINDS)

    def _choose_spawn_category(self, elapsed_time: float) -> str:
        minute_factor = elapsed_time / 60.0
        miniboss_chance = min(
            0.85,
            self.config.miniboss_spawn_chance
            + minute_factor * self.config.miniboss_spawn_chance_gain_per_minute,
        )
        boss_chance = min(
            0.55,
            self.config.boss_spawn_chance + minute_factor * self.config.boss_spawn_chance_gain_per_minute,
        )
        if elapsed_time < self.config.miniboss_start_time:
            return "enemy"

        if elapsed_time < self.config.boss_start_time:
            return "miniboss" if random.random() < miniboss_chance else "enemy"

        roll = random.random()
        if roll < boss_chance:
            return "boss"
        if roll < boss_chance + miniboss_chance:
            return "miniboss"
        return "enemy"

    def portals_per_cycle(self, world: GameWorld, elapsed_time: float) -> int:
        del world
        growth_step = max(1.0, self.config.portal_growth_time_step)
        return min(self.config.max_portals_per_cycle, 1 + int(elapsed_time // growth_step))

    def on_enemy_spawned(self, world: GameWorld, enemy: Entity) -> None:
        lifetime = min(
            self.config.enemy_lifetime_max,
            self.config.enemy_lifetime + max(0, world.level - 1) * self.config.enemy_lifetime_gain_per_level,
        )
        enemy.add_component(LifetimeComponent(time_left=lifetime))


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


class LabyrinthSpawnStrategy(SpawnStrategy):
    def initial_timer(self, world: GameWorld, elapsed_time: float) -> float:
        del world, elapsed_time
        return 999_999.0

    def next_interval(self, world: GameWorld, elapsed_time: float) -> float:
        del world, elapsed_time
        return 999_999.0

    def choose_enemy_kind(self, world: GameWorld, elapsed_time: float) -> str:
        del world, elapsed_time
        return EnemyFactory.registered_enemy_kinds()[0]

    def portals_per_cycle(self, world: GameWorld, elapsed_time: float) -> int:
        del world, elapsed_time
        return 0

    def on_enemy_spawned(self, world: GameWorld, enemy: Entity) -> None:
        del world, enemy
