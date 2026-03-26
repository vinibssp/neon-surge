from __future__ import annotations

import math
import random
from dataclasses import dataclass

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
    def __init__(self, font_size: int = 24, color: tuple[int, int, int] = (238, 242, 250)) -> None:
        self.font = pygame.font.Font(None, font_size)
        self.color = color
        self.panel_fill = (10, 16, 28, 150)
        self.panel_border = (92, 162, 218, 190)
        self.padding_x = 12
        self.padding_y = 10
        self.gap = 6

    def render_lines(self, screen: pygame.Surface, lines: list[str], x: int = 16, y: int = 12, line_height: int | None = None) -> None:
        visible_lines = [line for line in lines if line.strip()]
        if not visible_lines:
            return

        effective_line_height = line_height if line_height is not None else (self.font.get_height() + self.gap)
        rendered = [self.font.render(line, True, self.color) for line in visible_lines]
        panel_width = max(surface.get_width() for surface in rendered) + self.padding_x * 2
        panel_height = (
            self.padding_y * 2
            + (len(rendered) * self.font.get_height())
            + (max(0, len(rendered) - 1) * (effective_line_height - self.font.get_height()))
        )

        panel = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        pygame.draw.rect(panel, self.panel_fill, panel.get_rect(), border_radius=10)
        pygame.draw.rect(panel, self.panel_border, panel.get_rect(), width=1, border_radius=10)
        screen.blit(panel, (x, y))

        current_y = y + self.padding_y
        text_x = x + self.padding_x
        for surface in rendered:
            screen.blit(surface, (text_x, current_y))
            current_y += effective_line_height

    def render_boss_card(
        self,
        screen: pygame.Surface,
        card: BossHudCard,
        x: int = 16,
        y: int = 118,
        align_right: bool = False,
        right_margin: int = 16,
    ) -> None:
        name_surface = self.font.render(card.boss_name, True, self.color)
        card_width = name_surface.get_width() + self.padding_x * 2
        card_height = self.padding_y * 2 + name_surface.get_height()
        card_x = screen.get_width() - card_width - right_margin if align_right else x

        panel = pygame.Surface((card_width, card_height), pygame.SRCALPHA)
        pygame.draw.rect(panel, card.fill_color, panel.get_rect(), border_radius=10)
        pygame.draw.rect(panel, card.border_color, panel.get_rect(), width=2, border_radius=10)
        screen.blit(panel, (card_x, y))

        text_x = card_x + self.padding_x
        current_y = y + self.padding_y
        screen.blit(name_surface, (text_x, current_y))

    def boss_card_height(self) -> int:
        return self.padding_y * 2 + self.font.get_height()


@dataclass(frozen=True)
class BossHudCard:
    boss_name: str
    fill_color: tuple[int, int, int, int] = (24, 8, 14, 176)
    border_color: tuple[int, int, int, int] = (252, 94, 128, 220)


class CyberpunkMenuBackgroundRenderer:
    def __init__(self, neon_color: tuple[int, int, int] = ENEMY_BOUNCER_COLOR) -> None:
        self.neon_color = neon_color
        self._rng = random.Random()
        self._star_layout_size: tuple[int, int] | None = None
        self._stars: list[tuple[int, int, float, float, int]] = []
        self._shooting_stars: list[dict[str, float]] = []
        self._next_shooting_star_time = 0.0
        self._last_elapsed_time = 0.0

    def _ensure_star_layout(self, width: int, sky_height: int) -> None:
        target_size = (width, sky_height)
        if self._star_layout_size == target_size and self._stars:
            return

        self._star_layout_size = target_size
        self._stars = []
        cell_size = max(44, int(min(width, sky_height) * 0.06))
        columns = max(1, width // cell_size)
        rows = max(1, sky_height // cell_size)
        for row in range(rows):
            for column in range(columns):
                if self._rng.random() > 0.82:
                    continue
                origin_x = column * cell_size
                origin_y = row * cell_size
                jitter_x = self._rng.randint(int(cell_size * 0.18), int(cell_size * 0.82))
                jitter_y = self._rng.randint(int(cell_size * 0.18), int(cell_size * 0.82))
                star_x = min(width - 1, max(0, origin_x + jitter_x))
                star_y = min(sky_height - 1, max(0, origin_y + jitter_y))
                twinkle_phase = self._rng.uniform(0.0, math.tau)
                twinkle_speed = self._rng.uniform(1.2, 2.9)
                radius = 2 if self._rng.random() < 0.2 else 1
                self._stars.append((star_x, star_y, twinkle_phase, twinkle_speed, radius))

    def _spawn_shooting_star(self, elapsed_time: float, width: int, sky_height: int) -> None:
        start_x = self._rng.uniform(-0.12 * width, 0.72 * width)
        start_y = self._rng.uniform(0.03 * sky_height, 0.46 * sky_height)
        angle = self._rng.uniform(math.radians(20), math.radians(34))
        speed = self._rng.uniform(460.0, 760.0)
        lifetime = self._rng.uniform(0.42, 0.9)
        self._shooting_stars.append(
            {
                "start_time": elapsed_time,
                "start_x": start_x,
                "start_y": start_y,
                "velocity_x": math.cos(angle) * speed,
                "velocity_y": math.sin(angle) * speed,
                "lifetime": lifetime,
            }
        )

    def render(
        self,
        screen: pygame.Surface,
        elapsed_time: float,
        width: int,
        height: int,
        sun_rise_progress: float | None = None,
        sun_center_text: str | None = None,
    ) -> None:
        if elapsed_time < self._last_elapsed_time:
            self._shooting_stars.clear()
            self._next_shooting_star_time = elapsed_time + self._rng.uniform(1.8, 4.6)
        self._last_elapsed_time = elapsed_time

        horizon_y = int(height * 0.6)
        center_x = width // 2

        # 1. SKY GRADIENT (Enhanced)
        for y in range(height):
            t = y / max(1, height)
            if y <= horizon_y:
                # Deep space purple to horizon orange/pink
                red = int(10 + (180 * (y / horizon_y)**3.5))
                green = int(5 + (40 * (y / horizon_y)**4.0))
                blue = int(25 + (15 * (y / horizon_y)))
            else:
                # Dark ground
                t2 = (y - horizon_y) / max(1, (height - horizon_y))
                red = int(15 + (10 * t2))
                green = int(5 + (5 * t2))
                blue = int(25 + (20 * t2))
            pygame.draw.line(screen, (min(255, red), min(255, green), min(255, blue)), (0, y), (width, y))

        # 2. STARS (Twinkling)
        sky_height = max(1, int(horizon_y * 0.9))
        self._ensure_star_layout(width, sky_height)
        for star_x, star_y, twinkle_phase, twinkle_speed, radius in self._stars:
            twinkle = 0.45 + 0.55 * (0.5 + 0.5 * math.sin(elapsed_time * twinkle_speed + twinkle_phase))
            base = int(110 + 135 * twinkle)
            color = (min(255, base), min(255, base + 12), 255)
            if radius <= 1:
                screen.set_at((star_x, star_y), color)
            else:
                pygame.draw.circle(screen, color, (star_x, star_y), radius)

        # 3. SEGMENTED SYNTHWAVE SUN
        sun_radius = int(min(width, height) * 0.18)
        rise_progress = max(0.0, min(1.0, sun_rise_progress)) if sun_rise_progress is not None else 1.0
        sun_start_y = int(horizon_y + sun_radius)
        sun_end_y = int(horizon_y * 0.75)
        sun_center_y = int(sun_start_y + (sun_end_y - sun_start_y) * rise_progress)
        
        # Sun Glow
        sun_glow = pygame.Surface((width, height), pygame.SRCALPHA)
        pulse = 0.9 + 0.1 * math.sin(elapsed_time * 1.5)
        for multiplier, alpha in ((2.5, 12), (1.8, 22), (1.3, 45)):
            pygame.draw.circle(sun_glow, (255, 20, 147, int(alpha * pulse)), (center_x, sun_center_y), int(sun_radius * multiplier))
        screen.blit(sun_glow, (0, 0))

        # Draw sun segments
        sun_surf = pygame.Surface((sun_radius * 2, sun_radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(sun_surf, (255, 20, 147), (sun_radius, sun_radius), sun_radius)
        # Inner core glow
        pygame.draw.circle(sun_surf, (255, 215, 0), (sun_radius, sun_radius), int(sun_radius * 0.8))
        
        # Cut segments (the classic synthwave lines)
        for i in range(1, 12):
            line_y = int(sun_radius * 2 * (i / 12))
            thickness = int(2 + (i * 1.2)) # Thicker lines at the bottom
            pygame.draw.rect(sun_surf, (0, 0, 0, 0), (0, line_y, sun_radius * 2, thickness))
        
        screen.blit(sun_surf, (center_x - sun_radius, sun_center_y - sun_radius), special_flags=pygame.BLEND_RGBA_ADD)

        # 4. MOUNTAINS (Retro-Silicon)
        mountain_points = []
        for x in range(-100, width + 101, 60):
            base = horizon_y
            # Fractal-like peaks
            peak = (40 if (x // 60) % 2 == 0 else 70) + (20 * math.sin(x * 0.05))
            y = int(base - peak)
            mountain_points.append((x, y))

        mountain_polygon = list(mountain_points)
        mountain_polygon.append((width + 100, height))
        mountain_polygon.append((-100, height))
        pygame.draw.polygon(screen, (15, 0, 30), mountain_polygon)
        # Mountain outlines
        for i in range(1, len(mountain_points)):
            pygame.draw.line(screen, (255, 0, 255, 180), mountain_points[i-1], mountain_points[i], 2)

        # 5. HORIZON LINE
        pygame.draw.line(screen, (0, 255, 255), (0, horizon_y), (width, horizon_y), 3)

        # 6. PERSPECTIVE GRID
        grid_surf = pygame.Surface((width, height - horizon_y), pygame.SRCALPHA)
        grid_h = height - horizon_y
        shift = (elapsed_time * 120) % 40
        
        # Horizontal lines
        for y in range(0, grid_h + 40, 40):
            ly = y + shift
            if ly > grid_h: continue
            alpha = int(255 * (ly / grid_h)) # Fade out near horizon
            pygame.draw.line(grid_surf, (0, 255, 255, alpha), (0, ly), (width, ly), 1)
            
        # Vertical vanishing lines
        for i in range(-15, 16):
            x_start = width // 2 + i * 40
            x_end = width // 2 + i * 250
            pygame.draw.line(grid_surf, (0, 255, 255, 100), (x_start, 0), (x_end, grid_h), 1)
        
        screen.blit(grid_surf, (0, horizon_y))

        # 7. SCANLINES & VIGNETTE
        scanline = pygame.Surface((width, height), pygame.SRCALPHA)
        for y in range(0, height, 4):
            pygame.draw.line(scanline, (0, 0, 0, 40), (0, y), (width, y))
        screen.blit(scanline, (0, 0))

        vignette = pygame.Surface((width, height), pygame.SRCALPHA)
        margin = int(min(width, height) * 0.07)
        pygame.draw.rect(vignette, (0, 0, 0, 0), (margin, margin, width - margin * 2, height - margin * 2))
        for index in range(margin):
            alpha = int(120 * (1 - (index / max(1, margin))))
            pygame.draw.rect(vignette, (0, 0, 0, alpha), (index, index, width - index * 2, height - index * 2), 1)
        screen.blit(vignette, (0, 0))
