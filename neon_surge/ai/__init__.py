from .base import BaseAI
from .chaser import ChaserAI
from .charge import ChargeAI
from .explosive import ExplosiveAI
from .bounce import BounceAI
from .shooter import MetralhadoraAI, MinibossSniperAI, MinibossEspiralaAI, MinibossCacadorAI, MinibossEscudoAI, MorteiroAI
from .bosses import BossAI, BossArtilhariaAI, BossCaoticoAI

AI_MAPPING = {
    "perseguidor": ChaserAI,
    "investida": ChargeAI,
    "explosivo": ExplosiveAI,
    "quique": BounceAI,
    "boss": BossAI,
    "boss_artilharia": BossArtilhariaAI,
    "boss_caotico": BossCaoticoAI,
    "metralhadora": MetralhadoraAI,
    "morteiro": MorteiroAI,
    "miniboss_espiral": MinibossEspiralaAI,
    "miniboss_cacador": MinibossCacadorAI,
    "miniboss_escudo": MinibossEscudoAI,
    "miniboss_sniper": MinibossSniperAI,
}

def get_ai_for_type(tipo):
    ai_class = AI_MAPPING.get(tipo, BaseAI)
    return ai_class()
