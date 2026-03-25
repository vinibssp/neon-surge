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
    miniboss_start_level: int = 5
    boss_start_level: int = 9
    miniboss_spawn_chance: float = 0.15
    boss_spawn_chance: float = 0.05
    miniboss_spawn_chance_gain_per_level: float = 0.009
    boss_spawn_chance_gain_per_level: float = 0.003


@dataclass(frozen=True)
class RaceInfiniteConfig(RaceConfig):
    description: str = "Corrida infinita com aumento continuo de pressao a cada nivel."
    infinite: bool = True
    total_levels: int = 999_999
    spawn_interval_base: float = 3.1
    spawn_interval_min: float = 1.0
    spawn_interval_level_step: float = 0.075
    portal_growth_levels: int = 1
    max_portals_per_cycle: int = 10
    miniboss_start_level: int = 4
    boss_start_level: int = 7
    miniboss_spawn_chance: float = 0.20
    boss_spawn_chance: float = 0.08
    miniboss_spawn_chance_gain_per_level: float = 0.010
    boss_spawn_chance_gain_per_level: float = 0.005


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
    miniboss_start_time: float = 55.0
    boss_start_time: float = 135.0
    miniboss_spawn_chance: float = 0.20
    boss_spawn_chance: float = 0.08
    miniboss_spawn_chance_gain_per_minute: float = 0.018
    boss_spawn_chance_gain_per_minute: float = 0.008


@dataclass(frozen=True)
class SurvivalHardcoreConfig(SurvivalConfig):
    description: str = "Sobrevivencia extrema com ritmo agressivo e ondas densas."
    level_duration: float = 16.0
    spawn_interval_base: float = 1.8
    spawn_interval_min: float = 0.5
    spawn_interval_level_step: float = 0.13
    enemy_lifetime: float = 14.0
    enemy_lifetime_gain_per_level: float = 0.6
    enemy_lifetime_max: float = 22.0
    initial_spawn_cap: float = 1.0
    portal_growth_time_step: float = 18.0
    max_portals_per_cycle: int = 12
    miniboss_start_time: float = 35.0
    boss_start_time: float = 85.0
    miniboss_spawn_chance: float = 0.28
    boss_spawn_chance: float = 0.14
    miniboss_spawn_chance_gain_per_minute: float = 0.024
    boss_spawn_chance_gain_per_minute: float = 0.012


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
