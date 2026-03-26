from __future__ import annotations

import math

import pygame

from game.components.data_components import CollisionComponent, HealthComponent, RenderComponent, StaggeredComponent, TransformComponent
from game.core.world import GameWorld
from game.systems.world_queries import RENDERABLE_QUERY
from game.config import HEALTH_BAR_BG_COLOR, HEALTH_BAR_ENEMY_COLOR, HEALTH_BAR_PLAYER_COLOR


class RenderSystem:
    def __init__(self, world: GameWorld) -> None:
        self.world = world

    def render(self, screen: pygame.Surface, camera_offset: pygame.Vector2 | None = None) -> None:
        offset = pygame.Vector2() if camera_offset is None else pygame.Vector2(camera_offset)
        for entity in self.world.query(RENDERABLE_QUERY):
            transform = entity.get_component(TransformComponent)
            render = entity.get_component(RenderComponent)
            if transform is None or render is None:
                continue

            render_transform = TransformComponent(position=transform.position + offset)
            render.render_strategy.render(screen, entity, render_transform)

            self._render_health_bar(screen, entity, render_transform)

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
            screen.blit(
                overlay,
                (
                    int(render_transform.position.x - center[0]),
                    int(render_transform.position.y - center[1]),
                ),
            )

    def _render_health_bar(self, screen: pygame.Surface, entity, transform: TransformComponent) -> None:
        if not self.world.runtime_state.get("show_health_bars", True):
            return
        if not (entity.has_tag("enemy") or entity.has_tag("player")):
            return
        health = entity.get_component(HealthComponent)
        if health is None or health.maximum <= 0.0:
            return

        ratio = max(0.0, min(1.0, health.current / health.maximum))
        collision = entity.get_component(CollisionComponent)
        radius = 12.0 if collision is None else collision.radius

        bar_width = max(18, int(radius * 2.2))
        bar_height = 5 if entity.has_tag("player") else 4
        bar_x = int(transform.position.x - bar_width * 0.5)
        bar_y = int(transform.position.y + radius + (8 if entity.has_tag("player") else 6))

        fill_width = max(0, int(bar_width * ratio))
        pygame.draw.rect(screen, HEALTH_BAR_BG_COLOR, (bar_x, bar_y, bar_width, bar_height))
        if fill_width > 0:
            color = HEALTH_BAR_PLAYER_COLOR if entity.has_tag("player") else HEALTH_BAR_ENEMY_COLOR
            pygame.draw.rect(screen, color, (bar_x, bar_y, fill_width, bar_height))
