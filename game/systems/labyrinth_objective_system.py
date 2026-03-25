from __future__ import annotations

from typing import Callable

from game.components.data_components import (
    CollisionComponent,
    LabyrinthExitComponent,
    LabyrinthKeyComponent,
    TransformComponent,
)
from game.core.events import (
    LabyrinthBossCleared,
    LabyrinthExitUnlocked,
    LabyrinthKeyCollected,
    PortalEntered,
)
from game.core.world import GameWorld
from game.ecs.query import WorldQuery
from game.modes.labyrinth_layout import LabyrinthRuntimeState


MAZE_KEY_QUERY = WorldQuery(
    component_types=(TransformComponent, CollisionComponent, LabyrinthKeyComponent),
    tags=("maze-key",),
)
MAZE_EXIT_QUERY = WorldQuery(
    component_types=(TransformComponent, CollisionComponent, LabyrinthExitComponent),
    tags=("maze-exit",),
)


class LabyrinthObjectiveSystem:
    def __init__(self, world: GameWorld, runtime_provider: Callable[[], LabyrinthRuntimeState | None]) -> None:
        self.world = world
        self.runtime_provider = runtime_provider
        self._boss_level_completed = False

    def update(self, dt: float) -> None:
        del dt
        runtime = self.runtime_provider()
        if runtime is None:
            self._boss_level_completed = False
            return

        player = self.world.player
        if player is None:
            return
        player_transform = player.get_component(TransformComponent)
        player_collision = player.get_component(CollisionComponent)
        if player_transform is None or player_collision is None:
            return

        if runtime.is_boss_level:
            self._collect_boss_keys(runtime, player_transform.position, player_collision.radius)
            keys_completed = runtime.boss_keys_collected >= runtime.boss_keys_required
            if keys_completed and not self._boss_level_completed:
                self._boss_level_completed = True
                self.world.event_bus.publish(LabyrinthBossCleared(level=self.world.level))
                self.world.event_bus.publish(PortalEntered())
            return

        self._boss_level_completed = False

        if not runtime.has_key:
            for key_entity in self.world.query(MAZE_KEY_QUERY):
                key_transform = key_entity.get_component(TransformComponent)
                key_collision = key_entity.get_component(CollisionComponent)
                key_data = key_entity.get_component(LabyrinthKeyComponent)
                if key_transform is None or key_collision is None or key_data is None:
                    continue
                if not self._collides(
                    player_transform.position,
                    player_collision.radius,
                    key_transform.position,
                    key_collision.radius,
                ):
                    continue
                key_data.collected = True
                runtime.has_key = True
                runtime.exit_unlocked = True
                self.world.remove_entity(key_entity)
                # Fluxo de objetivo: ao coletar chave, porta destrava e passa a aceitar transição de nível.
                self.world.event_bus.publish(LabyrinthKeyCollected(level=self.world.level))
                self._unlock_exits()
                break

        if not runtime.exit_unlocked:
            return

        for exit_entity in self.world.query(MAZE_EXIT_QUERY):
            exit_transform = exit_entity.get_component(TransformComponent)
            exit_collision = exit_entity.get_component(CollisionComponent)
            exit_data = exit_entity.get_component(LabyrinthExitComponent)
            if exit_transform is None or exit_collision is None or exit_data is None:
                continue
            if not exit_data.unlocked:
                continue
            if not self._collides(
                player_transform.position,
                player_collision.radius,
                exit_transform.position,
                exit_collision.radius,
            ):
                continue
            self.world.event_bus.publish(PortalEntered())
            return

    def _unlock_exits(self) -> None:
        for exit_entity in self.world.query(MAZE_EXIT_QUERY):
            exit_component = exit_entity.get_component(LabyrinthExitComponent)
            if exit_component is None or exit_component.unlocked:
                continue
            exit_component.unlocked = True
            self.world.event_bus.publish(LabyrinthExitUnlocked(level=self.world.level))

    def _collect_boss_keys(self, runtime: LabyrinthRuntimeState, player_position, player_radius: float) -> None:
        if runtime.boss_keys_required <= 0:
            return

        for key_entity in self.world.query(MAZE_KEY_QUERY):
            key_transform = key_entity.get_component(TransformComponent)
            key_collision = key_entity.get_component(CollisionComponent)
            key_data = key_entity.get_component(LabyrinthKeyComponent)
            if key_transform is None or key_collision is None or key_data is None:
                continue
            if not self._collides(player_position, player_radius, key_transform.position, key_collision.radius):
                continue
            key_data.collected = True
            runtime.boss_keys_collected += 1
            self.world.remove_entity(key_entity)
            self.world.event_bus.publish(LabyrinthKeyCollected(level=self.world.level))

    @staticmethod
    def _collides(a_pos, a_radius: float, b_pos, b_radius: float) -> bool:
        distance_sq = (a_pos - b_pos).length_squared()
        radius_sum = a_radius + b_radius
        return distance_sq <= radius_sum * radius_sum
