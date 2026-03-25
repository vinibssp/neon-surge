from __future__ import annotations

import random
from typing import Callable

import pygame
from pygame import Vector2

from game.components.data_components import TransformComponent
from game.config import SCREEN_HEIGHT, SCREEN_WIDTH
from game.core.events import (
    AudioContextChanged,
    BulletExpired,
    CollectibleCollected,
    DashStarted,
    EnemySpawned,
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
from game.systems.render_system import RenderSystem
from game.systems.spawn_director import SpawnDirector
from game.systems.system_pipeline import SystemPipeline


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
        self.elapsed_time += dt
        self.level_progression.update(self, dt)
        self.spawn_director.update(dt=dt, elapsed_time=self.elapsed_time)

        self.system_pipeline.update(dt)
        self.world.apply_pending()

    def render(self, screen: pygame.Surface) -> None:
        self.background_renderer.render(screen, SCREEN_WIDTH, SCREEN_HEIGHT)
        self.render_system.render(screen)
        self._render_survival_lava_overlay(screen)
        self._render_environment_event_overlay(screen)
        self.hud_renderer.render_lines(screen, self.mode.build_hud_lines(self))

    def _render_survival_lava_overlay(self, screen: pygame.Surface) -> None:
        lava_state = self.world.runtime_state.get("survival_lava")
        if not isinstance(lava_state, dict):
            return

        state = str(lava_state.get("state", "idle"))
        height = int(float(lava_state.get("height", 0.0)))
        if height <= 0:
            return

        top = SCREEN_HEIGHT - height
        if state == "active":
            blink_visible = bool(lava_state.get("blink_visible", True))
            if not blink_visible:
                return
            overlay = pygame.Surface((SCREEN_WIDTH, height), pygame.SRCALPHA)
            overlay.fill((255, 80, 35, 112))
            screen.blit(overlay, (0, top))
            pygame.draw.line(screen, (255, 206, 94), (0, top), (SCREEN_WIDTH, top), 3)
            return

        warning_left = float(lava_state.get("time_to_lava", 0.0))
        warning_duration = float(lava_state.get("warning_duration", 0.0))
        if state != "warning" or warning_duration <= 0.0:
            return

        alpha_ratio = max(0.2, min(1.0, 1.0 - (warning_left / warning_duration)))
        alpha = int(40 + 90 * alpha_ratio)
        overlay = pygame.Surface((SCREEN_WIDTH, height), pygame.SRCALPHA)
        overlay.fill((255, 185, 42, alpha))
        screen.blit(overlay, (0, top))
        pygame.draw.line(screen, (255, 230, 120), (0, top), (SCREEN_WIDTH, top), 2)

    def _render_environment_event_overlay(self, screen: pygame.Surface) -> None:
        event_state = self.world.runtime_state.get("environment_event")
        if not isinstance(event_state, dict):
            return

        event_name = event_state.get("name")
        region = event_state.get("region")
        if isinstance(event_name, str) and isinstance(region, tuple) and len(region) == 4:
            rect = pygame.Rect(int(region[0]), int(region[1]), int(region[2]), int(region[3]))
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
        x = int(float(black_hole.get("x", 0.0)))
        y = int(float(black_hole.get("y", 0.0)))
        pull_radius = int(float(black_hole.get("pull_radius", 0.0)))
        consume_radius = int(float(black_hole.get("consume_radius", 0.0)))
        if pull_radius <= 0 or consume_radius <= 0:
            return
        pulse = 80 + int(35 * (0.5 + 0.5 * pygame.time.get_ticks() * 0.01 % 1.0))
        aura = pygame.Surface((pull_radius * 2, pull_radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(aura, (142, 90, 255, pulse), (pull_radius, pull_radius), pull_radius)
        screen.blit(aura, (x - pull_radius, y - pull_radius))
        pygame.draw.circle(screen, (15, 8, 28), (x, y), consume_radius)
        pygame.draw.circle(screen, (190, 148, 255), (x, y), consume_radius + 3, 2)

    def setup_level(self, level: int) -> None:
        self.world.level = level
        self.level_portal_spawned = False
        self._transition_in_progress = False

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
            random.uniform(padding, SCREEN_WIDTH - padding),
            random.uniform(padding, SCREEN_HEIGHT - padding),
        )

    def open_game_over(
        self,
        title: str,
        subtitle: str,
        retry_strategy_factory: Callable[[], GameModeStrategy],
    ) -> None:
        self.stack.replace(
            GameOverScene(
                self.stack,
                reached_level=self.world.level,
                title=title,
                subtitle=subtitle,
                retry_strategy_factory=retry_strategy_factory,
            )
        )

    def _register_event_handlers(self) -> None:
        event_bus = self.stack.event_bus
        self._event_tokens = [
            event_bus.on(PlayerDied, self._on_player_died),
            event_bus.on(PortalEntered, self._on_portal_entered),
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
        self.mode.on_player_death(self)

    def _on_portal_entered(self, event: PortalEntered) -> None:
        del event
        if self._transition_in_progress:
            return
        self._transition_in_progress = True
        self.level_progression.on_level_portal_crossed(self)
