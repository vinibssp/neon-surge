from __future__ import annotations

from pygame import Vector2

from game.components.data_components import (
    BulletComponent,
    CollisionComponent,
    LifetimeComponent,
    MovementComponent,
    MortarShellComponent,
    RenderComponent,
    TransformComponent,
)
from game.config import BULLET_COLOR, BULLET_LIFETIME
from game.ecs.entity import Entity
from game.rendering.strategies import CircleRenderStrategy, MortarTargetMarkerRenderStrategy


class BulletFactory:
    @staticmethod
    def create_enemy_bullet(
        origin: Vector2,
        direction: Vector2,
        speed: float,
        radius: float,
        color: tuple[int, int, int] | None = None,
        owner_entity_id: int | None = None,
        owner_kind: str | None = None,
    ) -> Entity:
        bullet = Entity()
        bullet.add_tag("bullet")
        bullet.add_component(TransformComponent(position=Vector2(origin)))
        normalized = direction.normalize() if direction.length_squared() > 0 else Vector2(1, 0)
        bullet.add_component(
            MovementComponent(
                velocity=normalized * speed,
                input_direction=normalized,
                max_speed=speed,
            )
        )
        bullet.add_component(
            BulletComponent(
                owner_tag="enemy",
                lifetime=BULLET_LIFETIME,
                owner_entity_id=owner_entity_id,
                owner_kind=owner_kind,
            )
        )
        bullet.add_component(CollisionComponent(radius=radius, layer="bullet"))
        bullet.add_component(
            RenderComponent(
                render_strategy=CircleRenderStrategy(
                    color=BULLET_COLOR if color is None else color,
                    radius=radius,
                    style="projectile",
                    pulse_speed=16.0,
                    projectile_variant="shard",
                    trail_length=3,
                )
            )
        )
        return bullet

    @staticmethod
    def create_mortar_shell(
        origin: Vector2,
        target: Vector2,
        speed: float,
        radius: float,
        explosion_radius: float,
        color: tuple[int, int, int] | None = None,
        owner_kind: str | None = None,
    ) -> Entity:
        shell = Entity()
        shell.add_tag("bullet")
        shell.add_component(TransformComponent(position=Vector2(origin)))
        direction = target - origin
        normalized = direction.normalize() if direction.length_squared() > 0 else Vector2(1, 0)
        shell.add_component(
            MovementComponent(
                velocity=normalized * speed,
                input_direction=normalized,
                max_speed=speed,
            )
        )
        shell.add_component(BulletComponent(owner_tag="enemy", lifetime=BULLET_LIFETIME, owner_kind=owner_kind))
        shell.add_component(
            MortarShellComponent(
                target_position=Vector2(target),
                explosion_radius=explosion_radius,
                arrival_epsilon=max(6.0, radius),
            )
        )
        shell.add_component(CollisionComponent(radius=radius, layer="bullet"))
        shell.add_component(
            RenderComponent(
                render_strategy=CircleRenderStrategy(
                    color=BULLET_COLOR if color is None else color,
                    radius=radius,
                    style="projectile",
                    pulse_speed=10.0,
                    projectile_variant="mortar_shell",
                    trail_length=2,
                )
            )
        )
        return shell

    @staticmethod
    def create_mortar_target_marker(
        position: Vector2,
        duration: float,
        color: tuple[int, int, int],
        radius: float,
    ) -> Entity:
        marker = Entity()
        marker.add_component(TransformComponent(position=Vector2(position)))
        marker.add_component(LifetimeComponent(time_left=duration))
        marker.add_component(
            RenderComponent(
                render_strategy=MortarTargetMarkerRenderStrategy(
                    color=color,
                    radius=radius,
                )
            )
        )
        return marker

    @staticmethod
    def create_acid_pool(
        position: Vector2,
        radius: float,
        lifetime: float,
        color: tuple[int, int, int],
        owner_kind: str | None = None,
    ) -> Entity:
        pool = Entity()
        pool.add_tag("bullet")
        pool.add_component(TransformComponent(position=Vector2(position)))
        pool.add_component(MovementComponent(velocity=Vector2(), input_direction=Vector2(), max_speed=0.0))
        pool.add_component(BulletComponent(owner_tag="enemy", lifetime=lifetime, owner_kind=owner_kind))
        pool.add_component(CollisionComponent(radius=radius, layer="bullet"))
        pool.add_component(
            RenderComponent(
                render_strategy=CircleRenderStrategy(
                    color=color,
                    radius=radius,
                    style="projectile",
                    pulse_speed=5.0,
                    projectile_variant="orb",
                    trail_length=0,
                )
            )
        )
        return pool
