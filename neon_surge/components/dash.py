import pygame


class DashAbility:
    """Space-bar dash — brief invincibility window in the direction of movement."""

    def __init__(self, speed: float, duration: int, cooldown: int) -> None:
        self.speed = speed
        self.duration = duration
        self.cooldown_max = cooldown
        self._cooldown = 0
        self._active_timer = 0
        self._extra_invuln_timer = 0

    @property
    def ready(self) -> bool:
        return self._cooldown <= 0

    @property
    def active(self) -> bool:
        return self._active_timer > 0

    @property
    def invulnerable(self) -> bool:
        return self._active_timer > 0 or self._extra_invuln_timer > 0

    @property
    def progress(self) -> float:
        """0.0 = full cooldown, 1.0 = ready to dash."""
        if self.cooldown_max == 0: return 1.0
        return 1.0 - (self._cooldown / self.cooldown_max)

    def try_activate(self, vel: pygame.math.Vector2, direction: pygame.math.Vector2) -> bool:
        """Attempt activation. Modifies vel in-place. Returns True if triggered."""
        if self.ready:
            vel.update(direction * self.speed)
            self._active_timer = self.duration
            self._cooldown = self.cooldown_max
            return True
        return False

    def update(self) -> None:
        if self._active_timer > 0:
            self._active_timer -= 1
            if self._active_timer == 0:
                self._extra_invuln_timer = 14
        elif self._extra_invuln_timer > 0:
            self._extra_invuln_timer -= 1

        if self._cooldown > 0:
            self._cooldown -= 1
