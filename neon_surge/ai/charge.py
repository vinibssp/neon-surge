from .base import BaseAI
import pygame
from ..entities.particle import Particula
from ..constants import LARANJA_NEON

class ChargeAI(BaseAI):
    def update(self, enemy, player, lista_inimigos, dt, lista_particulas, interface_principal, sound_manager):
        enemy.timer_investida += dt
        if enemy.estado_investida == "ESPERANDO":
            enemy.dir = enemy.dir.lerp(pygame.math.Vector2(0, 0), 0.1)
            enemy.travado = False
            if enemy.timer_investida > 1.2:
                enemy.estado_investida = "MIRANDO"
                enemy.timer_investida = 0.0

        elif enemy.estado_investida == "MIRANDO":
            if enemy.timer_investida < 0.5:
                enemy.alvo_mira = pygame.math.Vector2(player.pos.x, player.pos.y)
            else:
                enemy.travado = True

            if enemy.timer_investida > 0.9:
                vec = enemy.alvo_mira - enemy.pos
                if vec.length() > 0:
                    enemy.dir = vec.normalize() * (enemy.vel * 4.0)
                    sound_manager.play('enemy_shoot')
                enemy.estado_investida = "ATACANDO"
                enemy.timer_investida = 0.0

        elif enemy.estado_investida == "ATACANDO":
            lista_particulas.append(Particula(enemy.pos.x, enemy.pos.y, LARANJA_NEON))
            if enemy.timer_investida > 0.8:
                enemy.morto = True
                for _ in range(15):
                    lista_particulas.append(Particula(enemy.pos.x, enemy.pos.y, LARANJA_NEON))
