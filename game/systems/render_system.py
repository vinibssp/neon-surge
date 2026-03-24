from __future__ import annotations

import pygame

from game.components.data_components import RenderComponent, TransformComponent
from game.core.world import GameWorld
from game.systems.world_queries import RENDERABLE_QUERY


class RenderSystem:
    def __init__(self, world: GameWorld) -> None:
        self.world = world

    def render(self, screen: pygame.Surface) -> None:
        for entity in self.world.query(RENDERABLE_QUERY):
            transform = entity.get_component(TransformComponent)
            render = entity.get_component(RenderComponent)
            if transform is None or render is None:
                continue
            render.render_strategy.render(screen, entity, transform)
