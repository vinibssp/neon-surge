from __future__ import annotations

import math

import pygame
from game.config import (
    ENEMY_BOUNCER_COLOR,
    GAME_GRID_COLOR,
    GAME_GRID_STEP,
    MENU_MOUNTAIN_FILL_COLOR,
)


class BackgroundRenderer:
    def __init__(self, grid_color: tuple[int, int, int] = GAME_GRID_COLOR, grid_step: int = GAME_GRID_STEP) -> None:
        self.grid_color = grid_color
        self.grid_step = grid_step
        self._time = 0.0

    def render(self, screen: pygame.Surface, width: int, height: int) -> None:
        self._time += 1.0 / 60.0
        center_x = width * 0.5
        center_y = height * 0.5

        for y in range(height):
            t = y / max(1, height)
            pulse = 0.5 + 0.5 * math.sin(self._time * 0.7 + t * 4.2)
            red = int(6 + (12 * t) + pulse * 3)
            green = int(8 + (16 * t) + pulse * 4)
            blue = int(16 + (34 * t) + pulse * 7)
            pygame.draw.line(screen, (red, green, blue), (0, y), (width, y))

        scroll_x = int((self._time * 20.0) % self.grid_step)
        scroll_y = int((self._time * 11.0) % self.grid_step)
        grid = pygame.Surface((width, height), pygame.SRCALPHA)
        vertical_color = (self.grid_color[0] + 20, self.grid_color[1] + 42, self.grid_color[2] + 62, 44)
        horizontal_color = (self.grid_color[0] + 14, self.grid_color[1] + 28, self.grid_color[2] + 44, 36)

        for x in range(-self.grid_step, width + self.grid_step, self.grid_step):
            line_x = x + scroll_x
            pygame.draw.line(grid, vertical_color, (line_x, 0), (line_x, height), 1)

        for y in range(-self.grid_step, height + self.grid_step, self.grid_step):
            line_y = y + scroll_y
            pygame.draw.line(grid, horizontal_color, (0, line_y), (width, line_y), 1)
        screen.blit(grid, (0, 0))

        scan = pygame.Surface((width, height), pygame.SRCALPHA)
        for y in range(0, height, 4):
            scan_alpha = 12 if (y // 4) % 2 == 0 else 6
            pygame.draw.line(scan, (8, 16, 28, scan_alpha), (0, y), (width, y), 1)
        screen.blit(scan, (0, 0))

        stars = 84
        sky = pygame.Surface((width, height), pygame.SRCALPHA)
        for i in range(stars):
            px = int((i * 173 + self._time * (7 + (i % 5) * 2.5)) % width)
            py = int((i * 97 + (i % 11) * 13) % height)
            dx = px - center_x
            dy = py - center_y
            distance_ratio = min(1.0, math.sqrt(dx * dx + dy * dy) / (min(width, height) * 0.52))
            center_fade = 0.35 + 0.65 * distance_ratio
            twinkle = 65 + int(120 * (0.5 + 0.5 * math.sin(self._time * 3.1 + i * 0.63)))
            alpha = int(min(180, twinkle) * center_fade)
            sky.set_at((px, py), (132, 208, 245, alpha))
        screen.blit(sky, (0, 0))

        vignette = pygame.Surface((width, height), pygame.SRCALPHA)
        margin = int(min(width, height) * 0.09)
        for i in range(max(1, margin)):
            alpha = int(110 * (1.0 - i / max(1, margin)))
            pygame.draw.rect(vignette, (0, 0, 0, alpha), (i, i, width - i * 2, height - i * 2), 1)
        screen.blit(vignette, (0, 0))


class HudRenderer:
    def __init__(self, font_size: int = 32, color: tuple[int, int, int] = (240, 240, 245)) -> None:
        self.font = pygame.font.Font(None, font_size)
        self.color = color

    def render_lines(self, screen: pygame.Surface, lines: list[str], x: int = 16, y: int = 12, line_height: int = 24) -> None:
        current_y = y
        for line in lines:
            surface = self.font.render(line, True, self.color)
            screen.blit(surface, (x, current_y))
            current_y += line_height


class CyberpunkMenuBackgroundRenderer:
    def __init__(self, neon_color: tuple[int, int, int] = ENEMY_BOUNCER_COLOR) -> None:
        self.neon_color = neon_color

    def render(self, screen: pygame.Surface, elapsed_time: float, width: int, height: int) -> None:
        horizon_y = int(height * 0.6)
        center_x = width // 2

        for y in range(height):
            t = y / max(1, height)
            if y <= horizon_y:
                red = int(12 + (46 * t))
                green = int(8 + (10 * t))
                blue = int(34 + (90 * t))
            else:
                t2 = (y - horizon_y) / max(1, (height - horizon_y))
                red = int(18 + (16 * t2))
                green = int(4 + (14 * t2))
                blue = int(30 + (56 * t2))
            pygame.draw.line(screen, (red, green, blue), (0, y), (width, y))

        stars = 85
        sky_height = max(1, int(horizon_y * 0.9))
        for index in range(stars):
            x = int((index * 179 + (elapsed_time * (4 + (index % 5)))) % width)
            y = int((index * 97) % sky_height)
            brightness = 140 + int(100 * (0.5 + 0.5 * math.sin((elapsed_time * 2.4) + index)))
            screen.set_at((x, y), (min(255, brightness), min(255, brightness - 15), 255))

        sun_center_x = center_x
        sun_center_y = int(horizon_y * 0.66)
        sun_radius = int(min(width, height) * 0.12)

        sun_glow = pygame.Surface((width, height), pygame.SRCALPHA)
        pulse = 0.86 + 0.14 * math.sin(elapsed_time * 1.6)
        for multiplier, alpha in ((2.3, 18), (1.7, 30), (1.25, 55)):
            pygame.draw.circle(
                sun_glow,
                (255, 60, 175, int(alpha * pulse)),
                (sun_center_x, sun_center_y),
                int(sun_radius * multiplier),
            )
        screen.blit(sun_glow, (0, 0))

        pygame.draw.circle(screen, (255, 110, 70), (sun_center_x, sun_center_y), sun_radius)
        pygame.draw.circle(screen, (255, 185, 90), (sun_center_x, sun_center_y - 2), int(sun_radius * 0.72))

        for index in range(8):
            stripe_height = 5 + index * 2
            stripe_y = sun_center_y - sun_radius + 12 + index * int(sun_radius * 0.22)
            pygame.draw.rect(screen, (255, 70, 160), (sun_center_x - sun_radius, stripe_y, sun_radius * 2, stripe_height))

        mountain_points: list[tuple[int, int]] = []
        for x in range(-80, width + 81, 45):
            base = horizon_y - 12
            peak = 28 + (x % 140)
            y = int(base - peak - 14 * math.sin((x * 0.018) + elapsed_time * 0.35))
            mountain_points.append((x, y))

        mountain_fill_color = MENU_MOUNTAIN_FILL_COLOR
        mountain_base_y = horizon_y + 10
        for index in range(1, len(mountain_points)):
            x1, y1 = mountain_points[index - 1]
            x2, y2 = mountain_points[index]
            if x1 == x2:
                continue
            start_x = max(0, min(x1, x2))
            end_x = min(width - 1, max(x1, x2))
            if start_x > end_x:
                continue
            for x in range(start_x, end_x + 1):
                t = (x - x1) / (x2 - x1)
                ridge_y = int(y1 + (y2 - y1) * t)
                pygame.draw.line(screen, mountain_fill_color, (x, mountain_base_y), (x, ridge_y), 1)

        for index in range(1, len(mountain_points)):
            pygame.draw.line(screen, self.neon_color, mountain_points[index - 1], mountain_points[index], 2)

        pygame.draw.line(screen, self.neon_color, (0, horizon_y), (width, horizon_y), 2)

        shift = (elapsed_time * 180) % 38
        for y in range(horizon_y + 12, height + 42, 38):
            line_y = int(y + shift)
            if line_y > height:
                break
            opening = int((line_y - horizon_y) * 2.25)
            pygame.draw.line(
                screen,
                (45, 190, 220),
                (center_x - opening, line_y),
                (center_x + opening, line_y),
                1,
            )

        for index in range(-10, 11):
            x_base = center_x + index * 58
            x_end = int(center_x + index * 122)
            pygame.draw.line(screen, (30, 140, 190), (x_base, horizon_y), (x_end, height), 1)

        scanline = pygame.Surface((width, height), pygame.SRCALPHA)
        for y in range(0, height, 3):
            pygame.draw.line(scanline, (10, 0, 22, 18), (0, y), (width, y))
        screen.blit(scanline, (0, 0))

        vignette = pygame.Surface((width, height), pygame.SRCALPHA)
        margin = int(min(width, height) * 0.07)
        pygame.draw.rect(vignette, (0, 0, 0, 0), (margin, margin, width - margin * 2, height - margin * 2))
        for index in range(margin):
            alpha = int(120 * (1 - (index / max(1, margin))))
            pygame.draw.rect(vignette, (0, 0, 0, alpha), (index, index, width - index * 2, height - index * 2), 1)
        screen.blit(vignette, (0, 0))
