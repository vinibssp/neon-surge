from .base import BaseAI
import math
import time

class ChaserAI(BaseAI):
    def update(self, enemy, player, lista_inimigos, dt, lista_particulas, interface_principal, sound_manager):
        is_treino = getattr(interface_principal, "modo_jogo", "") == "TREINO"
        
        # No treino, a predição é mais agressiva
        fator_predicao = 18 if is_treino else 12
        pos_futura = player.pos + (player.vel * fator_predicao)
        
        vec_to_player = pos_futura - enemy.pos
        if vec_to_player.length() > 0:
            vel_multi = 1.15 if is_treino else 0.9
            direcao_desejada = vec_to_player.normalize() * (enemy.vel * vel_multi)
            
            # Movimento levemente senoidal para evitar ser muito linear
            onda = math.sin(time.time() * (8 if is_treino else 6)) * (25 if is_treino else 40)
            direcao_desejada = direcao_desejada.rotate(onda)
            
            # Interpolação mais rápida no treino (mais reativo)
            lerp_speed = 0.12 if is_treino else 0.08
            enemy.dir = enemy.dir.lerp(direcao_desejada, lerp_speed)
