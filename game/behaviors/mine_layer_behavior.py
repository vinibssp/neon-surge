from __future__ import annotations

from pygame import Vector2

from game.behaviors.advanced_helpers import normalized, predict_intercept_position
from game.behaviors.behavior import Behavior
from game.components.data_components import MovementComponent, TransformComponent
from game.config import ENEMY_MORTAR_BULLET_COLOR
from game.core.enemy_names import enemy_kind_from_entity
from game.ecs.entity import Entity
from game.factories.bullet_factory import BulletFactory


class MineLayerBehavior(Behavior):
    def __init__(self, drop_interval: float = 2.8) -> None:
        self.drop_interval = drop_interval
        self._drop_timer: dict[int, float] = {}

    def update(self, entity: Entity, world: "GameWorld", dt: float) -> None:
        player = world.player
        if player is None:
            return

        transform = entity.get_component(TransformComponent)
        movement = entity.get_component(MovementComponent)
        player_transform = player.get_component(TransformComponent)
        if transform is None or movement is None or player_transform is None:
            return

        chase_direction = normalized(player_transform.position - transform.position)
        movement.input_direction = chase_direction
        movement.max_speed = max(110.0, movement.max_speed)

        entity_id = entity.id
        drop_timer = self._drop_timer.get(entity_id, 0.0) + dt
        self._drop_timer[entity_id] = drop_timer
        if drop_timer < self.drop_interval:
            return

        self._drop_timer[entity_id] = 0.0
        player_movement = player.get_component(MovementComponent)
        target_velocity = Vector2() if player_movement is None else Vector2(player_movement.velocity)
        target = predict_intercept_position(
            origin=transform.position,
            target_position=player_transform.position,
            target_velocity=target_velocity,
            projectile_speed=220.0,
            max_lead_time=0.6,
        )
        owner_kind = enemy_kind_from_entity(entity)
        world.add_entity(
            BulletFactory.create_mortar_shell(
                origin=transform.position,
                target=target,
                speed=220.0,
                radius=9.0,
                explosion_radius=44.0,
                color=ENEMY_MORTAR_BULLET_COLOR,
                owner_kind=owner_kind,
            )
        )
        travel_dir = target - transform.position
        travel_time = 0.0 if travel_dir.length_squared() <= 0 else travel_dir.length() / 220.0
        world.add_entity(
            BulletFactory.create_mortar_target_marker(
                position=target,
                duration=max(0.18, travel_time),
                color=(255, 146, 96),
                radius=44.0,
            )
        )


from game.core.world import GameWorld
