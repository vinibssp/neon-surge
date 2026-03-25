from __future__ import annotations

from dataclasses import dataclass

from game.config import (
    LEVEL_COLLECTIBLE_BASE,
    MODE_INITIAL_SPAWN_CAP,
    RACE_SPAWN_INTERVAL_BASE,
    RACE_SPAWN_INTERVAL_LEVEL_STEP,
    RACE_SPAWN_INTERVAL_MIN,
    RACE_TOTAL_LEVELS,
    SURVIVAL_ENEMY_LIFETIME,
    SURVIVAL_LEVEL_DURATION,
    SURVIVAL_SPAWN_INTERVAL_BASE,
    SURVIVAL_SPAWN_INTERVAL_LEVEL_STEP,
    SURVIVAL_SPAWN_INTERVAL_MIN,
)


@dataclass(frozen=True)
class RaceConfig:
    description: str = "Colete energia e avance por todos os portais." 
    infinite: bool = False
    total_levels: int = RACE_TOTAL_LEVELS
    collectible_base: int = LEVEL_COLLECTIBLE_BASE
    collectible_growth_every: int = 2
    collectible_growth_step: int = 1
    spawn_interval_base: float = RACE_SPAWN_INTERVAL_BASE
    spawn_interval_min: float = RACE_SPAWN_INTERVAL_MIN
    spawn_interval_level_step: float = RACE_SPAWN_INTERVAL_LEVEL_STEP
    initial_spawn_cap: float = MODE_INITIAL_SPAWN_CAP
    portal_growth_levels: int = 2
    max_portals_per_cycle: int = 8
    miniboss_start_level: int = 4
    boss_start_level: int = 8
    miniboss_spawn_chance: float = 0.18
    boss_spawn_chance: float = 0.07
    miniboss_spawn_chance_gain_per_level: float = 0.01
    boss_spawn_chance_gain_per_level: float = 0.004


@dataclass(frozen=True)
class RaceInfiniteConfig(RaceConfig):
    description: str = "Corrida infinita com aumento continuo de pressao a cada nivel."
    infinite: bool = True
    total_levels: int = 999_999
    spawn_interval_base: float = 2.9
    spawn_interval_min: float = 0.9
    spawn_interval_level_step: float = 0.08
    portal_growth_levels: int = 1
    max_portals_per_cycle: int = 10
    miniboss_start_level: int = 3
    boss_start_level: int = 6
    miniboss_spawn_chance: float = 0.22
    boss_spawn_chance: float = 0.1
    miniboss_spawn_chance_gain_per_level: float = 0.012
    boss_spawn_chance_gain_per_level: float = 0.006


@dataclass(frozen=True)
class SurvivalConfig:
    description: str = "Sobreviva o maximo possivel contra ondas crescentes."
    level_duration: float = SURVIVAL_LEVEL_DURATION
    spawn_interval_base: float = SURVIVAL_SPAWN_INTERVAL_BASE
    spawn_interval_min: float = SURVIVAL_SPAWN_INTERVAL_MIN
    spawn_interval_level_step: float = SURVIVAL_SPAWN_INTERVAL_LEVEL_STEP
    enemy_lifetime: float = SURVIVAL_ENEMY_LIFETIME
    enemy_lifetime_gain_per_level: float = 0.4
    enemy_lifetime_max: float = 16.0
    initial_spawn_cap: float = MODE_INITIAL_SPAWN_CAP
    portal_growth_time_step: float = 28.0
    max_portals_per_cycle: int = 8
    miniboss_start_time: float = 45.0
    boss_start_time: float = 120.0
    miniboss_spawn_chance: float = 0.24
    boss_spawn_chance: float = 0.10
    miniboss_spawn_chance_gain_per_minute: float = 0.02
    boss_spawn_chance_gain_per_minute: float = 0.01


@dataclass(frozen=True)
class SurvivalHardcoreConfig(SurvivalConfig):
    description: str = "Sobrevivencia extrema com ritmo agressivo e ondas densas."
    level_duration: float = 16.0
    spawn_interval_base: float = 1.7
    spawn_interval_min: float = 0.45
    spawn_interval_level_step: float = 0.14
    enemy_lifetime: float = 14.0
    enemy_lifetime_gain_per_level: float = 0.6
    enemy_lifetime_max: float = 22.0
    initial_spawn_cap: float = 1.0
    portal_growth_time_step: float = 18.0
    max_portals_per_cycle: int = 12
    miniboss_start_time: float = 25.0
    boss_start_time: float = 70.0
    miniboss_spawn_chance: float = 0.32
    boss_spawn_chance: float = 0.16
    miniboss_spawn_chance_gain_per_minute: float = 0.028
    boss_spawn_chance_gain_per_minute: float = 0.014


@dataclass(frozen=True)
class OneVsOneConfig:
    description: str = "Enfrente um inimigo por vez e use o portal para progredir."


@dataclass(frozen=True)
class LabyrinthConfig:
    description: str = "Explore labirintos procedurais, pegue a chave e escape por uma saida bloqueada."
    base_enemy_speed: float = 82.0
    boss_level_interval: int = 5
    boss_speed_gain_per_level: float = 0.03
    boss_keys_required: int = 3
