from __future__ import annotations

from pygame import Vector2

from game.behaviors.advanced_helpers import predict_intercept_position
from game.behaviors.behavior import Behavior
from game.components.data_components import MovementComponent, TransformComponent, TurretComponent
from game.config import ENEMY_MORTAR_BULLET_COLOR
from game.core.enemy_names import enemy_kind_from_entity
from game.ecs.entity import Entity
from game.factories.bullet_factory import BulletFactory


class MortarBehavior(Behavior):
    def __init__(self) -> None:
        self._volley_toggle: dict[int, bool] = {}

    def update(self, entity: Entity, world: "GameWorld", dt: float) -> None:
        player = world.player
        if player is None:
            return

        transform = entity.get_component(TransformComponent)
        movement = entity.get_component(MovementComponent)
        turret = entity.get_component(TurretComponent)
        player_transform = player.get_component(TransformComponent)
        if transform is None or movement is None or turret is None or player_transform is None:
            return

        movement.velocity.update(0.0, 0.0)
        movement.input_direction = Vector2()
        movement.max_speed = 0.0

        turret.shot_timer += dt
        if turret.shot_timer < 2.0:
            return
        turret.shot_timer = 0.0

        player_movement = player.get_component(MovementComponent)
        target_velocity = Vector2() if player_movement is None else Vector2(player_movement.velocity)
        target = predict_intercept_position(
            origin=transform.position,
            target_position=player_transform.position,
            target_velocity=target_velocity,
            projectile_speed=240.0,
            max_lead_time=0.55,
        )
        bullet_speed = 240.0
        explosion_radius = 40.0
        owner_kind = enemy_kind_from_entity(entity)
        volley_double = self._volley_toggle.get(entity.id, False)
        self._volley_toggle[entity.id] = not volley_double

        targets = [target]
        if volley_double:
            lateral = (target - transform.position)
            side = Vector2(-lateral.y, lateral.x)
            side = side.normalize() if side.length_squared() > 0 else Vector2(0, 1)
            targets.append(target + (side * 36.0))

        for shell_target in targets:
            world.add_entity(
                BulletFactory.create_mortar_shell(
                    origin=transform.position,
                    target=shell_target,
                    speed=bullet_speed,
                    radius=10.0,
                    explosion_radius=explosion_radius,
                    color=ENEMY_MORTAR_BULLET_COLOR,
                    owner_kind=owner_kind,
                )
            )
        direction = target - transform.position
        travel_time = 0.0 if direction.length_squared() <= 0 else direction.length() / bullet_speed
        for shell_target in targets:
            world.add_entity(
                BulletFactory.create_mortar_target_marker(
                    position=shell_target,
                    duration=max(0.15, travel_time),
                    color=ENEMY_MORTAR_BULLET_COLOR,
                    radius=explosion_radius,
                )
            )


from game.core.world import GameWorld
