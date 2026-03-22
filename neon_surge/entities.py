import math
import random
import time

import pygame

from .config import (
    ALTURA_TELA,
    AMARELO_DADO,
    BRANCO,
    CIANO_NEON,
    LARANJA_NEON,
    LARGURA_TELA,
    PRETO_FUNDO,
    ROSA_NEON,
    ROXO_NEON,
    VERDE_NEON,
    VERMELHO_SANGUE,
    AZUL_ESCURO,
)
from .ui import desenhar_brilho_neon


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


class Player:
    def __init__(self, x, y):
        self.pos = pygame.math.Vector2(x, y)
        self.vel = pygame.math.Vector2(0, 0)
        self.aceleracao = 1.8
        self.atrito = 0.82
        self.velocidade_maxima = 10.0
        self.velocidade_dash = 25.0
        self.tamanho = 16
        self.dash_cooldown = 0
        self.dash_timer = 0
        self.pos_dash_invuln_timer = 0
        self.ultima_direcao = pygame.math.Vector2(1, 0)
        self.invencivel = False

    def update(self, teclas, lista_particulas):
        dir_x, dir_y = 0, 0
        if teclas[pygame.K_w] or teclas[pygame.K_UP]:
            dir_y = -1
        if teclas[pygame.K_s] or teclas[pygame.K_DOWN]:
            dir_y = 1
        if teclas[pygame.K_a] or teclas[pygame.K_LEFT]:
            dir_x = -1
        if teclas[pygame.K_d] or teclas[pygame.K_RIGHT]:
            dir_x = 1

        move_vec = pygame.math.Vector2(0, 0)
        if dir_x != 0 or dir_y != 0:
            move_vec = pygame.math.Vector2(dir_x, dir_y).normalize()
            self.ultima_direcao = pygame.math.Vector2(move_vec.x, move_vec.y)

        if teclas[pygame.K_SPACE] and self.dash_cooldown <= 0:
            if move_vec.length_squared() > 0:
                direcao_dash = move_vec
            elif self.vel.length_squared() > 0:
                direcao_dash = self.vel.normalize()
            else:
                direcao_dash = self.ultima_direcao

            self.vel = direcao_dash * self.velocidade_dash
            self.dash_timer = 10
            self.dash_cooldown = 45
            return True

        if self.dash_timer > 0:
            self.dash_timer -= 1
            self.invencivel = True
            if self.dash_timer == 0:
                self.pos_dash_invuln_timer = 12
            for _ in range(3):
                lista_particulas.append(Particula(self.pos.x, self.pos.y, CIANO_NEON))
        else:
            if move_vec.length_squared() > 0:
                self.vel = move_vec * self.velocidade_maxima
            else:
                self.vel = pygame.math.Vector2(0, 0)

            if self.pos_dash_invuln_timer > 0:
                self.pos_dash_invuln_timer -= 1
                self.invencivel = True
            else:
                self.invencivel = False

        if self.dash_cooldown > 0:
            self.dash_cooldown -= 1

        self.pos += self.vel
        self.pos.x = max(self.tamanho, min(LARGURA_TELA - self.tamanho, self.pos.x))
        self.pos.y = max(60 + self.tamanho, min(ALTURA_TELA - self.tamanho, self.pos.y))
        return False

    def draw(self, surface):
        cor = BRANCO if self.invencivel else CIANO_NEON
        desenhar_brilho_neon(surface, cor, self.pos.x, self.pos.y, self.tamanho // 2, intensidade=4)

        rect = pygame.Rect(0, 0, self.tamanho, self.tamanho)
        rect.center = (int(self.pos.x), int(self.pos.y))
        pygame.draw.rect(surface, cor, rect, border_radius=4)
        pygame.draw.rect(surface, BRANCO, rect.inflate(-6, -6), border_radius=2)

        raio_anel = 16
        rect_anel = pygame.Rect(0, 0, raio_anel * 2, raio_anel * 2)
        rect_anel.center = (int(self.pos.x), int(self.pos.y))
        espessura = 5

        if self.dash_cooldown > 0:
            ratio = 1.0 - (self.dash_cooldown / 45.0)
            angulo_inicio = -math.pi / 2
            angulo_fim = angulo_inicio + (math.pi * 2 * ratio)
            pygame.draw.arc(surface, cor, rect_anel, angulo_inicio, angulo_fim, espessura)
        else:
            pygame.draw.circle(surface, cor, rect_anel.center, raio_anel, espessura)


class Inimigo:
    def __init__(self, x, y, tipo, velocidade):
        self.pos = pygame.math.Vector2(x, y)
        self.tipo = tipo
        self.raio = 12
        self.vel = velocidade
        self.dir = pygame.math.Vector2(0, 0)
        self.morto = False
        self.variante = 1

        self.estado_investida = "ESPERANDO"
        self.timer_investida = 0.0
        self.alvo_mira = pygame.math.Vector2(x, y)
        self.travado = False

        self.timer_explosao = 0.0
        self.explodiu = False

        self.timer_tiro = 0.0
        self.timer_rajada = 0.0
        self.em_rajada = True
        self.direcao_tiro = pygame.math.Vector2(1, 0)

        if self.tipo == "boss":
            self.raio = 40
            self.timer_habilidade = 0.0
            self.estado_boss = "PERSEGUINDO"

        if self.tipo == "quique":
            ang = random.uniform(0, math.pi * 2)
            self.dir = pygame.math.Vector2(math.cos(ang), math.sin(ang)) * self.vel

        if self.tipo == "metralhadora":
            self.raio = 15
            self.dir = pygame.math.Vector2(0, 0)
            self.padrao_tiro = random.randint(0, 2)
            self.angulo_espiral = random.uniform(0, 360)
            self.timer_vida = 0.0

    def update(self, player, lista_inimigos, dt, lista_particulas, interface_principal):
        if self.tipo == "perseguidor":
            pos_futura = player.pos + (player.vel * 12)
            vec_to_player = pos_futura - self.pos
            if vec_to_player.length() > 0:
                direcao_desejada = vec_to_player.normalize() * (self.vel * 0.9)
                onda = math.sin(time.time() * 6) * 40
                direcao_desejada = direcao_desejada.rotate(onda)
                self.dir = self.dir.lerp(direcao_desejada, 0.08)

        elif self.tipo == "investida":
            self.timer_investida += dt
            if self.estado_investida == "ESPERANDO":
                self.dir = self.dir.lerp(pygame.math.Vector2(0, 0), 0.1)
                self.travado = False
                if self.timer_investida > 1.2:
                    self.estado_investida = "MIRANDO"
                    self.timer_investida = 0.0

            elif self.estado_investida == "MIRANDO":
                if self.timer_investida < 0.5:
                    self.alvo_mira = pygame.math.Vector2(player.pos.x, player.pos.y)
                else:
                    self.travado = True

                if self.timer_investida > 0.9:
                    vec = self.alvo_mira - self.pos
                    if vec.length() > 0:
                        self.dir = vec.normalize() * (self.vel * 4.0)
                    self.estado_investida = "ATACANDO"
                    self.timer_investida = 0.0

            elif self.estado_investida == "ATACANDO":
                lista_particulas.append(Particula(self.pos.x, self.pos.y, LARANJA_NEON))
                if self.timer_investida > 0.8:
                    self.morto = True
                    for _ in range(15):
                        lista_particulas.append(Particula(self.pos.x, self.pos.y, LARANJA_NEON))

        elif self.tipo == "explosivo":
            self.timer_explosao += dt
            if self.timer_explosao < 3.5:
                vec_to_player = player.pos - self.pos
                if vec_to_player.length() > 0:
                    self.dir = self.dir.lerp(vec_to_player.normalize() * (self.vel * 0.6), 0.05)
            else:
                self.dir = self.dir * 0.9
                if self.timer_explosao > 4.5:
                    self.morto = True
                    self.explodiu = True
                    for _ in range(40):
                        lista_particulas.append(Particula(self.pos.x, self.pos.y, AMARELO_DADO))

        elif self.tipo == "boss":
            self.timer_habilidade += dt

            if self.estado_boss == "PERSEGUINDO":
                vec_to_player = player.pos - self.pos
                if vec_to_player.length() > 0:
                    self.dir = self.dir.lerp(vec_to_player.normalize() * self.vel, 0.03)

                if self.timer_habilidade > 3.0:
                    self.estado_boss = "INVOCANDO"
                    self.timer_habilidade = 0.0

            elif self.estado_boss == "INVOCANDO":
                self.dir *= 0.9

                if self.timer_habilidade > 1.0:
                    if self.variante % 3 == 1:
                        interface_principal.portais_inimigos.append(
                            {"pos": pygame.math.Vector2(self.pos.x, self.pos.y), "tipo": "explosivo", "vel": 3.5, "tempo": 0.8}
                        )
                        interface_principal.portais_inimigos.append(
                            {"pos": pygame.math.Vector2(self.pos.x, self.pos.y), "tipo": "perseguidor", "vel": 4.5, "tempo": 0.8}
                        )
                    elif self.variante % 3 == 2:
                        interface_principal.portais_inimigos.append(
                            {"pos": pygame.math.Vector2(self.pos.x, self.pos.y), "tipo": "investida", "vel": 6.0, "tempo": 0.8}
                        )
                        interface_principal.portais_inimigos.append(
                            {"pos": pygame.math.Vector2(self.pos.x, self.pos.y), "tipo": "metralhadora", "vel": 5.0, "tempo": 0.8}
                        )
                    else:
                        interface_principal.portais_inimigos.append(
                            {"pos": pygame.math.Vector2(self.pos.x, self.pos.y), "tipo": "quique", "vel": 7.0, "tempo": 0.8}
                        )
                        interface_principal.portais_inimigos.append(
                            {"pos": pygame.math.Vector2(self.pos.x, self.pos.y), "tipo": "quique", "vel": 7.0, "tempo": 0.8}
                        )

                    for _ in range(30):
                        lista_particulas.append(Particula(self.pos.x, self.pos.y, BRANCO))
                    self.estado_boss = "DASH"
                    self.timer_habilidade = 0.0

            elif self.estado_boss == "DASH":
                if self.timer_habilidade < 0.6:
                    self.dir *= 0.8
                elif self.timer_habilidade < 1.2:
                    if self.timer_habilidade - dt < 0.6:
                        vec_to_player = player.pos - self.pos
                        if vec_to_player.length() > 0:
                            self.dir = vec_to_player.normalize() * (self.vel * 5.0)
                        for _ in range(25):
                            lista_particulas.append(Particula(self.pos.x, self.pos.y, VERMELHO_SANGUE))
                else:
                    self.estado_boss = "PERSEGUINDO"
                    self.timer_habilidade = 0.0

        elif self.tipo == "metralhadora":
            self.dir = pygame.math.Vector2(0, 0)
            self.timer_vida += dt
            if self.timer_vida >= 10.0:
                self.morto = True
                for _ in range(10):
                    lista_particulas.append(Particula(self.pos.x, self.pos.y, ROXO_NEON))
                return

            self.timer_tiro += dt

            if self.padrao_tiro == 0:
                self.em_rajada = True
                intervalo_tiro = 0.58
                while self.timer_tiro >= intervalo_tiro:
                    self.timer_tiro -= intervalo_tiro
                    for angulo in range(0, 360, 45):
                        direcao_proj = pygame.math.Vector2(1, 0).rotate(angulo)
                        interface_principal.projeteis_inimigos.append(
                            {
                                "pos": pygame.math.Vector2(self.pos.x, self.pos.y),
                                "vel": direcao_proj * 9.2,
                                "raio": 8,
                                "tempo": 2.4,
                                "cor": ROXO_NEON,
                            }
                        )
                    self.direcao_tiro = pygame.math.Vector2(1, 0)
                    for _ in range(8):
                        lista_particulas.append(Particula(self.pos.x, self.pos.y, ROXO_NEON))

            elif self.padrao_tiro == 1:
                self.em_rajada = False
                intervalo_tiro = 0.22
                while self.timer_tiro >= intervalo_tiro:
                    self.timer_tiro -= intervalo_tiro
                    fase = int(time.time() * 8) % 2
                    angulo_base = 45 if fase else 0
                    for angulo in [angulo_base, angulo_base + 90, angulo_base + 180, angulo_base + 270]:
                        direcao_proj = pygame.math.Vector2(1, 0).rotate(angulo)
                        interface_principal.projeteis_inimigos.append(
                            {
                                "pos": pygame.math.Vector2(self.pos.x, self.pos.y),
                                "vel": direcao_proj * 9.8,
                                "raio": 8,
                                "tempo": 2.2,
                                "cor": ROXO_NEON,
                            }
                        )
                    self.direcao_tiro = pygame.math.Vector2(1, 0).rotate(angulo_base)
                    for _ in range(4):
                        lista_particulas.append(Particula(self.pos.x, self.pos.y, ROXO_NEON))

            else:
                self.em_rajada = True
                intervalo_tiro = 0.11
                while self.timer_tiro >= intervalo_tiro:
                    self.timer_tiro -= intervalo_tiro
                    self.angulo_espiral = (self.angulo_espiral + 20) % 360
                    direcao_a = pygame.math.Vector2(1, 0).rotate(self.angulo_espiral)
                    direcao_b = pygame.math.Vector2(1, 0).rotate(self.angulo_espiral + 180)
                    for direcao_proj in [direcao_a, direcao_b]:
                        interface_principal.projeteis_inimigos.append(
                            {
                                "pos": pygame.math.Vector2(self.pos.x, self.pos.y),
                                "vel": direcao_proj * 10.4,
                                "raio": 8,
                                "tempo": 2.0,
                                "cor": ROXO_NEON,
                            }
                        )
                    self.direcao_tiro = direcao_a
                    lista_particulas.append(Particula(self.pos.x, self.pos.y, ROXO_NEON))

        forca_repulsao = pygame.math.Vector2(0, 0)
        for vizinho in lista_inimigos:
            if vizinho != self:
                distancia = self.pos.distance_to(vizinho.pos)
                distancia_segura = self.raio + vizinho.raio + 5
                if 0 < distancia < distancia_segura:
                    if self.tipo == "quique":
                        normal = (self.pos - vizinho.pos).normalize()
                        if self.dir.length() > 0:
                            self.dir = self.dir.reflect(normal)
                        self.pos += normal * 3
                    else:
                        diferenca = self.pos - vizinho.pos
                        forca_repulsao += diferenca.normalize() * (distancia_segura - distancia) * 0.1

        if self.tipo == "metralhadora":
            self.dir = pygame.math.Vector2(0, 0)
        else:
            self.pos += self.dir + forca_repulsao

        if self.pos.x <= self.raio:
            self.pos.x = self.raio
            if self.tipo in ["quique", "explosivo", "boss", "metralhadora"]:
                self.dir.x *= -1
            elif self.tipo == "investida":
                self.dir.x = 0
                if self.estado_investida == "ATACANDO":
                    self.estado_investida = "ESPERANDO"
                    self.timer_investida = 0.0
        elif self.pos.x >= LARGURA_TELA - self.raio:
            self.pos.x = LARGURA_TELA - self.raio
            if self.tipo in ["quique", "explosivo", "boss", "metralhadora"]:
                self.dir.x *= -1
            elif self.tipo == "investida":
                self.dir.x = 0
                if self.estado_investida == "ATACANDO":
                    self.estado_investida = "ESPERANDO"
                    self.timer_investida = 0.0

        if self.pos.y <= 60 + self.raio:
            self.pos.y = 60 + self.raio
            if self.tipo in ["quique", "explosivo", "boss", "metralhadora"]:
                self.dir.y *= -1
            elif self.tipo == "investida":
                self.dir.y = 0
                if self.estado_investida == "ATACANDO":
                    self.estado_investida = "ESPERANDO"
                    self.timer_investida = 0.0
        elif self.pos.y >= ALTURA_TELA - self.raio:
            self.pos.y = ALTURA_TELA - self.raio
            if self.tipo in ["quique", "explosivo", "boss", "metralhadora"]:
                self.dir.y *= -1
            elif self.tipo == "investida":
                self.dir.y = 0
                if self.estado_investida == "ATACANDO":
                    self.estado_investida = "ESPERANDO"
                    self.timer_investida = 0.0

    def draw(self, surface):
        cor_base = ROSA_NEON
        if self.tipo == "perseguidor":
            cor_base = VERMELHO_SANGUE
        elif self.tipo == "investida":
            cor_base = LARANJA_NEON
        elif self.tipo == "explosivo":
            cor_base = AMARELO_DADO
        elif self.tipo == "metralhadora":
            cor_base = ROXO_NEON

        if self.tipo == "investida" and self.estado_investida == "MIRANDO":
            cor_linha = VERMELHO_SANGUE if not self.travado else BRANCO
            espessura = 2 if not self.travado else 4
            pygame.draw.line(surface, cor_linha, self.pos, self.alvo_mira, espessura)
            if self.travado:
                cor_base = BRANCO

        if self.tipo == "explosivo":
            if self.timer_explosao > 2.5:
                if int(self.timer_explosao * 15) % 2 == 0:
                    cor_base = BRANCO
            desenhar_brilho_neon(surface, cor_base, self.pos.x, self.pos.y, self.raio, intensidade=4)
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

        elif self.tipo == "boss":
            cor_boss = ROXO_NEON if self.variante % 3 == 1 else (CIANO_NEON if self.variante % 3 == 2 else ROSA_NEON)
            tempo = time.time()

            for i in range(3):
                angulo = tempo * 4 + (i * math.pi * 2 / 3)
                distancia_orbe = self.raio + 35 if self.estado_boss == "DASH" else self.raio + 15
                x_orb = self.pos.x + math.cos(angulo) * distancia_orbe
                y_orb = self.pos.y + math.sin(angulo) * distancia_orbe

                pygame.draw.line(surface, cor_boss, self.pos, (x_orb, y_orb), 2)
                pygame.draw.circle(surface, VERMELHO_SANGUE, (int(x_orb), int(y_orb)), 8)
                desenhar_brilho_neon(surface, VERMELHO_SANGUE, x_orb, y_orb, 8, 2)
                pygame.draw.circle(surface, BRANCO, (int(x_orb), int(y_orb)), 3)

            if self.estado_boss == "DASH":
                cor_atual = VERMELHO_SANGUE
            elif self.estado_boss == "INVOCANDO":
                cor_atual = BRANCO
            else:
                cor_atual = cor_boss

            desenhar_brilho_neon(surface, cor_atual, self.pos.x, self.pos.y, self.raio, intensidade=5)
            pygame.draw.circle(surface, cor_atual, (int(self.pos.x), int(self.pos.y)), self.raio)
            pygame.draw.circle(surface, PRETO_FUNDO, (int(self.pos.x), int(self.pos.y)), self.raio - 6)

            pulso = abs(math.sin(tempo * 10)) * (self.raio // 1.5)
            pygame.draw.circle(surface, VERMELHO_SANGUE, (int(self.pos.x), int(self.pos.y)), int(pulso))

        elif self.tipo == "metralhadora":
            pulso = abs(math.sin(time.time() * 8))
            cor_nucleo = BRANCO if self.em_rajada else CIANO_NEON
            desenhar_brilho_neon(surface, cor_base, self.pos.x, self.pos.y, self.raio + (pulso * 2), intensidade=4)
            pygame.draw.circle(surface, cor_base, (int(self.pos.x), int(self.pos.y)), self.raio)
            pygame.draw.circle(surface, AZUL_ESCURO, (int(self.pos.x), int(self.pos.y)), self.raio - 5)
            pygame.draw.circle(surface, cor_nucleo, (int(self.pos.x), int(self.pos.y)), 5)

            if self.direcao_tiro.length() > 0:
                ponta = self.pos + self.direcao_tiro.normalize() * (self.raio + 14)
                pygame.draw.line(surface, cor_nucleo, self.pos, ponta, 4)
                pygame.draw.circle(surface, cor_nucleo, (int(ponta.x), int(ponta.y)), 4)

        else:
            desenhar_brilho_neon(surface, cor_base, self.pos.x, self.pos.y, self.raio, intensidade=3)
            pygame.draw.circle(surface, cor_base, (int(self.pos.x), int(self.pos.y)), self.raio)
            pygame.draw.circle(surface, BRANCO, (int(self.pos.x), int(self.pos.y)), self.raio // 3)


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
