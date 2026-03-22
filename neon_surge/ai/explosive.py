from .base import BaseAI
from ..entities.particle import Particula
from ..constants import AMARELO_DADO

class ExplosiveAI(BaseAI):
    def update(self, enemy, player, lista_inimigos, dt, lista_particulas, interface_principal, sound_manager):
        enemy.timer_explosao += dt
        if enemy.timer_explosao < 3.5:
            vec_to_player = player.pos - enemy.pos
            if vec_to_player.length() > 0:
                enemy.dir = enemy.dir.lerp(vec_to_player.normalize() * (enemy.vel * 0.6), 0.05)
        else:
            enemy.dir = enemy.dir * 0.9
            if enemy.timer_explosao > 4.5:
                enemy.morto = True
                enemy.explodiu = True
                for _ in range(40):
                    lista_particulas.append(Particula(enemy.pos.x, enemy.pos.y, AMARELO_DADO))
