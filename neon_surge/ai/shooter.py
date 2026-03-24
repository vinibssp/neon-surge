from .base import BaseAI
import pygame
import time
import random
from ..entities.particle import Particula
from ..constants import (
    ROXO_NEON, VERMELHO_SANGUE, CIANO_NEON, AMARELO_DADO, LARANJA_NEON
)

class MetralhadoraAI(BaseAI):
    def update(self, enemy, player, lista_inimigos, dt, lista_particulas, interface_principal, sound_manager):
        is_hardcore = getattr(interface_principal, "modo_jogo", "") == "HARDCORE"
        mult_vel = 1.6 if is_hardcore else 1.0
        mult_fire = 0.5 if is_hardcore else 1.0

        enemy.dir = pygame.math.Vector2(0, 0)
        enemy.timer_vida += dt
        if enemy.timer_vida >= (10.0 if not is_hardcore else 15.0):
            enemy.morto = True
            for _ in range(10):
                lista_particulas.append(Particula(enemy.pos.x, enemy.pos.y, ROXO_NEON))
            return

        enemy.timer_tiro += dt

        if enemy.padrao_tiro == 0:
            enemy.em_rajada = True
            intervalo_tiro = 0.64 * mult_fire
            while enemy.timer_tiro >= intervalo_tiro:
                enemy.timer_tiro -= intervalo_tiro
                sound_manager.play('enemy_shoot')
                for angulo in range(0, 360, 45):
                    direcao_proj = pygame.math.Vector2(1, 0).rotate(angulo)
                    interface_principal.projeteis_inimigos.append(
                        {
                            "pos": pygame.math.Vector2(enemy.pos.x, enemy.pos.y),
                            "vel": direcao_proj * 8.3 * mult_vel,
                            "raio": 8,
                            "tempo": 2.5,
                            "cor": ROXO_NEON,
                        }
                    )
                enemy.direcao_tiro = pygame.math.Vector2(1, 0)
                for _ in range(8):
                    lista_particulas.append(Particula(enemy.pos.x, enemy.pos.y, ROXO_NEON))

        elif enemy.padrao_tiro == 1:
            enemy.em_rajada = False
            intervalo_tiro = 0.26 * mult_fire
            while enemy.timer_tiro >= intervalo_tiro:
                enemy.timer_tiro -= intervalo_tiro
                sound_manager.play('enemy_shoot')
                fase = int(time.time() * 8) % 2
                angulo_base = 45 if fase else 0
                for angulo in [angulo_base, angulo_base + 90, angulo_base + 180, angulo_base + 270]:
                    direcao_proj = pygame.math.Vector2(1, 0).rotate(angulo)
                    interface_principal.projeteis_inimigos.append(
                        {
                            "pos": pygame.math.Vector2(enemy.pos.x, enemy.pos.y),
                            "vel": direcao_proj * 8.7 * mult_vel,
                            "raio": 8,
                            "tempo": 2.4,
                            "cor": ROXO_NEON,
                        }
                    )
                enemy.direcao_tiro = pygame.math.Vector2(1, 0).rotate(angulo_base)
                for _ in range(4):
                    lista_particulas.append(Particula(enemy.pos.x, enemy.pos.y, ROXO_NEON))


class MinibossEspiralaAI(BaseAI):
    def update(self, enemy, player, lista_inimigos, dt, lista_particulas, interface_principal, sound_manager):
        is_hardcore = getattr(interface_principal, "modo_jogo", "") == "HARDCORE"
        mult_vel = 1.5 if is_hardcore else 1.0
        mult_fire = 0.6 if is_hardcore else 1.0

        enemy.dir = pygame.math.Vector2(0, 0)
        enemy.timer_vida += dt
        if enemy.timer_vida >= (14.0 if not is_hardcore else 20.0):
            enemy.morto = True
            sound_manager.play('enemy_death')
            for _ in range(20):
                lista_particulas.append(Particula(enemy.pos.x, enemy.pos.y, ROXO_NEON))
            return

        enemy.em_rajada = True
        enemy.timer_tiro += dt
        intervalo_tiro = 0.13 * mult_fire
        while enemy.timer_tiro >= intervalo_tiro:
            enemy.timer_tiro -= intervalo_tiro
            sound_manager.play('enemy_shoot')
            enemy.angulo_espiral = (enemy.angulo_espiral + (17 if not is_hardcore else 25)) % 360
            direcao_a = pygame.math.Vector2(1, 0).rotate(enemy.angulo_espiral)
            direcao_b = pygame.math.Vector2(1, 0).rotate(enemy.angulo_espiral + 180)
            for direcao_proj in [direcao_a, direcao_b]:
                interface_principal.projeteis_inimigos.append(
                    {
                        "pos": pygame.math.Vector2(enemy.pos.x, enemy.pos.y),
                        "vel": direcao_proj * 9.6 * mult_vel,
                        "raio": 9,
                        "tempo": 2.6,
                        "cor": ROXO_NEON,
                    }
                )
            enemy.direcao_tiro = direcao_a
            lista_particulas.append(Particula(enemy.pos.x, enemy.pos.y, ROXO_NEON))


class MinibossCacadorAI(BaseAI):
    def update(self, enemy, player, lista_inimigos, dt, lista_particulas, interface_principal, sound_manager):
        is_hardcore = getattr(interface_principal, "modo_jogo", "") == "HARDCORE"
        mult_vel = 1.4 if is_hardcore else 1.0
        mult_fire = 0.65 if is_hardcore else 1.0

        vec_to_player = player.pos - enemy.pos
        if vec_to_player.length_squared() > 0:
            direcao = vec_to_player.normalize() * (enemy.vel * (1.08 if not is_hardcore else 1.4))
            enemy.dir = enemy.dir.lerp(direcao, 0.08)

        enemy.timer_tiro += dt
        if enemy.timer_tiro >= (1.1 * mult_fire) and vec_to_player.length_squared() > 0:
            enemy.timer_tiro = 0.0
            sound_manager.play('enemy_shoot')
            base = vec_to_player.normalize()
            for off in ([-14, 0, 14] if not is_hardcore else [-20, -10, 0, 10, 20]):
                direcao_proj = base.rotate(off)
                interface_principal.projeteis_inimigos.append(
                    {
                        "pos": pygame.math.Vector2(enemy.pos.x, enemy.pos.y),
                        "vel": direcao_proj * 8.9 * mult_vel,
                        "raio": 8,
                        "tempo": 2.3,
                        "cor": VERMELHO_SANGUE,
                    }
                )
            for _ in range(6):
                lista_particulas.append(Particula(enemy.pos.x, enemy.pos.y, VERMELHO_SANGUE))


class MinibossEscudoAI(BaseAI):
    def update(self, enemy, player, lista_inimigos, dt, lista_particulas, interface_principal, sound_manager):
        import math
        is_hardcore = getattr(interface_principal, "modo_jogo", "") == "HARDCORE"
        mult_vel = 1.3 if is_hardcore else 1.0
        mult_fire = 0.7 if is_hardcore else 1.0

        enemy.timer_tiro += dt
        enemy.timer_habilidade += dt
        enemy.orbita_angulo += dt * (1.8 if not is_hardcore else 2.5)

        alvo_orbita = player.pos + pygame.math.Vector2(math.cos(enemy.orbita_angulo), math.sin(enemy.orbita_angulo)) * 140
        vec = alvo_orbita - enemy.pos
        if vec.length_squared() > 0:
            enemy.dir = enemy.dir.lerp(vec.normalize() * (enemy.vel * (0.95 if not is_hardcore else 1.3)), 0.09)

        if enemy.timer_tiro >= (1.45 * mult_fire):
            enemy.timer_tiro = 0.0
            sound_manager.play('enemy_shoot')
            for ang in range(0, 360, (60 if not is_hardcore else 30)):
                direcao_proj = pygame.math.Vector2(1, 0).rotate(ang + (enemy.timer_habilidade * 35))
                interface_principal.projeteis_inimigos.append(
                    {
                        "pos": pygame.math.Vector2(enemy.pos.x, enemy.pos.y),
                        "vel": direcao_proj * 7.8 * mult_vel,
                        "raio": 7,
                        "tempo": 2.6,
                        "cor": CIANO_NEON,
                    }
                )


class MinibossSniperAI(BaseAI):
    def update(self, enemy, player, lista_inimigos, dt, lista_particulas, interface_principal, sound_manager):
        is_hardcore = getattr(interface_principal, "modo_jogo", "") == "HARDCORE"
        mult_vel = 1.8 if is_hardcore else 1.0
        mult_fire = 0.6 if is_hardcore else 1.0

        enemy.dir = pygame.math.Vector2(0, 0)
        enemy.timer_tiro += dt

        if enemy.estado_sniper == "MIRANDO":
            enemy.alvo_mira = pygame.math.Vector2(player.pos.x, player.pos.y)
            if enemy.timer_tiro >= (1.15 * mult_fire):
                enemy.estado_sniper = "DISPARANDO"
                enemy.timer_tiro = 0.0
        else:
            vec = enemy.alvo_mira - enemy.pos
            if vec.length_squared() > 0:
                sound_manager.play('enemy_shoot')
                direcao_proj = vec.normalize()
                interface_principal.projeteis_inimigos.append(
                    {
                        "pos": pygame.math.Vector2(enemy.pos.x, enemy.pos.y),
                        "vel": direcao_proj * 11.6 * mult_vel,
                        "raio": 9,
                        "tempo": 1.9,
                        "cor": AMARELO_DADO,
                    }
                )
            enemy.estado_sniper = "MIRANDO"
            enemy.timer_tiro = 0.0

class MorteiroAI(BaseAI):
    def update(self, enemy, player, lista_inimigos, dt, lista_particulas, interface_principal, sound_manager):
        is_hardcore = getattr(interface_principal, "modo_jogo", "") == "HARDCORE"
        mult_fire = 0.55 if is_hardcore else 1.0

        # Morteiro fica parado
        enemy.dir = pygame.math.Vector2(0, 0)
        
        # Vida limitada para o morteiro também
        if not hasattr(enemy, 'timer_vida'):
            enemy.timer_vida = 0.0
        
        enemy.timer_vida += dt
        if enemy.timer_vida >= (12.0 if not is_hardcore else 18.0):
            enemy.morto = True
            enemy.explodiu = True
            for _ in range(30):
                lista_particulas.append(Particula(enemy.pos.x, enemy.pos.y, LARANJA_NEON))
            return

        enemy.timer_tiro += dt
        intervalo_tiro = 2.0 * mult_fire # Atira muito mais rápido no Hardcore
        
        if enemy.timer_tiro >= intervalo_tiro:
            enemy.timer_tiro = 0
            sound_manager.play('enemy_shoot')
            
            # Alvo é a posição atual do player com um pouco de erro aleatório
            alvo = pygame.math.Vector2(player.pos.x, player.pos.y)
            # Menor erro aleatório no Hardcore (mira mais precisa)
            margem = 30 if not is_hardcore else 10
            alvo.x += random.uniform(-margem, margem)
            alvo.y += random.uniform(-margem, margem)
            
            # Adiciona uma "bomba" que é um projétil especial
            interface_principal.projeteis_inimigos.append({
                "pos": pygame.math.Vector2(enemy.pos.x, enemy.pos.y),
                "alvo_final": alvo,
                "tipo": "bomba",
                "timer_queda": 1.2 * mult_fire,  # Cai mais rápido no Hardcore
                "timer_total": 1.2 * mult_fire,
                "raio_explosao": 70 if not is_hardcore else 100, # Explosão maior no Hardcore
                "cor": LARANJA_NEON,
                "explodiu": False
            })
            
            for _ in range(5):
                lista_particulas.append(Particula(enemy.pos.x, enemy.pos.y, LARANJA_NEON))
