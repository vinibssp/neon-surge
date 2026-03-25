from __future__ import annotations

import math

from pygame import Vector2

from game.behaviors.advanced_helpers import normalized, smoothing_factor
from game.behaviors.behavior import Behavior
from game.components.data_components import (
    MovementComponent,
    OrbitComponent,
    TransformComponent,
    TurretComponent,
)
from game.config import ENEMY_SHIELD_BULLET_COLOR
from game.ecs.entity import Entity


class ShieldMinibossBehavior(Behavior):
    MIN_ORBIT_RADIUS = 120.0
    MAX_ORBIT_RADIUS = 210.0
    ORBIT_RADIUS_ADJUST_RATE = 0.08
    ORBIT_DIRECTION_SWITCH_INTERVAL = 2.6
    MOVE_RESPONSIVENESS = 0.16
    DASH_SPEED = 430.0
    DASH_DURATION = 0.42
    DASH_COOLDOWN = 2.1
    DASH_TRIGGER_DISTANCE = 250.0
    RING_BURST_INTERVAL = 3.4

    def __init__(self) -> None:
        self._dash_time_left = 0.0
        self._dash_cooldown_left = 0.9
        self._dash_direction = Vector2(1, 0)

    def update(self, entity: Entity, world: "GameWorld", dt: float) -> None:
        player = world.player
        if player is None:
            return

        transform = entity.get_component(TransformComponent)
        movement = entity.get_component(MovementComponent)
        turret = entity.get_component(TurretComponent)
        orbit = entity.get_component(OrbitComponent)
        player_transform = player.get_component(TransformComponent)
        if (
            transform is None
            or movement is None
            or turret is None
            or orbit is None
            or player_transform is None
        ):
            return

        turret.shot_timer += dt
        turret.burst_timer += dt
        to_player = player_transform.position - transform.position
        distance_to_player = to_player.length()

        self._dash_cooldown_left = max(0.0, self._dash_cooldown_left - dt)
        if self._dash_time_left > 0.0:
            self._dash_time_left = max(0.0, self._dash_time_left - dt)
            dash_velocity = self._dash_direction * self.DASH_SPEED
            movement.velocity = dash_velocity
            movement.input_direction = self._dash_direction
            movement.max_speed = self.DASH_SPEED
            if self._dash_time_left <= 0.0:
                self._dash_cooldown_left = self.DASH_COOLDOWN
                movement.velocity *= 0.35
                movement.input_direction = normalized(movement.velocity, normalized(to_player))
                movement.max_speed = max(1.0, movement.velocity.length())
            return

        if self._dash_cooldown_left <= 0.0 and distance_to_player <= self.DASH_TRIGGER_DISTANCE:
            self._dash_direction = normalized(player_transform.position - transform.position, self._dash_direction)
            self._dash_time_left = self.DASH_DURATION
            dash_velocity = self._dash_direction * self.DASH_SPEED
            movement.velocity = dash_velocity
            movement.input_direction = self._dash_direction
            movement.max_speed = self.DASH_SPEED
            return

        desired_orbit_radius = max(
            self.MIN_ORBIT_RADIUS,
            min(self.MAX_ORBIT_RADIUS, 90.0 + distance_to_player * 0.45),
        )
        orbit.radius += (desired_orbit_radius - orbit.radius) * smoothing_factor(self.ORBIT_RADIUS_ADJUST_RATE, dt)

        if turret.burst_timer >= self.ORBIT_DIRECTION_SWITCH_INTERVAL:
            turret.burst_timer = 0.0
            orbit.angular_speed *= -1.0

        angular_speed_abs = 1.2 + min(1.4, distance_to_player / 260.0)
        orbit.angular_speed = angular_speed_abs if orbit.angular_speed >= 0.0 else -angular_speed_abs
        orbit.angle += dt * orbit.angular_speed

        orbit_target = player_transform.position + Vector2(math.cos(orbit.angle), math.sin(orbit.angle)) * orbit.radius
        to_target = orbit_target - transform.position
        desired_velocity = normalized(to_target) * (movement.max_speed * 1.18)
        movement.velocity = movement.velocity.lerp(desired_velocity, smoothing_factor(self.MOVE_RESPONSIVENESS, dt))
        movement.input_direction = normalized(movement.velocity, normalized(to_player))
        movement.max_speed = max(1.0, movement.velocity.length())

        shot_interval = 1.35 if distance_to_player > 165.0 else 0.95
        if turret.shot_timer < shot_interval:
            if turret.burst_timer < self.RING_BURST_INTERVAL:
                return
            turret.burst_timer = 0.0
            for angle in range(0, 360, 60):
                world.spawn_enemy_bullet(
                    transform.position,
                    Vector2(1, 0).rotate(float(angle)),
                    speed=250.0,
                    radius=6.0,
                    color=ENEMY_SHIELD_BULLET_COLOR,
                )
            return
        turret.shot_timer = 0.0

        shot_direction = normalized(player_transform.position - transform.position)
        turret.shot_direction = shot_direction

        world.spawn_enemy_bullet(
            transform.position,
            shot_direction,
            speed=280.0,
            radius=7.0,
            color=ENEMY_SHIELD_BULLET_COLOR,
        )

        if distance_to_player <= 165.0:
            world.spawn_enemy_bullet(
                transform.position,
                shot_direction,
                speed=340.0,
                radius=6.0,
                color=ENEMY_SHIELD_BULLET_COLOR,
            )


from game.core.world import GameWorld
