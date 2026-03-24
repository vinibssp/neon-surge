from __future__ import annotations

from pygame import Vector2

from game.components.data_components import DashComponent, InvulnerabilityComponent, MovementComponent
from game.core.events import DashStarted
from game.core.world import GameWorld
from game.systems.world_queries import PLAYER_DASH_QUERY


class DashSystem:
    def __init__(self, world: GameWorld) -> None:
        self.world = world

    def update(self, dt: float) -> None:
        for entity in self.world.query(PLAYER_DASH_QUERY):
            dash = entity.get_component(DashComponent)
            movement = entity.get_component(MovementComponent)
            invulnerability = entity.get_component(InvulnerabilityComponent)
            if dash is None or movement is None or invulnerability is None:
                continue

            dash.cooldown_left = max(0.0, dash.cooldown_left - dt)

            should_start_dash = dash.requested and dash.cooldown_left <= 0
            dash.requested = False

            if should_start_dash:
                dash.active_time_left = dash.duration
                dash.cooldown_left = dash.cooldown
                self.world.event_bus.publish(DashStarted(entity_id=entity.id))
                if movement.input_direction.length_squared() > 0:
                    dash.dash_direction = movement.input_direction.normalize()
                elif movement.velocity.length_squared() > 0:
                    dash.dash_direction = movement.velocity.normalize()
                else:
                    dash.dash_direction = Vector2(1, 0)

            if dash.active_time_left > 0:
                dash.active_time_left = max(0.0, dash.active_time_left - dt)
                movement.velocity = dash.dash_direction * dash.dash_speed
                invulnerability.time_left = max(
                    invulnerability.time_left,
                    dash.active_time_left + dash.invulnerability_extra,
                )
