from __future__ import annotations

import math
import random
from dataclasses import dataclass
from typing import Callable

import pygame
from pygame import Vector2

from game.components.data_components import TransformComponent
from game.modes.dungeons_layout import DungeonRuntimeState
from game.config import SCREEN_HEIGHT, SCREEN_WIDTH
from game.core.events import (
    AudioContextChanged,
    BulletExpired,
    CollectibleCollected,
    DashStarted,
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
from game.scenes.services import BackgroundRenderer, HudRenderer
from game.modes.game_mode_strategy import GameModeStrategy
from game.services.ranking_orchestrator import RankingOrchestrator, RankingSyncHandle
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
        self.world.runtime_state.setdefault("show_health_bars", True)

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
        self._update_screen_shake(dt)
        self._update_explosion_fx(dt)

        if self._pending_game_over_transition is not None:
            self._commit_pending_game_over_transition()

    def render(self, screen: pygame.Surface) -> None:
        background_mode = self.world.runtime_state.get("background_mode")
        if background_mode == "void":
            self._world_surface.fill((0, 0, 0))
        elif background_mode == "dungeon":
            self._render_dungeon_background(self._world_surface)
        else:
            self.background_renderer.render(self._world_surface, SCREEN_WIDTH, SCREEN_HEIGHT)

        camera_offset = self.world.runtime_state.get("camera_offset")
        if not isinstance(camera_offset, pygame.Vector2):
            camera_offset = pygame.Vector2()

        self.render_system.render(self._world_surface, camera_offset)
        self._render_survival_lava_overlay(self._world_surface, camera_offset)
        self._render_environment_event_overlay(self._world_surface, camera_offset)
        self._render_explosion_fx(self._world_surface, camera_offset)
        self._render_dungeon_fog(self._world_surface, camera_offset)

        screen.fill((0, 0, 0))
        shake_offset = self._screen_shake_offset()
        screen.blit(self._world_surface, shake_offset)
        self.hud_renderer.render_lines(screen, self.mode.build_hud_lines(self))

    def _render_survival_lava_overlay(self, screen: pygame.Surface, camera_offset: pygame.Vector2) -> None:
        lava_state = self.world.runtime_state.get("survival_lava")
        if not isinstance(lava_state, dict):
            return

        state = str(lava_state.get("state", "idle"))
        region = lava_state.get("region")
        if not isinstance(region, tuple) or len(region) != 4:
            return
        rect = pygame.Rect(int(region[0]), int(region[1]), int(region[2]), int(region[3]))
        rect.x += int(camera_offset.x)
        rect.y += int(camera_offset.y)
        if rect.width <= 0 or rect.height <= 0:
            return

        if state == "active":
            blink_visible = bool(lava_state.get("blink_visible", True))
            if not blink_visible:
                return
            overlay = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
            overlay.fill((255, 80, 35, 112))
            screen.blit(overlay, rect.topleft)
            pygame.draw.rect(screen, (255, 206, 94), rect, 3)
            return

        warning_left = float(lava_state.get("time_to_lava", 0.0))
        warning_duration = float(lava_state.get("warning_duration", 0.0))
        if state != "warning" or warning_duration <= 0.0:
            return

        alpha_ratio = max(0.2, min(1.0, 1.0 - (warning_left / warning_duration)))
        alpha = int(40 + 90 * alpha_ratio)
        overlay = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        overlay.fill((255, 185, 42, alpha))
        screen.blit(overlay, rect.topleft)
        pygame.draw.rect(screen, (255, 230, 120), rect, 2)

    def _render_environment_event_overlay(self, screen: pygame.Surface, camera_offset: pygame.Vector2) -> None:
        event_state = self.world.runtime_state.get("environment_event")
        if not isinstance(event_state, dict):
            return

        event_name = event_state.get("name")
        region = event_state.get("region")
        if isinstance(event_name, str) and isinstance(region, tuple) and len(region) == 4:
            rect = pygame.Rect(int(region[0]), int(region[1]), int(region[2]), int(region[3]))
            rect.x += int(camera_offset.x)
            rect.y += int(camera_offset.y)
            if event_name == "snow_drift":
                surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
                surface.fill((180, 220, 255, 70))
                screen.blit(surface, rect.topleft)
                pygame.draw.rect(screen, (220, 245, 255), rect, 2)
            elif event_name == "water_region":
                surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
                surface.fill((60, 145, 220, 85))
                screen.blit(surface, rect.topleft)
                pygame.draw.rect(screen, (115, 200, 255), rect, 2)
            elif event_name == "bullet_cloud":
                surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
                surface.fill((255, 220, 120, 75))
                screen.blit(surface, rect.topleft)
                pygame.draw.rect(screen, (255, 236, 150), rect, 2)

        black_hole = event_state.get("black_hole")
        if not isinstance(black_hole, dict):
            return
        x = int(float(black_hole.get("x", 0.0)) + camera_offset.x)
        y = int(float(black_hole.get("y", 0.0)) + camera_offset.y)
        pull_radius = int(float(black_hole.get("pull_radius", 0.0)))
        consume_radius = int(float(black_hole.get("consume_radius", 0.0)))
        if pull_radius <= 0 or consume_radius <= 0:
            return

        now = pygame.time.get_ticks() * 0.001
        pulse = 0.5 + 0.5 * math.sin(now * 2.6)

        aura = pygame.Surface((pull_radius * 2 + 8, pull_radius * 2 + 8), pygame.SRCALPHA)
        aura_center = (aura.get_width() // 2, aura.get_height() // 2)
        outer_alpha = int(34 + pulse * 26)
        inner_alpha = int(55 + pulse * 42)
        pygame.draw.circle(aura, (72, 20, 130, outer_alpha), aura_center, pull_radius + 2)
        pygame.draw.circle(aura, (120, 46, 205, inner_alpha), aura_center, max(2, int(pull_radius * 0.66)))
        screen.blit(aura, (x - aura_center[0], y - aura_center[1]))

        ring_a = consume_radius + 10 + int(3 * math.sin(now * 3.7))
        ring_b = consume_radius + 20 + int(4 * math.cos(now * 2.4 + 0.8))
        pygame.draw.circle(screen, (196, 128, 255), (x, y), max(2, ring_a), 2)
        pygame.draw.circle(screen, (124, 214, 255), (x, y), max(2, ring_b), 1)

        for index in range(12):
            phase = (index / 12.0) * (math.pi * 2.0)
            angle = (now * (1.8 + 0.12 * index)) + phase
            orbit = consume_radius + 7 + (index % 3) * 5
            px = int(x + math.cos(angle) * orbit)
            py = int(y + math.sin(angle) * orbit)
            color = (235, 200, 255) if index % 2 == 0 else (150, 230, 255)
            pygame.draw.circle(screen, color, (px, py), 1)

        core_radius = max(2, int(consume_radius * (0.92 + 0.08 * math.sin(now * 6.4))))
        pygame.draw.circle(screen, (10, 6, 18), (x, y), core_radius)
        pygame.draw.circle(screen, (240, 188, 255), (x, y), consume_radius + 2, 2)

    def setup_level(self, level: int) -> None:
        self.world.level = level
        self.level_portal_spawned = False
        self._transition_in_progress = False
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

        self.mode.configure_level(self, level)

        self.spawn_director.reset(elapsed_time=self.elapsed_time)
        self.world.apply_pending()

    def random_play_area_position(self) -> Vector2:
        padding = 60.0
        return Vector2(
            random.uniform(padding, max(padding, self.world.width - padding)),
            random.uniform(padding, max(padding, self.world.height - padding)),
        )

    def open_game_over(
        self,
        title: str,
        subtitle: str,
        retry_strategy_factory: Callable[[], GameModeStrategy],
        death_cause: str | None = None,
        include_session_summary: bool = False,
        final_score: float | None = None,
    ) -> None:
        resolved_score = (
            float(final_score)
            if final_score is not None
            else float(self.mode.calcular_ranking(self.elapsed_time, self.world.level, self.session_stats))
        )
        self._pending_game_over_transition = PendingGameOverTransition(
            title=title,
            subtitle=subtitle,
            retry_strategy_factory=retry_strategy_factory,
            death_cause=death_cause,
            include_session_summary=include_session_summary,
            final_score=resolved_score,
            mode_key=self.mode.mode_key(),
        )

    def _commit_pending_game_over_transition(self) -> None:
        pending = self._pending_game_over_transition
        if pending is None:
            return
        self._pending_game_over_transition = None
        summary_stats = self.session_stats if pending.include_session_summary else None
        ranking_sync_handle: RankingSyncHandle = RankingOrchestrator().start(
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

    def _render_explosion_fx(self, screen: pygame.Surface, camera_offset: pygame.Vector2) -> None:
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
            screen.blit(
                overlay,
                (
                    int(effect.position.x + camera_offset.x - size / 2),
                    int(effect.position.y + camera_offset.y - size / 2),
                ),
            )

    def _render_dungeon_fog(self, screen: pygame.Surface, camera_offset: pygame.Vector2) -> None:
        runtime = self.world.runtime_state.get("dungeon_runtime")
        if not isinstance(runtime, DungeonRuntimeState):
            return

        fog = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        fog.fill((0, 0, 0, 255))

        cell_size = max(2, int(runtime.layout.geometry.cell_size))
        half = cell_size * 0.5
        for cell in runtime.revealed_cells:
            center = runtime.layout.cell_center(cell) + camera_offset
            rect = pygame.Rect(int(center.x - half), int(center.y - half), cell_size, cell_size)
            fog.fill((0, 0, 0, 140), rect)

        for cell in runtime.visible_cells:
            center = runtime.layout.cell_center(cell) + camera_offset
            rect = pygame.Rect(int(center.x - half), int(center.y - half), cell_size, cell_size)
            fog.fill((0, 0, 0, 0), rect)

        screen.blit(fog, (0, 0))

    def _render_dungeon_background(self, screen: pygame.Surface) -> None:
        screen.fill((20, 26, 34))
        grid_color = (40, 52, 66)
        grid_step = 32
        for x in range(0, SCREEN_WIDTH, grid_step):
            pygame.draw.line(screen, grid_color, (x, 0), (x, SCREEN_HEIGHT), 1)
        for y in range(0, SCREEN_HEIGHT, grid_step):
            pygame.draw.line(screen, grid_color, (0, y), (SCREEN_WIDTH, y), 1)

    def _start_screen_shake(self, intensity: float, duration: float) -> None:
        self._shake_intensity = max(self._shake_intensity, intensity)
        self._shake_duration = max(self._shake_duration, duration)
        self._shake_time_left = max(self._shake_time_left, duration)

    def _update_screen_shake(self, dt: float) -> None:
        if self._shake_time_left <= 0.0:
            self._shake_time_left = 0.0
            return
        self._shake_time_left = max(0.0, self._shake_time_left - dt)

    def _screen_shake_offset(self) -> tuple[int, int]:
        if self._shake_time_left <= 0.0 or self._shake_duration <= 0.0 or self._shake_intensity <= 0.0:
            return (0, 0)
        ratio = self._shake_time_left / self._shake_duration
        amplitude = self._shake_intensity * ratio
        return (
            int(random.uniform(-amplitude, amplitude)),
            int(random.uniform(-amplitude, amplitude)),
        )
