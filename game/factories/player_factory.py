from __future__ import annotations

from pygame import Vector2

from game.components.data_components import (
    CollisionComponent,
    DashComponent,
    InvulnerabilityComponent,
    MovementComponent,
    ParryComponent,
    RenderComponent,
    TransformComponent,
)
from game.config import (
    PLAYER_COLOR,
    PLAYER_CORE_COLOR,
    PLAYER_DASH_COOLDOWN,
    PLAYER_DASH_DURATION,
    PLAYER_DASH_INVULN_EXTRA,
    PLAYER_DASH_SPEED,
    PLAYER_PARRY_COOLDOWN,
    PLAYER_PARRY_DURATION,
    PLAYER_PARRY_RADIUS,
    PLAYER_PARRY_STAGGER_DURATION,
    PLAYER_RADIUS,
    PLAYER_SPEED,
)
from game.ecs.entity import Entity
from game.rendering.strategies import PlayerRenderStrategy


class PlayerFactory:
    @staticmethod
    def create(position: Vector2) -> Entity:
        player = Entity()
        player.add_tag("player")
        player.add_component(TransformComponent(position=position))
        player.add_component(MovementComponent(max_speed=PLAYER_SPEED))
        player.add_component(
            DashComponent(
                dash_speed=PLAYER_DASH_SPEED,
                duration=PLAYER_DASH_DURATION,
                cooldown=PLAYER_DASH_COOLDOWN,
                invulnerability_extra=PLAYER_DASH_INVULN_EXTRA,
            )
        )
        player.add_component(InvulnerabilityComponent())
        player.add_component(
            ParryComponent(
                duration=PLAYER_PARRY_DURATION,
                cooldown=PLAYER_PARRY_COOLDOWN,
                radius=PLAYER_PARRY_RADIUS,
                stagger_duration=PLAYER_PARRY_STAGGER_DURATION,
            )
        )
        player.add_component(CollisionComponent(radius=PLAYER_RADIUS, layer="player"))
        player.add_component(
            RenderComponent(
                render_strategy=PlayerRenderStrategy(
                    outer_color=PLAYER_COLOR,
                    inner_color=PLAYER_CORE_COLOR,
                    radius=PLAYER_RADIUS,
                )
            )
        )
        return player
