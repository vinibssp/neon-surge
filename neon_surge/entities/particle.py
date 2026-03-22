import random
import pygame
from ..constants import (
    ALTURA_TELA, LARGURA_TELA, CIANO_NEON, ROSA_NEON, VERDE_NEON, AZUL_ESCURO, BRANCO
)
from ..hud.ui import desenhar_brilho_neon

class ParticulaMenu:
    def __init__(self):
        self.pos = pygame.math.Vector2(random.uniform(0, LARGURA_TELA), random.uniform(0, ALTURA_TELA))
        self.vel = pygame.math.Vector2(random.uniform(-0.5, 0.5), random.uniform(-1.5, -0.5))
        self.cor = random.choice([CIANO_NEON, ROSA_NEON, VERDE_NEON, AZUL_ESCURO])
        self.tamanho = random.uniform(1, 3)

    def update(self):
        self.pos += self.vel
        if self.pos.y < -10:
            self.pos.y = ALTURA_TELA + 10
            self.pos.x = random.uniform(0, LARGURA_TELA)

    def draw(self, surface):
        pygame.draw.circle(surface, self.cor, (int(self.pos.x), int(self.pos.y)), int(self.tamanho))

class Particula:
    def __init__(self, x, y, cor):
        self.pos = pygame.math.Vector2(x, y)
        self.vel = pygame.math.Vector2(random.uniform(-3, 3), random.uniform(-3, 3))
        self.raio = random.uniform(4, 7)
        self.cor = cor

    def update(self):
        self.pos += self.vel
        self.raio -= 0.3

    def draw(self, surface):
        if self.raio > 0:
            desenhar_brilho_neon(surface, self.cor, self.pos.x, self.pos.y, self.raio, intensidade=2)
            pygame.draw.circle(surface, BRANCO, (int(self.pos.x), int(self.pos.y)), int(self.raio // 2))
