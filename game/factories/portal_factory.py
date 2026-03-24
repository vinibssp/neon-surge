from __future__ import annotations

from pygame import Vector2

from game.components.data_components import (
    CollisionComponent,
    PortalComponent,
    PortalSpawnComponent,
    RenderComponent,
    TransformComponent,
)
from game.config import BACKGROUND_COLOR, PLAYER_CORE_COLOR, PORTAL_GREEN_COLOR, PORTAL_RED_COLOR
from game.ecs.entity import Entity
from game.rendering.strategies import PortalRenderStrategy


class PortalFactory:
    @staticmethod
    def create_enemy_spawn_portal(position: Vector2, enemy_kind: str, delay: float) -> Entity:
        portal = Entity()
        portal.add_component(TransformComponent(position=position))
        portal.add_component(PortalSpawnComponent(time_left=delay, enemy_kind=enemy_kind))
        portal.add_component(CollisionComponent(radius=18.0, layer="portal-spawn"))
        portal.add_component(
            RenderComponent(
                render_strategy=PortalRenderStrategy(
                    neon_color=PORTAL_RED_COLOR,
                    background_color=BACKGROUND_COLOR,
                    arc_color=PLAYER_CORE_COLOR,
                    base_radius=18.0,
                )
            )
        )
        return portal

    @staticmethod
    def create_level_portal(position: Vector2) -> Entity:
        portal = Entity()
        portal.add_component(TransformComponent(position=position))
        portal.add_component(PortalComponent(is_level_portal=True))
        portal.add_component(CollisionComponent(radius=22.0, layer="portal"))
        portal.add_component(
            RenderComponent(
                render_strategy=PortalRenderStrategy(
                    neon_color=PORTAL_GREEN_COLOR,
                    background_color=BACKGROUND_COLOR,
                    arc_color=PLAYER_CORE_COLOR,
                    base_radius=22.0,
                )
            )
        )
        return portal
