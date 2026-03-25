from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from pygame import Vector2

from game.ecs.component import Component
from game.rendering.render_strategy import RenderStrategy


@dataclass
class TransformComponent(Component):
    position: Vector2


@dataclass
class MovementComponent(Component):
    velocity: Vector2 = field(default_factory=Vector2)
    input_direction: Vector2 = field(default_factory=Vector2)
    max_speed: float = 0.0


@dataclass
class DashComponent(Component):
    dash_speed: float
    duration: float
    cooldown: float
    invulnerability_extra: float
    active_time_left: float = 0.0
    cooldown_left: float = 0.0
    requested: bool = False
    dash_direction: Vector2 = field(default_factory=Vector2)


@dataclass
class CollisionComponent(Component):
    radius: float
    layer: str


@dataclass
class RenderComponent(Component):
    render_strategy: RenderStrategy


@dataclass
class ShootComponent(Component):
    cooldown: float
    aim_time: float
    bullet_speed: float
    bullet_radius: float
    bullet_color: tuple[int, int, int] = (255, 170, 200)
    cooldown_left: float = 0.0
    aim_left: float = 0.0
    is_aiming: bool = False
    target_direction: Vector2 = field(default_factory=Vector2)


@dataclass
class FollowComponent(Component):
    speed: float


@dataclass
class InvulnerabilityComponent(Component):
    time_left: float = 0.0


@dataclass
class PortalSpawnComponent(Component):
    time_left: float
    enemy_kind: str


@dataclass
class PortalComponent(Component):
    is_level_portal: bool


@dataclass
class CollectibleComponent(Component):
    value: int = 1


@dataclass
class BulletComponent(Component):
    owner_tag: str
    lifetime: float


@dataclass
class MortarShellComponent(Component):
    target_position: Vector2
    explosion_radius: float
    arrival_epsilon: float = 10.0


@dataclass
class LifetimeComponent(Component):
    time_left: float


@dataclass
class BehaviorComponent(Component):
    behavior: Any


@dataclass
class ChargeComponent(Component):
    state: str = "waiting"
    timer: float = 0.0
    locked_target: Vector2 = field(default_factory=Vector2)
    is_target_locked: bool = False
    cruise_speed: float = 0.0
    dash_speed: float = 0.0


@dataclass
class ExplosiveComponent(Component):
    timer: float = 0.0
    exploded: bool = False
    chase_time: float = 3.5
    detonate_time: float = 4.5


@dataclass
class TurretComponent(Component):
    shot_pattern: int = 0
    spiral_angle: float = 0.0
    shot_timer: float = 0.0
    burst_timer: float = 0.0
    is_in_burst: bool = True
    shot_direction: Vector2 = field(default_factory=lambda: Vector2(1, 0))
    shot_angles: tuple[float, ...] = ()


@dataclass
class OrbitComponent(Component):
    angle: float = 0.0
    radius: float = 140.0
    angular_speed: float = 1.8


@dataclass
class SniperComponent(Component):
    state: str = "aiming"
    shot_timer: float = 0.0
    aim_target: Vector2 = field(default_factory=Vector2)


@dataclass
class BossComponent(Component):
    boss_kind: str = "boss"
    state: str = "pursuing"
    variant: int = 1
    ability_timer: float = 0.0
    shot_timer: float = 0.0


@dataclass
class GhostComponent(Component):
    is_visible: bool = False
    timer: float = 0.0
    hidden_duration: float = 1.2
    visible_duration: float = 1.0
    reveal_distance: float = 120.0
    hidden_speed: float = 165.0


@dataclass
class KamehamehaComponent(Component):
    state: str = "charging"
    timer: float = 0.0
    tick_timer: float = 0.0
    charge_duration: float = 1.2
    fire_duration: float = 1.1
    cooldown_duration: float = 1.3
    fire_tick: float = 0.07
    beam_color: tuple[int, int, int] = (170, 235, 255)
    locked_direction: Vector2 = field(default_factory=lambda: Vector2(1, 0))


@dataclass
class DashOnlyDefeatComponent(Component):
    enabled: bool = True


@dataclass
class LabyrinthVirusComponent(Component):
    behavior_kind: str
    base_speed: float
    retarget_interval: float = 0.2
    retarget_time_left: float = 0.0
    interception_seconds: float = 0.45


@dataclass
class LabyrinthKeyComponent(Component):
    collected: bool = False


@dataclass
class LabyrinthExitComponent(Component):
    unlocked: bool = False
