import pygame

from ..constants import (
    PLAYER_ACCEL, PLAYER_FRICTION, PLAYER_SIZE,
    SCREEN_W, SCREEN_H, HUD_H,
    C_WHITE, C_NEON_CYN,
)
from ..utils       import draw_neon_glow
from ..components  import (
    TransformComponent, PhysicsComponent,
    ColliderComponent,  DashAbility, ParticleEmitter,
)


class Player:
    """
    Player-controlled ship.

    Composition
    -----------
    TransformComponent  pos / vel
    PhysicsComponent    acceleration + friction + clamping
    ColliderComponent   circle hitbox
    DashAbility         space-bar invincibility dash
    ParticleEmitter     trail during dash
    """

    def __init__(self, x: float, y: float) -> None:
        self.transform = TransformComponent(x, y)
        self.physics   = PhysicsComponent(PLAYER_ACCEL, PLAYER_FRICTION)
        self.collider  = ColliderComponent(PLAYER_SIZE // 2)
        self.dash      = DashAbility()
        self.emitter   = ParticleEmitter(C_NEON_CYN)
        self.size      = PLAYER_SIZE

    # ── shortcuts ─────────────────────────────────────────────────────────────
    @property
    def pos(self) -> pygame.math.Vector2:
        return self.transform.pos

    @property
    def invincible(self) -> bool:
        return self.dash.active

    # ── update ────────────────────────────────────────────────────────────────
    def update(self, keys, particle_pool: list, sound_manager) -> bool:
        """Returns True the frame a dash fires (lets Level trigger screen-shake)."""
        dx = dy = 0
        if keys[pygame.K_w] or keys[pygame.K_UP]:    dy = -1
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:  dy =  1
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:  dx = -1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]: dx =  1
        direction = pygame.math.Vector2(dx, dy)

        if direction.length_squared() > 0:
            sound_manager.start_walking()
        else:
            sound_manager.stop_walking()

        if keys[pygame.K_SPACE] and self.dash.ready and self.transform.vel.length() > 0:
            sound_manager.play('player_dash')
            self.dash.try_activate(self.transform.vel)
            return True

        self.dash.update()
        if self.dash.active:
            self.emitter.burst(self.pos.x, self.pos.y, particle_pool, 3)

        bx = (self.size, SCREEN_W - self.size)
        by = (HUD_H + self.size, SCREEN_H - self.size)
        self.physics.apply(self.transform, direction, bx, by)
        return False

    # ── draw ──────────────────────────────────────────────────────────────────
    def draw(self, surf) -> None:
        color = C_WHITE if self.invincible else C_NEON_CYN
        draw_neon_glow(surf, color, self.pos.x, self.pos.y, self.size // 2, 4)
        rect = pygame.Rect(0, 0, self.size, self.size)
        rect.center = (int(self.pos.x), int(self.pos.y))
        pygame.draw.rect(surf, color,   rect, border_radius=4)
        pygame.draw.rect(surf, C_WHITE, rect.inflate(-6, -6), border_radius=2)
