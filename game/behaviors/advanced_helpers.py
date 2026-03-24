from __future__ import annotations

from pygame import Vector2


def normalized(vector: Vector2, fallback: Vector2 | None = None) -> Vector2:
    if vector.length_squared() <= 0:
        return Vector2(1, 0) if fallback is None else Vector2(fallback)
    return vector.normalize()


def shoot_radial(
    world: "GameWorld",
    origin: Vector2,
    speed: float,
    radius: float,
    step_degrees: int,
    color: tuple[int, int, int],
) -> None:
    for angle in range(0, 360, step_degrees):
        direction = Vector2(1, 0).rotate(angle)
        world.spawn_enemy_bullet(origin, direction, speed, radius, color=color)


from game.core.world import GameWorld
