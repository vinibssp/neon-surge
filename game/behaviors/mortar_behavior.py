from __future__ import annotations

import random

from pygame import Vector2

from game.behaviors.behavior import Behavior
from game.components.data_components import MovementComponent, TransformComponent, TurretComponent
from game.config import ENEMY_MORTAR_BULLET_COLOR
from game.ecs.entity import Entity
from game.factories.bullet_factory import BulletFactory


class MortarBehavior(Behavior):
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

        target = Vector2(player_transform.position)
        target.x += random.uniform(-30.0, 30.0)
        target.y += random.uniform(-30.0, 30.0)
        bullet_speed = 240.0
        explosion_radius = 40.0
        world.add_entity(
            BulletFactory.create_mortar_shell(
                origin=transform.position,
                target=target,
                speed=bullet_speed,
                radius=10.0,
                explosion_radius=explosion_radius,
                color=ENEMY_MORTAR_BULLET_COLOR,
            )
        )
        direction = target - transform.position
        travel_time = 0.0 if direction.length_squared() <= 0 else direction.length() / bullet_speed
        world.add_entity(
            BulletFactory.create_mortar_target_marker(
                position=target,
                duration=max(0.15, travel_time),
                color=ENEMY_MORTAR_BULLET_COLOR,
                radius=explosion_radius,
            )
        )


from game.core.world import GameWorld
