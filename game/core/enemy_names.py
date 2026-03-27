from __future__ import annotations

from game.components.data_components import BossComponent, EnemyKindComponent, LabyrinthVirusComponent
from game.ecs.entity import Entity


_FRIENDLY_NAMES: dict[str, str] = {
    "follower": "Neon Pursuer",
    "shooter": "Arcshot Sentry",
    "quique": "Ricochet Imp",
    "investida": "Rift Charger",
    "explosivo": "Blast Wisp",
    "metralhadora": "Burst Turret",
    "morteiro": "Siege Mortar",
    "estrafador_arcano": "Arcane Strafer",
    "emboscador_escopeta": "Scatter Stalker",
    "orbitador_hex": "Hex Orbiter",
    "sombra_investida": "Shadow Pouncer",
    "bombardeiro_runa": "Runic Bombardier",
    "atirador_laser": "Laser Marksman",
    "kamehameha": "Nova Channeler",
    "lanca_chamas": "Flame Lancer",
    "fantasma": "Blink Specter",
    "buffer": "Aegis Buffer",
    "sapo": "Acid Hopper",
    "bandido_arcano": "Arcane Bandit",
    "mago_hobbit": "Hobbit Warlock",
    "escorpiao_rainha": "Scorpion Matriarch",
    "gazer_vazio": "Void Gazer",
    "assassino_crepuscular": "Twilight Assassin",
    "sentinela_estelar": "Stellar Sentinel",
    "necrolorde_orbital": "Necrolord Orbiter",
    "horror_igneo": "Ignis Horror",
    "espectro_lancante": "Lancer Specter",
    "aracnideo_venenoso": "Venom Arachnid",
    "bombardeiro_abyssal": "Abyssal Bombardier",
    "olho_orbitante": "Orbiting Eye",
    "vigia_supressor": "Suppressor Watcher",
    "xama_mineiro": "Mine Shaman",
    "algoz_faseado": "Phased Executioner",
    "guardiao_cosmico": "Cosmic Guardian",
    "caotico_estilha": "Shard Chaotic",
    "fuzileiro_runico": "Runic Rifleman",
    "cavaleiro_voraz": "Ravenous Knight",
    "necromante_torre": "Tower Necromancer",
    "aranha_laser": "Laser Arachnid",
    "miniboss_espiral": "Spiral Warden",
    "miniboss_cacador": "Hunter Vanguard",
    "miniboss_escudo": "Aegis Bastion",
    "miniboss_sniper": "Dread Sniper",
    "miniboss_laser_matrix": "Matrix Overseer",
    "miniboss_oraculo_kame": "Beam Oracle",
    "miniboss_piro_hidra": "Pyro Hydra",
    "miniboss_fantasma_senhor": "Phantom Overlord",
    "miniboss_alquimista": "Plague Alchemist",
    "boss": "Overseer Prime",
    "boss_artilharia": "War Cannon Sovereign",
    "boss_caotico": "Chaos Regent",
    "boss_colosso_laser": "Laser Colossus",
    "boss_druida_toxico": "Toxic Druid",
    "boss_soberano_espectral": "Spectral Overlord",
    "virus_chaser": "Maze Chaser",
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
        return "Unknown Enemy"
    if kind in _FRIENDLY_NAMES:
        return _FRIENDLY_NAMES[kind]
    return kind.replace("_", " ").title()
