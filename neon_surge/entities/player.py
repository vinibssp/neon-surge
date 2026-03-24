import math
import pygame

from ..constants import (
    ALTURA_TELA,
    BRANCO,
    CIANO_NEON,
    LARGURA_TELA,
)
from ..utils import draw_neon_glow
from ..components.transform import TransformComponent
from ..components.physics import PhysicsComponent
from ..components.collider import ColliderComponent
from ..components.dash import DashAbility
from ..components.emitter import ParticleEmitter


class Player:
    def __init__(self, x: float, y: float) -> None:
        # Composition: Use components for core data and logic
        self.transform = TransformComponent(x, y)
        self.physics = PhysicsComponent(accel=1.8, friction=0.82)
        self.collider = ColliderComponent(radius=8)  # size 16 = radius 8
        self.dash = DashAbility(speed=25.0, duration=10, cooldown=45)
        self.emitter = ParticleEmitter(CIANO_NEON)

        # Extra spatial state for input-based movement
        self.ultima_direcao = pygame.math.Vector2(1, 0)

    # --- Shortcuts for legacy code compatibility ---
    @property
    def pos(self) -> pygame.math.Vector2:
        return self.transform.pos

    @pos.setter
    def pos(self, value: pygame.math.Vector2):
        self.transform.pos = value

    @property
    def vel(self) -> pygame.math.Vector2:
        return self.transform.vel

    @vel.setter
    def vel(self, value: pygame.math.Vector2):
        self.transform.vel = value

    @property
    def raio(self) -> float:
        return self.collider.radius

    @property
    def invencivel(self) -> bool:
        return self.dash.invulnerable

    @property
    def dash_timer(self) -> int:
        return self.dash._active_timer

    @property
    def dash_cooldown(self) -> int:
        return self.dash._cooldown

    @property
    def tamanho(self) -> float:
        return self.collider.radius * 2

    def update(self, teclas: pygame.key.ScancodeWrapper, lista_particulas: list, sound_manager) -> bool:
        # 1. Determine movement direction from input
        dir_x, dir_y = 0, 0
        if teclas[pygame.K_w] or teclas[pygame.K_UP]:    dir_y = -1
        if teclas[pygame.K_s] or teclas[pygame.K_DOWN]:  dir_y = 1
        if teclas[pygame.K_a] or teclas[pygame.K_LEFT]:  dir_x = -1
        if teclas[pygame.K_d] or teclas[pygame.K_RIGHT]: dir_x = 1

        move_vec = pygame.math.Vector2(0, 0)
        if dir_x != 0 or dir_y != 0:
            move_vec = pygame.math.Vector2(dir_x, dir_y).normalize()
            self.ultima_direcao = move_vec.copy()

        # 2. Handle Dash logic
        triggered_shake = False
        if (teclas[pygame.K_SPACE] or teclas[pygame.K_LSHIFT] or teclas[pygame.K_RSHIFT]) and self.dash.ready:
            # Determine dash direction: input -> velocity -> memory
            if move_vec.length_squared() > 0:
                direcao_dash = move_vec
            elif self.transform.vel.length_squared() > 0:
                direcao_dash = self.transform.vel.normalize()
            else:
                direcao_dash = self.ultima_direcao

            if self.dash.try_activate(self.transform.vel, direcao_dash):
                sound_manager.play('player_dash')
                triggered_shake = True

        # 3. Apply physics and movement
        if self.dash.active:
            # During dash, we ignore normal physics/input and just move
            self.transform.pos += self.transform.vel
            # Boundary clamping during dash
            self.transform.pos.x = max(16, min(LARGURA_TELA - 16, self.transform.pos.x))
            self.transform.pos.y = max(60 + 16, min(ALTURA_TELA - 16, self.transform.pos.y))
            # Dash particles
            self.emitter.burst(self.transform.pos.x, self.transform.pos.y, lista_particulas, count=3)
        else:
            # Normal movement using physics component
            self.physics.apply(
                self.transform,
                move_vec,
                bounds_x=(16, LARGURA_TELA - 16),
                bounds_y=(60 + 16, ALTURA_TELA - 16)
            )

        # 4. Update component timers
        self.dash.update()

        return triggered_shake

    def draw(self, surface: pygame.Surface) -> None:
        cor = BRANCO if self.invencivel else CIANO_NEON
        draw_neon_glow(surface, cor, self.transform.pos.x, self.transform.pos.y, self.collider.radius, intensity=4)

        rect = pygame.Rect(0, 0, self.collider.radius * 2, self.collider.radius * 2)
        rect.center = (int(self.transform.pos.x), int(self.transform.pos.y))
        pygame.draw.rect(surface, cor, rect, border_radius=4)
        pygame.draw.rect(surface, BRANCO, rect.inflate(-6, -6), border_radius=2)

        # Dash cooldown indicator
        raio_anel = 16
        rect_anel = pygame.Rect(0, 0, raio_anel * 2, raio_anel * 2)
        rect_anel.center = (int(self.transform.pos.x), int(self.transform.pos.y))
        espessura = 5

        if not self.dash.ready:
            ratio = self.dash.progress
            angulo_inicio = -math.pi / 2
            angulo_fim = angulo_inicio + (math.pi * 2 * ratio)
            pygame.draw.arc(surface, cor, rect_anel, angulo_inicio, angulo_fim, espessura)
        else:
            pygame.draw.circle(surface, cor, rect_anel.center, raio_anel, espessura)
