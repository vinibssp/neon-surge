import math
import random
import time
import pygame
from ..constants import (
    LARGURA_TELA, ALTURA_TELA, ROSA_NEON, VERMELHO_SANGUE, LARANJA_NEON, 
    AMARELO_DADO, ROXO_NEON, CIANO_NEON, PRETO_FUNDO, BRANCO, AZUL_ESCURO
)
from ..hud.ui import desenhar_brilho_neon
from .particle import Particula
from ..ai import get_ai_for_type

def Inimigo(x, y, tipo, velocidade):
    """Factory function to maintain compatibility with gameplay.py."""
    registry = {
        "quique": InimigoQuique,
        "perseguidor": InimigoPerseguidor,
        "investida": InimigoInvestida,
        "explosivo": InimigoExplosivo,
        "metralhadora": InimigoMetralhadora,
        "morteiro": InimigoMorteiro,
        "miniboss_espiral": MinibossEspiral,
        "miniboss_cacador": MinibossCacador,
        "miniboss_escudo": MinibossEscudo,
        "miniboss_sniper": MinibossSniper,
        "boss": Boss,
        "boss_artilharia": BossArtilharia,
        "boss_caotico": BossCaotico,
    }
    cls = registry.get(tipo, InimigoQuique)
    return cls(x, y, velocidade)

class InimigoBase:
    def __init__(self, x, y, tipo, velocidade, raio=12):
        self.pos = pygame.math.Vector2(x, y)
        self.tipo = tipo
        self.raio = raio
        self.vel = velocidade
        self.dir = pygame.math.Vector2(0, 0)
        self.morto = False
        self.variante = 1
        
        self.ai = get_ai_for_type(self.tipo)

    def handle_wall_collision(self, axis):
        """Standard bounce behavior."""
        if axis == 'x':
            self.dir.x *= -1
        else:
            self.dir.y *= -1

    def update(self, player, lista_inimigos, dt, lista_particulas, interface_principal, sound_manager):
        # 1. AI Update
        self.ai.update(self, player, lista_inimigos, dt, lista_particulas, interface_principal, sound_manager)

        # 2. Collision / Repulsion between enemies
        forca_repulsao = self.calculate_repulsion(lista_inimigos)

        # 3. Apply position change
        self.apply_movement(forca_repulsao)

        # 4. Stay within screen boundaries
        self.check_boundaries()

    def calculate_repulsion(self, lista_inimigos):
        forca_repulsao = pygame.math.Vector2(0, 0)
        for vizinho in lista_inimigos:
            if vizinho != self:
                dist_sq = self.pos.distance_squared_to(vizinho.pos)
                distancia_segura = self.raio + vizinho.raio + 5
                if 0 < dist_sq < distancia_segura**2:
                    distancia = math.sqrt(dist_sq)
                    diferenca = self.pos - vizinho.pos
                    forca_repulsao += diferenca.normalize() * (distancia_segura - distancia) * 0.1
        return forca_repulsao

    def apply_movement(self, forca_repulsao):
        self.pos += self.dir + forca_repulsao

    def check_boundaries(self):
        if self.pos.x <= self.raio:
            self.pos.x = self.raio
            self.handle_wall_collision('x')
        elif self.pos.x >= LARGURA_TELA - self.raio:
            self.pos.x = LARGURA_TELA - self.raio
            self.handle_wall_collision('x')

        if self.pos.y <= 60 + self.raio:
            self.pos.y = 60 + self.raio
            self.handle_wall_collision('y')
        elif self.pos.y >= ALTURA_TELA - self.raio:
            self.pos.y = ALTURA_TELA - self.raio
            self.handle_wall_collision('y')

    def draw(self, surface, game=None):
        pass

class InimigoQuique(InimigoBase):
    def __init__(self, x, y, velocidade):
        super().__init__(x, y, "quique", velocidade, 12)
        ang = random.uniform(0, math.pi * 2)
        self.dir = pygame.math.Vector2(math.cos(ang), math.sin(ang)) * self.vel

    def calculate_repulsion(self, lista_inimigos):
        """Override repulsion to use reflection like a bounce."""
        for vizinho in lista_inimigos:
            if vizinho != self:
                distancia = self.pos.distance_to(vizinho.pos)
                distancia_segura = self.raio + vizinho.raio + 5
                if 0 < distancia < distancia_segura:
                    normal = (self.pos - vizinho.pos).normalize()
                    if self.dir.length() > 0:
                        self.dir = self.dir.reflect(normal)
                    self.pos += normal * 3
        return pygame.math.Vector2(0, 0)

    def draw(self, surface, game=None):
        desenhar_brilho_neon(surface, ROSA_NEON, self.pos.x, self.pos.y, self.raio, intensidade=3, game=game)
        pygame.draw.circle(surface, ROSA_NEON, (int(self.pos.x), int(self.pos.y)), self.raio)
        pygame.draw.circle(surface, BRANCO, (int(self.pos.x), int(self.pos.y)), self.raio // 3)

class InimigoPerseguidor(InimigoBase):
    def __init__(self, x, y, velocidade):
        super().__init__(x, y, "perseguidor", velocidade, 12)

    def draw(self, surface, game=None):
        desenhar_brilho_neon(surface, VERMELHO_SANGUE, self.pos.x, self.pos.y, self.raio, intensidade=3, game=game)
        pygame.draw.circle(surface, VERMELHO_SANGUE, (int(self.pos.x), int(self.pos.y)), self.raio)
        pygame.draw.circle(surface, BRANCO, (int(self.pos.x), int(self.pos.y)), self.raio // 3)

class InimigoInvestida(InimigoBase):
    def __init__(self, x, y, velocidade):
        super().__init__(x, y, "investida", velocidade, 12)
        self.estado_investida = "ESPERANDO"
        self.timer_investida = 0.0
        self.alvo_mira = pygame.math.Vector2(x, y)
        self.travado = False

    def handle_wall_collision(self, axis):
        if axis == 'x': self.dir.x = 0
        else: self.dir.y = 0
        if self.estado_investida == "ATACANDO":
            self.estado_investida = "ESPERANDO"
            self.timer_investida = 0.0

    def draw(self, surface, game=None):
        cor_base = LARANJA_NEON
        if self.estado_investida == "MIRANDO":
            cor_linha = VERMELHO_SANGUE if not self.travado else BRANCO
            espessura = 2 if not self.travado else 4
            pygame.draw.line(surface, cor_linha, self.pos, self.alvo_mira, espessura)
            if self.travado:
                cor_base = BRANCO
        
        desenhar_brilho_neon(surface, cor_base, self.pos.x, self.pos.y, self.raio, intensidade=3, game=game)
        pygame.draw.circle(surface, cor_base, (int(self.pos.x), int(self.pos.y)), self.raio)
        pygame.draw.circle(surface, BRANCO, (int(self.pos.x), int(self.pos.y)), self.raio // 3)

class InimigoExplosivo(InimigoBase):
    def __init__(self, x, y, velocidade):
        super().__init__(x, y, "explosivo", velocidade, 12)
        self.timer_explosao = 0.0
        self.explodiu = False

    def draw(self, surface, game=None):
        cor_base = AMARELO_DADO
        if self.timer_explosao > 2.5:
            if int(self.timer_explosao * 15) % 2 == 0:
                cor_base = BRANCO
        
        desenhar_brilho_neon(surface, cor_base, self.pos.x, self.pos.y, self.raio, intensidade=4, game=game)
        pygame.draw.circle(surface, cor_base, (int(self.pos.x), int(self.pos.y)), self.raio)
        pygame.draw.circle(surface, BRANCO, (int(self.pos.x), int(self.pos.y)), self.raio // 3)
        
        if self.timer_explosao > 3.5:
            raio_indicador = min(80, (self.timer_explosao - 3.5) * 80)
            pygame.draw.circle(
                surface,
                VERMELHO_SANGUE,
                (int(self.pos.x), int(self.pos.y)),
                int(raio_indicador),
                max(1, int((4.5 - self.timer_explosao) * 5)),
            )

class InimigoMetralhadora(InimigoBase):
    def __init__(self, x, y, velocidade):
        super().__init__(x, y, "metralhadora", velocidade, 15)
        self.padrao_tiro = random.randint(0, 1)
        self.angulo_espiral = random.uniform(0, 360)
        self.timer_vida = 0.0
        self.timer_tiro = 0.0
        self.timer_rajada = 0.0
        self.em_rajada = True
        self.direcao_tiro = pygame.math.Vector2(1, 0)

    def apply_movement(self, forca_repulsao):
        """Turrets stay still and ignore repulsion."""
        self.dir = pygame.math.Vector2(0, 0)

    def draw(self, surface, game=None):
        pulso = abs(math.sin(time.time() * 8))
        cor_nucleo = BRANCO if self.em_rajada else CIANO_NEON
        desenhar_brilho_neon(surface, ROXO_NEON, self.pos.x, self.pos.y, self.raio + (pulso * 2), intensidade=4, game=game)
        pygame.draw.circle(surface, ROXO_NEON, (int(self.pos.x), int(self.pos.y)), self.raio)
        pygame.draw.circle(surface, AZUL_ESCURO, (int(self.pos.x), int(self.pos.y)), self.raio - 5)
        pygame.draw.circle(surface, cor_nucleo, (int(self.pos.x), int(self.pos.y)), 5)

        if self.direcao_tiro.length() > 0:
            ponta = self.pos + self.direcao_tiro.normalize() * (self.raio + 14)
            pygame.draw.line(surface, cor_nucleo, self.pos, ponta, 4)
            pygame.draw.circle(surface, cor_nucleo, (int(ponta.x), int(ponta.y)), 4)

class MinibossEspiral(InimigoBase):
    def __init__(self, x, y, velocidade):
        super().__init__(x, y, "miniboss_espiral", velocidade, 26)
        self.padrao_tiro = 2
        self.angulo_espiral = random.uniform(0, 360)
        self.timer_vida = 0.0
        self.timer_tiro = 0.0
        self.direcao_tiro = pygame.math.Vector2(1, 0)

    def apply_movement(self, forca_repulsao):
        """Turrets stay still and ignore repulsion."""
        self.dir = pygame.math.Vector2(0, 0)

    def draw(self, surface, game=None):
        pulso = abs(math.sin(time.time() * 6))
        cor_borda = ROXO_NEON
        desenhar_brilho_neon(surface, cor_borda, self.pos.x, self.pos.y, self.raio + (pulso * 4), intensidade=5, game=game)
        pygame.draw.circle(surface, cor_borda, (int(self.pos.x), int(self.pos.y)), self.raio)
        pygame.draw.circle(surface, PRETO_FUNDO, (int(self.pos.x), int(self.pos.y)), self.raio - 6)
        pygame.draw.circle(surface, BRANCO, (int(self.pos.x), int(self.pos.y)), 6)

        if self.direcao_tiro.length() > 0:
            ponta = self.pos + self.direcao_tiro.normalize() * (self.raio + 18)
            pygame.draw.line(surface, BRANCO, self.pos, ponta, 4)
            pygame.draw.circle(surface, BRANCO, (int(ponta.x), int(ponta.y)), 5)

class MinibossCacador(InimigoBase):
    def __init__(self, x, y, velocidade):
        super().__init__(x, y, "miniboss_cacador", velocidade, 24)
        self.timer_tiro = 0.0
        ang = random.uniform(0, math.pi * 2)
        self.dir = pygame.math.Vector2(math.cos(ang), math.sin(ang)) * (self.vel * 0.65)

    def draw(self, surface, game=None):
        pulso = abs(math.sin(time.time() * 7))
        cor_mini = VERMELHO_SANGUE
        desenhar_brilho_neon(surface, cor_mini, self.pos.x, self.pos.y, self.raio + (pulso * 3), intensidade=4, game=game)
        pygame.draw.circle(surface, cor_mini, (int(self.pos.x), int(self.pos.y)), self.raio)
        pygame.draw.circle(surface, PRETO_FUNDO, (int(self.pos.x), int(self.pos.y)), self.raio - 5)
        pygame.draw.circle(surface, BRANCO, (int(self.pos.x), int(self.pos.y)), 6)

class MinibossEscudo(InimigoBase):
    def __init__(self, x, y, velocidade):
        super().__init__(x, y, "miniboss_escudo", velocidade, 23)
        self.timer_tiro = 0.0
        self.timer_habilidade = 0.0
        self.orbita_angulo = random.uniform(0, math.pi * 2)

    def draw(self, surface, game=None):
        pulso = abs(math.sin(time.time() * 6))
        cor_mini = CIANO_NEON
        desenhar_brilho_neon(surface, cor_mini, self.pos.x, self.pos.y, self.raio + (pulso * 4), intensidade=5, game=game)
        pygame.draw.circle(surface, cor_mini, (int(self.pos.x), int(self.pos.y)), self.raio)
        pygame.draw.circle(surface, PRETO_FUNDO, (int(self.pos.x), int(self.pos.y)), self.raio - 6)
        pygame.draw.circle(surface, BRANCO, (int(self.pos.x), int(self.pos.y)), 5)
        pygame.draw.circle(surface, BRANCO, (int(self.pos.x), int(self.pos.y)), self.raio + 9, 2)

class MinibossSniper(InimigoBase):
    def __init__(self, x, y, velocidade):
        super().__init__(x, y, "miniboss_sniper", velocidade, 21)
        self.timer_tiro = 0.0
        self.estado_sniper = "MIRANDO"
        self.alvo_mira = pygame.math.Vector2(x, y)

    def apply_movement(self, forca_repulsao):
        """Turrets stay still and ignore repulsion."""
        self.dir = pygame.math.Vector2(0, 0)

    def draw(self, surface, game=None):
        cor_mini = AMARELO_DADO
        desenhar_brilho_neon(surface, cor_mini, self.pos.x, self.pos.y, self.raio + 3, intensidade=4, game=game)
        pygame.draw.circle(surface, cor_mini, (int(self.pos.x), int(self.pos.y)), self.raio)
        pygame.draw.circle(surface, PRETO_FUNDO, (int(self.pos.x), int(self.pos.y)), self.raio - 5)
        pygame.draw.circle(surface, BRANCO, (int(self.pos.x), int(self.pos.y)), 4)
        if self.estado_sniper == "MIRANDO":
            pygame.draw.line(surface, BRANCO, self.pos, self.alvo_mira, 2)

class Boss(InimigoBase):
    def __init__(self, x, y, velocidade):
        super().__init__(x, y, "boss", velocidade, 40)
        self.timer_habilidade = 0.0
        self.timer_tiro = 0.0
        self.estado_boss = "PERSEGUINDO"

    def draw(self, surface, game=None):
        cor_boss = ROXO_NEON if self.variante % 3 == 1 else (CIANO_NEON if self.variante % 3 == 2 else ROSA_NEON)
        tempo = time.time()

        for i in range(3):
            angulo = tempo * 4 + (i * math.pi * 2 / 3)
            distancia_orbe = self.raio + 35 if self.estado_boss == "DASH" else self.raio + 15
            x_orb = self.pos.x + math.cos(angulo) * distancia_orbe
            y_orb = self.pos.y + math.sin(angulo) * distancia_orbe

            pygame.draw.line(surface, cor_boss, self.pos, (x_orb, y_orb), 2)
            pygame.draw.circle(surface, VERMELHO_SANGUE, (int(x_orb), int(y_orb)), 8)
            desenhar_brilho_neon(surface, VERMELHO_SANGUE, x_orb, y_orb, 8, 2, game=game)
            pygame.draw.circle(surface, BRANCO, (int(x_orb), int(y_orb)), 3)

        if self.estado_boss == "DASH":
            cor_atual = VERMELHO_SANGUE
        elif self.estado_boss == "INVOCANDO":
            cor_atual = BRANCO
        else:
            cor_atual = cor_boss

        desenhar_brilho_neon(surface, cor_atual, self.pos.x, self.pos.y, self.raio, intensidade=5, game=game)
        pygame.draw.circle(surface, cor_atual, (int(self.pos.x), int(self.pos.y)), self.raio)
        pygame.draw.circle(surface, PRETO_FUNDO, (int(self.pos.x), int(self.pos.y)), self.raio - 6)

        pulso = abs(math.sin(tempo * 10)) * (self.raio // 1.5)
        pygame.draw.circle(surface, VERMELHO_SANGUE, (int(self.pos.x), int(self.pos.y)), int(pulso))

class BossArtilharia(InimigoBase):
    def __init__(self, x, y, velocidade):
        super().__init__(x, y, "boss_artilharia", velocidade, 40)
        self.timer_habilidade = 0.0
        self.timer_tiro = 0.0
        self.estado_boss = "PERSEGUINDO"

    def draw(self, surface, game=None):
        tempo = time.time()
        cor_boss = LARANJA_NEON
        desenhar_brilho_neon(surface, cor_boss, self.pos.x, self.pos.y, self.raio + 6, intensidade=6, game=game)
        pygame.draw.circle(surface, cor_boss, (int(self.pos.x), int(self.pos.y)), self.raio)
        pygame.draw.circle(surface, PRETO_FUNDO, (int(self.pos.x), int(self.pos.y)), self.raio - 7)
        for i in range(4):
            ang = tempo * 2.5 + i * (math.pi / 2)
            x_orb = self.pos.x + math.cos(ang) * (self.raio + 16)
            y_orb = self.pos.y + math.sin(ang) * (self.raio + 16)
            pygame.draw.circle(surface, AMARELO_DADO, (int(x_orb), int(y_orb)), 6)
            pygame.draw.line(surface, AMARELO_DADO, self.pos, (x_orb, y_orb), 2)

class BossCaotico(InimigoBase):
    def __init__(self, x, y, velocidade):
        super().__init__(x, y, "boss_caotico", velocidade, 40)
        self.timer_habilidade = 0.0
        self.timer_tiro = 0.0
        self.estado_boss = "PERSEGUINDO"

    def draw(self, surface, game=None):
        tempo = time.time()
        cor_boss = ROSA_NEON
        desenhar_brilho_neon(surface, cor_boss, self.pos.x, self.pos.y, self.raio + 8, intensidade=6, game=game)
        pygame.draw.circle(surface, cor_boss, (int(self.pos.x), int(self.pos.y)), self.raio)
        pygame.draw.circle(surface, PRETO_FUNDO, (int(self.pos.x), int(self.pos.y)), self.raio - 7)
        for i in range(6):
            ang = tempo * 5.0 + i * (math.pi / 3)
            ponta = pygame.math.Vector2(self.pos.x + math.cos(ang) * (self.raio + 12), self.pos.y + math.sin(ang) * (self.raio + 12))
            pygame.draw.line(surface, BRANCO, self.pos, ponta, 2)

class InimigoMorteiro(InimigoBase):
    def __init__(self, x, y, velocidade):
        super().__init__(x, y, "morteiro", velocidade, 18)
        self.timer_tiro = 0.0
        self.timer_vida = 0.0

    def apply_movement(self, forca_repulsao):
        """Morteiro stays still."""
        self.dir = pygame.math.Vector2(0, 0)

    def draw(self, surface, game=None):
        pulso = abs(math.sin(time.time() * 5))
        cor_base = LARANJA_NEON
        desenhar_brilho_neon(surface, cor_base, self.pos.x, self.pos.y, self.raio + (pulso * 2), intensidade=4, game=game)
        
        # Desenho do corpo (hexágono/trapézio para parecer um morteiro)
        pontos = []
        for i in range(6):
            ang = i * (math.pi / 3)
            px = self.pos.x + math.cos(ang) * self.raio
            py = self.pos.y + math.sin(ang) * self.raio
            pontos.append((px, py))
        
        pygame.draw.polygon(surface, cor_base, pontos)
        pygame.draw.polygon(surface, PRETO_FUNDO, pontos, 2)
        pygame.draw.circle(surface, BRANCO, (int(self.pos.x), int(self.pos.y)), 6)
