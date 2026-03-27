from __future__ import annotations

from game.components.data_components import ParryComponent, StaggeredComponent, TransformComponent
from game.core.events import ParryLanded
from game.core.world import GameWorld
from game.systems.world_queries import ENEMY_TRANSFORM_QUERY, PLAYER_PARRY_QUERY


class ParrySystem:
    def __init__(self, world: GameWorld) -> None:
        self.world = world

    def update(self, dt: float) -> None:
        for player in self.world.query(PLAYER_PARRY_QUERY):
            parry = player.get_component(ParryComponent)
            transform = player.get_component(TransformComponent)
            if parry is None or transform is None:
                continue

            parry.cooldown_left = max(0.0, parry.cooldown_left - dt)

            should_start = parry.requested and parry.cooldown_left <= 0.0
            parry.requested = False
            if should_start:
                parry.active_time_left = parry.duration
                parry.cooldown_left = parry.cooldown
                self.world.runtime_state["parry_window_open"] = True
                self.world.runtime_state["parry_window_scored"] = False
                self.world.runtime_state["parry_window_player_id"] = player.id

            if parry.active_time_left <= 0.0:
                self._close_parry_window()
                continue

            parry.active_time_left = max(0.0, parry.active_time_left - dt)
            hit_confirmed = self._apply_parry_stagger(transform.position, parry.radius, parry.stagger_duration)
            if hit_confirmed:
                self._confirm_parry_hit(player.id)

            if parry.active_time_left <= 0.0:
                self._close_parry_window()

    def _apply_parry_stagger(self, center, radius: float, duration: float) -> bool:
        hit_confirmed = False
        radius_sq = radius * radius
        for enemy in self.world.query(ENEMY_TRANSFORM_QUERY):
            enemy_transform = enemy.get_component(TransformComponent)
            if enemy_transform is None:
                continue
            if (enemy_transform.position - center).length_squared() > radius_sq:
                continue

            stagger = enemy.get_component(StaggeredComponent)
            if stagger is None:
                enemy.add_component(StaggeredComponent(time_left=duration, pulse_time=0.0))
                hit_confirmed = True
                continue

            if stagger.time_left <= 0.0:
                hit_confirmed = True
            stagger.time_left = max(stagger.time_left, duration)
        return hit_confirmed

    def _confirm_parry_hit(self, player_id: int) -> None:
        is_open = bool(self.world.runtime_state.get("parry_window_open", False))
        if not is_open:
            return
        if bool(self.world.runtime_state.get("parry_window_scored", False)):
            return
        self.world.runtime_state["parry_window_scored"] = True
        self.world.event_bus.publish(ParryLanded(entity_id=player_id))

    def _close_parry_window(self) -> None:
        self.world.runtime_state["parry_window_open"] = False
        self.world.runtime_state["parry_window_scored"] = False
        self.world.runtime_state.pop("parry_window_player_id", None)
