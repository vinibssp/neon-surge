from __future__ import annotations

import math
import time
from dataclasses import dataclass

import pygame

from game.rendering.utils import draw_neon_glow


@dataclass(frozen=True)
class LabyrinthVisualPalette:
    floor_a: tuple[int, int, int] = (10, 16, 22)
    floor_b: tuple[int, int, int] = (12, 20, 27)
    floor_edge: tuple[int, int, int] = (20, 32, 40)
    wall_outline: tuple[int, int, int] = (7, 16, 12)
    wall_fill: tuple[int, int, int] = (58, 214, 136)
    wall_shadow: tuple[int, int, int] = (26, 104, 68)
    wall_edge: tuple[int, int, int] = (138, 255, 190)
    wall_outer_outline: tuple[int, int, int] = (18, 10, 6)
    wall_outer_fill: tuple[int, int, int] = (224, 132, 58)
    wall_outer_edge: tuple[int, int, int] = (255, 204, 128)
    boss_floor_a: tuple[int, int, int] = (22, 10, 28)
    boss_floor_b: tuple[int, int, int] = (28, 14, 36)
    boss_floor_rune: tuple[int, int, int] = (236, 108, 182)
    boss_floor_grid: tuple[int, int, int] = (116, 218, 255)


PALETTE = LabyrinthVisualPalette()


def render_boss_arena_background(screen: pygame.Surface, width: int, height: int, elapsed_time: float) -> None:
    del elapsed_time
    for y in range(height):
        t = y / max(1, height - 1)
        red = int(6 + 8 * t)
        green = int(8 + 10 * t)
        blue = int(16 + 14 * t)
        pygame.draw.line(screen, (red, green, blue), (0, y), (width, y))

    # Pattern 2D em tela inteira: discreto para manter leitura de gameplay.
    pattern = pygame.Surface((width, height), pygame.SRCALPHA)
    tile = 32
    for y in range(0, height, tile):
        for x in range(0, width, tile):
            variant = ((x // tile) + (y // tile)) % 2
            alpha = 4 if variant == 0 else 2
            pygame.draw.rect(pattern, (56, 52, 82, alpha), pygame.Rect(x, y, tile, tile))
    screen.blit(pattern, (0, 0))

    grid = pygame.Surface((width, height), pygame.SRCALPHA)
    grid_step = 56
    for x in range(0, width + grid_step, grid_step):
        pygame.draw.line(grid, (88, 114, 160, 8), (x, 0), (x, height), 1)
    for y in range(0, height + grid_step, grid_step):
        pygame.draw.line(grid, (88, 114, 160, 8), (0, y), (width, y), 1)
    screen.blit(grid, (0, 0))

    # Selo central baixo contraste para identidade da boss room sem poluir projeteis.
    sigil = pygame.Surface((width, height), pygame.SRCALPHA)
    center = (width // 2, height // 2)
    base_radius = int(min(width, height) * 0.18)
    draw_neon_glow(sigil, (120, 82, 150), center[0], center[1], base_radius + 8, 1)
    pygame.draw.circle(sigil, (132, 94, 164, 22), center, base_radius, 1)
    pygame.draw.circle(sigil, (96, 132, 170, 18), center, int(base_radius * 0.65), 1)
    screen.blit(sigil, (0, 0))

    scan = pygame.Surface((width, height), pygame.SRCALPHA)
    for y in range(0, height, 3):
        alpha = 14 if (y // 3) % 2 == 0 else 8
        pygame.draw.line(scan, (0, 0, 0, alpha), (0, y), (width, y), 1)
    screen.blit(scan, (0, 0))

    vignette = pygame.Surface((width, height), pygame.SRCALPHA)
    edge = int(min(width, height) * 0.12)
    for i in range(edge):
        alpha = int(96 * (1.0 - (i / max(1, edge))))
        pygame.draw.rect(vignette, (0, 0, 0, alpha), (i, i, width - i * 2, height - i * 2), 1)
    screen.blit(vignette, (0, 0))


def _brighten(color: tuple[int, int, int], gain: float = 1.15, bias: int = 12) -> tuple[int, int, int]:
    return (
        min(255, int(color[0] * gain) + bias),
        min(255, int(color[1] * gain) + bias),
        min(255, int(color[2] * gain) + bias),
    )


def _darken(color: tuple[int, int, int], amount: int = 48) -> tuple[int, int, int]:
    return (max(0, color[0] - amount), max(0, color[1] - amount), max(0, color[2] - amount))


class LabyrinthFloorTileRenderStrategy:
    def __init__(
        self,
        width: float,
        height: float,
        *,
        base_color: tuple[int, int, int],
        edge_color: tuple[int, int, int],
    ) -> None:
        self.width = width
        self.height = height
        self.base_color = base_color
        self.edge_color = edge_color

    def render(self, screen: pygame.Surface, entity, transform) -> None:
        del entity
        rect = pygame.Rect(
            round(transform.position.x - self.width * 0.5),
            round(transform.position.y - self.height * 0.5),
            max(1, round(self.width)),
            max(1, round(self.height)),
        )
        tile_surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        tile_surface.fill((*self.base_color, 210))
        pygame.draw.rect(tile_surface, (*self.edge_color, 120), tile_surface.get_rect(), width=1)
        screen.blit(tile_surface, rect.topleft)


class BossArenaFloorTileRenderStrategy:
    def __init__(
        self,
        width: float,
        height: float,
        *,
        base_color: tuple[int, int, int],
        grid_color: tuple[int, int, int],
        rune_color: tuple[int, int, int],
        checker_variant: bool,
    ) -> None:
        self.width = width
        self.height = height
        self.base_color = base_color
        self.grid_color = grid_color
        self.rune_color = rune_color
        self.checker_variant = checker_variant

    def render(self, screen: pygame.Surface, entity, transform) -> None:
        del entity
        rect = pygame.Rect(
            round(transform.position.x - self.width * 0.5),
            round(transform.position.y - self.height * 0.5),
            max(1, round(self.width)),
            max(1, round(self.height)),
        )
        tile_surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        tile_surface.fill((*self.base_color, 96))

        step = 10
        for x in range(0, rect.width, step):
            pygame.draw.line(tile_surface, (*self.grid_color, 6), (x, 0), (x, rect.height), 1)
        for y in range(0, rect.height, step):
            pygame.draw.line(tile_surface, (*self.grid_color, 5), (0, y), (rect.width, y), 1)

        pulse = 0.5 + 0.5 * math.sin((time.time() * 3.6) + (transform.position.x * 0.02) + (transform.position.y * 0.02))
        rune_alpha = int(12 + pulse * 16)
        cx = rect.width // 2
        cy = rect.height // 2
        rune_radius = max(3, min(rect.width, rect.height) // 4)
        pygame.draw.circle(tile_surface, (*self.rune_color, rune_alpha), (cx, cy), rune_radius, 1)

        if self.checker_variant:
            pygame.draw.line(tile_surface, (*self.rune_color, rune_alpha), (cx - rune_radius, cy), (cx + rune_radius, cy), 1)
            pygame.draw.line(tile_surface, (*self.rune_color, rune_alpha), (cx, cy - rune_radius), (cx, cy + rune_radius), 1)
        else:
            pygame.draw.line(
                tile_surface,
                (*self.rune_color, rune_alpha),
                (cx - rune_radius, cy - rune_radius),
                (cx + rune_radius, cy + rune_radius),
                1,
            )
            pygame.draw.line(
                tile_surface,
                (*self.rune_color, rune_alpha),
                (cx + rune_radius, cy - rune_radius),
                (cx - rune_radius, cy + rune_radius),
                1,
            )

        pygame.draw.rect(tile_surface, (*self.grid_color, 26), tile_surface.get_rect(), width=1)
        screen.blit(tile_surface, rect.topleft)


class LabyrinthWallRenderStrategy:
    def __init__(
        self,
        width: float,
        height: float,
        *,
        outline_color: tuple[int, int, int],
        fill_color: tuple[int, int, int],
        edge_color: tuple[int, int, int],
        edge_thickness: int = 2,
    ) -> None:
        self.width = width
        self.height = height
        self.outline_color = outline_color
        self.fill_color = fill_color
        self.shadow_color = _darken(fill_color, amount=64)
        self.highlight_color = _brighten(fill_color, gain=1.12, bias=18)
        self.edge_color = edge_color
        self.edge_thickness = max(1, int(edge_thickness))
        self.restrowave_low = (44, 208, 255)
        self.restrowave_high = (255, 92, 178)
        self.restrowave_grid = (120, 246, 255)

    def render(self, screen: pygame.Surface, entity, transform) -> None:
        del entity
        rect = pygame.Rect(
            round(transform.position.x - self.width * 0.5),
            round(transform.position.y - self.height * 0.5),
            max(1, round(self.width)),
            max(1, round(self.height)),
        )

        pygame.draw.rect(screen, self.outline_color, rect)
        inner_rect = rect.inflate(-2, -2)
        if inner_rect.width > 0 and inner_rect.height > 0:
            pygame.draw.rect(screen, self.fill_color, inner_rect)
        else:
            pygame.draw.rect(screen, self.fill_color, rect)

        shade_rect = inner_rect if inner_rect.width > 0 and inner_rect.height > 0 else rect
        if shade_rect.width >= 3 and shade_rect.height >= 3:
            shadow_strip = pygame.Rect(shade_rect.left + 1, shade_rect.bottom - 2, max(1, shade_rect.width - 2), 1)
            side_shadow = pygame.Rect(shade_rect.right - 2, shade_rect.top + 1, 1, max(1, shade_rect.height - 2))
            pygame.draw.rect(screen, self.shadow_color, shadow_strip)
            pygame.draw.rect(screen, self.shadow_color, side_shadow)

            top_highlight = pygame.Rect(shade_rect.left + 1, shade_rect.top + 1, max(1, shade_rect.width - 2), 1)
            left_highlight = pygame.Rect(shade_rect.left + 1, shade_rect.top + 1, 1, max(1, shade_rect.height - 2))
            pygame.draw.rect(screen, self.highlight_color, top_highlight)
            pygame.draw.rect(screen, self.highlight_color, left_highlight)

        border_width = min(self.edge_thickness, max(1, rect.width // 2), max(1, rect.height // 2))
        pygame.draw.rect(screen, self.edge_color, rect.inflate(-2, -2), width=border_width)

        if rect.width >= 3 and rect.height >= 3:
            wave_surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
            height = max(1, rect.height - 1)
            for y in range(rect.height):
                ratio = y / height
                red = int((self.restrowave_low[0] * (1.0 - ratio)) + (self.restrowave_high[0] * ratio))
                green = int((self.restrowave_low[1] * (1.0 - ratio)) + (self.restrowave_high[1] * ratio))
                blue = int((self.restrowave_low[2] * (1.0 - ratio)) + (self.restrowave_high[2] * ratio))
                alpha = 40 if y % 2 == 0 else 24
                pygame.draw.line(wave_surface, (red, green, blue, alpha), (0, y), (rect.width, y), 1)

            for x in range(0, rect.width, 6):
                pygame.draw.line(
                    wave_surface,
                    (*self.restrowave_grid, 24),
                    (x, 0),
                    (x, rect.height),
                    1,
                )

            drift = int((time.time() * 18.0) % 12)
            for x in range(-rect.height, rect.width + rect.height, 12):
                start = (x + drift, rect.height - 1)
                end = (x + rect.height + drift, 0)
                pygame.draw.line(wave_surface, (255, 166, 240, 20), start, end, 1)

            band_y = int((time.time() * 44.0) % max(1, rect.height))
            pygame.draw.line(
                wave_surface,
                (255, 230, 255, 70),
                (1, band_y),
                (max(1, rect.width - 2), band_y),
                1,
            )
            screen.blit(wave_surface, rect.topleft)


class LabyrinthKeyRenderStrategy:
    def __init__(self, color: tuple[int, int, int], radius: float) -> None:
        self.color = color
        self.radius = radius
        self.outline = _darken(color, 90)
        self.glint = _brighten(color, gain=1.2, bias=28)

    def render(self, screen: pygame.Surface, entity, transform) -> None:
        del entity
        now = time.time()
        pulse = 0.5 + 0.5 * math.sin(now * 7.0)
        center = (int(transform.position.x), int(transform.position.y))
        radius = max(4, int(self.radius + pulse * 2.2))

        draw_neon_glow(screen, self.color, center[0], center[1], radius + 6, 3)

        outer = [
            (center[0], center[1] - radius - 3),
            (center[0] + radius + 2, center[1]),
            (center[0], center[1] + radius + 3),
            (center[0] - radius - 2, center[1]),
        ]
        inner = [
            (center[0], center[1] - radius),
            (center[0] + radius - 1, center[1]),
            (center[0], center[1] + radius),
            (center[0] - radius + 1, center[1]),
        ]
        pygame.draw.polygon(screen, self.outline, outer)
        pygame.draw.polygon(screen, self.color, inner)
        pygame.draw.circle(screen, self.glint, center, max(1, int(radius * 0.28)))


class LabyrinthExitRenderStrategy:
    def __init__(self, locked_color: tuple[int, int, int], unlocked_color: tuple[int, int, int], size: float) -> None:
        self.locked_color = locked_color
        self.unlocked_color = unlocked_color
        self.size = size

    def render(self, screen: pygame.Surface, entity, transform) -> None:
        from game.components.data_components import LabyrinthExitComponent

        exit_component = entity.get_component(LabyrinthExitComponent)
        is_unlocked = exit_component is not None and exit_component.unlocked
        base_color = self.unlocked_color if is_unlocked else self.locked_color
        edge_color = _brighten(base_color, gain=1.1, bias=20)
        shadow_color = _darken(base_color, amount=70)

        center = (int(transform.position.x), int(transform.position.y))
        half = max(8, int(self.size * 0.5))
        rect = pygame.Rect(center[0] - half, center[1] - half, half * 2, half * 2)

        draw_neon_glow(screen, base_color, center[0], center[1], half + 4, 3)
        pygame.draw.rect(screen, shadow_color, rect)
        pygame.draw.rect(screen, base_color, rect.inflate(-4, -4))
        pygame.draw.rect(screen, edge_color, rect, width=2)

        if is_unlocked:
            check_a = (rect.left + half // 3, rect.centery)
            check_b = (rect.left + half // 2, rect.bottom - half // 3)
            check_c = (rect.right - half // 4, rect.top + half // 3)
            pygame.draw.line(screen, (236, 255, 244), check_a, check_b, 3)
            pygame.draw.line(screen, (236, 255, 244), check_b, check_c, 3)
        else:
            lock_rect = pygame.Rect(0, 0, half // 2, half // 2)
            lock_rect.center = center
            pygame.draw.rect(screen, (238, 242, 248), lock_rect, border_radius=2)
            shackle_rect = pygame.Rect(lock_rect.left + 2, lock_rect.top - 5, lock_rect.width - 4, 6)
            pygame.draw.arc(screen, (238, 242, 248), shackle_rect, math.pi, 0.0, 2)


class LabyrinthVirusRenderStrategy:
    def __init__(self, body_color: tuple[int, int, int], core_color: tuple[int, int, int], radius: float) -> None:
        self.body_color = body_color
        self.core_color = core_color
        self.radius = radius
        self.shadow_color = _darken(body_color, amount=78)
        self.highlight_color = _brighten(body_color, gain=1.1, bias=16)
        self.glitch_color = _brighten(body_color, gain=1.25, bias=32)

    def render(self, screen: pygame.Surface, entity, transform) -> None:
        now = time.time()
        phase = (entity.id % 19) * 0.41
        pulse = 0.5 + 0.5 * math.sin((now * 8.0) + phase)

        center = (int(transform.position.x), int(transform.position.y))
        radius = max(4, int(self.radius + pulse * 1.3))
        draw_neon_glow(screen, self.body_color, center[0], center[1], radius + 5, 3)

        body_ring = max(1, int(radius * 0.35))
        pygame.draw.circle(screen, self.shadow_color, center, radius + 2)
        pygame.draw.circle(screen, self.body_color, center, radius)
        pygame.draw.circle(screen, self.highlight_color, center, max(2, radius - 3), 1)

        # Nucleo infeccioso pulsante.
        core_radius = max(2, int(radius * (0.3 + pulse * 0.18)))
        pygame.draw.circle(screen, self.core_color, center, core_radius)
        pygame.draw.circle(screen, (255, 255, 255), center, max(1, core_radius // 2))

        # Ghost offsets para leitura de glitch sem perder hitbox visual.
        ghost_dx = int(math.sin((now * 14.0) + phase) * 2.0)
        ghost_dy = int(math.cos((now * 11.0) + phase) * 2.0)
        pygame.draw.circle(screen, (*self.glitch_color, 120), (center[0] + ghost_dx, center[1] + ghost_dy), body_ring, 1)
        pygame.draw.circle(screen, (*self.glitch_color, 100), (center[0] - ghost_dx, center[1] - ghost_dy), body_ring, 1)

        # Scanlines e cortes digitais.
        for index in range(3):
            y = center[1] - radius + 2 + (index * max(2, radius // 2))
            x_jitter = int(math.sin((now * 19.0) + phase + index) * 3.0)
            start = (center[0] - radius + x_jitter, y)
            end = (center[0] + radius - x_jitter, y)
            pygame.draw.line(screen, self.glitch_color, start, end, 1)

        # Particulas orbitais para identidade de "virus digital".
        orbit = radius + 4.0
        for index in range(4):
            angle = (now * 3.4) + phase + (index * (math.pi * 0.5))
            px = int(center[0] + math.cos(angle) * orbit)
            py = int(center[1] + math.sin(angle) * orbit)
            pygame.draw.circle(screen, self.core_color, (px, py), 1)

        eye_y = center[1] - max(1, radius // 5)
        eye_offset = max(2, radius // 3)
        pygame.draw.rect(screen, (244, 248, 255), pygame.Rect(center[0] - eye_offset - 1, eye_y, 2, 2))
        pygame.draw.rect(screen, (244, 248, 255), pygame.Rect(center[0] + eye_offset - 1, eye_y, 2, 2))
