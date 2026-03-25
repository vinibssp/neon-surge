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
    total_levels: int = RACE_TOTAL_LEVELS
    collectible_base: int = LEVEL_COLLECTIBLE_BASE
    spawn_interval_base: float = RACE_SPAWN_INTERVAL_BASE
    spawn_interval_min: float = RACE_SPAWN_INTERVAL_MIN
    spawn_interval_level_step: float = RACE_SPAWN_INTERVAL_LEVEL_STEP
    initial_spawn_cap: float = MODE_INITIAL_SPAWN_CAP
    miniboss_start_level: int = 4
    boss_start_level: int = 8
    miniboss_spawn_chance: float = 0.20
    boss_spawn_chance: float = 0.08


@dataclass(frozen=True)
class SurvivalConfig:
    description: str = "Sobreviva o maximo possivel contra ondas crescentes."
    level_duration: float = SURVIVAL_LEVEL_DURATION
    spawn_interval_base: float = SURVIVAL_SPAWN_INTERVAL_BASE
    spawn_interval_min: float = SURVIVAL_SPAWN_INTERVAL_MIN
    spawn_interval_level_step: float = SURVIVAL_SPAWN_INTERVAL_LEVEL_STEP
    enemy_lifetime: float = SURVIVAL_ENEMY_LIFETIME
    initial_spawn_cap: float = MODE_INITIAL_SPAWN_CAP
    miniboss_start_time: float = 45.0
    boss_start_time: float = 120.0
    miniboss_spawn_chance: float = 0.24
    boss_spawn_chance: float = 0.10


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
