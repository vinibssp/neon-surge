from __future__ import annotations

from pygame import Vector2

from game.behaviors.advanced_helpers import normalized
from game.behaviors.behavior import Behavior
from game.components.data_components import (
    BossComponent,
    ChargeComponent,
    ExplosiveComponent,
    MovementComponent,
    ShootComponent,
    SniperComponent,
    TransformComponent,
    TurretComponent,
)
from game.ecs.entity import Entity
from game.systems.world_queries import ENEMY_BEHAVIOR_QUERY


class BufferMageBehavior(Behavior):
    def __init__(self) -> None:
        self._buff_pulse_left: dict[int, float] = {}

    def update(self, entity: Entity, world: "GameWorld", dt: float) -> None:
        player = world.player
        if player is None:
            return

        transform = entity.get_component(TransformComponent)
        movement = entity.get_component(MovementComponent)
        player_transform = player.get_component(TransformComponent)
        if transform is None or movement is None or player_transform is None:
            return

        to_player = player_transform.position - transform.position
        tangent = Vector2(-to_player.y, to_player.x)
        movement.input_direction = normalized(
            (normalized(tangent) * 0.75) + (normalized(to_player) * 0.25),
            normalized(to_player),
        )
        movement.max_speed = 125.0

        pulse_left = self._buff_pulse_left.get(entity.id, 0.0) - dt
        self._buff_pulse_left[entity.id] = pulse_left
        if pulse_left > 0.0:
            return
        self._buff_pulse_left[entity.id] = 0.35

        for target in world.query(ENEMY_BEHAVIOR_QUERY):
            if target is entity:
                continue
            target_transform = target.get_component(TransformComponent)
            target_movement = target.get_component(MovementComponent)
            if target_transform is None or target_movement is None:
                continue

            distance = (target_transform.position - transform.position).length()
            if distance > 250.0:
                continue

            target_movement.max_speed *= 1.16
            if target_movement.velocity.length_squared() > 0.0:
                target_movement.velocity *= 1.08

            shoot = target.get_component(ShootComponent)
            if shoot is not None:
                shoot.cooldown_left = max(0.0, shoot.cooldown_left - 0.18)
                shoot.aim_left = max(0.0, shoot.aim_left - 0.12)

            turret = target.get_component(TurretComponent)
            if turret is not None:
                turret.shot_timer += 0.16

            sniper = target.get_component(SniperComponent)
            if sniper is not None:
                sniper.shot_timer += 0.18

            boss = target.get_component(BossComponent)
            if boss is not None:
                boss.shot_timer += 0.1
                boss.ability_timer += 0.06

            charge = target.get_component(ChargeComponent)
            if charge is not None:
                charge.timer += 0.06

            explosive = target.get_component(ExplosiveComponent)
            if explosive is not None and not explosive.exploded:
                explosive.timer = max(0.0, explosive.timer - 0.05)


from game.core.world import GameWorld
