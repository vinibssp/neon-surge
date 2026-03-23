import math
import random
import pygame
from ..constants import ROXO_NEON, BRANCO, VERMELHO_SANGUE, AMARELO_DADO, LARANJA_NEON, LARGURA_TELA, ALTURA_TELA
from ..hud.ui import desenhar_brilho_neon, desenhar_texto

class BlackHole:
    """
    Um perigo ambiental que persegue o jogador lentamente.
    Puxa o jogador e o deixa mais lento quanto mais próximo do centro.
    Causa dano apenas no centro (núcleo).
    """

    def __init__(self, x, y):
        self.pos = pygame.math.Vector2(x, y)
        self.raio_efeito = 160.0
        self.raio_dano = 18.0
        self.tempo_vida = 7.0
        self.forca_puxao = 110.0
        self.velocidade_persegicao = 1.4
        self.fator_lentidao_max = 0.6 
        
        # Partículas persistentes para o disco de acreção
        self.particulas_disco = []
        for _ in range(85): 
            dist = random.uniform(self.raio_dano + 5, self.raio_efeito * 0.9)
            ang = random.uniform(0, math.pi * 2)
            vel_rot = random.uniform(2, 6) 
            tamanho = random.randint(1, 3)
            cor = random.choice([BRANCO, ROXO_NEON])
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

        # Perseguição suave
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

            # Lentidão (mais forte conforme aproxima)
            progresso = 1.0 - (distancia / self.raio_efeito)
            lentidao_atual = 1.0 - (progresso * (1.0 - self.fator_lentidao_max))
            player.vel *= lentidao_atual

        return False

    def draw(self, surface):
        # Brilho externo
        desenhar_brilho_neon(surface, ROXO_NEON, self.pos.x, self.pos.y, 25, intensidade=4)
        
        # Disco de acreção
        for p in self.particulas_disco:
            px = self.pos.x + math.cos(p["ang"]) * p["dist"]
            py = self.pos.y + math.sin(p["ang"]) * p["dist"]
            pygame.draw.circle(surface, p["cor"], (int(px), int(py)), p["tamanho"])

        # Núcleo Sombrio
        pygame.draw.circle(surface, (5, 0, 10), (int(self.pos.x), int(self.pos.y)), int(self.raio_dano + 3))
        # Anel de luz
        pygame.draw.circle(surface, BRANCO, (int(self.pos.x), int(self.pos.y)), int(self.raio_dano + 3), 1)

class LavaManager:
    """
    Gerencia eventos de lava setorial no modo Sobrevivência/Hardcore.
    """
    def __init__(self):
        self.ativa = False
        self.tempo_restante = 0.0
        self.aviso_tempo = 0.0
        self.hitboxes = []
        self.tipo_lava = 0 # 1: Vertical, 2: Horizontal, 3: Cantos, 4: Centro
        
    def reset(self):
        self.ativa = False
        self.tempo_restante = 0.0
        self.aviso_tempo = 0.0
        self.hitboxes = []

    def disparar_evento(self, tipo=None):
        if self.ativa or self.aviso_tempo > 0:
            return
            
        self.tipo_lava = tipo if tipo else random.randint(1, 4)
        self.aviso_tempo = 3.0
        self.hitboxes = []
        
        margem_ui = 80
        if self.tipo_lava == 1: # Laterais Verticais
            largura = 150
            self.hitboxes.append(pygame.Rect(0, margem_ui, largura, ALTURA_TELA))
            self.hitboxes.append(pygame.Rect(LARGURA_TELA - largura, margem_ui, largura, ALTURA_TELA))
        elif self.tipo_lava == 2: # Topo e Base Horizontais
            altura = 140
            self.hitboxes.append(pygame.Rect(0, margem_ui, LARGURA_TELA, altura))
            self.hitboxes.append(pygame.Rect(0, ALTURA_TELA - altura, LARGURA_TELA, altura))
        elif self.tipo_lava == 3: # X (Cantos)
            t = 200
            self.hitboxes.append(pygame.Rect(0, margem_ui, t, t))
            self.hitboxes.append(pygame.Rect(LARGURA_TELA - t, margem_ui, t, t))
            self.hitboxes.append(pygame.Rect(0, ALTURA_TELA - t, t, t))
            self.hitboxes.append(pygame.Rect(LARGURA_TELA - t, ALTURA_TELA - t, t, t))
        else: # Centro
            cw, ch = 400, 300
            self.hitboxes.append(pygame.Rect((LARGURA_TELA - cw)//2, (ALTURA_TELA - ch + margem_ui)//2, cw, ch))

    def update(self, player, dt, sounds):
        if self.aviso_tempo > 0:
            self.aviso_tempo -= dt
            if self.aviso_tempo <= 0:
                self.ativa = True
                self.tempo_restante = 5.0
                sounds.play('player_dash') # Som sutil para início
            return False

        if self.ativa:
            self.tempo_restante -= dt
            if self.tempo_restante <= 0:
                self.ativa = False
                return False
                
            if not player.invencivel:
                for hb in self.hitboxes:
                    if hb.collidepoint(player.pos.x, player.pos.y):
                        return True # Morte por lava
        
        return False

    def draw(self, surface, fonte_titulo, fonte_sub):
        if self.aviso_tempo > 0:
            for r in self.hitboxes:
                s = pygame.Surface((r.width, r.height), pygame.SRCALPHA)
                al = int(100 + math.sin(pygame.time.get_ticks()*0.02)*50)
                s.fill((255, 150, 0, al))
                pygame.draw.rect(s, AMARELO_DADO, (0,0,r.width,r.height), 4)
                surface.blit(s, (r.x, r.y))
            desenhar_texto(surface, f"ALERTA DE LAVA: {int(self.aviso_tempo)+1}s!", fonte_titulo, VERMELHO_SANGUE, LARGURA_TELA//2, 160)

        if self.ativa:
            if (self.tempo_restante > 1.0) or (int(pygame.time.get_ticks()*0.008)%2 == 0):
                for r in self.hitboxes:
                    s = pygame.Surface((r.width, r.height), pygame.SRCALPHA)
                    s.fill((255, 60, 0, 160))
                    pygame.draw.rect(s, VERMELHO_SANGUE, (0,0,r.width,r.height), 4)
                    surface.blit(s, (r.x, r.y))
            desenhar_texto(surface, f"LAVA ATIVA: {self.tempo_restante:.1f}s", fonte_sub, LARANJA_NEON, LARGURA_TELA//2, 100)
