from ..constants import ENEMY_BASE_SPEED


class SpawnSystem:
    """Interval-based enemy spawner for survival modes.

    Speed scales linearly with elapsed time up to a configured cap.
    Config is injected at construction so the same class serves both
    SOBREVIVENCIA and HARDCORE without subclassing.
    """

    def __init__(self, interval: float, max_speed: float, speed_growth: float) -> None:
        self.interval     = interval
        self.max_speed    = max_speed
        self.speed_growth = speed_growth
        self._timer       = 0.0

    def update(self, dt: float) -> int:
        """Returns the number of enemies to spawn this tick (0 or 1)."""
        self._timer += dt
        if self._timer >= self.interval:
            self._timer = 0.0
            return 1
        return 0

    def current_speed(self, elapsed: float) -> float:
        return min(self.max_speed, ENEMY_BASE_SPEED + elapsed * self.speed_growth)

    def reset(self) -> None:
        self._timer = 0.0
