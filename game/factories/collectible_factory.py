from __future__ import annotations

from pygame import Vector2

from game.components.data_components import (
    CollectibleComponent,
    CollisionComponent,
    RenderComponent,
    TransformComponent,
)
from game.config import COLLECTIBLE_COLOR, COLLECTIBLE_RADIUS
from game.ecs.entity import Entity
from game.rendering.strategies import CircleRenderStrategy


class CollectibleFactory:
    @staticmethod
    def create(position: Vector2) -> Entity:
        collectible = Entity()
        collectible.add_tag("collectible")
        collectible.add_component(TransformComponent(position=position))
        collectible.add_component(CollectibleComponent(value=1))
        collectible.add_component(CollisionComponent(radius=COLLECTIBLE_RADIUS, layer="collectible"))
        collectible.add_component(
            RenderComponent(
                render_strategy=CircleRenderStrategy(
                    color=COLLECTIBLE_COLOR,
                    radius=COLLECTIBLE_RADIUS,
                    style="coin",
                    pulse_speed=8.5,
                )
            )
        )
        return collectible
