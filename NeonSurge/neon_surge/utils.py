"""
neon_surge/utils.py
===================
Pure drawing helpers — no game state, no classes.
Every function takes a surface and returns nothing (or a Rect).
"""
from __future__ import annotations

import math
import time

import pygame

from .constants import (
    SCREEN_W, SCREEN_H,
    C_BG, C_WHITE, C_BLOOD_RED, C_DARK_GRAY, C_DARK_BLUE,
    C_NEON_GRN, C_NEON_CYN, C_NEON_PNK, C_PANEL,
)


def draw_text(surf, text: str, font, color, x: int, y: int,
              align: str = "centro") -> pygame.Rect:
    img  = font.render(text, True, color)
    rect = img.get_rect()
    if   align == "centro":   rect.center   = (x, y)
    elif align == "esquerda": rect.midleft  = (x, y)
    elif align == "direita":  rect.midright = (x, y)
    surf.blit(img, rect)
    return rect


def draw_neon_glow(surf, color, x: float, y: float, radius: float,
                   intensity: int = 3) -> None:
    for i in range(intensity, 0, -1):
        size = int((radius + i * 4) * 2)
        s    = pygame.Surface((size, size), pygame.SRCALPHA)
        pygame.draw.circle(s, (*color, 15), (size // 2, size // 2), size // 2)
        surf.blit(s, (int(x - radius - i * 4), int(y - radius - i * 4)))


def draw_cyberpunk_bg(surf, t: float) -> None:
    surf.fill(C_BG)
    for x in range(0, SCREEN_W + 100, 100):
        pygame.draw.line(surf, (20, 25, 35), (x, 0), (x, SCREEN_H), 1)
    off = (t * 50) % 100
    for y in range(-100, SCREEN_H + 100, 100):
        pygame.draw.line(surf, (20, 25, 35), (0, y + off), (SCREEN_W, y + off), 1)
    fade = pygame.Surface((SCREEN_W, 300), pygame.SRCALPHA)
    for i in range(300):
        a = int(255 - (i / 300) * 255)
        pygame.draw.line(fade, (*C_BG, a), (0, i), (SCREEN_W, i))
    surf.blit(fade, (0, 0))


def draw_game_grid(surf) -> None:
    for x in range(0, SCREEN_W, 40):
        pygame.draw.line(surf, (15, 20, 25), (x, 0), (x, SCREEN_H), 1)
    for y in range(0, SCREEN_H, 40):
        pygame.draw.line(surf, (15, 20, 25), (0, y), (SCREEN_W, y), 1)


def make_panel(w: int, h: int) -> pygame.Surface:
    s = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.rect(s, C_PANEL,     (0, 0, w, h), border_radius=15)
    pygame.draw.rect(s, C_DARK_GRAY, (0, 0, w, h), 3, border_radius=15)
    return s


def draw_dynamic_button(surf, text: str, font, color, cx: int, cy: int,
                        hovered: bool) -> pygame.Rect:
    label      = f"> {text} <" if hovered else text
    text_color = C_BG if hovered else color
    img        = font.render(label, True, text_color)
    tr         = img.get_rect(center=(cx, cy))
    br         = tr.inflate(80, 40)
    if hovered:
        pulse = math.sin(time.time() * 10) * 3
        br    = br.inflate(pulse, pulse)
        pygame.draw.rect(surf, color,   br, border_radius=8)
        pygame.draw.rect(surf, C_WHITE, br, 2, border_radius=8)
    else:
        pygame.draw.rect(surf, (10, 15, 25), br, border_radius=8)
        pygame.draw.rect(surf, color,        br, 2, border_radius=8)
    surf.blit(img, tr)
    return br


def draw_sound_icon(surf, cx: int, cy: int, muted: bool, color) -> None:
    pts = [
        (cx - 12, cy - 6), (cx - 4, cy - 6), (cx + 6, cy - 14),
        (cx + 6, cy + 14), (cx - 4, cy + 6), (cx - 12, cy + 6),
    ]
    pygame.draw.polygon(surf, color, pts)
    if muted:
        pygame.draw.line(surf, C_BLOOD_RED, (cx + 12, cy - 8), (cx + 24, cy + 8), 3)
        pygame.draw.line(surf, C_BLOOD_RED, (cx + 24, cy - 8), (cx + 12, cy + 8), 3)
    else:
        pygame.draw.arc(surf, color, (cx - 4, cy - 8,  16, 16), -math.pi / 3, math.pi / 3, 2)
        pygame.draw.arc(surf, color, (cx - 4, cy - 14, 28, 28), -math.pi / 4, math.pi / 4, 2)
