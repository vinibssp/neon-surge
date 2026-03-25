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
    spawn_interval_min: float = 1.8
    spawn_interval_level_step: float = 0.14
    initial_spawn_cap: float = 2.0
    portal_growth_levels: int = 2
    max_portals_per_cycle: int = 8
    miniboss_start_level: int = 6
    boss_start_level: int = 10
    miniboss_spawn_chance: float = 0.10
    boss_spawn_chance: float = 0.03
    miniboss_spawn_chance_gain_per_level: float = 0.006
    boss_spawn_chance_gain_per_level: float = 0.002


@dataclass(frozen=True)
class RaceInfiniteConfig(RaceConfig):
    description: str = "Corrida infinita com aumento continuo de pressao a cada nivel."
    infinite: bool = True
    total_levels: int = 999_999
    spawn_interval_base: float = 3.4
    spawn_interval_min: float = 1.25
    spawn_interval_level_step: float = 0.06
    portal_growth_levels: int = 1
    max_portals_per_cycle: int = 10
    miniboss_start_level: int = 5
    boss_start_level: int = 9
    miniboss_spawn_chance: float = 0.14
    boss_spawn_chance: float = 0.05
    miniboss_spawn_chance_gain_per_level: float = 0.008
    boss_spawn_chance_gain_per_level: float = 0.003


@dataclass(frozen=True)
class SurvivalConfig:
    description: str = "Sobreviva o maximo possivel contra ondas crescentes."
    level_duration: float = 24.0
    spawn_interval_base: float = 2.5
    spawn_interval_min: float = 0.95
    spawn_interval_level_step: float = 0.09
    enemy_lifetime: float = 8.5
    enemy_lifetime_gain_per_level: float = 0.3
    enemy_lifetime_max: float = 13.0
    initial_spawn_cap: float = 2.1
    portal_growth_time_step: float = 34.0
    max_portals_per_cycle: int = 7
    miniboss_start_time: float = 75.0
    boss_start_time: float = 170.0
    miniboss_spawn_chance: float = 0.14
    boss_spawn_chance: float = 0.04
    miniboss_spawn_chance_gain_per_minute: float = 0.012
    boss_spawn_chance_gain_per_minute: float = 0.005
    lava_interval: float = 50.0
    lava_warning_duration: float = 4.0
    lava_active_duration: float = 7.0
    lava_blink_duration: float = 1.5
    lava_height_ratio: float = 0.16
    collectible_spawn_interval: float = 2.8
    collectible_spawn_cap: int = 12
    env_event_interval: float = 40.0
    env_event_duration: float = 11.0
    snow_drag_multiplier: float = 0.78
    snow_turn_response: float = 0.16
    water_pirate_count: int = 3
    bullet_cloud_fire_interval: float = 0.11
    black_hole_pull_radius: float = 170.0
    black_hole_pull_strength: float = 220.0
    black_hole_speed: float = 40.0
    black_hole_consume_radius: float = 24.0


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
    lava_interval: float = 30.0
    lava_warning_duration: float = 3.0
    lava_active_duration: float = 9.0
    lava_blink_duration: float = 2.0
    lava_height_ratio: float = 0.23
    collectible_spawn_interval: float = 2.5
    collectible_spawn_cap: int = 14
    env_event_interval: float = 24.0
    env_event_duration: float = 14.0
    snow_drag_multiplier: float = 0.72
    snow_turn_response: float = 0.12
    water_pirate_count: int = 4
    bullet_cloud_fire_interval: float = 0.055
    black_hole_pull_radius: float = 220.0
    black_hole_pull_strength: float = 360.0
    black_hole_speed: float = 55.0
    black_hole_consume_radius: float = 30.0


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
