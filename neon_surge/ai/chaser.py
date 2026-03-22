from .base import BaseAI
import math
import time

class ChaserAI(BaseAI):
    def update(self, enemy, player, lista_inimigos, dt, lista_particulas, interface_principal, sound_manager):
        pos_futura = player.pos + (player.vel * 12)
        vec_to_player = pos_futura - enemy.pos
        if vec_to_player.length() > 0:
            direcao_desejada = vec_to_player.normalize() * (enemy.vel * 0.9)
            onda = math.sin(time.time() * 6) * 40
            direcao_desejada = direcao_desejada.rotate(onda)
            enemy.dir = enemy.dir.lerp(direcao_desejada, 0.08)
