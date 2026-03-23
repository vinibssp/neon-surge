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
        "desc": "Unidade básica de patrulha. Reflete-se em superfícies e outros inimigos com velocidade constante. Perigosa em grandes grupos."
    },
    "perseguidor": {
        "nome": "CAÇADOR",
        "cor": VERMELHO_SANGUE,
        "categoria": "COMUNS",
        "desc": "Persegue o jogador incansavelmente. Embora lento, sua persistência força o jogador a se manter em movimento constante."
    },
    "investida": {
        "nome": "INVESTIDA",
        "cor": LARANJA_NEON,
        "categoria": "COMUNS",
        "desc": "Carrega energia antes de realizar um avanço veloz em linha reta. O rastro de mira indica sua trajetória iminente."
    },
    "explosivo": {
        "nome": "BOMBA",
        "cor": AMARELO_DADO,
        "categoria": "COMUNS",
        "desc": "Aproxima-se e detona após um curto período. A explosão causa dano em área, marcada por um anel de aviso vermelho."
    },
    "metralhadora": {
        "nome": "ATIRADOR",
        "cor": ROXO_NEON,
        "categoria": "COMUNS",
        "desc": "Unidade estática que dispara rajadas de projéteis em padrões geométricos. Controle de zona é sua principal função."
    },
    "morteiro": {
        "nome": "MORTEIRO",
        "cor": LARANJA_NEON,
        "categoria": "COMUNS",
        "desc": "Dispara bombas que viajam em arco e explodem ao atingir o solo. Exige atenção tanto ao céu quanto à terra."
    },
    "miniboss_espiral": {
        "nome": "ESPIRO",
        "cor": ROXO_NEON,
        "categoria": "MINIBOSSES",
        "desc": "Dispara projéteis em espiral contínua. Sua presença satura o campo de batalha com perigos rotativos."
    },
    "miniboss_cacador": {
        "nome": "PREDADOR",
        "cor": VERMELHO_SANGUE,
        "categoria": "MINIBOSSES",
        "desc": "Uma versão evoluída do Caçador. Dispara projéteis triplos enquanto persegue sua presa de forma agressiva."
    },
    "miniboss_escudo": {
        "nome": "BALUARTE",
        "cor": CIANO_NEON,
        "categoria": "MINIBOSSES",
        "desc": "Orbita o jogador disparando projéteis em leque. Difícil de evitar devido à sua proximidade constante."
    },
    "miniboss_sniper": {
        "nome": "SNIPER",
        "cor": AMARELO_DADO,
        "categoria": "MINIBOSSES",
        "desc": "Trava a mira no jogador e dispara um projétil de altíssima velocidade após carregar. Dash é essencial para sobreviver."
    },
    "boss": {
        "nome": "TITÃ",
        "cor": ROXO_NEON,
        "categoria": "BOSSES",
        "desc": "Entidade massiva com múltiplas fases. Invoca aliados, realiza investidas pesadas e dispara padrões complexos."
    },
    "boss_artilharia": {
        "nome": "COLOSSO",
        "cor": LARANJA_NEON,
        "categoria": "BOSSES",
        "desc": "Especialista em saturação de área. Dispara anéis de projéteis e invoca minibosses para auxiliar no combate."
    },
    "boss_caotico": {
        "nome": "CAOS",
        "cor": ROSA_NEON,
        "categoria": "BOSSES",
        "desc": "O ápice da instabilidade. Move-se erraticamente, dispara rajadas multidirecionais e realiza ataques de área devastadores."
    }
}
