from __future__ import annotations

from game.components.data_components import (
    BehaviorComponent,
    BulletComponent,
    CollisionComponent,
    DashComponent,
    EnergyComponent,
    FollowComponent,
    InvulnerabilityComponent,
    LifetimeComponent,
    MovementComponent,
    ParryComponent,
    MortarShellComponent,
    PortalSpawnComponent,
    RenderComponent,
    ShootComponent,
    StaggeredComponent,
    TransformComponent,
)
from game.ecs.query import WorldQuery

MOVABLE_QUERY = WorldQuery(component_types=(TransformComponent, MovementComponent))
RENDERABLE_QUERY = WorldQuery(component_types=(TransformComponent, RenderComponent))
COLLIDABLE_QUERY = WorldQuery(component_types=(CollisionComponent, TransformComponent))

PLAYER_DASH_QUERY = WorldQuery(
    component_types=(DashComponent, MovementComponent, InvulnerabilityComponent),
    tags=("player",),
)

PLAYER_PARRY_QUERY = WorldQuery(
    component_types=(ParryComponent, TransformComponent),
    tags=("player",),
)

ENEMY_FOLLOW_QUERY = WorldQuery(
    component_types=(FollowComponent, BehaviorComponent),
    tags=("enemy",),
)

ENEMY_BEHAVIOR_QUERY = WorldQuery(
    component_types=(BehaviorComponent,),
    tags=("enemy",),
)

ENEMY_STAGGER_QUERY = WorldQuery(
    component_types=(StaggeredComponent,),
    tags=("enemy",),
)

ENEMY_TRANSFORM_QUERY = WorldQuery(
    component_types=(TransformComponent,),
    tags=("enemy",),
)

ENEMY_SHOOT_QUERY = WorldQuery(
    component_types=(ShootComponent, BehaviorComponent),
    tags=("enemy",),
)

INVULNERABLE_QUERY = WorldQuery(component_types=(InvulnerabilityComponent,))
LIFETIME_QUERY = WorldQuery(component_types=(LifetimeComponent,))
BULLET_QUERY = WorldQuery(component_types=(BulletComponent,), tags=("bullet",))
MORTAR_SHELL_QUERY = WorldQuery(component_types=(MortarShellComponent, TransformComponent), tags=("bullet",))
PORTAL_SPAWN_QUERY = WorldQuery(component_types=(PortalSpawnComponent, TransformComponent))

PLAYER_QUERY = WorldQuery(
    component_types=(EnergyComponent,),
    tags=("player",),
)
