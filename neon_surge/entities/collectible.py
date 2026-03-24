import math
import random
import time
import pygame
from ..constants import BRANCO, CIANO_NEON, LARGURA_TELA, ALTURA_TELA
from ..hud.ui import desenhar_brilho_neon

class Collectible:
    """Núcleo de Energia (Moeda) com animações avançadas e magnetismo."""
    def __init__(self, x, y):
        self.pos = pygame.math.Vector2(x, y)
        self.base_pos = pygame.math.Vector2(x, y)
        self.angulo_oscilacao = random.uniform(0, math.pi * 2)
        self.velocidade_oscilacao = random.uniform(2.5, 4.0)
        self.raio_alerta = 140 # Raio onde ela começa a "perceber" o player
        self.velocidade_fuga = 220
        
        # Atributos Visuais
        self.escala = 1.0
        self.rotacao = 0
        self.pulso_glow = 0
        
    def update(self, player_pos, dt):
        # 1. Animação de Flutuação (Bobbing) - Apenas Visual
        self.angulo_oscilacao += self.velocidade_oscilacao * dt
        offset_y = math.sin(self.angulo_oscilacao) * 6
        self.pos.y = self.base_pos.y + offset_y
        
        # 2. Rotação e Pulso
        self.rotacao = (self.rotacao + 180 * dt) % 360
        self.pulso_glow = (math.sin(self.angulo_oscilacao * 1.5) + 1) / 2
        self.escala = 0.9 + (self.pulso_glow * 0.2)

    def draw(self, surface, game=None):
        x, y = int(self.pos.x), int(self.pos.y)
        
        # 1. Brilho Neon Pulsante
        cor_glow = CIANO_NEON
        raio_glow = 10 + (self.pulso_glow * 10)
        desenhar_brilho_neon(surface, cor_glow, x, y, raio_glow, 3, game=game)
        
        # 2. Desenho Geométrico (Losango Rotacionado)
        tamanho = 12 * self.escala
        pontos = []
        for i in range(4):
            ang = math.radians(self.rotacao + i * 90)
            px = x + math.cos(ang) * tamanho
            py = y + math.sin(ang) * tamanho
            pontos.append((px, py))
            
        pygame.draw.polygon(surface, CIANO_NEON, pontos)
        pygame.draw.polygon(surface, BRANCO, pontos, 2)
        
        # 3. Núcleo Interno (Estrela/Cruz que gira mais rápido)
        tamanho_i = 6 * self.escala
        for i in range(4):
            ang = math.radians(-self.rotacao * 2 + i * 90)
            px = x + math.cos(ang) * tamanho_i
            py = y + math.sin(ang) * tamanho_i
            pygame.draw.line(surface, BRANCO, (x, y), (px, py), 2)
