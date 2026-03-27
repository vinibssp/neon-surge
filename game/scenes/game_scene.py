from __future__ import annotations

import math
import random
from dataclasses import dataclass
from typing import Callable

import pygame
from pygame import Vector2

from game.components.data_components import BossComponent, InvulnerabilityComponent, TransformComponent
from game.config import PLAYER_RESPAWN_INVULN, SCREEN_HEIGHT, SCREEN_WIDTH
from game.core.enemy_names import format_enemy_name
from game.core.events import (
    AudioContextChanged,
    BulletExpired,
    CollectibleCollected,
    DashStarted,
    ParryLanded,
    EnemySpawned,
    ExplosionTriggered,
    LifetimeExpired,
    PlayerDied,
    PortalEntered,
    SubscriptionToken,
    SpawnPortalDestroyed,
)
from game.core.input_handler import InputHandler
from game.core.session_stats import StatsCollector
from game.core.scene_stack import Scene
from game.core.world import GameWorld
from game.factories.player_factory import PlayerFactory
from game.scenes.game_over_scene import GameOverScene
from game.scenes.pause_scene import PauseScene
from game.scenes.services import BackgroundRenderer, BossHudCard, HudRenderer
from game.services.ranking_orchestrator import RankingOrchestrator
from game.modes.game_mode_strategy import GameModeStrategy
from game.systems.render_system import RenderSystem
from game.systems.spawn_director import SpawnDirector
from game.systems.system_pipeline import SystemPipeline


@dataclass
class ExplosionFxState:
    position: Vector2
    age: float = 0.0
    duration: float = 0.34
    max_radius: float = 86.0


@dataclass(frozen=True)
class PendingGameOverTransition:
    title: str
    subtitle: str
    retry_strategy_factory: Callable[[], GameModeStrategy]
    death_cause: str | None
    include_session_summary: bool
    final_score: float
    mode_key: str


@dataclass
class BossCardState:
    entity_id: int
    boss_name: str


class GameScene(Scene):
    def __init__(self, stack, mode: GameModeStrategy) -> None:
        super().__init__(stack)
        self.mode = mode
        self.world = GameWorld(width=SCREEN_WIDTH, height=SCREEN_HEIGHT, event_bus=self.stack.event_bus)
        self.input_handler = InputHandler()
        self.elapsed_time = 0.0
        self.level_portal_spawned = False
        self.background_renderer = BackgroundRenderer()
        self.hud_renderer = HudRenderer()
        self.spawn_director = SpawnDirector(
            world=self.world,
            strategy=self.mode.build_spawn_strategy(),
            position_provider=self.random_play_area_position,
        )
        self.level_progression = self.mode.build_level_progression_strategy()
        self.render_system = RenderSystem(self.world)
        self.system_pipeline = SystemPipeline(systems=self.mode.build_systems(self.world))
        self._event_tokens: list[SubscriptionToken] = []
        self._transition_in_progress = False
        self.stats_collector = StatsCollector()
        self.session_stats = self.stats_collector.stats
        self._explosion_fx: list[ExplosionFxState] = []
        self._shake_time_left = 0.0
        self._shake_duration = 0.0
        self._shake_intensity = 0.0
        self._world_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        self._pending_game_over_transition: PendingGameOverTransition | None = None
        self._boss_card_states: list[BossCardState] = []

    def on_enter(self) -> None:
        self.stack.event_bus.publish(AudioContextChanged(context="gameplay", reason="game_scene_entered"))
        self._register_event_handlers()
        self.mode.on_enter(self)

    def on_exit(self) -> None:
        self._unregister_event_handlers()

    def handle_input(self, events: list[pygame.event.Event]) -> None:
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.stack.push(PauseScene(self.stack))
                return

        if self.world.player is None:
            return

        pressed = pygame.key.get_pressed()
        commands = self.input_handler.build_commands(events, pressed)
        for command in commands:
            command.execute(self.world.player, self.world)

    def update(self, dt: float) -> None:
        if self._pending_game_over_transition is not None:
            self._commit_pending_game_over_transition()
            return

        self.elapsed_time += dt
        self.level_progression.update(self, dt)
        self.spawn_director.update(dt=dt, elapsed_time=self.elapsed_time)

        self.system_pipeline.update(dt)
        self.world.apply_pending()
        self._update_boss_cards()
        self._update_screen_shake(dt)
        self._update_explosion_fx(dt)

        if self._pending_game_over_transition is not None:
            self._commit_pending_game_over_transition()

    def render(self, screen: pygame.Surface) -> None:
        self.background_renderer.render(self._world_surface, SCREEN_WIDTH, SCREEN_HEIGHT)
        self.render_system.render(self._world_surface)
        self._render_survival_lava_overlay(self._world_surface)
        self._render_environment_event_overlay(self._world_surface)
        self._render_explosion_fx(self._world_surface)

        screen.fill((0, 0, 0))
        shake_offset = self._screen_shake_offset()
        screen.blit(self._world_surface, shake_offset)
        self.hud_renderer.render_lines(screen, self.mode.build_hud_lines(self))
        if self._boss_card_states:
            self._render_boss_cards(screen)

    def _render_survival_lava_overlay(self, screen: pygame.Surface) -> None:
        lava_state = self.world.runtime_state.get("survival_lava")
        if not isinstance(lava_state, dict):
            return

        state = str(lava_state.get("state", "idle"))
        raw_regions = lava_state.get("regions")
        regions: list[pygame.Rect] = []
        if isinstance(raw_regions, tuple):
            for raw_region in raw_regions:
                if not isinstance(raw_region, tuple) or len(raw_region) != 4:
                    continue
                rect = pygame.Rect(int(raw_region[0]), int(raw_region[1]), int(raw_region[2]), int(raw_region[3]))
                if rect.width > 0 and rect.height > 0:
                    regions.append(rect)
        if not regions:
            region = lava_state.get("region")
            if isinstance(region, tuple) and len(region) == 4:
                rect = pygame.Rect(int(region[0]), int(region[1]), int(region[2]), int(region[3]))
                if rect.width > 0 and rect.height > 0:
                    regions.append(rect)
        if not regions:
            return

        now = pygame.time.get_ticks() * 0.001
        pattern = str(lava_state.get("pattern", "pool"))

        if state == "active":
            blink_visible = bool(lava_state.get("blink_visible", True))
            if not blink_visible:
                return
            for index, rect in enumerate(regions):
                self._render_lava_active_region(screen, rect, pattern, now, index)
            return

        warning_left = float(lava_state.get("time_to_lava", 0.0))
        warning_duration = float(lava_state.get("warning_duration", 0.0))
        if state != "warning" or warning_duration <= 0.0:
            return

        alpha_ratio = max(0.2, min(1.0, 1.0 - (warning_left / warning_duration)))
        for index, rect in enumerate(regions):
            self._render_lava_warning_region(screen, rect, pattern, now, index, alpha_ratio)

    def _render_lava_active_region(
        self,
        screen: pygame.Surface,
        rect: pygame.Rect,
        pattern: str,
        now: float,
        region_index: int,
    ) -> None:
        pulse = 0.5 + 0.5 * math.sin((now * 6.2) + (region_index * 0.9))
        overlay = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        overlay.fill((38, 10, 8, int(104 + (24 * pulse))))

        tile = 12
        palette = (
            (120, 26, 10),
            (164, 38, 12),
            (212, 58, 14),
            (255, 96, 18),
            (255, 154, 42),
        )
        for y in range(0, rect.height, tile):
            for x in range(0, rect.width, tile):
                heat_wave = 0.5 + 0.5 * math.sin((x * 0.11) + (y * 0.09) + (now * 8.1) + (region_index * 0.8))
                palette_index = min(len(palette) - 1, int(heat_wave * len(palette)))
                base_r, base_g, base_b = palette[palette_index]
                alpha = int(72 + (96 * heat_wave))
                inset = 1 if ((x // tile) + (y // tile) + region_index) % 2 == 0 else 2
                cell_w = min(tile - inset, rect.width - x)
                cell_h = min(tile - inset, rect.height - y)
                if cell_w > 1 and cell_h > 1:
                    pygame.draw.rect(
                        overlay,
                        (base_r, base_g, base_b, alpha),
                        pygame.Rect(x, y, cell_w, cell_h),
                        border_radius=2,
                    )

        for y in range(0, rect.height, 18):
            shimmer = 0.5 + 0.5 * math.sin((now * 5.0) + (y * 0.18) + region_index)
            line_alpha = int(34 + 66 * shimmer)
            pygame.draw.line(overlay, (255, 182, 86, line_alpha), (0, y), (rect.width, y), 1)

        fissure_count = 5 if pattern in ("cross", "fork", "checker") else 3
        for fissure_index in range(fissure_count):
            seed = (fissure_index + 1) * 0.73 + (region_index * 0.51)
            x0 = int((rect.width * (fissure_index + 1)) / (fissure_count + 1))
            y0 = int(rect.height * (0.12 + 0.12 * math.sin((now * 1.8) + seed)))
            x1 = int(x0 + (rect.width * 0.06 * math.sin((now * 3.7) + seed)))
            y1 = int(rect.height * (0.84 + 0.1 * math.cos((now * 1.2) + seed)))
            pygame.draw.line(overlay, (255, 236, 144, 160), (x0, y0), (x1, y1), 1)
            pygame.draw.circle(overlay, (255, 252, 192, 132), (x0, y0), 1)

        ember_count = 10 + (region_index % 5)
        for ember_index in range(ember_count):
            px = int((rect.width * (ember_index + 1)) / (ember_count + 1))
            py = int(
                rect.height
                * (0.12 + 0.74 * (0.5 + 0.5 * math.sin((now * 7.6) + ember_index * 1.22 + region_index)))
            )
            radius = 1 + (ember_index % 2)
            pygame.draw.circle(overlay, (255, 252, 206, 180), (px, py), radius)

        glyph_count = 5 if pattern in ("ring", "checker") else 3
        for glyph_index in range(glyph_count):
            gx = int((rect.width * (glyph_index + 1)) / (glyph_count + 1))
            gy = int(rect.height * (0.35 + 0.22 * math.sin((now * 3.1) + glyph_index + (region_index * 0.4))))
            size = 3
            pygame.draw.line(overlay, (255, 206, 120, 170), (gx - size, gy), (gx + size, gy), 1)
            pygame.draw.line(overlay, (255, 206, 120, 170), (gx, gy - size), (gx, gy + size), 1)

        screen.blit(overlay, rect.topleft)

        border_color = (255, 238, 134)
        if pattern in ("ring", "checker"):
            border_color = (255, 248, 170)
        elif pattern in ("cross", "fork"):
            border_color = (255, 226, 122)
        pygame.draw.rect(screen, border_color, rect, 3)

        rim_glow = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        pygame.draw.rect(rim_glow, (255, 164, 62, int(90 + 48 * pulse)), rim_glow.get_rect(), 1)

        segment = 9
        for x in range(0, rect.width, segment):
            glow = 0.5 + 0.5 * math.sin((now * 10.0) + (x * 0.22) + region_index)
            alpha = int(92 + 100 * glow)
            pygame.draw.rect(
                rim_glow,
                (255, 236, 156, alpha),
                pygame.Rect(x, 0, min(4, rect.width - x), 2),
            )
            pygame.draw.rect(
                rim_glow,
                (255, 236, 156, alpha),
                pygame.Rect(x, max(0, rect.height - 2), min(4, rect.width - x), 2),
            )
        for y in range(0, rect.height, segment):
            glow = 0.5 + 0.5 * math.sin((now * 10.0) + (y * 0.22) + region_index + 1.7)
            alpha = int(92 + 100 * glow)
            pygame.draw.rect(
                rim_glow,
                (255, 236, 156, alpha),
                pygame.Rect(0, y, 2, min(4, rect.height - y)),
            )
            pygame.draw.rect(
                rim_glow,
                (255, 236, 156, alpha),
                pygame.Rect(max(0, rect.width - 2), y, 2, min(4, rect.height - y)),
            )
        screen.blit(rim_glow, rect.topleft)

    def _render_lava_warning_region(
        self,
        screen: pygame.Surface,
        rect: pygame.Rect,
        pattern: str,
        now: float,
        region_index: int,
        alpha_ratio: float,
    ) -> None:
        pulse = 0.5 + 0.5 * math.sin((now * 12.5) + (region_index * 0.7))
        alpha = int(38 + 88 * alpha_ratio + 28 * pulse)
        overlay = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        overlay.fill((255, 168, 34, alpha))

        stripe_step = 12
        for x in range(-rect.height, rect.width, stripe_step):
            x0 = x + int(12 * math.sin((now * 4.8) + (region_index * 0.8)))
            pygame.draw.line(
                overlay,
                (255, 234, 150, int(54 + (72 * alpha_ratio))),
                (x0, 0),
                (x0 + rect.height, rect.height),
                2,
            )

        tile = 18
        for y in range(0, rect.height, tile):
            for x in range(0, rect.width, tile):
                beat = 0.5 + 0.5 * math.sin((now * 9.8) + (x * 0.2) + (y * 0.17))
                if beat < 0.72:
                    continue
                pygame.draw.rect(
                    overlay,
                    (255, 248, 184, int(38 + 80 * beat)),
                    pygame.Rect(x + 2, y + 2, min(6, rect.width - x), min(6, rect.height - y)),
                    border_radius=1,
                )
        screen.blit(overlay, rect.topleft)

        border_alpha = int(128 + (96 * pulse))
        border_surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        pygame.draw.rect(border_surface, (255, 244, 162, border_alpha), border_surface.get_rect(), 2)
        screen.blit(border_surface, rect.topleft)

        rune_count = 9 if pattern in ("lanes", "checker", "ring") else 6
        for rune_index in range(rune_count):
            marker_phase = (now * 6.2) + (rune_index * 0.9) + (region_index * 0.6)
            marker_x = int((rect.width * (rune_index + 1)) / (rune_count + 1))
            marker_y = int((rect.height * 0.5) + (rect.height * 0.24 * math.sin(marker_phase)))
            size = 5 if rune_index % 2 == 0 else 3
            pygame.draw.line(
                screen,
                (255, 248, 188),
                (rect.left + marker_x - size, rect.top + marker_y),
                (rect.left + marker_x + size, rect.top + marker_y),
                1,
            )
            pygame.draw.line(
                screen,
                (255, 248, 188),
                (rect.left + marker_x, rect.top + marker_y - size),
                (rect.left + marker_x, rect.top + marker_y + size),
                1,
            )
            pygame.draw.circle(screen, (255, 254, 214), (rect.left + marker_x, rect.top + marker_y), 1)

    def _render_environment_event_overlay(self, screen: pygame.Surface) -> None:
        event_state = self.world.runtime_state.get("environment_event")
        if not isinstance(event_state, dict):
            return

        now = pygame.time.get_ticks() * 0.001
        self._render_survival_water_overlay(screen, now)
        event_name = event_state.get("name")
        region = event_state.get("region")
        if isinstance(event_name, str) and isinstance(region, tuple) and len(region) == 4:
            rect = pygame.Rect(int(region[0]), int(region[1]), int(region[2]), int(region[3]))
            if event_name == "snow_drift":
                self._render_event_snow_overlay(screen, rect, now)
            elif event_name == "bullet_cloud":
                self._render_event_bullet_cloud_overlay(screen, rect, now)

        black_hole = event_state.get("black_hole")
        if not isinstance(black_hole, dict):
            return
        x = int(float(black_hole.get("x", 0.0)))
        y = int(float(black_hole.get("y", 0.0)))
        pull_radius = int(float(black_hole.get("pull_radius", 0.0)))
        consume_radius = int(float(black_hole.get("consume_radius", 0.0)))
        phase = str(black_hole.get("phase", "active"))
        if pull_radius <= 0 or consume_radius <= 0:
            return

        if phase == "warning":
            warning_left = float(black_hole.get("time_to_active", 0.0))
            warning_duration = float(black_hole.get("warning_duration", 0.0))
            if warning_duration <= 0.0:
                return
            warning_ratio = max(0.15, min(1.0, 1.0 - (warning_left / warning_duration)))
            self._render_event_black_hole_warning_overlay(screen, x, y, pull_radius, consume_radius, now, warning_ratio)
            return

        self._render_event_black_hole_overlay(screen, x, y, pull_radius, consume_radius, now)

    def _render_event_black_hole_warning_overlay(
        self,
        screen: pygame.Surface,
        x: int,
        y: int,
        pull_radius: int,
        consume_radius: int,
        now: float,
        warning_ratio: float,
    ) -> None:
        pulse = 0.5 + 0.5 * math.sin((now * 9.4) + (warning_ratio * 2.0))
        overlay_radius = pull_radius + 12
        overlay = pygame.Surface((overlay_radius * 2, overlay_radius * 2), pygame.SRCALPHA)
        center = (overlay_radius, overlay_radius)

        base_alpha = int(26 + 78 * warning_ratio)
        pygame.draw.circle(overlay, (78, 26, 136, base_alpha), center, pull_radius)

        ring_count = 4
        for ring_index in range(ring_count):
            ring_phase = (ring_index / ring_count) * math.pi
            ring_radius = int(consume_radius + 10 + ring_index * ((pull_radius - consume_radius) / max(1, ring_count)))
            ring_wave = 0.5 + 0.5 * math.sin((now * 8.6) + ring_phase)
            ring_alpha = int(62 + 130 * warning_ratio * ring_wave)
            pygame.draw.circle(overlay, (236, 186, 255, ring_alpha), center, max(2, ring_radius), 2)

        spoke_count = 10
        spoke_span = max(8.0, pull_radius - consume_radius)
        for spoke_index in range(spoke_count):
            angle = (spoke_index / spoke_count) * (math.pi * 2.0) + (now * 1.6)
            start_radius = consume_radius + 4 + (2 if spoke_index % 2 == 0 else 0)
            end_radius = min(pull_radius - 3, start_radius + spoke_span)
            x0 = int(center[0] + math.cos(angle) * start_radius)
            y0 = int(center[1] + math.sin(angle) * start_radius)
            x1 = int(center[0] + math.cos(angle) * end_radius)
            y1 = int(center[1] + math.sin(angle) * end_radius)
            spoke_alpha = int(70 + 110 * pulse)
            pygame.draw.line(overlay, (188, 238, 255, spoke_alpha), (x0, y0), (x1, y1), 1)

        screen.blit(overlay, (x - overlay_radius, y - overlay_radius))

        pulse_radius = consume_radius + 8 + int(10 * pulse)
        pygame.draw.circle(screen, (255, 226, 255), (x, y), max(2, pulse_radius), 2)
        pygame.draw.circle(screen, (156, 232, 255), (x, y), max(2, consume_radius + 3), 1)

        marker_count = 8
        for marker_index in range(marker_count):
            angle = (marker_index / marker_count) * (math.pi * 2.0) - (now * 2.3)
            marker_radius = pull_radius - 8
            mx = int(x + math.cos(angle) * marker_radius)
            my = int(y + math.sin(angle) * marker_radius)
            marker_size = 4 if marker_index % 2 == 0 else 3
            marker_color = (255, 242, 194) if marker_index % 2 == 0 else (218, 248, 255)
            pygame.draw.line(screen, marker_color, (mx - marker_size, my), (mx + marker_size, my), 1)
            pygame.draw.line(screen, marker_color, (mx, my - marker_size), (mx, my + marker_size), 1)

    def _render_event_snow_overlay(self, screen: pygame.Surface, rect: pygame.Rect, now: float) -> None:
        if rect.width <= 0 or rect.height <= 0:
            return
        overlay = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        overlay.fill((126, 168, 214, 72))

        for y in range(0, rect.height, 12):
            drift = int(5 * math.sin((now * 3.4) + (y * 0.09)))
            pygame.draw.line(
                overlay,
                (214, 240, 255, 58),
                (max(0, drift), y),
                (min(rect.width, rect.width + drift), y),
                1,
            )

        flake_count = max(10, (rect.width * rect.height) // 12000)
        for index in range(flake_count):
            fx = int((index * 37 + now * 42) % max(1, rect.width))
            fy = int((index * 53 + now * 28 + index * 9) % max(1, rect.height))
            pygame.draw.circle(overlay, (236, 250, 255, 135), (fx, fy), 1)

        screen.blit(overlay, rect.topleft)
        pygame.draw.rect(screen, (214, 244, 255), rect, 2)

    def _render_event_water_overlay(self, screen: pygame.Surface, rect: pygame.Rect, now: float) -> None:
        if rect.width <= 0 or rect.height <= 0:
            return
        overlay = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        overlay.fill((36, 94, 168, 84))

        stripe_step = 16
        for y in range(0, rect.height, stripe_step):
            wave = int(8 * math.sin((now * 3.0) + (y * 0.15)))
            pygame.draw.line(
                overlay,
                (94, 182, 255, 94),
                (max(0, wave), y),
                (min(rect.width, rect.width + wave), y),
                2,
            )

        foam_count = max(8, rect.width // 40)
        for index in range(foam_count):
            px = int((rect.width * (index + 1)) / (foam_count + 1))
            py = int(rect.height * (0.2 + 0.6 * (0.5 + 0.5 * math.sin((now * 2.6) + (index * 0.9)))))
            pygame.draw.circle(overlay, (198, 236, 255, 120), (px, py), 2)

        screen.blit(overlay, rect.topleft)
        pygame.draw.rect(screen, (120, 210, 255), rect, 2)

    def _render_survival_water_overlay(self, screen: pygame.Surface, now: float) -> None:
        water_state = self.world.runtime_state.get("survival_water")
        if not isinstance(water_state, dict):
            return

        state = str(water_state.get("state", "idle"))
        region = water_state.get("region")
        if not isinstance(region, tuple) or len(region) != 4:
            return

        rect = pygame.Rect(int(region[0]), int(region[1]), int(region[2]), int(region[3]))
        if rect.width <= 0 or rect.height <= 0:
            return

        if state != "active":
            return
        blink_visible = bool(water_state.get("blink_visible", True))
        if not blink_visible:
            return
        self._render_event_water_overlay(screen, rect, now)

    def _render_event_bullet_cloud_overlay(self, screen: pygame.Surface, rect: pygame.Rect, now: float) -> None:
        if rect.width <= 0 or rect.height <= 0:
            return
        overlay = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        overlay.fill((120, 56, 12, 76))

        grid = 14
        for y in range(0, rect.height, grid):
            for x in range(0, rect.width, grid):
                flash = 0.5 + 0.5 * math.sin((now * 8.0) + (x * 0.19) + (y * 0.13))
                if flash < 0.64:
                    continue
                pygame.draw.rect(
                    overlay,
                    (255, 202, 108, int(34 + 90 * flash)),
                    pygame.Rect(x, y, 5, 5),
                    border_radius=1,
                )

        column_count = max(5, rect.width // 80)
        for index in range(column_count):
            cx = int((rect.width * (index + 1)) / (column_count + 1))
            travel = 0.5 + 0.5 * math.sin((now * 4.8) + index)
            cy = int(rect.height * (0.12 + (0.76 * travel)))
            pygame.draw.line(overlay, (255, 236, 154, 170), (cx, max(0, cy - 18)), (cx, min(rect.height, cy + 18)), 1)
            pygame.draw.circle(overlay, (255, 246, 194, 190), (cx, cy), 2)

        screen.blit(overlay, rect.topleft)
        pygame.draw.rect(screen, (255, 228, 140), rect, 2)

    def _render_event_black_hole_overlay(
        self,
        screen: pygame.Surface,
        x: int,
        y: int,
        pull_radius: int,
        consume_radius: int,
        now: float,
    ) -> None:
        pulse = 0.5 + 0.5 * math.sin(now * 2.8)

        aura = pygame.Surface((pull_radius * 2 + 10, pull_radius * 2 + 10), pygame.SRCALPHA)
        aura_center = (aura.get_width() // 2, aura.get_height() // 2)
        pygame.draw.circle(aura, (58, 18, 114, int(40 + pulse * 32)), aura_center, pull_radius + 3)
        pygame.draw.circle(aura, (110, 40, 188, int(58 + pulse * 42)), aura_center, max(2, int(pull_radius * 0.64)))

        tile = 10
        for ty in range(0, aura.get_height(), tile):
            for tx in range(0, aura.get_width(), tile):
                ox = tx - aura_center[0]
                oy = ty - aura_center[1]
                dist = math.sqrt((ox * ox) + (oy * oy))
                if dist > pull_radius:
                    continue
                swirl = 0.5 + 0.5 * math.sin((dist * 0.13) - (now * 7.0) + (tx * 0.08))
                if swirl < 0.7:
                    continue
                pygame.draw.rect(
                    aura,
                    (188, 138, 255, int(20 + 76 * swirl)),
                    pygame.Rect(tx, ty, 3, 3),
                )

        screen.blit(aura, (x - aura_center[0], y - aura_center[1]))

        ring_a = consume_radius + 10 + int(4 * math.sin(now * 3.8))
        ring_b = consume_radius + 22 + int(5 * math.cos(now * 2.5 + 0.8))
        pygame.draw.circle(screen, (202, 146, 255), (x, y), max(2, ring_a), 2)
        pygame.draw.circle(screen, (130, 222, 255), (x, y), max(2, ring_b), 1)

        glyph_count = 14
        for index in range(glyph_count):
            phase = (index / glyph_count) * (math.pi * 2.0)
            angle = (now * (1.9 + 0.08 * index)) + phase
            orbit = consume_radius + 8 + (index % 4) * 4
            px = int(x + math.cos(angle) * orbit)
            py = int(y + math.sin(angle) * orbit)
            size = 2 if index % 2 == 0 else 1
            color = (242, 214, 255) if index % 2 == 0 else (160, 236, 255)
            pygame.draw.line(screen, color, (px - size, py), (px + size, py), 1)
            pygame.draw.line(screen, color, (px, py - size), (px, py + size), 1)

        core_radius = max(2, int(consume_radius * (0.9 + 0.1 * math.sin(now * 6.6))))
        pygame.draw.circle(screen, (10, 6, 18), (x, y), core_radius)
        pygame.draw.circle(screen, (246, 196, 255), (x, y), consume_radius + 2, 2)

    def setup_level(self, level: int) -> None:
        self.world.level = level
        self.level_portal_spawned = False
        self._transition_in_progress = False
        self._boss_card_states.clear()
        self.world.runtime_state.pop("death_transition", None)
        self.world.runtime_state.pop("last_death_cause", None)

        if self.world.player is None:
            player = PlayerFactory.create(Vector2(SCREEN_WIDTH * 0.5, SCREEN_HEIGHT * 0.5))
            self.world.player = player
            self.world.entities = [player]
        else:
            self.world.clear_non_player_entities()
            player_transform = self.world.player.get_component(TransformComponent)
            if player_transform is not None:
                player_transform.position = Vector2(SCREEN_WIDTH * 0.5, SCREEN_HEIGHT * 0.5)

        if self.world.player is not None:
            invulnerability = self.world.player.get_component(InvulnerabilityComponent)
            if invulnerability is not None:
                invulnerability.time_left = max(invulnerability.time_left, PLAYER_RESPAWN_INVULN)

        self.mode.configure_level(self, level)

        self.spawn_director.reset(elapsed_time=self.elapsed_time)
        self.world.apply_pending()

    def random_play_area_position(self) -> Vector2:
        padding = 60.0
        return Vector2(
            random.uniform(padding, SCREEN_WIDTH - padding),
            random.uniform(padding, SCREEN_HEIGHT - padding),
        )

    def open_game_over(
        self,
        title: str,
        subtitle: str,
        retry_strategy_factory: Callable[[], GameModeStrategy],
        death_cause: str | None = None,
        include_session_summary: bool = False,
        final_score: float | None = None,
        mode_key: str | None = None,
    ) -> None:
        resolved_score = (
            float(final_score)
            if final_score is not None
            else float(self.mode.calcular_ranking(self.elapsed_time, self.world.level, self.session_stats))
        )
        resolved_mode_key = self.mode.mode_key() if mode_key is None else mode_key
        self._pending_game_over_transition = PendingGameOverTransition(
            title=title,
            subtitle=subtitle,
            retry_strategy_factory=retry_strategy_factory,
            death_cause=death_cause,
            include_session_summary=include_session_summary,
            final_score=resolved_score,
            mode_key=resolved_mode_key,
        )

    def _commit_pending_game_over_transition(self) -> None:
        pending = self._pending_game_over_transition
        if pending is None:
            return
        self._pending_game_over_transition = None
        summary_stats = self.session_stats if pending.include_session_summary else None
        ranking_sync_handle = RankingOrchestrator().start(
            mode=pending.mode_key,
            score=pending.final_score,
            limit=10,
        )
        self.stack.replace(
            GameOverScene(
                self.stack,
                reached_level=self.world.level,
                title=pending.title,
                subtitle=pending.subtitle,
                retry_strategy_factory=pending.retry_strategy_factory,
                mode_key=pending.mode_key,
                death_cause=pending.death_cause,
                session_stats=summary_stats,
                elapsed_time=self.elapsed_time if pending.include_session_summary else None,
                final_score=pending.final_score,
                ranking_sync_handle=ranking_sync_handle,
            )
        )

    def _register_event_handlers(self) -> None:
        event_bus = self.stack.event_bus
        self._event_tokens = [
            event_bus.on(PlayerDied, self._on_player_died),
            event_bus.on(PortalEntered, self._on_portal_entered),
            event_bus.on(ExplosionTriggered, self._on_explosion_triggered),
            event_bus.on(EnemySpawned, self.stats_collector.on_enemy_spawned),
            event_bus.on(CollectibleCollected, self.stats_collector.on_collectible_collected),
            event_bus.on(SpawnPortalDestroyed, self.stats_collector.on_spawn_portal_destroyed),
            event_bus.on(DashStarted, self.stats_collector.on_dash_started),
            event_bus.on(ParryLanded, self.stats_collector.on_parry_landed),
            event_bus.on(BulletExpired, self.stats_collector.on_bullet_expired),
            event_bus.on(LifetimeExpired, self.stats_collector.on_lifetime_expired),
        ]

    def _unregister_event_handlers(self) -> None:
        event_bus = self.stack.event_bus
        for token in self._event_tokens:
            event_bus.off(token)
        self._event_tokens.clear()

    def _on_player_died(self, event: PlayerDied) -> None:
        del event
        if self._transition_in_progress:
            return
        self._transition_in_progress = True
        self.world.runtime_state["death_transition"] = True
        self.mode.on_player_death(self)

    def _on_portal_entered(self, event: PortalEntered) -> None:
        del event
        if self._transition_in_progress:
            return
        self._transition_in_progress = True
        self.level_progression.on_level_portal_crossed(self)

    def _on_explosion_triggered(self, event: ExplosionTriggered) -> None:
        self._explosion_fx.append(ExplosionFxState(position=event.position.copy()))
        self._start_screen_shake(intensity=9.0, duration=0.22)

    def _update_explosion_fx(self, dt: float) -> None:
        if not self._explosion_fx:
            return
        active_fx: list[ExplosionFxState] = []
        for effect in self._explosion_fx:
            effect.age += dt
            if effect.age < effect.duration:
                active_fx.append(effect)
        self._explosion_fx = active_fx

    def _render_explosion_fx(self, screen: pygame.Surface) -> None:
        for effect in self._explosion_fx:
            progress = min(1.0, effect.age / max(0.001, effect.duration))
            radius = int(10 + effect.max_radius * progress)
            alpha = int(200 * (1.0 - progress))
            if radius <= 0 or alpha <= 0:
                continue

            size = radius * 2 + 8
            overlay = pygame.Surface((size, size), pygame.SRCALPHA)
            center = (size // 2, size // 2)
            core_radius = max(2, int(radius * 0.33))
            ring_radius = max(core_radius + 2, radius)
            pygame.draw.circle(overlay, (255, 242, 188, min(255, alpha + 20)), center, core_radius)
            pygame.draw.circle(overlay, (255, 140, 70, alpha), center, ring_radius, 3)
            pygame.draw.circle(overlay, (255, 210, 120, max(0, alpha - 40)), center, max(core_radius + 3, ring_radius - 8), 2)
            screen.blit(overlay, (int(effect.position.x - size / 2), int(effect.position.y - size / 2)))

    def _start_screen_shake(self, intensity: float, duration: float) -> None:
        self._shake_intensity = max(self._shake_intensity, intensity)
        self._shake_duration = max(self._shake_duration, duration)
        self._shake_time_left = max(self._shake_time_left, duration)

    def _update_screen_shake(self, dt: float) -> None:
        if self._shake_time_left <= 0.0:
            self._shake_time_left = 0.0
            return
        self._shake_time_left = max(0.0, self._shake_time_left - dt)

    def _update_boss_cards(self) -> None:
        alive_bosses: list[BossCardState] = []
        for entity in self.world.entities:
            if not entity.active:
                continue
            boss_component = entity.get_component(BossComponent)
            if boss_component is None:
                continue
            alive_bosses.append(
                BossCardState(
                    entity_id=entity.id,
                    boss_name=format_enemy_name(boss_component.boss_kind),
                )
            )
        alive_bosses.sort(key=lambda boss: boss.entity_id)
        self._boss_card_states = alive_bosses

    def _render_boss_cards(self, screen: pygame.Surface) -> None:
        card_height = self.hud_renderer.boss_card_height()
        y = 20
        for boss_state in self._boss_card_states:
            self.hud_renderer.render_boss_card(
                screen,
                BossHudCard(boss_name=boss_state.boss_name),
                y=y,
                align_right=True,
            )
            y += card_height + 8

    def _screen_shake_offset(self) -> tuple[int, int]:
        if self._shake_time_left <= 0.0 or self._shake_duration <= 0.0 or self._shake_intensity <= 0.0:
            return (0, 0)
        ratio = self._shake_time_left / self._shake_duration
        amplitude = self._shake_intensity * ratio
        return (
            int(random.uniform(-amplitude, amplitude)),
            int(random.uniform(-amplitude, amplitude)),
        )

