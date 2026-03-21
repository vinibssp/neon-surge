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
        self.tamanho = 16
        self.dash_cooldown = 0
        self.dash_timer = 0
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

        if dir_x != 0 or dir_y != 0:
            move_vec = pygame.math.Vector2(dir_x, dir_y).normalize()
            self.vel += move_vec * self.aceleracao

        if teclas[pygame.K_SPACE] and self.dash_cooldown <= 0 and self.vel.length() > 0:
            self.vel = self.vel.normalize() * 25
            self.dash_timer = 10
            self.dash_cooldown = 45
            return True

        if self.dash_timer > 0:
            self.dash_timer -= 1
            self.invencivel = True
            for _ in range(3):
                lista_particulas.append(Particula(self.pos.x, self.pos.y, CIANO_NEON))
        else:
            self.invencivel = False

        if self.dash_cooldown > 0:
            self.dash_cooldown -= 1

        self.vel *= self.atrito
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

        if self.tipo == "boss":
            self.raio = 40
            self.timer_habilidade = 0.0
            self.estado_boss = "PERSEGUINDO"

        if self.tipo == "quique":
            ang = random.uniform(0, math.pi * 2)
            self.dir = pygame.math.Vector2(math.cos(ang), math.sin(ang)) * self.vel

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
                            {"pos": pygame.math.Vector2(self.pos.x, self.pos.y), "tipo": "explosivo", "vel": 3.5, "tempo": 1.5}
                        )
                        interface_principal.portais_inimigos.append(
                            {"pos": pygame.math.Vector2(self.pos.x, self.pos.y), "tipo": "perseguidor", "vel": 4.5, "tempo": 1.5}
                        )
                    elif self.variante % 3 == 2:
                        interface_principal.portais_inimigos.append(
                            {"pos": pygame.math.Vector2(self.pos.x, self.pos.y), "tipo": "investida", "vel": 6.0, "tempo": 1.5}
                        )
                        interface_principal.portais_inimigos.append(
                            {"pos": pygame.math.Vector2(self.pos.x, self.pos.y), "tipo": "investida", "vel": 6.0, "tempo": 1.5}
                        )
                    else:
                        interface_principal.portais_inimigos.append(
                            {"pos": pygame.math.Vector2(self.pos.x, self.pos.y), "tipo": "quique", "vel": 7.0, "tempo": 1.5}
                        )
                        interface_principal.portais_inimigos.append(
                            {"pos": pygame.math.Vector2(self.pos.x, self.pos.y), "tipo": "quique", "vel": 7.0, "tempo": 1.5}
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

        self.pos += self.dir + forca_repulsao

        if self.pos.x <= self.raio:
            self.pos.x = self.raio
            if self.tipo in ["quique", "explosivo", "boss"]:
                self.dir.x *= -1
            elif self.tipo == "investida":
                self.dir.x = 0
                if self.estado_investida == "ATACANDO":
                    self.estado_investida = "ESPERANDO"
                    self.timer_investida = 0.0
        elif self.pos.x >= LARGURA_TELA - self.raio:
            self.pos.x = LARGURA_TELA - self.raio
            if self.tipo in ["quique", "explosivo", "boss"]:
                self.dir.x *= -1
            elif self.tipo == "investida":
                self.dir.x = 0
                if self.estado_investida == "ATACANDO":
                    self.estado_investida = "ESPERANDO"
                    self.timer_investida = 0.0

        if self.pos.y <= 60 + self.raio:
            self.pos.y = 60 + self.raio
            if self.tipo in ["quique", "explosivo", "boss"]:
                self.dir.y *= -1
            elif self.tipo == "investida":
                self.dir.y = 0
                if self.estado_investida == "ATACANDO":
                    self.estado_investida = "ESPERANDO"
                    self.timer_investida = 0.0
        elif self.pos.y >= ALTURA_TELA - self.raio:
            self.pos.y = ALTURA_TELA - self.raio
            if self.tipo in ["quique", "explosivo", "boss"]:
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

        else:
            desenhar_brilho_neon(surface, cor_base, self.pos.x, self.pos.y, self.raio, intensidade=3)
            pygame.draw.circle(surface, cor_base, (int(self.pos.x), int(self.pos.y)), self.raio)
            pygame.draw.circle(surface, BRANCO, (int(self.pos.x), int(self.pos.y)), self.raio // 3)
