from __future__ import annotations

from pygame import Vector2

from game.behaviors.advanced_helpers import normalized, smoothing_factor
from game.behaviors.behavior import Behavior
from game.components.data_components import (
    CollisionComponent,
    ExplosiveComponent,
    MovementComponent,
    TransformComponent,
)
from game.core.events import ExplosionTriggered, PlayerDamaged, PlayerDied
from game.ecs.entity import Entity


class ExplosiveBehavior(Behavior):
    BASE_RADIUS = 12.0
    DIRECT_CHASE_SPEED = 168.0
    CHASE_RESPONSIVENESS = 0.18
    ARMING_DISTANCE = 110.0

    def update(self, entity: Entity, world: "GameWorld", dt: float) -> None:
        player = world.player
        if player is None:
            return

        explosive = entity.get_component(ExplosiveComponent)
        transform = entity.get_component(TransformComponent)
        movement = entity.get_component(MovementComponent)
        collision = entity.get_component(CollisionComponent)
        player_transform = player.get_component(TransformComponent)
        if (
            explosive is None
            or transform is None
            or movement is None
            or collision is None
            or player_transform is None
        ):
            return
        if explosive.exploded:
            return

        player_collision = player.get_component(CollisionComponent)
        if player_collision is None:
            return

        explosive.timer += dt
        to_player = player_transform.position - transform.position
        distance_to_player = to_player.length()

        if explosive.timer < explosive.chase_time and distance_to_player > self.ARMING_DISTANCE:
            desired_direction = normalized(to_player)
            desired_velocity = desired_direction * self.DIRECT_CHASE_SPEED
            movement.velocity = movement.velocity.lerp(
                desired_velocity,
                smoothing_factor(self.CHASE_RESPONSIVENESS, dt),
            )
            movement.input_direction = desired_direction
            movement.max_speed = self.DIRECT_CHASE_SPEED
            return

        slowdown = 0.82 if distance_to_player <= self.ARMING_DISTANCE else 0.9
        movement.velocity *= slowdown
        movement.input_direction = normalized(movement.velocity, normalized(to_player))

        arm_time_boost = 0.0
        if distance_to_player <= self.ARMING_DISTANCE:
            arm_time_boost += dt * 0.42
        if distance_to_player <= self.ARMING_DISTANCE * 0.6:
            arm_time_boost += dt * 0.38
        explosive.timer += arm_time_boost

        if explosive.timer >= explosive.detonate_time:
            blast_radius = max(18.0, explosive.blast_radius)
            world.event_bus.publish(ExplosionTriggered(position=Vector2(transform.position)))
            if self._collides(player_transform.position, player_collision.radius, transform.position, blast_radius):
                self._kill_player(world, "Explosao de inimigo")

            for angle in range(0, 360, 45):
                world.spawn_enemy_bullet(
                    transform.position,
                    Vector2(1, 0).rotate(float(angle)),
                    speed=240.0,
                    radius=5.0,
                    color=(250, 228, 96),
                )
            explosive.exploded = True
            world.remove_entity(entity)

    @staticmethod
    def _collides(a_pos: Vector2, a_radius: float, b_pos: Vector2, b_radius: float) -> bool:
        distance_sq = (a_pos - b_pos).length_squared()
        radius_sum = a_radius + b_radius
        return distance_sq <= radius_sum * radius_sum

    @staticmethod
    def _kill_player(world: "GameWorld", cause: str) -> None:
        if world.runtime_state.get("death_transition"):
            return
        world.runtime_state["death_transition"] = True
        world.runtime_state["last_death_cause"] = cause
        world.event_bus.publish(PlayerDamaged())
        world.event_bus.publish(PlayerDied())


from game.core.world import GameWorld
