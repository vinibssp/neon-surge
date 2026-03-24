from __future__ import annotations

from typing import Callable

from pygame import Vector2

from game.components.data_components import PortalSpawnComponent, TransformComponent
from game.config import PORTAL_SPAWN_TIME
from game.core.events import EnemySpawned
from game.core.world import GameWorld
from game.factories.enemy_factory import EnemyFactory
from game.factories.portal_factory import PortalFactory
from game.modes.spawn_strategy import SpawnStrategy
from game.systems.world_queries import PORTAL_SPAWN_QUERY


class SpawnDirector:
    def __init__(
        self,
        world: GameWorld,
        strategy: SpawnStrategy,
        position_provider: Callable[[], Vector2],
    ) -> None:
        self.world = world
        self.strategy = strategy
        self.position_provider = position_provider
        self._spawn_timer = 0.0

    def reset(self, elapsed_time: float) -> None:
        self._spawn_timer = self.strategy.initial_timer(self.world, elapsed_time)

    def update(self, dt: float, elapsed_time: float) -> None:
        self._update_enemy_portals(dt, elapsed_time)
        self._update_spawn_portals(dt)

    def _update_enemy_portals(self, dt: float, elapsed_time: float) -> None:
        self._spawn_timer -= dt
        if self._spawn_timer > 0:
            return

        portal_count = self.strategy.portals_per_cycle(self.world, elapsed_time)
        for _ in range(portal_count):
            enemy_kind = self.strategy.choose_enemy_kind(self.world, elapsed_time)
            portal = PortalFactory.create_enemy_spawn_portal(
                self.position_provider(),
                enemy_kind=enemy_kind,
                delay=PORTAL_SPAWN_TIME,
            )
            self.world.add_entity(portal)

        self._spawn_timer = self.strategy.next_interval(self.world, elapsed_time)

    def _update_spawn_portals(self, dt: float) -> None:
        portals = self.world.query(PORTAL_SPAWN_QUERY)
        for portal in portals:
            spawn = portal.get_component(PortalSpawnComponent)
            transform = portal.get_component(TransformComponent)
            if spawn is None or transform is None:
                continue

            spawn.time_left -= dt
            if spawn.time_left > 0:
                continue

            enemy = EnemyFactory.create_by_kind(spawn.enemy_kind, transform.position)
            self.strategy.on_enemy_spawned(self.world, enemy)
            self.world.add_entity(enemy)
            self.world.event_bus.publish(EnemySpawned(enemy_kind=spawn.enemy_kind))
            self.world.remove_entity(portal)
