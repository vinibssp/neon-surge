from __future__ import annotations

from typing import Callable

from game.core.events import PortalActivated
from game.core.world import GameWorld
from game.ecs.query import WorldQuery
from game.factories.portal_factory import PortalFactory
from game.modes.dungeons_layout import DungeonRuntimeState


DUNGEON_BOSS_QUERY = WorldQuery(component_types=(), tags=("dungeon_boss",))


class DungeonObjectiveSystem:
    def __init__(self, world: GameWorld, runtime_provider: Callable[[], DungeonRuntimeState | None]) -> None:
        self.world = world
        self.runtime_provider = runtime_provider

    def update(self, dt: float) -> None:
        del dt
        runtime = self.runtime_provider()
        if runtime is None:
            return

        boss_entities = self.world.query(DUNGEON_BOSS_QUERY)
        if boss_entities:
            runtime.boss_defeated = False
            return

        if not runtime.boss_defeated:
            runtime.boss_defeated = True

        if runtime.exit_portal_spawned:
            return

        portal_position = runtime.layout.room_center(runtime.layout.boss_room_index)
        self.world.add_entity(PortalFactory.create_level_portal(portal_position))
        self.world.event_bus.publish(PortalActivated(portal_kind="level"))
        runtime.exit_portal_spawned = True
