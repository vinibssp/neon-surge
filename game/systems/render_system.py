from __future__ import annotations

import math

import pygame

from game.components.data_components import CollisionComponent, RenderComponent, StaggeredComponent, TransformComponent
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

            stagger = entity.get_component(StaggeredComponent)
            collision = entity.get_component(CollisionComponent)
            if stagger is None or collision is None or stagger.time_left <= 0.0:
                continue

            pulse = 0.5 + 0.5 * math.sin(stagger.pulse_time * 16.0)
            radius = int(collision.radius + 4 + pulse * 3.0)
            tone = int(75 + pulse * 130)
            overlay = pygame.Surface((radius * 2 + 10, radius * 2 + 10), pygame.SRCALPHA)
            center = (overlay.get_width() // 2, overlay.get_height() // 2)
            pygame.draw.circle(overlay, (tone, tone, tone, 118), center, max(2, int(collision.radius + 1)))
            ring_color = (255, 255, 255, 85) if pulse > 0.5 else (22, 22, 22, 95)
            pygame.draw.circle(overlay, ring_color, center, radius, 2)
            screen.blit(overlay, (int(transform.position.x - center[0]), int(transform.position.y - center[1])))
