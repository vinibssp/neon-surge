import pygame
from ..constants import DASH_SPEED, DASH_DURATION, DASH_COOLDOWN


class DashAbility:
    """Space-bar dash — brief invincibility window in the direction of movement.

    Swap this for ShieldAbility, TeleportAbility, etc. without touching Player.
    """

    def __init__(self) -> None:
        self._cooldown     = 0
        self._active_timer = 0

    @property
    def ready(self) -> bool:
        return self._cooldown <= 0

    @property
    def active(self) -> bool:
        return self._active_timer > 0

    @property
    def progress(self) -> float:
        """0.0 = full cooldown, 1.0 = ready to dash."""
        return 1.0 - (self._cooldown / DASH_COOLDOWN)

    def try_activate(self, vel: pygame.math.Vector2) -> bool:
        """Attempt activation. Modifies vel in-place. Returns True if triggered."""
        if self.ready and vel.length() > 0:
            vel.update(vel.normalize() * DASH_SPEED)
            self._active_timer = DASH_DURATION
            self._cooldown     = DASH_COOLDOWN
            return True
        return False

    def update(self) -> None:
        if self._active_timer > 0:
            self._active_timer -= 1
        if self._cooldown > 0:
            self._cooldown -= 1
