from __future__ import annotations

import math
import random
from typing import Callable

from pygame import Vector2

from game.behaviors.boss_behavior import BossBehavior
from game.behaviors.bouncer_behavior import BouncerBehavior
from game.behaviors.charge_behavior import ChargeBehavior
from game.behaviors.explosive_behavior import ExplosiveBehavior
from game.behaviors.follow_behavior import FollowBehavior
from game.behaviors.hunter_miniboss_behavior import HunterMinibossBehavior
from game.behaviors.mortar_behavior import MortarBehavior
from game.behaviors.shield_miniboss_behavior import ShieldMinibossBehavior
from game.behaviors.shoot_behavior import ShootBehavior
from game.behaviors.sniper_miniboss_behavior import SniperMinibossBehavior
from game.behaviors.spiral_turret_behavior import SpiralTurretBehavior
from game.behaviors.turret_burst_behavior import TurretBurstBehavior
from game.components.data_components import (
    BehaviorComponent,
    BossComponent,
    ChargeComponent,
    CollisionComponent,
    ExplosiveComponent,
    FollowComponent,
    LifetimeComponent,
    MovementComponent,
    OrbitComponent,
    RenderComponent,
    SniperComponent,
    ShootComponent,
    TransformComponent,
    TurretComponent,
)
from game.config import (
    BULLET_RADIUS,
    ENEMY_BOUNCER_COLOR,
    ENEMY_BOUNCER_CORE_COLOR,
    ENEMY_CHARGE_COLOR,
    ENEMY_EXPLOSIVE_COLOR,
    ENEMY_EXPLOSIVE_WARNING_COLOR,
    ENEMY_FOLLOWER_COLOR,
    ENEMY_FOLLOWER_CORE_COLOR,
    ENEMY_MINIBOSS_HUNTER_COLOR,
    ENEMY_MINIBOSS_HUNTER_CORE_COLOR,
    ENEMY_MINIBOSS_SHIELD_COLOR,
    ENEMY_MINIBOSS_SNIPER_COLOR,
    ENEMY_MORTAR_COLOR,
    ENEMY_SHOOTER_COLOR,
    ENEMY_SHOOTER_INNER_COLOR,
    ENEMY_TURRET_COLOR,
    ENEMY_TURRET_MIDDLE_COLOR,
    FOLLOWER_RADIUS,
    FOLLOWER_SPEED,
    SHOOTER_RADIUS,
)
from game.ecs.entity import Entity
from game.rendering.strategies import (
    BossRenderStrategy,
    ChargeEnemyRenderStrategy,
    ExplosiveEnemyRenderStrategy,
    FollowerRenderStrategy,
    MortarRenderStrategy,
    NeonCoreEnemyRenderStrategy,
    ShieldMinibossRenderStrategy,
    ShooterRenderStrategy,
    SniperMinibossRenderStrategy,
    TurretEnemyRenderStrategy,
)


class EnemyFactory:
    _enemy_registry: dict[str, Callable[[Vector2], Entity]] = {}
    _enemy_spawn_weights: dict[str, float] = {}
    _miniboss_registry: dict[str, Callable[[Vector2], Entity]] = {}
    _miniboss_spawn_weights: dict[str, float] = {}
    _boss_registry: dict[str, Callable[[Vector2], Entity]] = {}
    _boss_spawn_weights: dict[str, float] = {}

    @classmethod
    def _register_kind(
        cls,
        registry: dict[str, Callable[[Vector2], Entity]],
        spawn_weights: dict[str, float],
        kind: str,
        creator: Callable[[Vector2], Entity],
        weight: float,
    ) -> None:
        registry[kind] = creator
        spawn_weights[kind] = max(0.0, weight)

    @classmethod
    def register_enemy(cls, kind: str, creator: Callable[[Vector2], Entity], weight: float) -> None:
        cls._register_kind(cls._enemy_registry, cls._enemy_spawn_weights, kind, creator, weight)

    @classmethod
    def register_miniboss(cls, kind: str, creator: Callable[[Vector2], Entity], weight: float) -> None:
        cls._register_kind(cls._miniboss_registry, cls._miniboss_spawn_weights, kind, creator, weight)

    @classmethod
    def register_boss(cls, kind: str, creator: Callable[[Vector2], Entity], weight: float) -> None:
        cls._register_kind(cls._boss_registry, cls._boss_spawn_weights, kind, creator, weight)

    @classmethod
    def _ensure_registry(cls) -> None:
        if cls._enemy_registry or cls._miniboss_registry or cls._boss_registry:
            return
        cls.register_enemy("follower", cls.create_follower, weight=0.22)
        cls.register_enemy("shooter", cls.create_shooter, weight=0.12)
        cls.register_enemy("quique", cls.create_bouncer, weight=0.11)
        cls.register_enemy("investida", cls.create_charge, weight=0.10)
        cls.register_enemy("explosivo", cls.create_explosive, weight=0.08)
        cls.register_enemy("metralhadora", cls.create_turret, weight=0.06)
        cls.register_enemy("morteiro", cls.create_mortar, weight=0.05)
        cls.register_miniboss("miniboss_espiral", cls.create_miniboss_spiral, weight=0.04)
        cls.register_miniboss("miniboss_cacador", cls.create_miniboss_hunter, weight=0.04)
        cls.register_miniboss("miniboss_escudo", cls.create_miniboss_shield, weight=0.03)
        cls.register_miniboss("miniboss_sniper", cls.create_miniboss_sniper, weight=0.02)
        cls.register_boss("boss", cls.create_boss, weight=0.01)
        cls.register_boss("boss_artilharia", cls.create_boss_artillery, weight=0.005)
        cls.register_boss("boss_caotico", cls.create_boss_chaotic, weight=0.005)

    @classmethod
    def _choose_random_kind_from(
        cls,
        registry: dict[str, Callable[[Vector2], Entity]],
        spawn_weights: dict[str, float],
    ) -> str:
        kinds = list(registry.keys())
        if not kinds:
            raise ValueError("No enemy kinds registered for requested category")
        weights = [spawn_weights.get(kind, 0.0) for kind in kinds]
        total = sum(weights)
        if total <= 0:
            return kinds[0]
        return random.choices(kinds, weights=weights, k=1)[0]

    @classmethod
    def _find_creator(cls, kind: str) -> Callable[[Vector2], Entity] | None:
        creator = cls._enemy_registry.get(kind)
        if creator is not None:
            return creator
        creator = cls._miniboss_registry.get(kind)
        if creator is not None:
            return creator
        return cls._boss_registry.get(kind)

    @classmethod
    def choose_random_enemy_kind(cls) -> str:
        cls._ensure_registry()
        return cls._choose_random_kind_from(cls._enemy_registry, cls._enemy_spawn_weights)

    @classmethod
    def choose_random_miniboss_kind(cls) -> str:
        cls._ensure_registry()
        return cls._choose_random_kind_from(cls._miniboss_registry, cls._miniboss_spawn_weights)

    @classmethod
    def choose_random_boss_kind(cls) -> str:
        cls._ensure_registry()
        return cls._choose_random_kind_from(cls._boss_registry, cls._boss_spawn_weights)

    @classmethod
    def create_random_enemy(cls, position: Vector2) -> Entity:
        kind = cls.choose_random_enemy_kind()
        return cls.create_by_kind(kind, position)

    @classmethod
    def create_by_kind(cls, kind: str, position: Vector2) -> Entity:
        cls._ensure_registry()
        creator = cls._find_creator(kind)
        if creator is None:
            raise ValueError(f"Unknown enemy kind: {kind}")
        return creator(position)

    @classmethod
    def registered_enemy_kinds(cls) -> list[str]:
        cls._ensure_registry()
        return list(cls._enemy_registry.keys())

    @classmethod
    def registered_miniboss_kinds(cls) -> list[str]:
        cls._ensure_registry()
        return list(cls._miniboss_registry.keys())

    @classmethod
    def registered_boss_kinds(cls) -> list[str]:
        cls._ensure_registry()
        return list(cls._boss_registry.keys())

    @classmethod
    def registered_all_kinds(cls) -> list[str]:
        cls._ensure_registry()
        return [
            *cls.registered_enemy_kinds(),
            *cls.registered_miniboss_kinds(),
            *cls.registered_boss_kinds(),
        ]

    @staticmethod
    def create_follower(position: Vector2) -> Entity:
        enemy = Entity()
        enemy.add_tag("enemy")
        enemy.add_component(TransformComponent(position=position))
        enemy.add_component(MovementComponent(max_speed=FOLLOWER_SPEED))
        enemy.add_component(FollowComponent(speed=FOLLOWER_SPEED))
        enemy.add_component(BehaviorComponent(behavior=FollowBehavior()))
        enemy.add_component(CollisionComponent(radius=FOLLOWER_RADIUS, layer="enemy"))
        enemy.add_component(
            RenderComponent(
                render_strategy=FollowerRenderStrategy(
                    outer_color=ENEMY_FOLLOWER_COLOR,
                    core_color=ENEMY_FOLLOWER_CORE_COLOR,
                    radius=FOLLOWER_RADIUS,
                )
            )
        )
        return enemy

    @staticmethod
    def create_shooter(position: Vector2) -> Entity:
        enemy = Entity()
        enemy.add_tag("enemy")
        enemy.add_component(TransformComponent(position=position))
        enemy.add_component(MovementComponent(max_speed=0.0))
        enemy.add_component(
            ShootComponent(
                cooldown=3.0,
                aim_time=2.0,
                bullet_speed=260.0,
                bullet_radius=BULLET_RADIUS,
                bullet_color=ENEMY_SHOOTER_COLOR,
            )
        )
        enemy.add_component(BehaviorComponent(behavior=ShootBehavior()))
        enemy.add_component(CollisionComponent(radius=SHOOTER_RADIUS, layer="enemy"))
        enemy.add_component(
            RenderComponent(
                render_strategy=ShooterRenderStrategy(
                    outer_color=ENEMY_SHOOTER_COLOR,
                    inner_color=ENEMY_SHOOTER_INNER_COLOR,
                    radius=SHOOTER_RADIUS,
                )
            )
        )
        return enemy

    @staticmethod
    def create_bouncer(position: Vector2) -> Entity:
        enemy = Entity()
        enemy.add_tag("enemy")
        enemy.add_component(TransformComponent(position=position))
        enemy.add_component(MovementComponent(max_speed=230.0))
        enemy.add_component(BehaviorComponent(behavior=BouncerBehavior()))
        enemy.add_component(CollisionComponent(radius=12.0, layer="enemy"))
        enemy.add_component(
            RenderComponent(
                render_strategy=NeonCoreEnemyRenderStrategy(
                    outer_color=ENEMY_BOUNCER_COLOR,
                    core_color=ENEMY_BOUNCER_CORE_COLOR,
                    radius=12.0,
                )
            )
        )
        return enemy


    @staticmethod
    def create_charge(position: Vector2) -> Entity:
        enemy = Entity()
        enemy.add_tag("enemy")
        enemy.add_component(TransformComponent(position=position))
        enemy.add_component(MovementComponent(max_speed=140.0))
        enemy.add_component(ChargeComponent())
        enemy.add_component(BehaviorComponent(behavior=ChargeBehavior()))
        enemy.add_component(CollisionComponent(radius=12.0, layer="enemy"))
        enemy.add_component(
            RenderComponent(
                render_strategy=ChargeEnemyRenderStrategy(
                    base_color=ENEMY_CHARGE_COLOR,
                    radius=12.0,
                )
            )
        )
        return enemy

    @staticmethod
    def create_explosive(position: Vector2) -> Entity:
        enemy = Entity()
        enemy.add_tag("enemy")
        enemy.add_component(TransformComponent(position=position))
        enemy.add_component(MovementComponent(max_speed=185.0))
        enemy.add_component(ExplosiveComponent())
        enemy.add_component(BehaviorComponent(behavior=ExplosiveBehavior()))
        enemy.add_component(CollisionComponent(radius=12.0, layer="enemy"))
        enemy.add_component(
            RenderComponent(
                render_strategy=ExplosiveEnemyRenderStrategy(
                    base_color=ENEMY_EXPLOSIVE_COLOR,
                    warning_color=ENEMY_EXPLOSIVE_WARNING_COLOR,
                    radius=12.0,
                )
            )
        )
        return enemy

    @staticmethod
    def create_turret(position: Vector2) -> Entity:
        enemy = Entity()
        enemy.add_tag("enemy")
        enemy.add_component(TransformComponent(position=position))
        enemy.add_component(MovementComponent(max_speed=0.0))
        enemy.add_component(TurretComponent(shot_pattern=random.randint(0, 1), spiral_angle=random.uniform(0, 360)))
        # enemy.add_component(LifetimeComponent(time_left=10.0))
        enemy.add_component(BehaviorComponent(behavior=TurretBurstBehavior()))
        enemy.add_component(CollisionComponent(radius=15.0, layer="enemy"))
        enemy.add_component(
            RenderComponent(
                render_strategy=TurretEnemyRenderStrategy(
                    base_color=ENEMY_TURRET_COLOR,
                    middle_color=ENEMY_TURRET_MIDDLE_COLOR,
                    active_color=(245, 245, 245),
                    idle_color=(0, 255, 255),
                    radius=15.0,
                    pulse_speed=8.0,
                    pulse_gain=2.0,
                    glow_layers=4,
                )
            )
        )
        return enemy

    @staticmethod
    def create_miniboss_spiral(position: Vector2) -> Entity:
        enemy = Entity()
        enemy.add_tag("enemy")
        enemy.add_component(TransformComponent(position=position))
        enemy.add_component(MovementComponent(max_speed=0.0))
        enemy.add_component(TurretComponent(shot_pattern=2, spiral_angle=random.uniform(0, 360)))
        enemy.add_component(BehaviorComponent(behavior=SpiralTurretBehavior()))
        enemy.add_component(CollisionComponent(radius=26.0, layer="enemy"))
        enemy.add_component(
            RenderComponent(
                render_strategy=TurretEnemyRenderStrategy(
                    base_color=ENEMY_TURRET_COLOR,
                    middle_color=(5, 5, 8),
                    active_color=(245, 245, 245),
                    idle_color=(245, 245, 245),
                    radius=26.0,
                    pulse_speed=6.0,
                    pulse_gain=4.0,
                    glow_layers=5,
                )
            )
        )
        return enemy

    @staticmethod
    def create_miniboss_hunter(position: Vector2) -> Entity:
        enemy = Entity()
        enemy.add_tag("enemy")
        enemy.add_component(TransformComponent(position=position))
        enemy.add_component(MovementComponent(max_speed=150.0))
        enemy.add_component(TurretComponent())
        enemy.add_component(BehaviorComponent(behavior=HunterMinibossBehavior()))
        enemy.add_component(CollisionComponent(radius=24.0, layer="enemy"))
        enemy.add_component(
            RenderComponent(
                render_strategy=NeonCoreEnemyRenderStrategy(
                    outer_color=ENEMY_MINIBOSS_HUNTER_COLOR,
                    core_color=ENEMY_MINIBOSS_HUNTER_CORE_COLOR,
                    radius=24.0,
                )
            )
        )
        return enemy

    @staticmethod
    def create_miniboss_shield(position: Vector2) -> Entity:
        enemy = Entity()
        enemy.add_tag("enemy")
        enemy.add_component(TransformComponent(position=position))
        enemy.add_component(MovementComponent(max_speed=185.0))
        enemy.add_component(TurretComponent())
        enemy.add_component(OrbitComponent(angle=random.uniform(0.0, math.pi * 2.0)))
        enemy.add_component(BehaviorComponent(behavior=ShieldMinibossBehavior()))
        enemy.add_component(CollisionComponent(radius=23.0, layer="enemy"))
        enemy.add_component(
            RenderComponent(
                render_strategy=ShieldMinibossRenderStrategy(
                    base_color=ENEMY_MINIBOSS_SHIELD_COLOR,
                    radius=23.0,
                )
            )
        )
        return enemy

    @staticmethod
    def create_miniboss_sniper(position: Vector2) -> Entity:
        enemy = Entity()
        enemy.add_tag("enemy")
        enemy.add_component(TransformComponent(position=position))
        enemy.add_component(MovementComponent(max_speed=0.0))
        enemy.add_component(SniperComponent(aim_target=Vector2(position)))
        enemy.add_component(BehaviorComponent(behavior=SniperMinibossBehavior()))
        enemy.add_component(CollisionComponent(radius=21.0, layer="enemy"))
        enemy.add_component(
            RenderComponent(
                render_strategy=SniperMinibossRenderStrategy(
                    base_color=ENEMY_MINIBOSS_SNIPER_COLOR,
                    radius=21.0,
                )
            )
        )
        return enemy

    @staticmethod
    def create_boss(position: Vector2) -> Entity:
        enemy = Entity()
        enemy.add_tag("enemy")
        enemy.add_component(TransformComponent(position=position))
        enemy.add_component(MovementComponent(max_speed=95.0))
        enemy.add_component(BossComponent(boss_kind="boss", variant=random.randint(1, 3)))
        enemy.add_component(BehaviorComponent(behavior=BossBehavior()))
        enemy.add_component(CollisionComponent(radius=40.0, layer="enemy"))
        enemy.add_component(RenderComponent(render_strategy=BossRenderStrategy(radius=40.0)))
        return enemy

    @staticmethod
    def create_boss_artillery(position: Vector2) -> Entity:
        enemy = Entity()
        enemy.add_tag("enemy")
        enemy.add_component(TransformComponent(position=position))
        enemy.add_component(MovementComponent(max_speed=90.0))
        enemy.add_component(BossComponent(boss_kind="boss_artilharia", variant=random.randint(1, 3)))
        enemy.add_component(BehaviorComponent(behavior=BossBehavior()))
        enemy.add_component(CollisionComponent(radius=40.0, layer="enemy"))
        enemy.add_component(RenderComponent(render_strategy=BossRenderStrategy(radius=40.0)))
        return enemy

    @staticmethod
    def create_boss_chaotic(position: Vector2) -> Entity:
        enemy = Entity()
        enemy.add_tag("enemy")
        enemy.add_component(TransformComponent(position=position))
        enemy.add_component(MovementComponent(max_speed=105.0))
        enemy.add_component(BossComponent(boss_kind="boss_caotico", variant=random.randint(1, 3)))
        enemy.add_component(BehaviorComponent(behavior=BossBehavior()))
        enemy.add_component(CollisionComponent(radius=40.0, layer="enemy"))
        enemy.add_component(RenderComponent(render_strategy=BossRenderStrategy(radius=40.0)))
        return enemy

    @staticmethod
    def create_mortar(position: Vector2) -> Entity:
        enemy = Entity()
        enemy.add_tag("enemy")
        enemy.add_component(TransformComponent(position=position))
        enemy.add_component(MovementComponent(max_speed=0.0))
        enemy.add_component(TurretComponent())
        enemy.add_component(BehaviorComponent(behavior=MortarBehavior()))
        enemy.add_component(CollisionComponent(radius=18.0, layer="enemy"))
        enemy.add_component(
            RenderComponent(
                render_strategy=MortarRenderStrategy(
                    base_color=ENEMY_MORTAR_COLOR,
                    radius=18.0,
                )
            )
        )
        return enemy
