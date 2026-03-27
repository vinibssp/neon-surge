from __future__ import annotations

import math
import random
from typing import Callable

from pygame import Vector2

from game.behaviors.boss_behavior import BossBehavior
from game.behaviors.alchemist_miniboss_behavior import AlchemistMinibossBehavior
from game.behaviors.blink_striker_behavior import BlinkStrikerBehavior
from game.behaviors.bouncer_behavior import BouncerBehavior
from game.behaviors.buffer_mage_behavior import BufferMageBehavior
from game.behaviors.charge_behavior import ChargeBehavior
from game.behaviors.explosive_behavior import ExplosiveBehavior
from game.behaviors.flamethrower_behavior import FlamethrowerBehavior
from game.behaviors.follow_behavior import FollowBehavior
from game.behaviors.frog_acid_behavior import FrogAcidBehavior
from game.behaviors.ghost_boo_behavior import GhostBooBehavior
from game.behaviors.hex_orbiter_behavior import HexOrbiterBehavior
from game.behaviors.hunter_miniboss_behavior import HunterMinibossBehavior
from game.behaviors.kamehameha_behavior import KamehamehaBehavior
from game.behaviors.laser_shooter_behavior import LaserShooterBehavior
from game.behaviors.laser_matrix_miniboss_behavior import LaserMatrixMinibossBehavior
from game.behaviors.mortar_behavior import MortarBehavior
from game.behaviors.mine_layer_behavior import MineLayerBehavior
from game.behaviors.arcane_strafer_behavior import ArcaneStraferBehavior
from game.behaviors.orbit_shooter_behavior import OrbitShooterBehavior
from game.behaviors.runic_bombardier_behavior import RunicBombardierBehavior
from game.behaviors.shadow_pouncer_behavior import ShadowPouncerBehavior
from game.behaviors.phantom_overlord_miniboss_behavior import PhantomOverlordMinibossBehavior
from game.behaviors.shield_miniboss_behavior import ShieldMinibossBehavior
from game.behaviors.shoot_behavior import ShootBehavior
from game.behaviors.shotgun_ambusher_behavior import ShotgunAmbusherBehavior
from game.behaviors.sniper_miniboss_behavior import SniperMinibossBehavior
from game.behaviors.spiral_turret_behavior import SpiralTurretBehavior
from game.behaviors.suppressor_behavior import SuppressorBehavior
from game.behaviors.turret_burst_behavior import TurretBurstBehavior
from game.components.data_components import (
    BehaviorComponent,
    BossComponent,
    ChargeComponent,
    CollisionComponent,
    DashOnlyDefeatComponent,
    ExplosiveComponent,
    FollowComponent,
    EnemyKindComponent,
    GhostComponent,
    KamehamehaComponent,
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
    ENEMY_ARCANE_STRAFER_COLOR,
    ENEMY_ARCANE_STRAFER_INNER_COLOR,
    ENEMY_BOUNCER_COLOR,
    ENEMY_BOUNCER_CORE_COLOR,
    ENEMY_BOSS_LASER_COLOR,
    ENEMY_BOSS_SPECTRAL_COLOR,
    ENEMY_BOSS_TOXIC_COLOR,
    ENEMY_CHARGE_COLOR,
    ENEMY_EXPLOSIVE_COLOR,
    ENEMY_EXPLOSIVE_WARNING_COLOR,
    ENEMY_FLAMETHROWER_COLOR,
    ENEMY_FROG_COLOR,
    ENEMY_FOLLOWER_COLOR,
    ENEMY_FOLLOWER_CORE_COLOR,
    ENEMY_GHOST_COLOR,
    ENEMY_KAMEHAMEHA_COLOR,
    ENEMY_LASER_SHOOTER_COLOR,
    ENEMY_LASER_SHOOTER_INNER_COLOR,
    ENEMY_MINIBOSS_HUNTER_COLOR,
    ENEMY_MINIBOSS_HUNTER_CORE_COLOR,
    ENEMY_MINIBOSS_KAME_ORACLE_COLOR,
    ENEMY_MINIBOSS_LASER_MATRIX_COLOR,
    ENEMY_MINIBOSS_ALCHEMIST_COLOR,
    ENEMY_MINIBOSS_PHANTOM_COLOR,
    ENEMY_MINIBOSS_PYRO_COLOR,
    ENEMY_MINIBOSS_SHIELD_COLOR,
    ENEMY_MINIBOSS_SNIPER_COLOR,
    ENEMY_MORTAR_COLOR,
    ENEMY_BUFFER_COLOR,
    ENEMY_BUFFER_CORE_COLOR,
    ENEMY_HEX_ORBITER_COLOR,
    ENEMY_HEX_ORBITER_MIDDLE_COLOR,
    ENEMY_RUNIC_BOMBARDIER_COLOR,
    ENEMY_SHADOW_POUNCER_COLOR,
    ENEMY_SHOOTER_COLOR,
    ENEMY_SHOOTER_INNER_COLOR,
    ENEMY_SHOTGUN_AMBUSHER_COLOR,
    ENEMY_SHOTGUN_AMBUSHER_CORE_COLOR,
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
    GhostRenderStrategy,
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
        # Enemies
        cls.register_enemy("follower", cls.create_follower, weight=0.22)  # perseguidor basico
        cls.register_enemy("shooter", cls.create_shooter, weight=0.12)  # atirador de mira lenta
        cls.register_enemy("quique", cls.create_bouncer, weight=0.11)  # ricochete agressivo
        cls.register_enemy("investida", cls.create_charge, weight=0.10)  # dash telegrafado
        cls.register_enemy("explosivo", cls.create_explosive, weight=0.08)  # bomba suicida
        cls.register_enemy("metralhadora", cls.create_turret, weight=0.06)  # torre de rajada
        cls.register_enemy("morteiro", cls.create_mortar, weight=0.05)  # artilharia em area
        cls.register_enemy("estrafador_arcano", cls.create_arcane_strafer, weight=0.08)  # strafe com tiro preciso
        cls.register_enemy("emboscador_escopeta", cls.create_shotgun_ambusher, weight=0.07)  # burst de curta distancia
        cls.register_enemy("orbitador_hex", cls.create_hex_orbiter, weight=0.06)  # orbita com pressao
        cls.register_enemy("sombra_investida", cls.create_shadow_pouncer, weight=0.06)  # pulo de emboscada
        cls.register_enemy("bombardeiro_runa", cls.create_runic_bombardier, weight=0.06)  # bombardeio runico
        cls.register_enemy("atirador_laser", cls.create_laser_shooter, weight=0.06)  # laser rapido
        cls.register_enemy("kamehameha", cls.create_kamehameha, weight=0.05)  # feixe canalizado
        cls.register_enemy("lanca_chamas", cls.create_flamethrower, weight=0.06)  # cone continuo
        cls.register_enemy("fantasma", cls.create_ghost_boo, weight=0.05)  # invisibilidade intermitente
        cls.register_enemy("buffer", cls.create_buffer_mage, weight=0.04)  # suporte de campo
        cls.register_enemy("sapo", cls.create_frog_acid, weight=0.05)  # acido em rajada
        cls.register_enemy("olho_orbitante", cls.create_orbiting_eye, weight=0.04)  # orbita e triplo disparo
        cls.register_enemy("vigia_supressor", cls.create_suppressor_sentry, weight=0.04)  # controle de distancia
        cls.register_enemy("xama_mineiro", cls.create_miner_shaman, weight=0.04)  # minas preditivas
        cls.register_enemy("algoz_faseado", cls.create_phased_executioner, weight=0.04)  # teleporte ofensivo
        cls.register_enemy("fuzileiro_runico", cls.create_runic_rifleman, weight=0.04)  # rifle de supressao
        cls.register_enemy("necromante_torre", cls.create_tower_necromancer, weight=0.03)  # caster estatico
        cls.register_enemy("aranha_laser", cls.create_laser_arachnid, weight=0.03)  # laser com mobilidade

        # Minibosses
        cls.register_miniboss("miniboss_espiral", cls.create_miniboss_spiral, weight=0.04)  # espiral de projeteis
        cls.register_miniboss("miniboss_cacador", cls.create_miniboss_hunter, weight=0.04)  # caca agressiva
        cls.register_miniboss("miniboss_escudo", cls.create_miniboss_shield, weight=0.03)  # defesa orbital
        cls.register_miniboss("miniboss_sniper", cls.create_miniboss_sniper, weight=0.02)  # tiro de precisao
        cls.register_miniboss("miniboss_laser_matrix", cls.create_miniboss_laser_matrix, weight=0.03)  # grade de laser
        cls.register_miniboss("miniboss_oraculo_kame", cls.create_miniboss_kame_oracle, weight=0.03)  # feixe prolongado
        cls.register_miniboss("miniboss_piro_hidra", cls.create_miniboss_pyro_hydra, weight=0.03)  # fogo multiponto
        cls.register_miniboss("miniboss_fantasma_senhor", cls.create_miniboss_phantom_overlord, weight=0.02)  # stealth tatico
        cls.register_miniboss("miniboss_alquimista", cls.create_miniboss_alchemist, weight=0.02)  # rajada alquimica

        # Bosses
        cls.register_boss("boss", cls.create_boss, weight=0.01)  # chefe balanceado
        cls.register_boss("boss_artilharia", cls.create_boss_artillery, weight=0.005)  # radial de artilharia
        cls.register_boss("boss_caotico", cls.create_boss_chaotic, weight=0.005)  # pressao imprevisivel
        cls.register_boss("boss_colosso_laser", cls.create_boss_laser_colossus, weight=0.004)  # varredura de laser
        cls.register_boss("boss_druida_toxico", cls.create_boss_toxic_druid, weight=0.004)  # invocacao toxica
        cls.register_boss("boss_soberano_espectral", cls.create_boss_spectral_overlord, weight=0.004)  # rajada espectral

    @classmethod
    def _choose_random_kind_from(
        cls,
        registry: dict[str, Callable[[Vector2], Entity]],
        spawn_weights: dict[str, float],
        allowed_kinds: list[str] | None = None,
    ) -> str:
        kinds = list(registry.keys())
        if allowed_kinds is not None:
            allowed_set = set(allowed_kinds)
            kinds = [kind for kind in kinds if kind in allowed_set]
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
    def choose_random_enemy_kind_from(cls, allowed_kinds: list[str]) -> str:
        cls._ensure_registry()
        return cls._choose_random_kind_from(
            cls._enemy_registry,
            cls._enemy_spawn_weights,
            allowed_kinds=allowed_kinds,
        )

    @classmethod
    def choose_random_miniboss_kind(cls) -> str:
        cls._ensure_registry()
        return cls._choose_random_kind_from(cls._miniboss_registry, cls._miniboss_spawn_weights)

    @classmethod
    def choose_random_miniboss_kind_from(cls, allowed_kinds: list[str]) -> str:
        cls._ensure_registry()
        return cls._choose_random_kind_from(
            cls._miniboss_registry,
            cls._miniboss_spawn_weights,
            allowed_kinds=allowed_kinds,
        )

    @classmethod
    def choose_random_boss_kind(cls) -> str:
        cls._ensure_registry()
        return cls._choose_random_kind_from(cls._boss_registry, cls._boss_spawn_weights)

    @classmethod
    def choose_random_boss_kind_from(cls, allowed_kinds: list[str]) -> str:
        cls._ensure_registry()
        return cls._choose_random_kind_from(
            cls._boss_registry,
            cls._boss_spawn_weights,
            allowed_kinds=allowed_kinds,
        )

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
        enemy = creator(position)
        if enemy.has_tag("enemy") and enemy.get_component(EnemyKindComponent) is None:
            enemy.add_component(EnemyKindComponent(kind=kind))
        return enemy

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
        enemy.add_component(ExplosiveComponent(chase_time=3.7, detonate_time=5.1, blast_radius=80.0))
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
        enemy.add_component(MovementComponent(max_speed=168.0))
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
    def create_miniboss_laser_matrix(position: Vector2) -> Entity:
        enemy = Entity()
        enemy.add_tag("enemy")
        enemy.add_component(TransformComponent(position=position))
        enemy.add_component(MovementComponent(max_speed=0.0))
        enemy.add_component(TurretComponent(spiral_angle=random.uniform(0, 360)))
        enemy.add_component(BehaviorComponent(behavior=LaserMatrixMinibossBehavior()))
        enemy.add_component(CollisionComponent(radius=24.0, layer="enemy"))
        enemy.add_component(
            RenderComponent(
                render_strategy=TurretEnemyRenderStrategy(
                    base_color=ENEMY_MINIBOSS_LASER_MATRIX_COLOR,
                    middle_color=(44, 14, 30),
                    active_color=(245, 245, 255),
                    idle_color=ENEMY_MINIBOSS_LASER_MATRIX_COLOR,
                    radius=24.0,
                    pulse_speed=7.0,
                    pulse_gain=3.2,
                    glow_layers=5,
                )
            )
        )
        return enemy

    @staticmethod
    def create_miniboss_kame_oracle(position: Vector2) -> Entity:
        enemy = Entity()
        enemy.add_tag("enemy")
        enemy.add_component(TransformComponent(position=position))
        enemy.add_component(MovementComponent(max_speed=95.0))
        enemy.add_component(
            KamehamehaComponent(
                beam_color=ENEMY_MINIBOSS_KAME_ORACLE_COLOR,
                charge_duration=1.0,
                fire_duration=1.5,
                cooldown_duration=1.0,
                fire_tick=0.06,
            )
        )
        enemy.add_component(BehaviorComponent(behavior=KamehamehaBehavior()))
        enemy.add_component(CollisionComponent(radius=24.0, layer="enemy"))
        enemy.add_component(
            RenderComponent(
                render_strategy=TurretEnemyRenderStrategy(
                    base_color=ENEMY_MINIBOSS_KAME_ORACLE_COLOR,
                    middle_color=(12, 36, 70),
                    active_color=(245, 245, 255),
                    idle_color=ENEMY_MINIBOSS_KAME_ORACLE_COLOR,
                    radius=24.0,
                    pulse_speed=6.4,
                    pulse_gain=3.4,
                    glow_layers=5,
                )
            )
        )
        return enemy

    @staticmethod
    def create_miniboss_pyro_hydra(position: Vector2) -> Entity:
        enemy = Entity()
        enemy.add_tag("enemy")
        enemy.add_component(TransformComponent(position=position))
        enemy.add_component(MovementComponent(max_speed=170.0))
        enemy.add_component(TurretComponent())
        enemy.add_component(BehaviorComponent(behavior=FlamethrowerBehavior()))
        enemy.add_component(CollisionComponent(radius=23.0, layer="enemy"))
        enemy.add_component(
            RenderComponent(
                render_strategy=MortarRenderStrategy(
                    base_color=ENEMY_MINIBOSS_PYRO_COLOR,
                    radius=23.0,
                )
            )
        )
        return enemy

    @staticmethod
    def create_miniboss_phantom_overlord(position: Vector2) -> Entity:
        enemy = Entity()
        enemy.add_tag("enemy")
        enemy.add_component(TransformComponent(position=position))
        enemy.add_component(MovementComponent(max_speed=170.0))
        enemy.add_component(
            GhostComponent(
                hidden_duration=0.95,
                visible_duration=1.3,
                reveal_distance=150.0,
                hidden_speed=190.0,
            )
        )
        enemy.add_component(TurretComponent())
        enemy.add_component(BehaviorComponent(behavior=PhantomOverlordMinibossBehavior()))
        enemy.add_component(CollisionComponent(radius=22.0, layer="enemy"))
        enemy.add_component(
            RenderComponent(
                render_strategy=GhostRenderStrategy(
                    base_color=ENEMY_MINIBOSS_PHANTOM_COLOR,
                    radius=22.0,
                )
            )
        )
        return enemy

    @staticmethod
    def create_miniboss_alchemist(position: Vector2) -> Entity:
        enemy = Entity()
        enemy.add_tag("enemy")
        enemy.add_component(TransformComponent(position=position))
        enemy.add_component(MovementComponent(max_speed=150.0))
        enemy.add_component(
            ShootComponent(
                cooldown=1.1,
                aim_time=0.0,
                bullet_speed=315.0,
                bullet_radius=6.0,
                bullet_color=ENEMY_MINIBOSS_ALCHEMIST_COLOR,
            )
        )
        enemy.add_component(BehaviorComponent(behavior=AlchemistMinibossBehavior()))
        enemy.add_component(CollisionComponent(radius=22.0, layer="enemy"))
        enemy.add_component(
            RenderComponent(
                render_strategy=NeonCoreEnemyRenderStrategy(
                    outer_color=ENEMY_MINIBOSS_ALCHEMIST_COLOR,
                    core_color=(245, 230, 255),
                    radius=22.0,
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
    def create_boss_laser_colossus(position: Vector2) -> Entity:
        enemy = Entity()
        enemy.add_tag("enemy")
        enemy.add_component(TransformComponent(position=position))
        enemy.add_component(MovementComponent(max_speed=100.0))
        enemy.add_component(BossComponent(boss_kind="boss_colosso_laser", variant=random.randint(1, 3)))
        enemy.add_component(BehaviorComponent(behavior=BossBehavior()))
        enemy.add_component(CollisionComponent(radius=42.0, layer="enemy"))
        enemy.add_component(RenderComponent(render_strategy=BossRenderStrategy(radius=42.0)))
        return enemy

    @staticmethod
    def create_boss_toxic_druid(position: Vector2) -> Entity:
        enemy = Entity()
        enemy.add_tag("enemy")
        enemy.add_component(TransformComponent(position=position))
        enemy.add_component(MovementComponent(max_speed=92.0))
        enemy.add_component(BossComponent(boss_kind="boss_druida_toxico", variant=random.randint(1, 3)))
        enemy.add_component(BehaviorComponent(behavior=BossBehavior()))
        enemy.add_component(CollisionComponent(radius=42.0, layer="enemy"))
        enemy.add_component(RenderComponent(render_strategy=BossRenderStrategy(radius=42.0)))
        return enemy

    @staticmethod
    def create_boss_spectral_overlord(position: Vector2) -> Entity:
        enemy = Entity()
        enemy.add_tag("enemy")
        enemy.add_component(TransformComponent(position=position))
        enemy.add_component(MovementComponent(max_speed=108.0))
        enemy.add_component(BossComponent(boss_kind="boss_soberano_espectral", variant=random.randint(1, 3)))
        enemy.add_component(BehaviorComponent(behavior=BossBehavior()))
        enemy.add_component(CollisionComponent(radius=42.0, layer="enemy"))
        enemy.add_component(RenderComponent(render_strategy=BossRenderStrategy(radius=42.0)))
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

    @staticmethod
    def create_arcane_strafer(position: Vector2) -> Entity:
        enemy = Entity()
        enemy.add_tag("enemy")
        enemy.add_component(TransformComponent(position=position))
        enemy.add_component(MovementComponent(max_speed=190.0))
        enemy.add_component(
            ShootComponent(
                cooldown=1.05,
                aim_time=0.3,
                bullet_speed=290.0,
                bullet_radius=6.0,
                bullet_color=ENEMY_ARCANE_STRAFER_COLOR,
            )
        )
        enemy.add_component(BehaviorComponent(behavior=ArcaneStraferBehavior()))
        enemy.add_component(CollisionComponent(radius=14.0, layer="enemy"))
        enemy.add_component(
            RenderComponent(
                render_strategy=ShooterRenderStrategy(
                    outer_color=ENEMY_ARCANE_STRAFER_COLOR,
                    inner_color=ENEMY_ARCANE_STRAFER_INNER_COLOR,
                    radius=14.0,
                )
            )
        )
        return enemy

    @staticmethod
    def create_shotgun_ambusher(position: Vector2) -> Entity:
        enemy = Entity()
        enemy.add_tag("enemy")
        enemy.add_component(TransformComponent(position=position))
        enemy.add_component(MovementComponent(max_speed=145.0))
        enemy.add_component(TurretComponent())
        enemy.add_component(BehaviorComponent(behavior=ShotgunAmbusherBehavior()))
        enemy.add_component(CollisionComponent(radius=14.0, layer="enemy"))
        enemy.add_component(
            RenderComponent(
                render_strategy=NeonCoreEnemyRenderStrategy(
                    outer_color=ENEMY_SHOTGUN_AMBUSHER_COLOR,
                    core_color=ENEMY_SHOTGUN_AMBUSHER_CORE_COLOR,
                    radius=14.0,
                )
            )
        )
        return enemy

    @staticmethod
    def create_hex_orbiter(position: Vector2) -> Entity:
        enemy = Entity()
        enemy.add_tag("enemy")
        enemy.add_component(TransformComponent(position=position))
        enemy.add_component(MovementComponent(max_speed=165.0))
        enemy.add_component(TurretComponent(spiral_angle=random.uniform(0, 360)))
        enemy.add_component(BehaviorComponent(behavior=HexOrbiterBehavior()))
        enemy.add_component(CollisionComponent(radius=15.0, layer="enemy"))
        enemy.add_component(
            RenderComponent(
                render_strategy=TurretEnemyRenderStrategy(
                    base_color=ENEMY_HEX_ORBITER_COLOR,
                    middle_color=ENEMY_HEX_ORBITER_MIDDLE_COLOR,
                    active_color=(245, 245, 245),
                    idle_color=ENEMY_HEX_ORBITER_COLOR,
                    radius=15.0,
                    pulse_speed=6.0,
                    pulse_gain=2.2,
                    glow_layers=4,
                )
            )
        )
        return enemy

    @staticmethod
    def create_shadow_pouncer(position: Vector2) -> Entity:
        enemy = Entity()
        enemy.add_tag("enemy")
        enemy.add_component(TransformComponent(position=position))
        enemy.add_component(MovementComponent(max_speed=210.0))
        enemy.add_component(ChargeComponent(state="stalking", timer=1.2))
        enemy.add_component(BehaviorComponent(behavior=ShadowPouncerBehavior()))
        enemy.add_component(CollisionComponent(radius=13.0, layer="enemy"))
        enemy.add_component(
            RenderComponent(
                render_strategy=ChargeEnemyRenderStrategy(
                    base_color=ENEMY_SHADOW_POUNCER_COLOR,
                    radius=13.0,
                )
            )
        )
        return enemy

    @staticmethod
    def create_runic_bombardier(position: Vector2) -> Entity:
        enemy = Entity()
        enemy.add_tag("enemy")
        enemy.add_component(TransformComponent(position=position))
        enemy.add_component(MovementComponent(max_speed=145.0))
        enemy.add_component(TurretComponent())
        enemy.add_component(BehaviorComponent(behavior=RunicBombardierBehavior()))
        enemy.add_component(CollisionComponent(radius=17.0, layer="enemy"))
        enemy.add_component(
            RenderComponent(
                render_strategy=MortarRenderStrategy(
                    base_color=ENEMY_RUNIC_BOMBARDIER_COLOR,
                    radius=17.0,
                )
            )
        )
        return enemy

    @staticmethod
    def create_laser_shooter(position: Vector2) -> Entity:
        enemy = Entity()
        enemy.add_tag("enemy")
        enemy.add_component(TransformComponent(position=position))
        enemy.add_component(MovementComponent(max_speed=0.0))
        enemy.add_component(
            ShootComponent(
                cooldown=0.42,
                aim_time=0.0,
                bullet_speed=420.0,
                bullet_radius=5.0,
                bullet_color=ENEMY_LASER_SHOOTER_COLOR,
            )
        )
        enemy.add_component(BehaviorComponent(behavior=LaserShooterBehavior()))
        enemy.add_component(CollisionComponent(radius=14.0, layer="enemy"))
        enemy.add_component(
            RenderComponent(
                render_strategy=ShooterRenderStrategy(
                    outer_color=ENEMY_LASER_SHOOTER_COLOR,
                    inner_color=ENEMY_LASER_SHOOTER_INNER_COLOR,
                    radius=14.0,
                )
            )
        )
        return enemy

    @staticmethod
    def create_kamehameha(position: Vector2) -> Entity:
        enemy = Entity()
        enemy.add_tag("enemy")
        enemy.add_component(TransformComponent(position=position))
        enemy.add_component(MovementComponent(max_speed=0.0))
        enemy.add_component(KamehamehaComponent(beam_color=ENEMY_KAMEHAMEHA_COLOR))
        enemy.add_component(BehaviorComponent(behavior=KamehamehaBehavior()))
        enemy.add_component(CollisionComponent(radius=18.0, layer="enemy"))
        enemy.add_component(
            RenderComponent(
                render_strategy=TurretEnemyRenderStrategy(
                    base_color=ENEMY_KAMEHAMEHA_COLOR,
                    middle_color=(12, 36, 70),
                    active_color=(245, 245, 255),
                    idle_color=ENEMY_KAMEHAMEHA_COLOR,
                    radius=18.0,
                    pulse_speed=7.0,
                    pulse_gain=2.6,
                    glow_layers=4,
                )
            )
        )
        return enemy

    @staticmethod
    def create_flamethrower(position: Vector2) -> Entity:
        enemy = Entity()
        enemy.add_tag("enemy")
        enemy.add_component(TransformComponent(position=position))
        enemy.add_component(MovementComponent(max_speed=135.0))
        enemy.add_component(TurretComponent())
        enemy.add_component(BehaviorComponent(behavior=FlamethrowerBehavior()))
        enemy.add_component(CollisionComponent(radius=15.0, layer="enemy"))
        enemy.add_component(
            RenderComponent(
                render_strategy=MortarRenderStrategy(
                    base_color=ENEMY_FLAMETHROWER_COLOR,
                    radius=15.0,
                )
            )
        )
        return enemy

    @staticmethod
    def create_ghost_boo(position: Vector2) -> Entity:
        enemy = Entity()
        enemy.add_tag("enemy")
        enemy.add_component(TransformComponent(position=position))
        enemy.add_component(MovementComponent(max_speed=165.0))
        enemy.add_component(GhostComponent())
        enemy.add_component(BehaviorComponent(behavior=GhostBooBehavior()))
        enemy.add_component(CollisionComponent(radius=13.0, layer="enemy"))
        enemy.add_component(
            RenderComponent(
                render_strategy=GhostRenderStrategy(
                    base_color=ENEMY_GHOST_COLOR,
                    radius=13.0,
                )
            )
        )
        return enemy

    @staticmethod
    def create_buffer_mage(position: Vector2) -> Entity:
        enemy = Entity()
        enemy.add_tag("enemy")
        enemy.add_component(TransformComponent(position=position))
        enemy.add_component(MovementComponent(max_speed=125.0))
        enemy.add_component(DashOnlyDefeatComponent(enabled=True))
        enemy.add_component(BehaviorComponent(behavior=BufferMageBehavior()))
        enemy.add_component(CollisionComponent(radius=14.0, layer="enemy"))
        enemy.add_component(
            RenderComponent(
                render_strategy=NeonCoreEnemyRenderStrategy(
                    outer_color=ENEMY_BUFFER_COLOR,
                    core_color=ENEMY_BUFFER_CORE_COLOR,
                    radius=14.0,
                )
            )
        )
        return enemy

    @staticmethod
    def create_frog_acid(position: Vector2) -> Entity:
        enemy = Entity()
        enemy.add_tag("enemy")
        enemy.add_component(TransformComponent(position=position))
        enemy.add_component(MovementComponent(max_speed=180.0))
        enemy.add_component(TurretComponent())
        enemy.add_component(BehaviorComponent(behavior=FrogAcidBehavior()))
        enemy.add_component(CollisionComponent(radius=16.0, layer="enemy"))
        enemy.add_component(
            RenderComponent(
                render_strategy=NeonCoreEnemyRenderStrategy(
                    outer_color=ENEMY_FROG_COLOR,
                    core_color=(210, 255, 214),
                    radius=16.0,
                )
            )
        )
        return enemy

    @staticmethod
    def create_orbiting_eye(position: Vector2) -> Entity:
        enemy = EnemyFactory.create_follower(position)
        enemy.add_component(MovementComponent(max_speed=170.0))
        enemy.add_component(BehaviorComponent(behavior=OrbitShooterBehavior(orbit_radius=175.0, angular_speed=2.1)))
        enemy.add_component(CollisionComponent(radius=14.0, layer="enemy"))
        enemy.add_component(
            RenderComponent(
                render_strategy=TurretEnemyRenderStrategy(
                    base_color=(138, 216, 255),
                    middle_color=(18, 36, 66),
                    active_color=(245, 245, 255),
                    idle_color=(138, 216, 255),
                    radius=14.0,
                    pulse_speed=7.0,
                    pulse_gain=2.0,
                    glow_layers=4,
                )
            )
        )
        return enemy

    @staticmethod
    def create_suppressor_sentry(position: Vector2) -> Entity:
        enemy = EnemyFactory.create_follower(position)
        enemy.add_component(MovementComponent(max_speed=178.0))
        enemy.add_component(BehaviorComponent(behavior=SuppressorBehavior(preferred_distance=240.0)))
        enemy.add_component(CollisionComponent(radius=14.0, layer="enemy"))
        enemy.add_component(
            RenderComponent(
                render_strategy=NeonCoreEnemyRenderStrategy(
                    outer_color=(252, 238, 150),
                    core_color=(255, 248, 205),
                    radius=14.0,
                )
            )
        )
        return enemy

    @staticmethod
    def create_miner_shaman(position: Vector2) -> Entity:
        enemy = EnemyFactory.create_flamethrower(position)
        enemy.add_component(MovementComponent(max_speed=148.0))
        enemy.add_component(BehaviorComponent(behavior=MineLayerBehavior(drop_interval=2.45)))
        enemy.add_component(CollisionComponent(radius=16.0, layer="enemy"))
        enemy.add_component(
            RenderComponent(
                render_strategy=MortarRenderStrategy(
                    base_color=(255, 148, 102),
                    radius=16.0,
                )
            )
        )
        return enemy

    @staticmethod
    def create_phased_executioner(position: Vector2) -> Entity:
        enemy = EnemyFactory.create_shadow_pouncer(position)
        enemy.add_component(BehaviorComponent(behavior=BlinkStrikerBehavior(blink_interval=2.2, blink_distance=172.0)))
        enemy.add_component(CollisionComponent(radius=13.0, layer="enemy"))
        enemy.add_component(
            RenderComponent(
                render_strategy=ChargeEnemyRenderStrategy(
                    base_color=(232, 204, 255),
                    radius=13.0,
                )
            )
        )
        return enemy

    @staticmethod
    def create_runic_rifleman(position: Vector2) -> Entity:
        enemy = EnemyFactory.create_arcane_strafer(position)
        enemy.add_component(MovementComponent(max_speed=202.0))
        enemy.add_component(BehaviorComponent(behavior=SuppressorBehavior(preferred_distance=220.0)))
        enemy.add_component(CollisionComponent(radius=14.0, layer="enemy"))
        enemy.add_component(
            RenderComponent(
                render_strategy=ShooterRenderStrategy(
                    outer_color=(118, 236, 255),
                    inner_color=(226, 252, 255),
                    radius=14.0,
                )
            )
        )
        return enemy

    @staticmethod
    def create_tower_necromancer(position: Vector2) -> Entity:
        enemy = EnemyFactory.create_kamehameha(position)
        enemy.add_component(MovementComponent(max_speed=0.0))
        enemy.add_component(BehaviorComponent(behavior=MineLayerBehavior(drop_interval=2.95)))
        enemy.add_component(CollisionComponent(radius=17.0, layer="enemy"))
        enemy.add_component(
            RenderComponent(
                render_strategy=TurretEnemyRenderStrategy(
                    base_color=(176, 124, 255),
                    middle_color=(48, 22, 72),
                    active_color=(248, 240, 255),
                    idle_color=(176, 124, 255),
                    radius=17.0,
                    pulse_speed=6.0,
                    pulse_gain=2.6,
                    glow_layers=4,
                )
            )
        )
        return enemy

    @staticmethod
    def create_laser_arachnid(position: Vector2) -> Entity:
        enemy = EnemyFactory.create_laser_shooter(position)
        enemy.add_component(MovementComponent(max_speed=188.0))
        enemy.add_component(BehaviorComponent(behavior=SuppressorBehavior(preferred_distance=190.0)))
        enemy.add_component(CollisionComponent(radius=14.0, layer="enemy"))
        enemy.add_component(
            RenderComponent(
                render_strategy=ShooterRenderStrategy(
                    outer_color=(118, 255, 146),
                    inner_color=(230, 255, 238),
                    radius=14.0,
                )
            )
        )
        return enemy
