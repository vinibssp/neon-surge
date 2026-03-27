from __future__ import annotations

from game.components.data_components import BossComponent, EnemyKindComponent, LabyrinthVirusComponent
from game.ecs.entity import Entity


_FRIENDLY_NAMES: dict[str, str] = {
    "boss": "Boss Prime",
    "boss_artilharia": "Boss Artilharia",
    "boss_caotico": "Boss Caotico",
    "boss_colosso_laser": "Boss Colosso Laser",
    "boss_druida_toxico": "Boss Druida Toxico",
    "boss_soberano_espectral": "Boss Soberano Espectral",
    "virus_chaser": "Virus Cacador",
    "virus_interceptor": "Virus Interceptor",
}


def enemy_kind_from_entity(entity: Entity) -> str | None:
    identity = entity.get_component(EnemyKindComponent)
    if identity is not None and identity.kind.strip() != "":
        return identity.kind

    boss = entity.get_component(BossComponent)
    if boss is not None and boss.boss_kind.strip() != "":
        return boss.boss_kind

    virus = entity.get_component(LabyrinthVirusComponent)
    if virus is not None and virus.behavior_kind.strip() != "":
        return f"virus_{virus.behavior_kind}"

    return None


def format_enemy_name(kind: str | None) -> str:
    if kind is None or kind.strip() == "":
        return "Inimigo desconhecido"
    if kind in _FRIENDLY_NAMES:
        return _FRIENDLY_NAMES[kind]
    return kind.replace("_", " ").title()
