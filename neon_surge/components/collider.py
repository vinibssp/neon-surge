import pygame


class ColliderComponent:
    """Circle collider — simple radius-based overlap test."""

    def __init__(self, radius: float) -> None:
        self.radius = radius

    def overlaps(self, my_pos, other_pos, other_radius: float) -> bool:
        return my_pos.distance_to(other_pos) < (self.radius + other_radius)
