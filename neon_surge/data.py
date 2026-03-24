from .constants import ROSA_NEON, VERMELHO_SANGUE, LARANJA_NEON, AMARELO_DADO, ROXO_NEON, CIANO_NEON, BRANCO, CINZA_ESCURO

# UI Theme Constants
UI_COLORS = {
    "HIGHLIGHT": CIANO_NEON,
    "SELECTED": AMARELO_DADO,
    "HOVER": ROSA_NEON,
    "TEXT_NORMAL": BRANCO,
    "TEXT_SELECTED": (10, 15, 25),
    "BORDER_NORMAL": CINZA_ESCURO,
    "PANEL_BG": (15, 20, 25, 200)
}

UI_ANIMATION = {
    "HOVER_SCALE": 1.05,
    "PULSE_SPEED": 10.0,
    "GLOW_INTENSITY": 4
}

INIMIGOS_DATA = {
    "quique": {
        "nome": "SENTINELA",
        "cor": ROSA_NEON,
        "categoria": "COMUNS",
        "desc": "Unidade básica de patrulha. Reflete-se em superfícies e outros inimigos com velocidade constante. Perigosa em grandes grupos.",
        "stats": {"atq": 3, "vel": 6, "res": 2}
    },
    "perseguidor": {
        "nome": "CAÇADOR",
        "cor": VERMELHO_SANGUE,
        "categoria": "COMUNS",
        "desc": "Persegue o jogador incansavelmente. Embora lento, sua persistência força o jogador a se manter em movimento constante.",
        "stats": {"atq": 4, "vel": 5, "res": 4}
    },
    "investida": {
        "nome": "INVESTIDA",
        "cor": LARANJA_NEON,
        "categoria": "COMUNS",
        "desc": "Carrega energia antes de realizar um avanço veloz em linha reta. O rastro de mira indica sua trajetória iminente.",
        "stats": {"atq": 6, "vel": 9, "res": 3}
    },
    "explosivo": {
        "nome": "BOMBA",
        "cor": AMARELO_DADO,
        "categoria": "COMUNS",
        "desc": "Aproxima-se e detona após um curto período. A explosão causa dano em área, marcada por um anel de aviso vermelho.",
        "stats": {"atq": 9, "vel": 4, "res": 2}
    },
    "metralhadora": {
        "nome": "ATIRADOR",
        "cor": ROXO_NEON,
        "categoria": "COMUNS",
        "desc": "Unidade de supressão avançada. Dispara rajadas geométricas de alta densidade. Sua capacidade de saturação de área a torna a ameaça comum mais letal do sistema.",
        "stats": {"atq": 9, "vel": 3, "res": 6}
    },
    "morteiro": {
        "nome": "MORTEIRO",
        "cor": LARANJA_NEON,
        "categoria": "COMUNS",
        "desc": "Dispara bombas que viajam em arco e explodem ao atingir o solo. Exige atenção tanto ao céu quanto à terra.",
        "stats": {"atq": 7, "vel": 2, "res": 4}
    },
    "miniboss_espiral": {
        "nome": "ESPIRO",
        "cor": ROXO_NEON,
        "categoria": "MINIBOSSES",
        "desc": "Dispara projéteis em espiral contínua. Sua presença satura o campo de batalha com perigos rotativos.",
        "stats": {"atq": 7, "vel": 4, "res": 8}
    },
    "miniboss_cacador": {
        "nome": "PREDADOR",
        "cor": VERMELHO_SANGUE,
        "categoria": "MINIBOSSES",
        "desc": "Uma versão evoluída do Caçador. Dispara projéteis triplos enquanto persegue sua presa de forma agressiva.",
        "stats": {"atq": 8, "vel": 6, "res": 7}
    },
    "miniboss_escudo": {
        "nome": "BALUARTE",
        "cor": CIANO_NEON,
        "categoria": "MINIBOSSES",
        "desc": "Orbita o jogador disparando projéteis em leque. Difícil de evitar devido à sua proximidade constante.",
        "stats": {"atq": 6, "vel": 7, "res": 9}
    },
    "miniboss_sniper": {
        "nome": "SNIPER",
        "cor": AMARELO_DADO,
        "categoria": "MINIBOSSES",
        "desc": "Trava a mira no jogador e dispara um projétil de altíssima velocidade após carregar. Dash é essencial para sobreviver.",
        "stats": {"atq": 9, "vel": 3, "res": 6}
    },
    "boss": {
        "nome": "TITÃ",
        "cor": ROXO_NEON,
        "categoria": "BOSSES",
        "desc": "Entidade massiva com múltiplas fases. Invoca aliados, realiza investidas pesadas e dispara padrões complexos.",
        "stats": {"atq": 9, "vel": 5, "res": 10}
    },
    "boss_artilharia": {
        "nome": "COLOSSO",
        "cor": LARANJA_NEON,
        "categoria": "BOSSES",
        "desc": "Especialista em saturação de área. Dispara anéis de projéteis e invoca minibosses para auxiliar no combate.",
        "stats": {"atq": 10, "vel": 3, "res": 9}
    },
    "boss_caotico": {
        "nome": "CAOS",
        "cor": ROSA_NEON,
        "categoria": "BOSSES",
        "desc": "O ápice da instabilidade. Move-se erraticamente, dispara rajadas multidirecionais e realiza ataques de área devastadores.",
        "stats": {"atq": 10, "vel": 10, "res": 8}
    }
}
