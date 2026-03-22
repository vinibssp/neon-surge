import math
import random
import time
import pygame
from ..constants import ROXO_NEON, BRANCO
from ..hud.ui import desenhar_brilho_neon

class BlackHole:
    """
    Um perigo ambiental que persegue o jogador lentamente.
    Puxa o jogador e o deixa mais lento quanto mais próximo do centro.
    Causa dano apenas no centro (núcleo).
    """

    def __init__(self, x, y):
        self.pos = pygame.math.Vector2(x, y)
        self.raio_efeito = 150.0
        self.raio_dano = 15.0
        self.tempo_vida = 6.0
        self.forca_puxao = 90.0
        self.velocidade_persegicao = 1.2
        self.fator_lentidao_max = 0.7 
        self.angulo_visual = 0.0
        
        # Partículas persistentes para o disco de acreção (Apenas brancas e em menor volume)
        self.particulas_disco = []
        for _ in range(70): 
            dist = random.uniform(self.raio_dano + 5, self.raio_efeito * 0.8)
            ang = random.uniform(0, math.pi * 2)
            vel_rot = random.uniform(2, 5) 
            tamanho = random.randint(1, 2) # Partículas menores
            cor = BRANCO
            self.particulas_disco.append({
                "dist": dist,
                "ang": ang,
                "vel_rot": vel_rot,
                "tamanho": tamanho,
                "cor": cor
            })

    @property
    def expirado(self):
        return self.tempo_vida <= 0

    def update(self, player, dt):
        self.tempo_vida -= dt
        
        # Atualiza o ângulo das partículas do disco
        for p in self.particulas_disco:
            p["ang"] += p["vel_rot"] * dt

        # Perseguição lenta
        direcao_persegicao = (player.pos - self.pos)
        if direcao_persegicao.length() > 0:
            self.pos += direcao_persegicao.normalize() * self.velocidade_persegicao

        distancia = self.pos.distance_to(player.pos)
        
        # Dano no centro
        if distancia < self.raio_dano and not player.invencivel:
            self.tempo_vida = 0
            return True

        # Puxão e Lentidão Progressiva
        if distancia < self.raio_efeito:
            # Puxão
            if distancia > 0:
                direcao_puxao = (self.pos - player.pos).normalize()
                player.pos += direcao_puxao * self.forca_puxao * dt

            # Lentidão
            progresso = 1.0 - (distancia / self.raio_efeito)
            lentidao_atual = 1.0 - (progresso * (1.0 - self.fator_lentidao_max))
            player.vel *= lentidao_atual

        return False

    def draw(self, surface):
        # Horizonte de eventos (Brilho sutil)
        desenhar_brilho_neon(surface, ROXO_NEON, self.pos.x, self.pos.y, 20, intensidade=3)
        
        # Disco de acreção (Partículas/Estrelas)
        for p in self.particulas_disco:
            # Posição baseada em órbita
            px = self.pos.x + math.cos(p["ang"]) * p["dist"]
            py = self.pos.y + math.sin(p["ang"]) * p["dist"]
            
            # Desenha a "cauda" ou rastro da partícula (opcional, vamos manter simples como estrelas)
            pygame.draw.circle(surface, p["cor"], (int(px), int(py)), p["tamanho"])

        # Núcleo (Sólido e Escuro como na imagem)
        pygame.draw.circle(surface, (0, 0, 0), (int(self.pos.x), int(self.pos.y)), int(self.raio_dano + 2))
        # Pequeno anel de luz no limite
        pygame.draw.circle(surface, BRANCO, (int(self.pos.x), int(self.pos.y)), int(self.raio_dano + 2), 1)
