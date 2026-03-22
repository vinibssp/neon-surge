from .base import BaseAI
import pygame
import time
import random
from ..entities.particle import Particula
from ..constants import (
    VERMELHO_SANGUE, LARANJA_NEON, ROSA_NEON, BRANCO
)

class BossAI(BaseAI):
    def update(self, enemy, player, lista_inimigos, dt, lista_particulas, interface_principal, sound_manager):
        enemy.timer_habilidade += dt
        enemy.timer_tiro += dt

        intervalo_tiro = max(0.42, 0.85 - (enemy.variante * 0.06))
        if enemy.estado_boss == "PERSEGUINDO" and enemy.timer_tiro >= intervalo_tiro:
            enemy.timer_tiro = 0.0
            sound_manager.play('enemy_shoot')
            vec = player.pos - enemy.pos
            if vec.length_squared() > 0:
                direcao_base = vec.normalize()
                spread = 8 + min(14, enemy.variante * 2)
                quantidade = 3 if enemy.variante < 3 else 5
                offsets = [-spread, 0, spread] if quantidade == 3 else [-spread * 1.6, -spread * 0.7, 0, spread * 0.7, spread * 1.6]
                velocidade_proj = 8.6 + min(2.4, enemy.variante * 0.35)
                for off in offsets:
                    direcao_proj = direcao_base.rotate(off)
                    interface_principal.projeteis_inimigos.append(
                        {
                            "pos": pygame.math.Vector2(enemy.pos.x, enemy.pos.y),
                            "vel": direcao_proj * velocidade_proj,
                            "raio": 8,
                            "tempo": 2.5,
                            "cor": VERMELHO_SANGUE,
                        }
                    )
                for _ in range(6):
                    lista_particulas.append(Particula(enemy.pos.x, enemy.pos.y, VERMELHO_SANGUE))

        if enemy.estado_boss == "PERSEGUINDO":
            vec_to_player = player.pos - enemy.pos
            if vec_to_player.length() > 0:
                enemy.dir = enemy.dir.lerp(vec_to_player.normalize() * enemy.vel, 0.03)

            if enemy.timer_habilidade > 3.0:
                enemy.estado_boss = "INVOCANDO"
                enemy.timer_habilidade = 0.0

        elif enemy.estado_boss == "INVOCANDO":
            enemy.dir *= 0.9

            if enemy.timer_habilidade > 1.0:
                if enemy.variante % 3 == 1:
                    interface_principal.portais_inimigos.append(
                        {"pos": pygame.math.Vector2(enemy.pos.x, enemy.pos.y), "tipo": "explosivo", "vel": 3.5, "tempo": 0.8}
                    )
                    interface_principal.portais_inimigos.append(
                        {"pos": pygame.math.Vector2(enemy.pos.x, enemy.pos.y), "tipo": "perseguidor", "vel": 4.5, "tempo": 0.8}
                    )
                elif enemy.variante % 3 == 2:
                    interface_principal.portais_inimigos.append(
                        {"pos": pygame.math.Vector2(enemy.pos.x, enemy.pos.y), "tipo": "investida", "vel": 6.0, "tempo": 0.8}
                    )
                    interface_principal.portais_inimigos.append(
                        {"pos": pygame.math.Vector2(enemy.pos.x, enemy.pos.y), "tipo": "metralhadora", "vel": 4.7, "tempo": 0.8}
                    )
                else:
                    interface_principal.portais_inimigos.append(
                        {"pos": pygame.math.Vector2(enemy.pos.x, enemy.pos.y), "tipo": "quique", "vel": 7.0, "tempo": 0.8}
                    )
                    interface_principal.portais_inimigos.append(
                        {"pos": pygame.math.Vector2(enemy.pos.x, enemy.pos.y), "tipo": "quique", "vel": 7.0, "tempo": 0.8}
                    )
                    if enemy.variante >= 2:
                        interface_principal.portais_inimigos.append(
                            {
                                "pos": pygame.math.Vector2(enemy.pos.x, enemy.pos.y),
                                "tipo": "miniboss_espiral",
                                "vel": 0.0,
                                "tempo": 1.0,
                            }
                        )

                for _ in range(30):
                    lista_particulas.append(Particula(enemy.pos.x, enemy.pos.y, BRANCO))
                enemy.estado_boss = "DASH"
                enemy.timer_habilidade = 0.0

        elif enemy.estado_boss == "DASH":
            if enemy.timer_habilidade < 0.6:
                enemy.dir *= 0.8
            elif enemy.timer_habilidade < 1.2:
                if enemy.timer_habilidade - dt < 0.6:
                    sound_manager.play('player_dash')
                    vec_to_player = player.pos - enemy.pos
                    if vec_to_player.length() > 0:
                        enemy.dir = vec_to_player.normalize() * (enemy.vel * 5.0)
                    for _ in range(25):
                        lista_particulas.append(Particula(enemy.pos.x, enemy.pos.y, VERMELHO_SANGUE))
            else:
                enemy.estado_boss = "PERSEGUINDO"
                enemy.timer_habilidade = 0.0


class BossArtilhariaAI(BaseAI):
    def update(self, enemy, player, lista_inimigos, dt, lista_particulas, interface_principal, sound_manager):
        enemy.timer_habilidade += dt
        enemy.timer_tiro += dt

        vec_to_player = player.pos - enemy.pos
        if vec_to_player.length_squared() > 0:
            alvo = vec_to_player.normalize().rotate(90) * (enemy.vel * 0.8)
            enemy.dir = enemy.dir.lerp(alvo, 0.04)

        if enemy.timer_tiro >= max(0.9, 1.35 - (enemy.variante * 0.06)):
            enemy.timer_tiro = 0.0
            sound_manager.play('enemy_shoot')
            passos = 10 + min(6, enemy.variante)
            velocidade_proj = 8.2 + min(2.0, enemy.variante * 0.25)
            for ang in range(0, 360, max(18, 360 // passos)):
                direcao_proj = pygame.math.Vector2(1, 0).rotate(ang + (enemy.timer_habilidade * 40))
                interface_principal.projeteis_inimigos.append(
                    {
                        "pos": pygame.math.Vector2(enemy.pos.x, enemy.pos.y),
                        "vel": direcao_proj * velocidade_proj,
                        "raio": 8,
                        "tempo": 2.4,
                        "cor": LARANJA_NEON,
                    }
                )
            for _ in range(16):
                lista_particulas.append(Particula(enemy.pos.x, enemy.pos.y, LARANJA_NEON))

        if enemy.timer_habilidade >= 4.3:
            enemy.timer_habilidade = 0.0
            interface_principal.portais_inimigos.append(
                {
                    "pos": pygame.math.Vector2(enemy.pos.x, enemy.pos.y),
                    "tipo": random.choice(["miniboss_cacador", "miniboss_sniper"]),
                    "vel": 6.0,
                    "tempo": 0.85,
                }
            )


class BossCaoticoAI(BaseAI):
    def update(self, enemy, player, lista_inimigos, dt, lista_particulas, interface_principal, sound_manager):
        enemy.timer_habilidade += dt
        enemy.timer_tiro += dt

        vec_to_player = player.pos - enemy.pos
        if vec_to_player.length_squared() > 0:
            direcao = vec_to_player.normalize() * (enemy.vel * 1.1)
            enemy.dir = enemy.dir.lerp(direcao, 0.06)

        if enemy.timer_tiro >= max(0.34, 0.62 - (enemy.variante * 0.03)) and vec_to_player.length_squared() > 0:
            enemy.timer_tiro = 0.0
            sound_manager.play('enemy_shoot')
            base = vec_to_player.normalize()
            for off in [-24, -10, 0, 10, 24]:
                direcao_proj = base.rotate(off)
                interface_principal.projeteis_inimigos.append(
                    {
                        "pos": pygame.math.Vector2(enemy.pos.x, enemy.pos.y),
                        "vel": direcao_proj * (9.2 + min(2.2, enemy.variante * 0.3)),
                        "raio": 7,
                        "tempo": 2.2,
                        "cor": ROSA_NEON,
                    }
                )

        if enemy.timer_habilidade >= 3.2 and vec_to_player.length_squared() > 0:
            enemy.timer_habilidade = 0.0
            sound_manager.play('enemy_shoot')
            enemy.dir = vec_to_player.normalize() * (enemy.vel * 4.6)
            for _ in range(22):
                lista_particulas.append(Particula(enemy.pos.x, enemy.pos.y, ROSA_NEON))
