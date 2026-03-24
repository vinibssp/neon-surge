from __future__ import annotations

import pygame


def draw_neon_glow(
    surface: pygame.Surface,
    color: tuple[int, int, int],
    center_x: int,
    center_y: int,
    radius: int,
    layers: int,
) -> None:
    glow_radius = radius + layers * 3
    glow_surface = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
    center = (glow_radius, glow_radius)
    for layer_index in range(layers, 0, -1):
        layer_radius = radius + layer_index * 2
        alpha = max(20, int(170 / (layer_index + 1)))
        pygame.draw.circle(glow_surface, (*color, alpha), center, layer_radius)
    surface.blit(glow_surface, (center_x - glow_radius, center_y - glow_radius))
