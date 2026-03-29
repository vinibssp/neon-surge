from __future__ import annotations

import math
import random

from pygame import Rect, Vector2

from game.components.data_components import CollisionComponent, InvulnerabilityComponent, MovementComponent, TransformComponent
from game.config import TEST_PLAYER_IMMORTAL
from game.core.events import PlayerDamaged, PlayerDied
from game.core.world import GameWorld
from game.systems.world_queries import COLLIDABLE_QUERY


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
        black_hole_warning_duration: float,
        lava_warning_duration: float,
        lava_active_duration: float,
        lava_blink_duration: float,
        lava_height_ratio: float,
        forced_event: str | None = None,
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
        self.black_hole_warning_duration = max(0.5, black_hole_warning_duration)
        self.lava_warning_duration = max(0.5, lava_warning_duration)
        self.lava_active_duration = max(0.6, lava_active_duration)
        self.lava_blink_duration = max(0.2, min(lava_blink_duration, self.lava_active_duration))
        self.lava_height_ratio = max(0.08, min(0.45, lava_height_ratio))
        available_events = {
            self.EVENT_SNOW,
            self.EVENT_WATER,
            self.EVENT_BULLET_CLOUD,
            self.EVENT_BLACK_HOLE,
            self.EVENT_LAVA,
        }
        self._forced_event = forced_event if forced_event in available_events else None

        self._cooldown_left = self.interval
        self._event_time_left = 0.0
        self._active_event: str | None = None
        self._event_region: Rect | None = None
        self._bullet_timer = 0.0
        self._black_hole_position = Vector2()
        self._black_hole_velocity = Vector2()
        self._black_hole_phase = "warning"
        self._black_hole_phase_time_left = 0.0
        self._lava_phase = "warning"
        self._lava_phase_time_left = 0.0
        self._lava_regions: list[Rect] = []
        self._lava_pattern = "pool"
        self._water_phase = "warning"
        self._water_phase_time_left = 0.0
        self._water_warning_duration = 0.0
        self._water_active_duration = max(2.4, self.duration)
        self._water_blink_duration = min(1.2, self._water_active_duration * 0.35)

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
        event_options = [self.EVENT_SNOW, self.EVENT_WATER, self.EVENT_BULLET_CLOUD, self.EVENT_BLACK_HOLE, self.EVENT_LAVA]
        self._active_event = self._forced_event if self._forced_event is not None else random.choice(event_options)
        self._event_time_left = self.duration
        self._event_region = self._random_region(0.34, 0.46)
        self._bullet_timer = 0.0

        if self._active_event == self.EVENT_SNOW:
            self._event_region = Rect(0, 0, self.world.width, self.world.height)

        if self._active_event == self.EVENT_WATER:
            self._event_region = Rect(0, 0, self.world.width, self.world.height)
            self._event_time_left = self._water_active_duration
            self._water_phase = "active"
            self._water_phase_time_left = self._water_active_duration

        if self._active_event == self.EVENT_BLACK_HOLE:
            self._event_time_left = self.black_hole_warning_duration + self.duration
            self._black_hole_phase = "warning"
            self._black_hole_phase_time_left = self.black_hole_warning_duration
            self._black_hole_position = self._random_point_with_margin(120.0)
            heading = Vector2(1, 0).rotate(random.uniform(0.0, 360.0))
            self._black_hole_velocity = heading * self.black_hole_speed

        if self._active_event == self.EVENT_LAVA:
            self._lava_pattern, self._lava_regions = self._build_lava_regions()
            self._event_region = self._lava_regions[0] if self._lava_regions else None
            self._event_time_left = self.lava_warning_duration + self.lava_active_duration
            self._lava_phase = "warning"
            self._lava_phase_time_left = self.lava_warning_duration

    def _finish_event(self) -> None:
        self._active_event = None
        self._event_region = None
        self._lava_regions = []
        self._black_hole_phase = "warning"
        self._black_hole_phase_time_left = 0.0
        self._water_phase = "warning"
        self._water_phase_time_left = 0.0
        self._event_time_left = 0.0
        self._cooldown_left = self.interval
        self.world.runtime_state.pop("environment_event", None)
        self.world.runtime_state.pop("survival_lava", None)
        self.world.runtime_state.pop("survival_water", None)

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
        self._water_phase_time_left = max(0.0, self._water_phase_time_left - dt)

        self._apply_water_drag(dt)
        self._publish_water_state()

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
        self._black_hole_phase_time_left = max(0.0, self._black_hole_phase_time_left - dt)

        if self._black_hole_phase == "warning":
            if self._black_hole_phase_time_left <= 0.0:
                self._black_hole_phase = "active"
                self._black_hole_phase_time_left = self.duration
            return

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
                self._kill_player("Consumido pelo buraco negro")
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

    def _kill_player(self, cause: str) -> None:
        if TEST_PLAYER_IMMORTAL:
            return
        if self.world.runtime_state.get("death_transition"):
            return
        self.world.runtime_state["death_transition"] = True
        self.world.runtime_state["last_death_cause"] = cause
        self.world.event_bus.publish(PlayerDamaged())
        self.world.event_bus.publish(PlayerDied())

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

        if not self._lava_regions:
            return

        in_lava = any(
            self._circle_overlaps_rect(transform.position, collision.radius, lava_region)
            for lava_region in self._lava_regions
        )
        if not in_lava:
            return

        self._kill_player("Queimado na lava")

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
        region = self._event_region
        region_payload = None
        if region is not None:
            region_payload = (
                float(region.left),
                float(region.top),
                float(region.width),
                float(region.height),
            )
        regions_payload: tuple[tuple[float, float, float, float], ...] = tuple(
            (
                float(lava_region.left),
                float(lava_region.top),
                float(lava_region.width),
                float(lava_region.height),
            )
            for lava_region in self._lava_regions
        )
        self.world.runtime_state["survival_lava"] = {
            "state": state,
            "time_to_lava": warning_left,
            "active_time_left": active_left,
            "blink_visible": self._lava_blink_visible(),
            "height": 0.0 if region is None else float(region.height),
            "region": region_payload,
            "regions": regions_payload,
            "pattern": self._lava_pattern,
            "warning_duration": self.lava_warning_duration,
            "blink_duration": self.lava_blink_duration,
        }

    def _water_blink_visible(self) -> bool:
        if self._water_phase != "active":
            return False
        if self._water_phase_time_left > self._water_blink_duration:
            return True
        progress = (self._water_blink_duration - self._water_phase_time_left) * 8.0
        return int(progress) % 2 == 0

    def _publish_water_state(self) -> None:
        state = "warning" if self._water_phase == "warning" else "active"
        warning_left = self._water_phase_time_left if state == "warning" else 0.0
        active_left = self._water_phase_time_left if state == "active" else 0.0
        region = self._event_region
        region_payload = None
        if region is not None:
            region_payload = (
                float(region.left),
                float(region.top),
                float(region.width),
                float(region.height),
            )
        self.world.runtime_state["survival_water"] = {
            "state": state,
            "time_to_water": warning_left,
            "active_time_left": active_left,
            "blink_visible": self._water_blink_visible(),
            "region": region_payload,
            "warning_duration": self._water_warning_duration,
            "blink_duration": self._water_blink_duration,
        }

    def _apply_water_drag(self, dt: float) -> None:
        region = self._event_region
        if region is None:
            return

        player = self.world.player
        for entity in self.world.query(COLLIDABLE_QUERY):
            if not (entity.has_tag("player") or entity.has_tag("enemy")):
                continue
            transform = entity.get_component(TransformComponent)
            movement = entity.get_component(MovementComponent)
            if transform is None or movement is None:
                continue
            if not region.collidepoint(transform.position.x, transform.position.y):
                continue

            drag_multiplier = 0.62 if entity is player else 0.74
            if entity is player:
                base_speed = self._player_base_speed(movement)
                movement.max_speed = base_speed * drag_multiplier
            else:
                movement.max_speed *= drag_multiplier
            movement.velocity *= max(0.0, 1.0 - (dt * 2.6))

            current_input = Vector2(movement.input_direction)
            if current_input.length_squared() <= 0.0:
                continue
            desired = current_input.normalize()
            sway = Vector2(-desired.y, desired.x) * (
                0.22 * math.sin((self._event_time_left * 4.2) + transform.position.x * 0.01)
            )
            mixed = desired + sway
            if mixed.length_squared() > 0.0:
                movement.input_direction = mixed.normalize()

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
            warning_left = self._black_hole_phase_time_left if self._black_hole_phase == "warning" else 0.0
            active_left = self._black_hole_phase_time_left if self._black_hole_phase == "active" else 0.0
            payload["black_hole"] = {
                "x": float(self._black_hole_position.x),
                "y": float(self._black_hole_position.y),
                "pull_radius": self.black_hole_pull_radius,
                "consume_radius": self.black_hole_consume_radius,
                "phase": self._black_hole_phase,
                "time_to_active": warning_left,
                "active_time_left": active_left,
                "warning_duration": self.black_hole_warning_duration,
            }
        elif self._active_event == self.EVENT_WATER:
            payload["water_phase"] = self._water_phase
            payload["water_time_left"] = self._water_phase_time_left
        elif self._active_event == self.EVENT_LAVA:
            payload["lava_phase"] = self._lava_phase
            payload["lava_time_left"] = self._lava_phase_time_left
            payload["lava_pattern"] = self._lava_pattern

        self.world.runtime_state["environment_event"] = payload

    def _random_region(self, width_ratio: float, height_ratio: float) -> Rect:
        width = int(self.world.width * width_ratio)
        height = int(self.world.height * height_ratio)
        margin = 48
        left = random.randint(margin, max(margin, self.world.width - width - margin))
        top = random.randint(margin, max(margin, self.world.height - height - margin))
        return Rect(left, top, width, height)

    def _build_lava_regions(self) -> tuple[str, list[Rect]]:
        lava_height_ratio = max(0.08, min(0.45, self.lava_height_ratio))
        pattern = random.choice(("pool", "cross", "lanes", "ring", "fork", "checker"))
        margin = 54

        if pattern == "pool":
            width_ratio = max(0.28, min(0.55, 0.22 + (lava_height_ratio * 1.2)))
            height_ratio = max(0.14, min(0.42, lava_height_ratio * 1.35))
            return pattern, [self._random_region(width_ratio, height_ratio)]

        if pattern == "cross":
            stripe_thickness = int(self.world.height * max(0.08, min(0.2, lava_height_ratio * 0.72)))
            vertical_width = int(self.world.width * max(0.08, min(0.18, lava_height_ratio * 0.66)))
            cross_x = random.randint(
                margin + vertical_width,
                max(margin + vertical_width, self.world.width - margin - vertical_width),
            )
            cross_y = random.randint(
                margin + stripe_thickness,
                max(margin + stripe_thickness, self.world.height - margin - stripe_thickness),
            )
            horizontal = Rect(margin, cross_y - stripe_thickness // 2, self.world.width - (margin * 2), stripe_thickness)
            vertical = Rect(cross_x - vertical_width // 2, margin, vertical_width, self.world.height - (margin * 2))
            return pattern, [horizontal, vertical]

        if pattern == "ring":
            arena_w = self.world.width - (margin * 2)
            arena_h = self.world.height - (margin * 2)
            ring_thickness = int(min(arena_w, arena_h) * max(0.07, min(0.16, lava_height_ratio * 0.72)))
            center_box_w = int(arena_w * random.uniform(0.28, 0.42))
            center_box_h = int(arena_h * random.uniform(0.26, 0.4))
            center_left = (self.world.width // 2) - (center_box_w // 2)
            center_top = (self.world.height // 2) - (center_box_h // 2)
            top_band = Rect(margin, margin, arena_w, ring_thickness)
            bottom_band = Rect(margin, self.world.height - margin - ring_thickness, arena_w, ring_thickness)
            left_band = Rect(margin, margin + ring_thickness, ring_thickness, arena_h - (ring_thickness * 2))
            right_band = Rect(
                self.world.width - margin - ring_thickness,
                margin + ring_thickness,
                ring_thickness,
                arena_h - (ring_thickness * 2),
            )
            center_horizontal = Rect(center_left, center_top, center_box_w, max(12, ring_thickness // 2))
            center_vertical = Rect(
                center_left + (center_box_w // 2) - (max(12, ring_thickness // 2) // 2),
                center_top,
                max(12, ring_thickness // 2),
                center_box_h,
            )
            return pattern, [top_band, bottom_band, left_band, right_band, center_horizontal, center_vertical]

        if pattern == "fork":
            base_thickness = int(self.world.height * max(0.07, min(0.16, lava_height_ratio * 0.62)))
            center_x = random.randint(margin + 120, max(margin + 120, self.world.width - margin - 120))
            stem = Rect(center_x - (base_thickness // 2), margin, base_thickness, self.world.height - (margin * 2))
            branch_w = int(self.world.width * random.uniform(0.22, 0.34))
            branch_h = max(12, int(base_thickness * 0.9))
            split_y = random.randint(margin + 140, max(margin + 140, self.world.height - margin - 140))
            left_branch = Rect(max(margin, center_x - branch_w), split_y - (branch_h // 2), branch_w, branch_h)
            right_branch = Rect(center_x, split_y + 50 - (branch_h // 2), branch_w, branch_h)
            return pattern, [stem, left_branch, right_branch]

        if pattern == "checker":
            cell_w = int(self.world.width * random.uniform(0.12, 0.18))
            cell_h = int(self.world.height * random.uniform(0.1, 0.16))
            cols = 4
            rows = 3
            gap_x = int((self.world.width - (margin * 2) - (cell_w * cols)) / max(1, cols - 1))
            gap_y = int((self.world.height - (margin * 2) - (cell_h * rows)) / max(1, rows - 1))
            regions: list[Rect] = []
            for row in range(rows):
                for col in range(cols):
                    if (row + col) % 2 != 0:
                        continue
                    left = margin + (col * (cell_w + gap_x))
                    top = margin + (row * (cell_h + gap_y))
                    regions.append(Rect(left, top, cell_w, cell_h))
            return pattern, regions

        lane_thickness = int(self.world.height * max(0.08, min(0.17, lava_height_ratio * 0.6)))
        if random.random() < 0.5:
            lane_gap = int(self.world.height * random.uniform(0.14, 0.24))
            center = random.randint(margin + lane_thickness, max(margin + lane_thickness, self.world.height - margin - lane_thickness))
            top_lane_y = max(margin, center - lane_gap // 2 - lane_thickness)
            bottom_lane_y = min(self.world.height - margin - lane_thickness, center + lane_gap // 2)
            top_lane = Rect(margin, top_lane_y, self.world.width - (margin * 2), lane_thickness)
            bottom_lane = Rect(margin, bottom_lane_y, self.world.width - (margin * 2), lane_thickness)
            return pattern, [top_lane, bottom_lane]

        lane_width = int(self.world.width * max(0.08, min(0.17, lava_height_ratio * 0.6)))
        lane_gap = int(self.world.width * random.uniform(0.14, 0.24))
        center = random.randint(margin + lane_width, max(margin + lane_width, self.world.width - margin - lane_width))
        left_lane_x = max(margin, center - lane_gap // 2 - lane_width)
        right_lane_x = min(self.world.width - margin - lane_width, center + lane_gap // 2)
        left_lane = Rect(left_lane_x, margin, lane_width, self.world.height - (margin * 2))
        right_lane = Rect(right_lane_x, margin, lane_width, self.world.height - (margin * 2))
        return pattern, [left_lane, right_lane]

    def _random_point_with_margin(self, margin: float) -> Vector2:
        return Vector2(
            random.uniform(margin, self.world.width - margin),
            random.uniform(margin, self.world.height - margin),
        )

    @staticmethod
    def _circle_overlaps_rect(center: Vector2, radius: float, rect: Rect) -> bool:
        closest_x = max(rect.left, min(center.x, rect.right))
        closest_y = max(rect.top, min(center.y, rect.bottom))
        dx = center.x - closest_x
        dy = center.y - closest_y
        return (dx * dx) + (dy * dy) <= (radius * radius)
