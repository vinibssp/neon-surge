from __future__ import annotations

from pygame import Vector2

from game.behaviors.advanced_helpers import normalized
from game.behaviors.behavior import Behavior
from game.components.data_components import MovementComponent, ShootComponent, TransformComponent
from game.ecs.entity import Entity
from game.systems.world_queries import ENEMY_BEHAVIOR_QUERY


class AlchemistMinibossBehavior(Behavior):
    def __init__(self) -> None:
        self._buff_tick: dict[int, float] = {}
        self._ring_tick: dict[int, float] = {}

    def update(self, entity: Entity, world: "GameWorld", dt: float) -> None:
        player = world.player
        if player is None:
            return

        transform = entity.get_component(TransformComponent)
        movement = entity.get_component(MovementComponent)
        shoot = entity.get_component(ShootComponent)
        player_transform = player.get_component(TransformComponent)
        if transform is None or movement is None or shoot is None or player_transform is None:
            return

        to_player = player_transform.position - transform.position
        tangent = Vector2(-to_player.y, to_player.x)
        movement.input_direction = normalized((normalized(tangent) * 0.85) + (normalized(to_player) * 0.15), normalized(to_player))
        movement.max_speed = 150.0

        buff_tick = self._buff_tick.get(entity.id, 0.0) + dt
        self._buff_tick[entity.id] = buff_tick
        if buff_tick >= 0.5:
            self._buff_tick[entity.id] = 0.0
            for target in world.query(ENEMY_BEHAVIOR_QUERY):
                if target is entity:
                    continue
                t_pos = target.get_component(TransformComponent)
                t_move = target.get_component(MovementComponent)
                if t_pos is None or t_move is None:
                    continue
                if (t_pos.position - transform.position).length() > 260.0:
                    continue
                t_move.max_speed *= 1.1
                if t_move.velocity.length_squared() > 0.0:
                    t_move.velocity *= 1.05

        shoot.cooldown_left -= dt
        if shoot.cooldown_left <= 0.0:
            shoot.cooldown_left = shoot.cooldown
            world.spawn_enemy_bullet(
                transform.position,
                normalized(to_player),
                speed=shoot.bullet_speed,
                radius=shoot.bullet_radius,
                color=shoot.bullet_color,
            )

        ring_tick = self._ring_tick.get(entity.id, 0.0) + dt
        self._ring_tick[entity.id] = ring_tick
        if ring_tick < 2.2:
            return
        self._ring_tick[entity.id] = 0.0
        for angle in range(0, 360, 45):
            world.spawn_enemy_bullet(
                transform.position,
                Vector2(1, 0).rotate(float(angle)),
                speed=250.0,
                radius=5.0,
                color=(176, 130, 255),
            )


from game.core.world import GameWorld
