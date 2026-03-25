from __future__ import annotations

import random

from pygame import Rect, Vector2

from game.components.data_components import CollisionComponent, InvulnerabilityComponent, MovementComponent, TransformComponent
from game.core.events import PlayerDamaged, PlayerDied
from game.core.world import GameWorld
from game.ecs.entity import Entity
from game.factories.enemy_factory import EnemyFactory


class EnvironmentEventSystem:
    EVENT_LAVA = "lava"
    EVENT_SNOW = "snow_drift"
    EVENT_WATER = "water_region"
    EVENT_BULLET_CLOUD = "bullet_cloud"
    EVENT_BLACK_HOLE = "black_hole"

    def __init__(
        self,
        world: GameWorld,
        interval: float,
        duration: float,
        snow_drag_multiplier: float,
        snow_turn_response: float,
        water_pirate_count: int,
        bullet_cloud_fire_interval: float,
        black_hole_pull_radius: float,
        black_hole_pull_strength: float,
        black_hole_speed: float,
        black_hole_consume_radius: float,
        lava_warning_duration: float,
        lava_active_duration: float,
        lava_blink_duration: float,
        lava_height_ratio: float,
    ) -> None:
        self.world = world
        self.interval = max(6.0, interval)
        self.duration = max(4.0, duration)
        self.snow_drag_multiplier = max(0.45, min(0.95, snow_drag_multiplier))
        self.snow_turn_response = max(0.04, min(0.6, snow_turn_response))
        self.water_pirate_count = max(1, water_pirate_count)
        self.bullet_cloud_fire_interval = max(0.02, bullet_cloud_fire_interval)
        self.black_hole_pull_radius = max(80.0, black_hole_pull_radius)
        self.black_hole_pull_strength = max(60.0, black_hole_pull_strength)
        self.black_hole_speed = max(8.0, black_hole_speed)
        self.black_hole_consume_radius = max(12.0, min(self.black_hole_pull_radius * 0.5, black_hole_consume_radius))
        self.lava_warning_duration = max(0.5, lava_warning_duration)
        self.lava_active_duration = max(0.6, lava_active_duration)
        self.lava_blink_duration = max(0.2, min(lava_blink_duration, self.lava_active_duration))
        self.lava_height_ratio = max(0.08, min(0.45, lava_height_ratio))

        self._cooldown_left = self.interval
        self._event_time_left = 0.0
        self._active_event: str | None = None
        self._event_region: Rect | None = None
        self._bullet_timer = 0.0
        self._black_hole_position = Vector2()
        self._black_hole_velocity = Vector2()
        self._lava_phase = "warning"
        self._lava_phase_time_left = 0.0

    def update(self, dt: float) -> None:
        self._restore_player_speed()

        if self._active_event is None:
            self._cooldown_left = max(0.0, self._cooldown_left - dt)
            if self._cooldown_left <= 0.0:
                self._start_random_event()
            self._publish_runtime_state()
            return

        self._event_time_left = max(0.0, self._event_time_left - dt)

        if self._active_event == self.EVENT_SNOW:
            self._update_snow_drift(dt)
        elif self._active_event == self.EVENT_WATER:
            self._update_water_region(dt)
        elif self._active_event == self.EVENT_BULLET_CLOUD:
            self._update_bullet_cloud(dt)
        elif self._active_event == self.EVENT_BLACK_HOLE:
            self._update_black_hole(dt)
        elif self._active_event == self.EVENT_LAVA:
            self._update_lava_event(dt)

        if self._event_time_left <= 0.0:
            self._finish_event()

        self._publish_runtime_state()

    def _start_random_event(self) -> None:
        self._active_event = random.choice(
            [self.EVENT_SNOW, self.EVENT_WATER, self.EVENT_BULLET_CLOUD, self.EVENT_BLACK_HOLE, self.EVENT_LAVA]
        )
        self._event_time_left = self.duration
        self._event_region = self._random_region(0.34, 0.46)
        self._bullet_timer = 0.0

        if self._active_event == self.EVENT_WATER:
            self._spawn_water_pirates()

        if self._active_event == self.EVENT_BLACK_HOLE:
            self._black_hole_position = self._random_point_with_margin(120.0)
            heading = Vector2(1, 0).rotate(random.uniform(0.0, 360.0))
            self._black_hole_velocity = heading * self.black_hole_speed

        if self._active_event == self.EVENT_LAVA:
            self._event_region = None
            self._event_time_left = self.lava_warning_duration + self.lava_active_duration
            self._lava_phase = "warning"
            self._lava_phase_time_left = self.lava_warning_duration

    def _finish_event(self) -> None:
        if self._active_event == self.EVENT_WATER:
            self._cleanup_water_pirates()

        self._active_event = None
        self._event_region = None
        self._event_time_left = 0.0
        self._cooldown_left = self.interval
        self.world.runtime_state.pop("environment_event", None)
        self.world.runtime_state.pop("survival_lava", None)

    def _update_snow_drift(self, dt: float) -> None:
        player = self.world.player
        if player is None or self._event_region is None:
            return

        transform = player.get_component(TransformComponent)
        movement = player.get_component(MovementComponent)
        if transform is None or movement is None:
            return

        if not self._event_region.collidepoint(transform.position.x, transform.position.y):
            self.world.runtime_state.pop("snow_last_dir", None)
            return

        base_speed = self._player_base_speed(movement)
        movement.max_speed = base_speed * self.snow_drag_multiplier

        current_input = Vector2(movement.input_direction)
        if current_input.length_squared() <= 0.0:
            return

        desired = current_input.normalize()
        previous = self.world.runtime_state.get("snow_last_dir")
        if not isinstance(previous, Vector2) or previous.length_squared() <= 0.0:
            blended = desired
        else:
            t = max(0.0, min(1.0, self.snow_turn_response * 60.0 * dt))
            blended = previous.lerp(desired, t)
            if blended.length_squared() > 0.0:
                blended = blended.normalize()
            else:
                blended = desired

        movement.input_direction = blended
        self.world.runtime_state["snow_last_dir"] = Vector2(blended)

    def _update_water_region(self, dt: float) -> None:
        del dt

    def _update_bullet_cloud(self, dt: float) -> None:
        region = self._event_region
        if region is None:
            return

        self._bullet_timer += dt
        while self._bullet_timer >= self.bullet_cloud_fire_interval:
            self._bullet_timer -= self.bullet_cloud_fire_interval
            spawn_x = random.uniform(region.left + 8.0, region.right - 8.0)
            direction = Vector2(0, 1).rotate(random.uniform(-10.0, 10.0))
            self.world.spawn_enemy_bullet(
                origin=Vector2(spawn_x, float(region.top + 4)),
                direction=direction,
                speed=330.0,
                radius=4.8,
                color=(255, 205, 105),
            )

    def _update_black_hole(self, dt: float) -> None:
        self._black_hole_position += self._black_hole_velocity * dt
        margin = self.black_hole_consume_radius + 10.0
        if self._black_hole_position.x <= margin or self._black_hole_position.x >= self.world.width - margin:
            self._black_hole_velocity.x *= -1
        if self._black_hole_position.y <= margin or self._black_hole_position.y >= self.world.height - margin:
            self._black_hole_velocity.y *= -1
        self._black_hole_position = self.world.clamp_to_bounds(self._black_hole_position, self.black_hole_consume_radius)

        player = self.world.player
        for entity in tuple(self.world.entities):
            if entity.has_tag("portal") or entity.has_tag("collectible"):
                continue
            if not (entity.has_tag("player") or entity.has_tag("enemy")):
                continue

            transform = entity.get_component(TransformComponent)
            if transform is None:
                continue

            offset = self._black_hole_position - transform.position
            distance = offset.length()
            if distance <= 0.001 or distance > self.black_hole_pull_radius:
                continue

            direction = offset / distance
            pull_ratio = 1.0 - (distance / self.black_hole_pull_radius)
            pull_speed = self.black_hole_pull_strength * pull_ratio

            movement = entity.get_component(MovementComponent)
            if movement is not None:
                movement.velocity += direction * (pull_speed * dt)

            transform.position += direction * (pull_speed * dt)
            radius = self.world.get_collision_radius(entity)
            transform.position = self.world.clamp_to_bounds(transform.position, radius)

            if distance > self.black_hole_consume_radius:
                continue

            if entity is player:
                invulnerability = entity.get_component(InvulnerabilityComponent)
                if invulnerability is not None and invulnerability.time_left > 0.0:
                    continue
                self.world.runtime_state["last_death_cause"] = "Consumido pelo buraco negro"
                self.world.event_bus.publish(PlayerDamaged())
                self.world.event_bus.publish(PlayerDied())
                return

            if entity.has_tag("enemy"):
                self.world.remove_entity(entity)

    def _update_lava_event(self, dt: float) -> None:
        self._lava_phase_time_left = max(0.0, self._lava_phase_time_left - dt)

        if self._lava_phase == "warning":
            if self._lava_phase_time_left <= 0.0:
                self._lava_phase = "active"
                self._lava_phase_time_left = self.lava_active_duration
            self._publish_lava_state()
            return

        self._apply_lava_damage()
        self._publish_lava_state()

    def _apply_lava_damage(self) -> None:
        player = self.world.player
        if player is None:
            return

        transform = player.get_component(TransformComponent)
        collision = player.get_component(CollisionComponent)
        if transform is None or collision is None:
            return

        invulnerability = player.get_component(InvulnerabilityComponent)
        if invulnerability is not None and invulnerability.time_left > 0.0:
            return

        lava_height = self.world.height * self.lava_height_ratio
        lava_line = self.world.height - lava_height
        if transform.position.y + collision.radius < lava_line:
            return

        self.world.runtime_state["last_death_cause"] = "Queimado na lava"
        self.world.event_bus.publish(PlayerDamaged())
        self.world.event_bus.publish(PlayerDied())

    def _lava_blink_visible(self) -> bool:
        if self._lava_phase != "active":
            return False
        if self._lava_phase_time_left > self.lava_blink_duration:
            return True
        progress = (self.lava_blink_duration - self._lava_phase_time_left) * 9.0
        return int(progress) % 2 == 0

    def _publish_lava_state(self) -> None:
        state = "warning" if self._lava_phase == "warning" else "active"
        warning_left = self._lava_phase_time_left if state == "warning" else 0.0
        active_left = self._lava_phase_time_left if state == "active" else 0.0
        self.world.runtime_state["survival_lava"] = {
            "state": state,
            "time_to_lava": warning_left,
            "active_time_left": active_left,
            "blink_visible": self._lava_blink_visible(),
            "height": self.world.height * self.lava_height_ratio,
            "warning_duration": self.lava_warning_duration,
            "blink_duration": self.lava_blink_duration,
        }

    def _spawn_water_pirates(self) -> None:
        region = self._event_region
        if region is None:
            return

        for _ in range(self.water_pirate_count):
            position = Vector2(
                random.uniform(region.left + 30.0, region.right - 30.0),
                random.uniform(region.top + 30.0, region.bottom - 30.0),
            )
            pirate = EnemyFactory.create_by_kind("metralhadora", position)
            pirate.add_tag("env_water_pirate")
            self.world.add_entity(pirate)

    def _cleanup_water_pirates(self) -> None:
        for entity in tuple(self.world.entities):
            if entity.has_tag("env_water_pirate"):
                self.world.remove_entity(entity)
        self.world.pending_add = [
            entity for entity in self.world.pending_add if not entity.has_tag("env_water_pirate")
        ]

    def _player_base_speed(self, movement: MovementComponent) -> float:
        base = self.world.runtime_state.get("player_base_speed")
        if isinstance(base, (float, int)):
            return float(base)
        value = float(movement.max_speed)
        self.world.runtime_state["player_base_speed"] = value
        return value

    def _restore_player_speed(self) -> None:
        player = self.world.player
        if player is None:
            return
        movement = player.get_component(MovementComponent)
        if movement is None:
            return
        base = self.world.runtime_state.get("player_base_speed")
        if isinstance(base, (float, int)):
            movement.max_speed = float(base)

    def _publish_runtime_state(self) -> None:
        payload: dict[str, object] = {
            "name": self._active_event,
            "time_left": self._event_time_left,
            "cooldown_left": self._cooldown_left,
        }

        if self._event_region is not None:
            payload["region"] = (
                float(self._event_region.left),
                float(self._event_region.top),
                float(self._event_region.width),
                float(self._event_region.height),
            )

        if self._active_event == self.EVENT_BLACK_HOLE:
            payload["black_hole"] = {
                "x": float(self._black_hole_position.x),
                "y": float(self._black_hole_position.y),
                "pull_radius": self.black_hole_pull_radius,
                "consume_radius": self.black_hole_consume_radius,
            }
        elif self._active_event == self.EVENT_LAVA:
            payload["lava_phase"] = self._lava_phase
            payload["lava_time_left"] = self._lava_phase_time_left

        self.world.runtime_state["environment_event"] = payload

    def _random_region(self, width_ratio: float, height_ratio: float) -> Rect:
        width = int(self.world.width * width_ratio)
        height = int(self.world.height * height_ratio)
        margin = 48
        left = random.randint(margin, max(margin, self.world.width - width - margin))
        top = random.randint(margin, max(margin, self.world.height - height - margin))
        return Rect(left, top, width, height)

    def _random_point_with_margin(self, margin: float) -> Vector2:
        return Vector2(
            random.uniform(margin, self.world.width - margin),
            random.uniform(margin, self.world.height - margin),
        )
