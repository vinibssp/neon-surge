from __future__ import annotations

import random
from typing import Callable

import pygame
from pygame import Vector2

from game.components.data_components import TransformComponent
from game.config import SCREEN_HEIGHT, SCREEN_WIDTH
from game.core.events import (
    BulletExpired,
    CollectibleCollected,
    DashStarted,
    DomainEvent,
    DomainEventDispatcher,
    EnemySpawned,
    LifetimeExpired,
    PlayerDied,
    PortalEntered,
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
        self.world = GameWorld(width=SCREEN_WIDTH, height=SCREEN_HEIGHT)
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
        self.event_dispatcher = DomainEventDispatcher()
        self.stats_collector = StatsCollector()
        self.session_stats = self.stats_collector.stats
        self._pending_events: list[DomainEvent] | None = None
        self._register_event_handlers()
        self.mode.on_enter(self)

    def on_enter(self) -> None:
        pass

    def on_exit(self) -> None:
        pass

    def handle_input(self, events: list[pygame.event.Event]) -> None:
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.stack.push(PauseScene(self.stack, retry_strategy_factory=self.mode.create_retry_strategy))
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

        self._pending_events = self.world.event_bus.drain()
        while self._pending_events:
            event = self._pending_events.pop(0)
            self.event_dispatcher.dispatch(event)

    def render(self, screen: pygame.Surface) -> None:
        self.background_renderer.render(screen, SCREEN_WIDTH, SCREEN_HEIGHT)
        self.render_system.render(screen)
        self.hud_renderer.render_lines(screen, self.mode.build_hud_lines(self))

    def setup_level(self, level: int) -> None:
        self.world.level = level
        self.level_portal_spawned = False
        self.world.event_bus.drain()

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
        self.event_dispatcher.on(PlayerDied, self._on_player_died)
        self.event_dispatcher.on(PortalEntered, self._on_portal_entered)
        self.event_dispatcher.on(EnemySpawned, self.stats_collector.on_enemy_spawned)
        self.event_dispatcher.on(CollectibleCollected, self.stats_collector.on_collectible_collected)
        self.event_dispatcher.on(SpawnPortalDestroyed, self.stats_collector.on_spawn_portal_destroyed)
        self.event_dispatcher.on(DashStarted, self.stats_collector.on_dash_started)
        self.event_dispatcher.on(BulletExpired, self.stats_collector.on_bullet_expired)
        self.event_dispatcher.on(LifetimeExpired, self.stats_collector.on_lifetime_expired)

    def _on_player_died(self, event: PlayerDied) -> None:
        del event
        self._clear_pending_events()
        self.mode.on_player_death(self)

    def _on_portal_entered(self, event: PortalEntered) -> None:
        del event
        self._clear_pending_events()
        self.level_progression.on_level_portal_crossed(self)

    def _clear_pending_events(self) -> None:
        if self._pending_events is not None:
            self._pending_events.clear()
