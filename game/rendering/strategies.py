from __future__ import annotations

import math
import time

import pygame

from game.components.data_components import (
    BossComponent,
    ChargeComponent,
    DashComponent,
    ExplosiveComponent,
    InvulnerabilityComponent,
    ShootComponent,
    SniperComponent,
    TurretComponent,
)
from game.config import ENEMY_SHOOTER_CORE_COLOR, PLAYER_CORE_COLOR
from game.rendering.utils import draw_neon_glow


class PlayerRenderStrategy:
    def __init__(
        self,
        outer_color: tuple[int, int, int],
        inner_color: tuple[int, int, int],
        radius: float,
        thickness: int = 0,
    ) -> None:
        self.outer_color = outer_color
        self.inner_color = inner_color
        self.radius = radius
        self.thickness = thickness

    def render(self, screen: pygame.Surface, entity, transform) -> None:
        invulnerability = entity.get_component(InvulnerabilityComponent)
        outer_color = self.outer_color
        if invulnerability is not None and invulnerability.time_left > 0:
            outer_color = PLAYER_CORE_COLOR

        draw_neon_glow(
            surface=screen,
            color=outer_color,
            center_x=int(transform.position.x),
            center_y=int(transform.position.y),
            radius=max(1, int(self.radius + 1)),
            layers=3,
        )

        pygame.draw.circle(
            screen,
            outer_color,
            transform.position,
            self.radius,
            self.thickness,
        )

        inner_color = self.inner_color
        inner_radius = max(2, int(self.radius - 6))
        pygame.draw.circle(screen, inner_color, transform.position, inner_radius)

        dash = entity.get_component(DashComponent)
        if dash is None:
            return

        ring_radius = 16
        ring_rect = pygame.Rect(0, 0, ring_radius * 2, ring_radius * 2)
        ring_rect.center = (int(transform.position.x), int(transform.position.y))
        ring_thickness = 5

        if dash.cooldown_left > 0:
            ratio = 1.0 if dash.cooldown <= 0 else 1.0 - (dash.cooldown_left / dash.cooldown)
            ratio = max(0.0, min(1.0, ratio))
            start_angle = -math.pi / 2
            end_angle = start_angle + (math.pi * 2 * ratio)
            pygame.draw.arc(screen, inner_color, ring_rect, start_angle, end_angle, ring_thickness)
        else:
            pygame.draw.circle(screen, inner_color, ring_rect.center, ring_radius, ring_thickness)


class FollowerRenderStrategy:
    def __init__(
        self,
        outer_color: tuple[int, int, int],
        core_color: tuple[int, int, int],
        radius: float,
        thickness: int = 0,
    ) -> None:
        self.outer_color = outer_color
        self.core_color = core_color
        self.radius = radius
        self.thickness = thickness

    def render(self, screen: pygame.Surface, entity, transform) -> None:
        del entity
        now = time.time()
        pulse = 0.5 + 0.5 * math.sin(now * 6.2)
        ring_radius = self.radius + 3 + pulse * 3
        draw_neon_glow(
            surface=screen,
            color=self.outer_color,
            center_x=int(transform.position.x),
            center_y=int(transform.position.y),
            radius=max(1, int(self.radius + 2 + pulse * 2)),
            layers=4,
        )
        pygame.draw.circle(
            screen,
            self.outer_color,
            transform.position,
            self.radius,
            self.thickness,
        )
        pygame.draw.circle(screen, self.core_color, transform.position, int(ring_radius), 1)
        pygame.draw.circle(
            screen,
            self.core_color,
            transform.position,
            max(1, int(self.radius // 3)),
        )


class ShooterRenderStrategy:
    def __init__(
        self,
        outer_color: tuple[int, int, int],
        inner_color: tuple[int, int, int],
        radius: float,
        thickness: int = 0,
    ) -> None:
        self.outer_color = outer_color
        self.inner_color = inner_color
        self.radius = radius
        self.thickness = thickness

    def render(self, screen: pygame.Surface, entity, transform) -> None:
        now = time.time()
        pulse = 0.5 + 0.5 * math.sin(now * 8.0)
        draw_neon_glow(
            surface=screen,
            color=self.outer_color,
            center_x=int(transform.position.x),
            center_y=int(transform.position.y),
            radius=max(1, int(self.radius + 2 + pulse * 2)),
            layers=4,
        )
        pygame.draw.circle(
            screen,
            self.outer_color,
            transform.position,
            self.radius,
            self.thickness,
        )

        pygame.draw.circle(screen, self.inner_color, transform.position, max(1, int(self.radius - 5)))
        pygame.draw.circle(screen, ENEMY_SHOOTER_CORE_COLOR, transform.position, 5)

        ring_rect = pygame.Rect(0, 0, int((self.radius + 10) * 2), int((self.radius + 10) * 2))
        ring_rect.center = (int(transform.position.x), int(transform.position.y))
        angle = (now * 5.0) % (math.pi * 2)
        pygame.draw.arc(screen, self.outer_color, ring_rect, angle, angle + math.pi * 0.8, 2)
        pygame.draw.arc(screen, ENEMY_SHOOTER_CORE_COLOR, ring_rect, angle + math.pi, angle + math.pi * 1.75, 2)

        shoot = entity.get_component(ShootComponent)
        if shoot is None or shoot.target_direction.length_squared() <= 0:
            return

        tip = transform.position + shoot.target_direction.normalize() * (self.radius + 14)
        pygame.draw.line(screen, ENEMY_SHOOTER_CORE_COLOR, transform.position, tip, 4)
        pygame.draw.circle(screen, ENEMY_SHOOTER_CORE_COLOR, tip, 4)


class CircleRenderStrategy:
    def __init__(
        self,
        color: tuple[int, int, int],
        radius: float,
        thickness: int = 0,
    ) -> None:
        self.color = color
        self.radius = radius
        self.thickness = thickness

    def render(self, screen: pygame.Surface, entity, transform) -> None:
        del entity
        pygame.draw.circle(
            screen,
            self.color,
            transform.position,
            self.radius,
            self.thickness,
        )


class RectRenderStrategy:
    def __init__(
        self,
        color: tuple[int, int, int],
        width: float,
        height: float,
        thickness: int = 0,
    ) -> None:
        self.color = color
        self.width = width
        self.height = height
        self.thickness = thickness

    def render(self, screen: pygame.Surface, entity, transform) -> None:
        del entity
        rect = pygame.Rect(
            transform.position.x - self.width / 2,
            transform.position.y - self.height / 2,
            self.width,
            self.height,
        )
        pygame.draw.rect(screen, self.color, rect, self.thickness)


class LineRenderStrategy:
    def __init__(
        self,
        color: tuple[int, int, int],
        width: float,
        height: float,
        thickness: int = 1,
    ) -> None:
        self.color = color
        self.width = width
        self.height = height
        self.thickness = thickness

    def render(self, screen: pygame.Surface, entity, transform) -> None:
        del entity
        end = transform.position + pygame.Vector2(self.width, self.height)
        pygame.draw.line(screen, self.color, transform.position, end, max(1, self.thickness))


class PortalRenderStrategy:
    def __init__(
        self,
        neon_color: tuple[int, int, int],
        background_color: tuple[int, int, int],
        arc_color: tuple[int, int, int],
        base_radius: float = 22.0,
        vortex_color: tuple[int, int, int] | None = None,
        spin_speed: float = 5.0,
    ) -> None:
        self.neon_color = neon_color
        self.background_color = background_color
        self.arc_color = arc_color
        self.base_radius = base_radius
        self.vortex_color = arc_color if vortex_color is None else vortex_color
        self.spin_speed = spin_speed

    def render(self, screen: pygame.Surface, entity, transform) -> None:
        del entity
        center_x = int(transform.position.x)
        center_y = int(transform.position.y)
        now = time.time()

        pulse_radius = self.base_radius + abs(math.sin(now * self.spin_speed)) * 4.0
        radius_int = int(pulse_radius)

        draw_neon_glow(screen, self.neon_color, center_x, center_y, int(pulse_radius + 2), 4)
        draw_neon_glow(screen, self.arc_color, center_x, center_y, int(pulse_radius - 2), 2)

        aura_radius = int(pulse_radius + 4)
        aura_surface = pygame.Surface((aura_radius * 2, aura_radius * 2), pygame.SRCALPHA)
        aura_center = (aura_radius, aura_radius)
        pygame.draw.circle(aura_surface, (*self.neon_color, 150), aura_center, aura_radius)
        pygame.draw.circle(aura_surface, (*self.arc_color, 100), aura_center, max(1, aura_radius - 5), 3)
        screen.blit(aura_surface, (center_x - aura_radius, center_y - aura_radius))

        inner_background_radius = max(1, int(pulse_radius - 6))
        pygame.draw.circle(screen, self.background_color, (center_x, center_y), inner_background_radius)
        pygame.draw.circle(screen, self.neon_color, (center_x, center_y), radius_int, 3)
        pygame.draw.circle(screen, self.arc_color, (center_x, center_y), max(1, radius_int - 3), 1)

        vortex_radius = max(2, int(pulse_radius * 0.45 + math.sin(now * (self.spin_speed * 1.8)) * 1.5))
        pygame.draw.circle(screen, self.vortex_color, (center_x, center_y), vortex_radius, 2)

        angle_start = (now * self.spin_speed) % (math.pi * 2)
        rect = pygame.Rect(
            int(center_x - pulse_radius),
            int(center_y - pulse_radius),
            int(pulse_radius * 2),
            int(pulse_radius * 2),
        )
        pygame.draw.arc(screen, self.arc_color, rect, angle_start, angle_start + math.pi * 1.25, 4)
        pygame.draw.arc(
            screen,
            self.arc_color,
            rect,
            angle_start + math.pi,
            angle_start + math.pi + math.pi * 0.85,
            3,
        )

        sparkle_orbit_radius = pulse_radius + 2.0
        for offset in (0.0, math.pi / 2, math.pi, math.pi * 1.5):
            sparkle_angle = angle_start * 1.1 + offset
            sparkle_x = int(center_x + math.cos(sparkle_angle) * sparkle_orbit_radius)
            sparkle_y = int(center_y + math.sin(sparkle_angle) * sparkle_orbit_radius)
            pygame.draw.circle(screen, self.arc_color, (sparkle_x, sparkle_y), 2)


class NeonCoreEnemyRenderStrategy:
    def __init__(self, outer_color: tuple[int, int, int], core_color: tuple[int, int, int], radius: float) -> None:
        self.outer_color = outer_color
        self.core_color = core_color
        self.radius = radius

    def render(self, screen: pygame.Surface, entity, transform) -> None:
        del entity
        now = time.time()
        pulse = 0.5 + 0.5 * math.sin(now * 7.4)
        draw_neon_glow(
            surface=screen,
            color=self.outer_color,
            center_x=int(transform.position.x),
            center_y=int(transform.position.y),
            radius=max(1, int(self.radius + 2 + pulse * 2)),
            layers=4,
        )
        pygame.draw.circle(screen, self.outer_color, transform.position, self.radius)
        pygame.draw.circle(screen, self.core_color, transform.position, int(self.radius + 4 + pulse * 2), 1)
        pygame.draw.circle(screen, self.core_color, transform.position, max(1, int(self.radius // 3)))


class ChargeEnemyRenderStrategy:
    def __init__(self, base_color: tuple[int, int, int], radius: float) -> None:
        self.base_color = base_color
        self.radius = radius

    def render(self, screen: pygame.Surface, entity, transform) -> None:
        charge = entity.get_component(ChargeComponent)
        now = time.time()
        pulse = 0.5 + 0.5 * math.sin(now * 9.0)
        if charge is None:
            neon_color = self.base_color
        else:
            neon_color = (245, 245, 245) if charge.is_target_locked else self.base_color
            if charge.state == "aiming":
                line_color = (245, 245, 245) if charge.is_target_locked else (230, 60, 60)
                line_width = 4 if charge.is_target_locked else 2
                pygame.draw.line(screen, line_color, transform.position, charge.locked_target, line_width)
                aim_ring = int(self.radius + 8 + pulse * 3)
                pygame.draw.circle(screen, line_color, transform.position, aim_ring, 2)
            elif charge.state == "attacking":
                pygame.draw.circle(screen, (230, 60, 60), transform.position, int(self.radius + 10), 2)

        draw_neon_glow(
            surface=screen,
            color=neon_color,
            center_x=int(transform.position.x),
            center_y=int(transform.position.y),
            radius=max(1, int(self.radius + 2 + pulse * 2)),
            layers=4,
        )
        pygame.draw.circle(screen, neon_color, transform.position, self.radius)
        pygame.draw.circle(screen, (245, 245, 245), transform.position, max(1, int(self.radius // 3)))


class ExplosiveEnemyRenderStrategy:
    def __init__(self, base_color: tuple[int, int, int], warning_color: tuple[int, int, int], radius: float) -> None:
        self.base_color = base_color
        self.warning_color = warning_color
        self.radius = radius

    def render(self, screen: pygame.Surface, entity, transform) -> None:
        explosive = entity.get_component(ExplosiveComponent)
        color = self.base_color
        timer = 0.0 if explosive is None else explosive.timer
        now = time.time()
        if timer > 2.5 and int(timer * 15) % 2 == 0:
            color = (245, 245, 245)

        draw_neon_glow(
            surface=screen,
            color=color,
            center_x=int(transform.position.x),
            center_y=int(transform.position.y),
            radius=max(1, int(self.radius + 2 + abs(math.sin(now * 8.0)) * 3)),
            layers=4,
        )
        pygame.draw.circle(screen, color, transform.position, self.radius)
        pygame.draw.circle(screen, (245, 245, 245), transform.position, max(1, int(self.radius // 3)))

        orbit = self.radius + 7
        for index in range(3):
            angle = (now * 3.8) + index * (math.pi * 2 / 3)
            px = int(transform.position.x + math.cos(angle) * orbit)
            py = int(transform.position.y + math.sin(angle) * orbit)
            pygame.draw.circle(screen, self.warning_color, (px, py), 2)

        if timer > 3.5:
            indicator_radius = min(80.0, (timer - 3.5) * 80.0)
            thickness = max(1, int((4.5 - timer) * 5.0))
            pygame.draw.circle(screen, self.warning_color, transform.position, int(indicator_radius), thickness)


class TurretEnemyRenderStrategy:
    def __init__(
        self,
        base_color: tuple[int, int, int],
        middle_color: tuple[int, int, int],
        active_color: tuple[int, int, int],
        idle_color: tuple[int, int, int],
        radius: float,
        pulse_speed: float,
        pulse_gain: float,
        glow_layers: int,
    ) -> None:
        self.base_color = base_color
        self.middle_color = middle_color
        self.active_color = active_color
        self.idle_color = idle_color
        self.radius = radius
        self.pulse_speed = pulse_speed
        self.pulse_gain = pulse_gain
        self.glow_layers = glow_layers

    def render(self, screen: pygame.Surface, entity, transform) -> None:
        turret = entity.get_component(TurretComponent)
        now = time.time()
        pulse = abs(math.sin(now * self.pulse_speed)) * self.pulse_gain
        core_color = self.idle_color
        direction = pygame.Vector2(1, 0)
        shot_angles: tuple[float, ...] = ()
        if turret is not None:
            core_color = self.active_color if turret.is_in_burst else self.idle_color
            direction = turret.shot_direction if turret.shot_direction.length_squared() > 0 else direction
            shot_angles = turret.shot_angles

        draw_neon_glow(
            surface=screen,
            color=self.base_color,
            center_x=int(transform.position.x),
            center_y=int(transform.position.y),
            radius=max(1, int(self.radius + pulse)),
            layers=self.glow_layers,
        )
        pygame.draw.circle(screen, self.base_color, transform.position, self.radius)
        pygame.draw.circle(screen, self.middle_color, transform.position, max(1, int(self.radius - 5)))
        pygame.draw.circle(screen, core_color, transform.position, 5)

        ring_rect = pygame.Rect(0, 0, int((self.radius + 9) * 2), int((self.radius + 9) * 2))
        ring_rect.center = (int(transform.position.x), int(transform.position.y))
        angle = (now * 4.2) % (math.pi * 2)
        pygame.draw.arc(screen, core_color, ring_rect, angle, angle + math.pi * 0.9, 2)

        if shot_angles:
            for angle in shot_angles:
                barrel_direction = pygame.Vector2(1, 0).rotate(angle)
                tip = transform.position + barrel_direction.normalize() * (self.radius + 14)
                pygame.draw.line(screen, core_color, transform.position, tip, 4)
                pygame.draw.circle(screen, core_color, tip, 4)
            return

        tip = transform.position + direction.normalize() * (self.radius + 14)
        pygame.draw.line(screen, core_color, transform.position, tip, 4)
        pygame.draw.circle(screen, core_color, tip, 4)


class MortarTargetMarkerRenderStrategy:
    def __init__(self, color: tuple[int, int, int], radius: float) -> None:
        self.color = color
        self.radius = radius

    def render(self, screen: pygame.Surface, entity, transform) -> None:
        pulse = 1.0 + abs(math.sin(time.time() * 8.0)) * 0.2
        radius = self.radius * pulse
        draw_neon_glow(
            surface=screen,
            color=self.color,
            center_x=int(transform.position.x),
            center_y=int(transform.position.y),
            radius=max(1, int(radius + 2)),
            layers=2,
        )
        pygame.draw.circle(screen, self.color, transform.position, int(radius), 2)
        pygame.draw.circle(screen, self.color, transform.position, max(1, int(radius * 0.45)), 1)


class ShieldMinibossRenderStrategy:
    def __init__(self, base_color: tuple[int, int, int], radius: float) -> None:
        self.base_color = base_color
        self.radius = radius

    def render(self, screen: pygame.Surface, entity, transform) -> None:
        del entity
        now = time.time()
        pulse = abs(math.sin(now * 6.0)) * 4.0
        draw_neon_glow(
            surface=screen,
            color=self.base_color,
            center_x=int(transform.position.x),
            center_y=int(transform.position.y),
            radius=max(1, int(self.radius + pulse)),
            layers=5,
        )
        pygame.draw.circle(screen, self.base_color, transform.position, self.radius)
        pygame.draw.circle(screen, (5, 5, 8), transform.position, max(1, int(self.radius - 6)))
        pygame.draw.circle(screen, (245, 245, 245), transform.position, 5)
        pygame.draw.circle(screen, (245, 245, 245), transform.position, int(self.radius + 9), 2)

        ring_radius = self.radius + 12
        ring_rect = pygame.Rect(0, 0, int(ring_radius * 2), int(ring_radius * 2))
        ring_rect.center = (int(transform.position.x), int(transform.position.y))
        angle = (now * 3.6) % (math.pi * 2)
        pygame.draw.arc(screen, self.base_color, ring_rect, angle, angle + math.pi * 0.8, 3)
        pygame.draw.arc(screen, (245, 245, 245), ring_rect, angle + math.pi, angle + math.pi * 1.7, 2)


class SniperMinibossRenderStrategy:
    def __init__(self, base_color: tuple[int, int, int], radius: float) -> None:
        self.base_color = base_color
        self.radius = radius

    def render(self, screen: pygame.Surface, entity, transform) -> None:
        sniper = entity.get_component(SniperComponent)
        now = time.time()
        draw_neon_glow(
            surface=screen,
            color=self.base_color,
            center_x=int(transform.position.x),
            center_y=int(transform.position.y),
            radius=max(1, int(self.radius + 3)),
            layers=4,
        )
        pygame.draw.circle(screen, self.base_color, transform.position, self.radius)
        pygame.draw.circle(screen, (5, 5, 8), transform.position, max(1, int(self.radius - 5)))
        pygame.draw.circle(screen, (245, 245, 245), transform.position, 4)

        scope_radius = int(self.radius + 8 + abs(math.sin(now * 5.6)) * 2)
        pygame.draw.circle(screen, (245, 245, 245), transform.position, scope_radius, 1)
        if sniper is not None and sniper.state == "aiming":
            pygame.draw.line(screen, (245, 245, 245), transform.position, sniper.aim_target, 2)
            pygame.draw.circle(screen, self.base_color, sniper.aim_target, 8, 1)
            pygame.draw.line(
                screen,
                (245, 245, 245),
                (sniper.aim_target.x - 6, sniper.aim_target.y),
                (sniper.aim_target.x + 6, sniper.aim_target.y),
                1,
            )
            pygame.draw.line(
                screen,
                (245, 245, 245),
                (sniper.aim_target.x, sniper.aim_target.y - 6),
                (sniper.aim_target.x, sniper.aim_target.y + 6),
                1,
            )


class BossRenderStrategy:
    def __init__(self, radius: float) -> None:
        self.radius = radius

    def render(self, screen: pygame.Surface, entity, transform) -> None:
        boss = entity.get_component(BossComponent)
        if boss is None:
            return

        if boss.boss_kind == "boss_artilharia":
            self._render_artillery(screen, transform, boss)
            return
        if boss.boss_kind == "boss_caotico":
            self._render_chaotic(screen, transform, boss)
            return
        self._render_standard(screen, transform, boss)

    def _render_standard(self, screen: pygame.Surface, transform, boss: BossComponent) -> None:
        color_cycle = ((180, 60, 240), (0, 255, 255), (255, 105, 180))
        base_color = color_cycle[(boss.variant - 1) % len(color_cycle)]
        current_color = base_color
        if boss.state == "dash":
            current_color = (230, 60, 60)
        elif boss.state == "invoking":
            current_color = (245, 245, 245)

        now = time.time()
        for index in range(3):
            angle = now * 4.0 + (index * math.pi * 2 / 3)
            orb_distance = self.radius + 35 if boss.state == "dash" else self.radius + 15
            orb_x = transform.position.x + math.cos(angle) * orb_distance
            orb_y = transform.position.y + math.sin(angle) * orb_distance
            pygame.draw.line(screen, base_color, transform.position, (orb_x, orb_y), 2)
            pygame.draw.circle(screen, (230, 60, 60), (int(orb_x), int(orb_y)), 8)
            draw_neon_glow(screen, (230, 60, 60), int(orb_x), int(orb_y), 8, 2)
            pygame.draw.circle(screen, (245, 245, 245), (int(orb_x), int(orb_y)), 3)

        draw_neon_glow(screen, current_color, int(transform.position.x), int(transform.position.y), int(self.radius), 5)
        pygame.draw.circle(screen, current_color, transform.position, self.radius)
        pygame.draw.circle(screen, (5, 5, 8), transform.position, max(1, int(self.radius - 6)))
        pulse = abs(math.sin(now * 10.0)) * (self.radius / 1.5)
        pygame.draw.circle(screen, (230, 60, 60), transform.position, int(pulse))

    def _render_artillery(self, screen: pygame.Surface, transform, boss: BossComponent) -> None:
        del boss
        now = time.time()
        color = (255, 150, 70)
        draw_neon_glow(screen, color, int(transform.position.x), int(transform.position.y), int(self.radius + 6), 6)
        pygame.draw.circle(screen, color, transform.position, self.radius)
        pygame.draw.circle(screen, (5, 5, 8), transform.position, max(1, int(self.radius - 7)))
        for index in range(4):
            angle = now * 2.5 + index * (math.pi / 2)
            orb_x = transform.position.x + math.cos(angle) * (self.radius + 16)
            orb_y = transform.position.y + math.sin(angle) * (self.radius + 16)
            pygame.draw.circle(screen, (250, 210, 70), (int(orb_x), int(orb_y)), 6)
            pygame.draw.line(screen, (250, 210, 70), transform.position, (orb_x, orb_y), 2)

    def _render_chaotic(self, screen: pygame.Surface, transform, boss: BossComponent) -> None:
        del boss
        now = time.time()
        color = (255, 105, 180)
        draw_neon_glow(screen, color, int(transform.position.x), int(transform.position.y), int(self.radius + 8), 6)
        pygame.draw.circle(screen, color, transform.position, self.radius)
        pygame.draw.circle(screen, (5, 5, 8), transform.position, max(1, int(self.radius - 7)))
        for index in range(6):
            angle = now * 5.0 + index * (math.pi / 3)
            tip = pygame.Vector2(
                transform.position.x + math.cos(angle) * (self.radius + 12),
                transform.position.y + math.sin(angle) * (self.radius + 12),
            )
            pygame.draw.line(screen, (245, 245, 245), transform.position, tip, 2)


class MortarRenderStrategy:
    def __init__(self, base_color: tuple[int, int, int], radius: float) -> None:
        self.base_color = base_color
        self.radius = radius

    def render(self, screen: pygame.Surface, entity, transform) -> None:
        del entity
        now = time.time()
        pulse = abs(math.sin(now * 5.0)) * 2.0
        draw_neon_glow(
            surface=screen,
            color=self.base_color,
            center_x=int(transform.position.x),
            center_y=int(transform.position.y),
            radius=max(1, int(self.radius + pulse)),
            layers=4,
        )

        outer_rect = pygame.Rect(0, 0, int(self.radius * 1.7), int(self.radius * 1.3))
        outer_rect.center = (int(transform.position.x), int(transform.position.y))
        pygame.draw.rect(screen, self.base_color, outer_rect)
        pygame.draw.rect(screen, (5, 5, 8), outer_rect, 2)

        barrel_len = int(self.radius * 1.2)
        angle = now * 1.9
        tip = (
            int(transform.position.x + math.cos(angle) * barrel_len),
            int(transform.position.y + math.sin(angle) * barrel_len),
        )
        pygame.draw.line(screen, (245, 245, 245), transform.position, tip, 3)
        pygame.draw.circle(screen, (245, 245, 245), tip, 3)


class VirusGlitchRenderStrategy:
    def __init__(self, primary_color: tuple[int, int, int], secondary_color: tuple[int, int, int], radius: float) -> None:
        self.primary_color = primary_color
        self.secondary_color = secondary_color
        self.radius = radius

    def render(self, screen: pygame.Surface, entity, transform) -> None:
        now = time.time()
        phase = (entity.id % 17) * 0.33
        pulse = 1.0 + 0.06 * math.sin((now * 5.5) + phase)
        radius = self.radius * pulse
        center_x = int(transform.position.x)
        center_y = int(transform.position.y)

        draw_neon_glow(
            surface=screen,
            color=self.primary_color,
            center_x=center_x,
            center_y=center_y,
            radius=max(1, int(radius + 2)),
            layers=3,
        )
        pygame.draw.circle(screen, self.primary_color, transform.position, max(1, int(radius)), width=2)
        pygame.draw.circle(screen, self.secondary_color, transform.position, max(1, int(radius * 0.48)))

        # Glitch scanlines determinísticas por entidade para efeito "vírus" sem custo alto de random.
        for index in range(2):
            jitter_x = int(math.sin((now * 10.0) + phase + (index * 1.7)) * (self.radius * 0.55))
            jitter_y = int(math.cos((now * 12.0) + phase + (index * 2.1)) * (self.radius * 0.45))
            line_width = max(6, int(self.radius * 1.4))
            line_start = (center_x + jitter_x - line_width // 2, center_y + jitter_y)
            line_end = (line_start[0] + line_width, line_start[1])
            pygame.draw.line(screen, self.primary_color, line_start, line_end, 1)

        # Partículas orbitais digitais.
        particle_radius = max(1, int(self.radius * 0.16))
        orbit = self.radius + 4.0
        for index in range(4):
            angle = (now * 2.4) + phase + (index * (math.pi * 0.5))
            px = int(center_x + math.cos(angle) * orbit)
            py = int(center_y + math.sin(angle) * orbit)
            pygame.draw.circle(screen, self.secondary_color, (px, py), particle_radius)


class LabyrinthWallRenderStrategy:
    def __init__(
        self,
        fill_color: tuple[int, int, int],
        edge_color: tuple[int, int, int],
        width: float,
        height: float,
        line_thickness: int,
    ) -> None:
        self.fill_color = fill_color
        self.edge_color = edge_color
        self.width = width
        self.height = height
        self.line_thickness = max(1, int(line_thickness))

    def render(self, screen: pygame.Surface, entity, transform) -> None:
        del entity
        rect = pygame.Rect(
            int(transform.position.x - self.width * 0.5),
            int(transform.position.y - self.height * 0.5),
            int(self.width),
            int(self.height),
        )
        if rect.width >= rect.height:
            start = (rect.left, rect.centery)
            end = (rect.right, rect.centery)
        else:
            start = (rect.centerx, rect.top)
            end = (rect.centerx, rect.bottom)

        pygame.draw.line(screen, self.edge_color, start, end, self.line_thickness + 2)
        pygame.draw.line(screen, self.fill_color, start, end, self.line_thickness)


class LabyrinthKeyRenderStrategy:
    def __init__(self, color: tuple[int, int, int], radius: float) -> None:
        self.color = color
        self.radius = radius

    def render(self, screen: pygame.Surface, entity, transform) -> None:
        del entity
        pulse = abs(math.sin(time.time() * 5.2))
        radius = self.radius + pulse * 3.0
        center = (int(transform.position.x), int(transform.position.y))
        draw_neon_glow(screen, self.color, center[0], center[1], max(1, int(radius + 3)), 3)
        pygame.draw.circle(screen, self.color, center, max(1, int(radius)), 2)
        pygame.draw.rect(
            screen,
            self.color,
            pygame.Rect(center[0] - int(radius * 0.25), center[1] - int(radius * 0.1), int(radius * 0.85), 3),
            border_radius=2,
        )
        pygame.draw.circle(screen, self.color, (center[0] + int(radius * 0.72), center[1]), max(2, int(radius * 0.2)), 2)


class LabyrinthExitRenderStrategy:
    def __init__(self, locked_color: tuple[int, int, int], unlocked_color: tuple[int, int, int], size: float) -> None:
        self.locked_color = locked_color
        self.unlocked_color = unlocked_color
        self.size = size

    def render(self, screen: pygame.Surface, entity, transform) -> None:
        from game.components.data_components import LabyrinthExitComponent

        exit_component = entity.get_component(LabyrinthExitComponent)
        is_unlocked = exit_component is not None and exit_component.unlocked
        color = self.unlocked_color if is_unlocked else self.locked_color
        center = (int(transform.position.x), int(transform.position.y))
        half = int(self.size * 0.5)
        rect = pygame.Rect(center[0] - half, center[1] - half, half * 2, half * 2)
        draw_neon_glow(screen, color, center[0], center[1], half + 4, 4)
        pygame.draw.rect(screen, color, rect, width=3, border_radius=6)
        if not is_unlocked:
            pygame.draw.line(screen, color, rect.topleft, rect.bottomright, 3)
            pygame.draw.line(screen, color, rect.topright, rect.bottomleft, 3)
        pygame.draw.circle(screen, (245, 245, 245), transform.position, 6)
