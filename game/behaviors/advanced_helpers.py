from __future__ import annotations

from pygame import Vector2


def normalized(vector: Vector2, fallback: Vector2 | None = None) -> Vector2:
    if vector.length_squared() <= 0:
        return Vector2(1, 0) if fallback is None else Vector2(fallback)
    return vector.normalize()


def smoothing_factor(responsiveness: float, dt: float) -> float:
    return max(0.0, min(1.0, responsiveness * 60.0 * dt))


def predict_intercept_position(
    origin: Vector2,
    target_position: Vector2,
    target_velocity: Vector2,
    projectile_speed: float,
    max_lead_time: float = 0.9,
) -> Vector2:
    if projectile_speed <= 0.0:
        return Vector2(target_position)
    distance = (target_position - origin).length()
    lead_time = min(max_lead_time, distance / max(1.0, projectile_speed))
    return target_position + (target_velocity * lead_time)


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
