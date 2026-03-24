import random
import math
import pygame
import threading
import time

from ..constants import ALTURA_TELA, AMARELO_DADO, CIANO_NEON, LARGURA_TELA, LARANJA_NEON, ROSA_NEON, ROXO_NEON, VERDE_NEON, VERMELHO_SANGUE
from ..entities import BlackHole, Collectible, Inimigo, Particula, Player, LavaManager
from ..services.ranking import buscar_ranking_global


MAX_PARTICULAS = 650
MAX_PROJETEIS_INIMIGOS = 240
MAX_INIMIGOS_SOBREVIVENCIA = 18
MAX_INIMIGOS_HARDCORE = 24
LABIRINTO_ESPESSURA_PAREDE = 8
MAX_FANTASMAS_LABIRINTO = 6
FANTASMA_INTERVALO_DECISAO = 0.12
MINIBOSS_TIPOS = ["miniboss_espiral", "miniboss_cacador", "miniboss_escudo", "miniboss_sniper"]
BOSS_TIPOS = ["boss", "boss_artilharia", "boss_caotico"]


def entrar_menu_modo(self):
    self.sounds.play_bgm("neon_surge/assets/sounds/trilha_menu.wav", self.volume_musica)
    self.estado = "MENU_MODO"
    self.player = None
    self.particulas.clear()
    self.botao_selecionado = 0


def obter_pads_menu(self):
    modos = [
        {
            "id": 0,
            "modo": "CORRIDA",
            "texto": "CORRIDA",
            "cor": CIANO_NEON,
            "descricao": "Complete 10 fases no menor tempo possível.",
            "tag": "10 FASES",
        },
        {
            "id": 5,
            "modo": "CORRIDA_INFINITA",
            "texto": "INFINITA",
            "cor": ROXO_NEON,
            "descricao": "Escalada infinita de fases com bosses evolutivos.",
            "tag": "SEM FIM",
        },
        {
            "id": 2,
            "modo": "SOBREVIVENCIA",
            "texto": "SOBREVIVÊNCIA",
            "cor": ROSA_NEON,
            "descricao": "Resista ao caos crescente e fuja da lava setorial.",
            "tag": "RESISTIR",
        },
        {
            "id": 3,
            "modo": "HARDCORE",
            "texto": "HARDCORE",
            "cor": LARANJA_NEON,
            "descricao": "Versão extrema da sobrevivência, com pressão máxima.",
            "tag": "EXTREMO",
        },
        {
            "id": 6,
            "modo": "LABIRINTO",
            "texto": "LABIRINTO",
            "cor": VERDE_NEON,
            "descricao": "Fases infinitas em um labirinto procedural com saída dinâmica.",
            "tag": "PROCEDURAL",
        },
        {
            "id": 1,
            "modo": "TREINO",
            "texto": "TREINO",
            "cor": VERDE_NEON,
            "descricao": "Pratique suas habilidades sem medo de morrer.",
            "tag": "IMORTAL",
        },
        {
            "id": 4,
            "modo": "INFO",
            "texto": "GUIA",
            "cor": AMARELO_DADO,
            "descricao": "Revise modos, ameaças e regras principais.",
            "tag": "AJUDA",
        },
        {
            "id": 99,
            "modo": "CONFIG",
            "texto": "CONFIG",
            "cor": CIANO_NEON,
            "descricao": "Ajuste áudio, resolução e tela cheia.",
            "tag": "SISTEMA",
        },
    ]

    return modos


def _gerar_layout_labirinto(self):
    cols = min(20, 10 + (self.fase_atual // 2))
    rows = min(14, 7 + (self.fase_atual // 3))

    margem_x = 36
    margem_y_topo = 86
    margem_y_base = 30
    largura_disp = LARGURA_TELA - (margem_x * 2)
    altura_disp = ALTURA_TELA - margem_y_topo - margem_y_base

    cell = max(34, min(largura_disp // cols, altura_disp // rows))
    area_largura = cols * cell
    area_altura = rows * cell
    area_x = (LARGURA_TELA - area_largura) // 2
    area_y = margem_y_topo + ((altura_disp - area_altura) // 2)

    paredes = {(cx, cy): [True, True, True, True] for cy in range(rows) for cx in range(cols)}
    visitados = {(0, 0)}
    pilha = [(0, 0)]
    dirs = [(0, -1, 0, 2), (1, 0, 1, 3), (0, 1, 2, 0), (-1, 0, 3, 1)]

    while pilha:
        cx, cy = pilha[-1]
        candidatos = []
        for dx, dy, lado_atual, lado_vizinho in dirs:
            nx, ny = cx + dx, cy + dy
            if 0 <= nx < cols and 0 <= ny < rows and (nx, ny) not in visitados:
                candidatos.append((nx, ny, lado_atual, lado_vizinho))

        if candidatos:
            nx, ny, lado_atual, lado_vizinho = random.choice(candidatos)
            paredes[(cx, cy)][lado_atual] = False
            paredes[(nx, ny)][lado_vizinho] = False
            visitados.add((nx, ny))
            pilha.append((nx, ny))
        else:
            pilha.pop()

    segmentos = set()
    for cy in range(rows):
        for cx in range(cols):
            px = area_x + (cx * cell)
            py = area_y + (cy * cell)
            n, l, s, o = paredes[(cx, cy)]
            if n:
                segmentos.add((px, py, px + cell, py))
            if l:
                segmentos.add((px + cell, py, px + cell, py + cell))
            if s:
                segmentos.add((px, py + cell, px + cell, py + cell))
            if o:
                segmentos.add((px, py, px, py + cell))

    hitboxes = []
    esp = LABIRINTO_ESPESSURA_PAREDE
    for x1, y1, x2, y2 in segmentos:
        if y1 == y2:
            x_ini = min(x1, x2)
            largura = abs(x2 - x1)
            hitboxes.append(pygame.Rect(int(x_ini), int(y1 - (esp // 2)), int(largura), esp))
        else:
            y_ini = min(y1, y2)
            altura = abs(y2 - y1)
            hitboxes.append(pygame.Rect(int(x1 - (esp // 2)), int(y_ini), esp, int(altura)))

    inicio = (0, 0)
    fim = (cols - 1, rows - 1)
    inicio_pos = pygame.math.Vector2(area_x + (inicio[0] * cell) + (cell * 0.5), area_y + (inicio[1] * cell) + (cell * 0.5))
    fim_pos = pygame.math.Vector2(area_x + (fim[0] * cell) + (cell * 0.5), area_y + (fim[1] * cell) + (cell * 0.5))

    self.labirinto_paredes = hitboxes
    self.labirinto_area = pygame.Rect(area_x, area_y, area_largura, area_altura)
    self.labirinto_info = {"cols": cols, "rows": rows, "cell": cell}

    qtd_armadilhas = min(22, 4 + (self.fase_atual // 2))
    ocupadas = {inicio, fim}
    armadilhas = []
    tentativas = 0

    while len(armadilhas) < qtd_armadilhas and tentativas < (qtd_armadilhas * 30):
        tentativas += 1
        gx = random.randint(0, cols - 1)
        gy = random.randint(0, rows - 1)
        cel = (gx, gy)
        if cel in ocupadas:
            continue

        ocupadas.add(cel)
        trap_pos = pygame.math.Vector2(area_x + (gx * cell) + (cell * 0.5), area_y + (gy * cell) + (cell * 0.5))
        armadilhas.append({"pos": trap_pos, "raio": 8 + min(4, self.fase_atual // 8), "fase": random.uniform(0, 6.28)})

    self.labirinto_armadilhas = armadilhas

    cores_fantasma = [ROSA_NEON, CIANO_NEON, LARANJA_NEON, ROXO_NEON, AMARELO_DADO, VERMELHO_SANGUE]
    qtd_fantasmas = min(MAX_FANTASMAS_LABIRINTO, 3 + (self.fase_atual // 3))
    fantasmas = []

    for idx in range(qtd_fantasmas):
        tentativas_spawn = 0
        spawn_cell = None
        while tentativas_spawn < 80:
            tentativas_spawn += 1
            gx = random.randint(0, cols - 1)
            gy = random.randint(0, rows - 1)
            manhattan_inicio = abs(gx - inicio[0]) + abs(gy - inicio[1])
            cel = (gx, gy)
            if cel in ocupadas:
                continue
            if manhattan_inicio < max(4, (cols + rows) // 4):
                continue
            spawn_cell = cel
            ocupadas.add(cel)
            break

        if spawn_cell is None:
            continue

        gx, gy = spawn_cell
        pos_fantasma = pygame.math.Vector2(area_x + (gx * cell) + (cell * 0.5), area_y + (gy * cell) + (cell * 0.5))

        cantos_scatter = [
            pygame.math.Vector2(area_x + (cell * 0.5), area_y + (cell * 0.5)),
            pygame.math.Vector2(area_x + area_largura - (cell * 0.5), area_y + (cell * 0.5)),
            pygame.math.Vector2(area_x + (cell * 0.5), area_y + area_altura - (cell * 0.5)),
            pygame.math.Vector2(area_x + area_largura - (cell * 0.5), area_y + area_altura - (cell * 0.5)),
        ]

        fantasmas.append(
            {
                "pos": pos_fantasma,
                "dir": pygame.math.Vector2(random.choice([(1, 0), (-1, 0), (0, 1), (0, -1)])),
                "speed": min(10.8, 5.2 + (self.fase_atual * 0.28)),
                "raio": 10,
                "cor": cores_fantasma[idx % len(cores_fantasma)],
                "mode": "CHASE",
                "mode_timer": random.uniform(2.6, 4.4),
                "decision_timer": random.uniform(0.0, FANTASMA_INTERVALO_DECISAO),
                "scatter_target": cantos_scatter[idx % len(cantos_scatter)],
            }
        )

    self.labirinto_fantasmas = fantasmas

    tempo_base = 38.0 - min(22.0, (self.fase_atual - 1) * 1.35)
    self.labirinto_tempo_max = max(16.0, tempo_base)
    self.labirinto_tempo_restante = self.labirinto_tempo_max

    self.player.pos = pygame.math.Vector2(inicio_pos.x, inicio_pos.y)
    self.player.vel = pygame.math.Vector2(0, 0)
    self.portal_pos = pygame.math.Vector2(fim_pos.x, fim_pos.y)
    self.portal_aberto = True


def _resolver_colisao_labirinto(self, pos_anterior):
    if not self.labirinto_paredes:
        return

    raio = self.player.tamanho * 0.45

    alvo = pygame.math.Vector2(self.player.pos.x, self.player.pos.y)
    delta = alvo - pos_anterior
    dist = delta.length()

    if dist == 0:
        self.player.pos = pygame.math.Vector2(pos_anterior.x, pos_anterior.y)
        return

    passos = max(1, int(dist / 3.0))
    passo = delta / passos
    atual = pygame.math.Vector2(pos_anterior.x, pos_anterior.y)

    for _ in range(passos):
        alvo_passo = atual + passo
        teste_x = pygame.math.Vector2(alvo_passo.x, atual.y)
        if not self._colide_com_paredes_labirinto(teste_x, raio):
            atual.x = teste_x.x

        teste_y = pygame.math.Vector2(atual.x, alvo_passo.y)
        if not self._colide_com_paredes_labirinto(teste_y, raio):
            atual.y = teste_y.y

    self.player.pos = atual


def _colide_com_paredes_labirinto(self, pos, raio):
    rect = pygame.Rect(pos.x - raio, pos.y - raio, raio * 2, raio * 2)
    return any(rect.colliderect(w) for w in self.labirinto_paredes)


def _atualizar_fantasmas_labirinto(self):
    if not self.labirinto_fantasmas:
        return False

    direcoes = [
        pygame.math.Vector2(1, 0),
        pygame.math.Vector2(-1, 0),
        pygame.math.Vector2(0, 1),
        pygame.math.Vector2(0, -1),
    ]

    raio_player = self.player.tamanho * 0.45

    for fantasma in self.labirinto_fantasmas:
        fantasma["mode_timer"] -= self.dt
        if fantasma["mode_timer"] <= 0:
            if fantasma["mode"] == "CHASE":
                fantasma["mode"] = "SCATTER"
                fantasma["mode_timer"] = random.uniform(1.2, 2.0)
            else:
                fantasma["mode"] = "CHASE"
                fantasma["mode_timer"] = random.uniform(2.2, 3.8)

        fantasma["decision_timer"] -= self.dt
        if fantasma["decision_timer"] <= 0:
            fantasma["decision_timer"] = FANTASMA_INTERVALO_DECISAO

            alvo = self.player.pos if fantasma["mode"] == "CHASE" else fantasma["scatter_target"]
            reverse = -fantasma["dir"] if fantasma["dir"].length_squared() > 0 else pygame.math.Vector2(0, 0)

            opcoes = []
            for direcao in direcoes:
                if reverse.length_squared() > 0 and direcao.dot(reverse) > 0.99:
                    continue
                prox = fantasma["pos"] + (direcao * (fantasma["speed"] + 2))
                if not self._colide_com_paredes_labirinto(prox, fantasma["raio"]):
                    opcoes.append((prox.distance_to(alvo), direcao))

            if not opcoes:
                for direcao in direcoes:
                    prox = fantasma["pos"] + (direcao * (fantasma["speed"] + 2))
                    if not self._colide_com_paredes_labirinto(prox, fantasma["raio"]):
                        opcoes.append((prox.distance_to(alvo), direcao))

            if opcoes:
                opcoes.sort(key=lambda item: item[0])
                fantasma["dir"] = opcoes[0][1]

        proposed = fantasma["pos"] + (fantasma["dir"] * fantasma["speed"])
        delta = proposed - fantasma["pos"]
        dist = delta.length()
        passos = max(1, int(dist / 3.0))
        passo = delta / passos
        bloqueado_total = True

        for _ in range(passos):
            alvo_passo = fantasma["pos"] + passo
            moveu = False

            test_x = pygame.math.Vector2(alvo_passo.x, fantasma["pos"].y)
            if not self._colide_com_paredes_labirinto(test_x, fantasma["raio"]):
                fantasma["pos"].x = test_x.x
                moveu = True

            test_y = pygame.math.Vector2(fantasma["pos"].x, alvo_passo.y)
            if not self._colide_com_paredes_labirinto(test_y, fantasma["raio"]):
                fantasma["pos"].y = test_y.y
                moveu = True

            if moveu:
                bloqueado_total = False

        if bloqueado_total:
            fantasma["dir"] = pygame.math.Vector2(0, 0)

        if not self.player.invencivel:
            if fantasma["pos"].distance_to(self.player.pos) < (fantasma["raio"] + raio_player):
                return True

    return False


def iniciar_fase(self):
    self.sounds.play_bgm("neon_surge/assets/sounds/trilha_gameplay.wav", self.volume_musica)
    self.player = Player(LARGURA_TELA // 2, ALTURA_TELA // 2)
    self.inimigos.clear()
    self.projeteis_inimigos.clear()
    self.portais_inimigos.clear()
    self.coletaveis.clear()
    self.particulas.clear()
    self.portal_aberto = False

    self.lava_manager.reset()
    self.temporizador_buraco_negro = 8.0
    self.buracos_negros.clear()
    self.labirinto_paredes = []
    self.labirinto_area = None
    self.labirinto_info = {}
    self.labirinto_armadilhas = []
    self.labirinto_fantasmas = []
    self.labirinto_tempo_restante = 0.0
    self.labirinto_tempo_max = 0.0

    if self.fase_atual == 1:
        self.tempo_corrida = 0.0
        self.tempo_sobrevivencia = 0.0
        self.temporizador_spawn = 0.0
        self.temporizador_buraco_negro = 8.0

    self.tempo_renascer_corrida = 0.0
    self.limite_inimigos_corrida = 0

    if self.modo_jogo in ["CORRIDA", "CORRIDA_INFINITA"]:
        eh_fase_boss = (self.modo_jogo == "CORRIDA" and self.fase_atual == 10) or (
            self.modo_jogo == "CORRIDA_INFINITA" and self.fase_atual > 0 and self.fase_atual % 10 == 0
        )
        fase_miniboss_corrida = self.modo_jogo == "CORRIDA" and self.fase_atual > 0 and self.fase_atual % 3 == 0

        if eh_fase_boss:
            for _ in range(9):
                x = random.randint(50, LARGURA_TELA - 50)
                y = random.randint(110, ALTURA_TELA - 50)
                self.coletaveis.append(Collectible(x, y))

            ex, ey = LARGURA_TELA // 2, 120
            while abs(ex - self.player.pos.x) < 300 and abs(ey - self.player.pos.y) < 300:
                ex = random.randint(50, LARGURA_TELA - 50)
                ey = random.randint(110, ALTURA_TELA - 50)

            if self.modo_jogo == "CORRIDA_INFINITA":
                variante_boss = max(1, self.fase_atual // 10)
            else:
                variante_boss = 1 + (self.fase_atual // 5)
            tipo_boss = random.choice(BOSS_TIPOS)
            self.portais_inimigos.append(
                {
                    "pos": pygame.math.Vector2(ex, ey),
                    "tipo": tipo_boss,
                    "vel": 4.2 + (variante_boss * 0.28),
                    "tempo": 1.1,
                    "variante": variante_boss,
                }
            )
            self.limite_inimigos_corrida = 4 + variante_boss
            self._spawn_inimigos(4 + variante_boss, 4.8 + (variante_boss * 0.32))

            if fase_miniboss_corrida:
                ex_mini, ey_mini = ex, ey
                tentativas = 0
                while tentativas < 40 and abs(ex_mini - ex) < 180 and abs(ey_mini - ey) < 140:
                    tentativas += 1
                    ex_mini = random.randint(70, LARGURA_TELA - 70)
                    ey_mini = random.randint(130, ALTURA_TELA - 70)

                self.portais_inimigos.append(
                    {
                        "pos": pygame.math.Vector2(ex_mini, ey_mini),
                        "tipo": random.choice(MINIBOSS_TIPOS),
                        "vel": 5.6 + (0.2 * variante_boss),
                        "tempo": 0.95,
                    }
                )

        else:
            for _ in range(5):
                x = random.randint(50, LARGURA_TELA - 50)
                y = random.randint(110, ALTURA_TELA - 50)
                self.coletaveis.append(Collectible(x, y))

            limite_inimigos = 2 + min(self.fase_atual, 14)
            vel_inimigo = 4.0 + min((self.fase_atual * 0.18), 6.8)
            self.limite_inimigos_corrida = limite_inimigos
            self._spawn_inimigos(limite_inimigos, vel_inimigo)

            if fase_miniboss_corrida:
                ex, ey = self.player.pos.x, self.player.pos.y
                while abs(ex - self.player.pos.x) < 280 and abs(ey - self.player.pos.y) < 240:
                    ex = random.randint(70, LARGURA_TELA - 70)
                    ey = random.randint(130, ALTURA_TELA - 70)

                self.portais_inimigos.append(
                    {
                        "pos": pygame.math.Vector2(ex, ey),
                        "tipo": random.choice(MINIBOSS_TIPOS),
                        "vel": 5.4 + min(2.4, self.fase_atual * 0.22),
                        "tempo": 0.95,
                    }
                )

    elif self.modo_jogo == "SOBREVIVENCIA":
        self._spawn_inimigos(2, 4)

    elif self.modo_jogo == "HARDCORE":
        self._spawn_inimigos(4, 6)

    elif self.modo_jogo == "LABIRINTO":
        self._gerar_layout_labirinto()

    elif self.modo_jogo == "TREINO":
        # No modo treino, spawnamos exatamente o que o jogador escolheu
        for tid, count in self.inimigos_treino_selecionados.items():
            for _ in range(count):
                self._spawn_unitario(tid, 4.0)

    self.estado = "JOGANDO"

def _spawn_unitario(self, tipo, velocidade):
    """Spawna um inimigo específico (usado no Treino)."""
    variante = 1
    tempo_portal = 0.8
    vel_final = velocidade

    if tipo in BOSS_TIPOS:
        tempo_portal = 1.2
        vel_final = 4.5
        variante = 1
    elif tipo in MINIBOSS_TIPOS:
        tempo_portal = 1.0
        vel_final = 5.5
    elif tipo == "metralhadora":
        vel_final = max(0.0, velocidade * 0.9)

    ex, ey = self.player.pos.x, self.player.pos.y
    while abs(ex - self.player.pos.x) < 300 and abs(ey - self.player.pos.y) < 300:
        ex = random.randint(50, LARGURA_TELA - 50)
        ey = random.randint(110, ALTURA_TELA - 50)

    p_data = {"pos": pygame.math.Vector2(ex, ey), "tipo": tipo, "vel": vel_final, "tempo": tempo_portal}
    if tipo in BOSS_TIPOS:
        p_data["variante"] = variante
    
    self.portais_inimigos.append(p_data)


def _spawn_inimigos(self, quantidade, velocidade):
    tipos_comuns = ["quique", "perseguidor", "investida", "explosivo", "metralhadora", "morteiro"]
    tipos_disponiveis = tipos_comuns

    for _ in range(quantidade):
        tipo = random.choice(tipos_disponiveis)
        self._spawn_unitario(tipo, velocidade)


def atualizar_jogo(self):
    teclas = pygame.key.get_pressed()
    pos_player_anterior = pygame.math.Vector2(self.player.pos.x, self.player.pos.y)
    if self.player.update(teclas, self.particulas, self.sounds):
        self.shake_frames = 6

    if self.modo_jogo == "LABIRINTO":
        self._resolver_colisao_labirinto(pos_player_anterior)
        if self._atualizar_fantasmas_labirinto():
            self._lidar_com_morte()
            return

    particulas_ativas = []
    for p in self.particulas:
        p.update()
        if p.raio > 0:
            particulas_ativas.append(p)
    self.particulas = particulas_ativas[-MAX_PARTICULAS:]

    projeteis_ativos = []
    for proj in self.projeteis_inimigos:
        if proj.get("tipo") == "bomba":
            proj["timer_queda"] -= self.dt
            progresso = max(0.0, min(1.0, 1.0 - (proj["timer_queda"] / proj["timer_total"])))
            
            # Movimento em arco (falso 3D)
            altura_arco = math.sin(progresso * math.pi) * 100
            origem = proj.get("origem_falsa", proj["pos"].copy())
            if "origem_falsa" not in proj: proj["origem_falsa"] = origem
            
            proj["pos"] = origem.lerp(proj["alvo_final"], progresso)
            proj["pos_visual"] = (proj["pos"].x, proj["pos"].y - altura_arco)
            
            if proj["timer_queda"] <= 0:
                # Explosão!
                proj["explodiu"] = True
                self.shake_frames = 6
                self.sounds.play('som_explosao')
                for _ in range(25):
                    ang = random.uniform(0, math.pi * 2)
                    dist = random.uniform(0, proj["raio_explosao"])
                    self.particulas.append(Particula(
                        proj["pos"].x + math.cos(ang)*dist, 
                        proj["pos"].y + math.sin(ang)*dist, 
                        LARANJA_NEON
                    ))
                
                # Dano na explosão
                if not self.player.invencivel:
                    if proj["pos"].distance_to(self.player.pos) < proj["raio_explosao"]:
                        self._lidar_com_morte()
                        return
                continue
        else:
            proj["pos"] += proj["vel"]
            proj["tempo"] -= self.dt
            proj["pos_visual"] = (proj["pos"].x, proj["pos"].y)

        fora_tela = (
            proj["pos"].x < -30
            or proj["pos"].x > LARGURA_TELA + 30
            or proj["pos"].y < 30
            or proj["pos"].y > ALTURA_TELA + 30
        )
        if (not proj.get("tipo") == "bomba" and proj["tempo"] <= 0) or fora_tela:
            continue

        if random.random() < 0.25:
            pv = proj.get("pos_visual", (proj["pos"].x, proj["pos"].y))
            self.particulas.append(Particula(pv[0], pv[1], proj.get("cor", LARANJA_NEON)))

        if not self.player.invencivel and not proj.get("tipo") == "bomba":
            raio_colisao = proj.get("raio", 4) + (self.player.tamanho * 0.45)
            if proj["pos"].distance_to(self.player.pos) < raio_colisao:
                self._lidar_com_morte()
                return

        projeteis_ativos.append(proj)

    self.projeteis_inimigos = projeteis_ativos[-MAX_PROJETEIS_INIMIGOS:]

    for p in self.portais_inimigos[:]:
        if self.player.dash_timer > 0:
            if p.get("tipo") in BOSS_TIPOS:
                raio_portal = 20
            elif p.get("tipo") in MINIBOSS_TIPOS:
                raio_portal = 18
            else:
                raio_portal = 16
            raio_interacao = raio_portal + (self.player.tamanho * 0.7)
            if p["pos"].distance_to(self.player.pos) <= raio_interacao:
                self.portais_inimigos.remove(p)
                self.shake_frames = 5
                for _ in range(32):
                    self.particulas.append(Particula(p["pos"].x, p["pos"].y, VERMELHO_SANGUE))
                continue

        p["tempo"] -= self.dt
        if p["tempo"] <= 0:
            if p.get("tipo") == "metralhadora":
                atiradores_ativos = sum(1 for ini in self.inimigos if ini.tipo == "metralhadora")
                if atiradores_ativos >= 2:
                    self.portais_inimigos.remove(p)
                    continue
            elif p.get("tipo") in MINIBOSS_TIPOS:
                miniboss_ativos = sum(1 for ini in self.inimigos if ini.tipo in MINIBOSS_TIPOS)
                if miniboss_ativos >= 1:
                    self.portais_inimigos.remove(p)
                    continue

            inimigo = Inimigo(p["pos"].x, p["pos"].y, p["tipo"], p["vel"])
            if "variante" in p:
                inimigo.variante = p["variante"]
            if inimigo.tipo in BOSS_TIPOS:
                inimigo.raio = 40 + (inimigo.variante * 5)
            self.inimigos.append(inimigo)
            self.portais_inimigos.remove(p)
            self.shake_frames = 3
            for _ in range(15):
                self.particulas.append(Particula(p["pos"].x, p["pos"].y, VERMELHO_SANGUE))

    mortes_inimigos_corrida = 0
    novos_inimigos = []
    for ini in self.inimigos[:]:
        ini.update(self.player, self.inimigos, self.dt, self.particulas, self, self.sounds)

        if ini.morto:
            if getattr(ini, "explodiu", False):
                self.shake_frames = 15
                self.sounds.play('som_explosao')
                if not self.player.invencivel and ini.pos.distance_to(self.player.pos) < 80:
                    self._lidar_com_morte()
                    return

            if self.modo_jogo in ["CORRIDA", "CORRIDA_INFINITA"] and ini.tipo not in BOSS_TIPOS:
                mortes_inimigos_corrida += 1
            continue

        dist = ini.pos.distance_to(self.player.pos)
        if not self.player.invencivel and dist < (ini.raio + self.player.tamanho // 2 - 2):
            self._lidar_com_morte()
            return

        novos_inimigos.append(ini)

    self.inimigos = novos_inimigos

    if self.modo_jogo in ["CORRIDA", "CORRIDA_INFINITA"]:
        self.tempo_renascer_corrida = max(0.0, float(getattr(self, "tempo_renascer_corrida", 0.0)) - self.dt)

        eh_fase_boss = (self.modo_jogo == "CORRIDA" and self.fase_atual == 10) or (
            self.modo_jogo == "CORRIDA_INFINITA" and self.fase_atual > 0 and self.fase_atual % 10 == 0
        )
        alvo = int(getattr(self, "limite_inimigos_corrida", 0))
        total_ativo = len(self.inimigos) + len(self.portais_inimigos)
        faltando = max(0, alvo - total_ativo)

        if not eh_fase_boss and mortes_inimigos_corrida > 0 and faltando > 0 and self.tempo_renascer_corrida <= 0:
            qtd = min(faltando, max(1, min(2, mortes_inimigos_corrida)))
            vel_respawn = 4.2 + min((self.fase_atual * 0.2), 7.0)
            self._spawn_inimigos(qtd, vel_respawn)
            self.tempo_renascer_corrida = 1.1 if self.modo_jogo == "CORRIDA" else 0.9

    # -- Atualização do Buraco Negro --
    if self.modo_jogo != "LABIRINTO":
        self.temporizador_buraco_negro -= self.dt
        if self.temporizador_buraco_negro <= 0:
            bx = random.randint(100, LARGURA_TELA - 100)
            by = random.randint(110, ALTURA_TELA - 100)
            self.sounds.play('black_hole')
            self.buracos_negros.append(BlackHole(bx, by))
            self.temporizador_buraco_negro = random.uniform(8.0, 15.0)

        for b in self.buracos_negros:
            if b.update(self.player, self.dt):
                self._lidar_com_morte()
                return

        self.buracos_negros = [b for b in self.buracos_negros if not b.expirado]

    if self.modo_jogo == "LABIRINTO":
        self.labirinto_tempo_restante -= self.dt
        if self.labirinto_tempo_restante <= 0:
            self._lidar_com_morte()
            return

        if not self.player.invencivel:
            raio_player = self.player.tamanho * 0.45
            for arm in self.labirinto_armadilhas:
                if self.player.pos.distance_to(arm["pos"]) < (raio_player + arm["raio"]):
                    self._lidar_com_morte()
                    return

        if self.player.pos.distance_to(self.portal_pos) < 30:
            self.fase_atual += 1
            self.shake_frames = 10
            self.iniciar_fase()
            return

    elif self.modo_jogo in ["CORRIDA", "CORRIDA_INFINITA"]:
        self.tempo_corrida += self.dt
        raio_coleta = 32 if self.modo_jogo == "CORRIDA" else 25
        for d in self.coletaveis[:]:
            d.update(self.player.pos, self.dt)
            
            # Coleta apenas pelo Player
            if self.player.pos.distance_to(d.pos) < raio_coleta:
                self.sounds.play('coin_collect')
                self.coletaveis.remove(d)
                self.shake_frames = 2
                for _ in range(12):
                    self.particulas.append(Particula(d.pos.x, d.pos.y, CIANO_NEON))

        if len(self.coletaveis) == 0 and not self.portal_aberto:
            self.portal_aberto = True

            margem_x, margem_y = 100, 100
            px = random.randint(margem_x, LARGURA_TELA - margem_x)
            py = random.randint(margem_y + 60, ALTURA_TELA - margem_y)

            self.portal_pos = pygame.math.Vector2(px, py)
            self.shake_frames = 10

        if self.portal_aberto and self.player.pos.distance_to(self.portal_pos) < 30:
            self.sounds.play('exit_portal')
            if self.modo_jogo == "CORRIDA_INFINITA":
                self.fase_atual += 1
                self.iniciar_fase()
            elif self.fase_atual < 10:
                self.fase_atual += 1
                self.iniciar_fase()
            else:
                self.salvar_ranking(self.modo_jogo, self.tempo_corrida)
                self.estado = "RANKING"
                self.botao_selecionado = 0

    elif self.modo_jogo in ["SOBREVIVENCIA", "HARDCORE"]:
        self.tempo_sobrevivencia += self.dt
        
        # Spawn progressivo de inimigos comuns
        max_ini = MAX_INIMIGOS_SOBREVIVENCIA if self.modo_jogo == "SOBREVIVENCIA" else MAX_INIMIGOS_HARDCORE
        progressao = min(1.0, self.tempo_sobrevivencia / 300.0)
        alvo_atual = 3 + int(progressao * (max_ini - 3))
        
        total_ativo = len(self.inimigos) + len(self.portais_inimigos)
        if total_ativo < alvo_atual:
            self.temporizador_spawn -= self.dt
            if self.temporizador_spawn <= 0:
                vel = 4.0 + (progressao * 3.5)
                self._spawn_inimigos(1, vel)
                self.temporizador_spawn = max(0.5, 2.0 - (progressao * 1.5))

        # --- Lógica de Bosses e Minibosses por Tempo ---
        tempo = int(self.tempo_sobrevivencia)
        is_hardcore = (self.modo_jogo == "HARDCORE")
        
        # Miniboss a cada 45s (30s no Hardcore)
        intervalo_mini = 30 if is_hardcore else 45
        if tempo > 0 and tempo % intervalo_mini == 0 and not getattr(self, "_last_mini_spawn", -1) == tempo:
            self._last_mini_spawn = tempo
            self._spawn_unitario(random.choice(MINIBOSS_TIPOS), 5.5 + (progressao * 2))
            
        # Boss a cada 90s (75s no Hardcore)
        intervalo_boss = 75 if is_hardcore else 90
        if tempo > 0 and tempo % intervalo_boss == 0 and not getattr(self, "_last_boss_spawn", -1) == tempo:
            self._last_boss_spawn = tempo
            tipo_boss = random.choice(BOSS_TIPOS)
            self._spawn_unitario(tipo_boss, 4.5 + (progressao * 1.5))

        # Gerenciamento de Lava
        if self.tempo_sobrevivencia > 20:
            intervalo_lava = 15 if self.modo_jogo == "HARDCORE" else 25
            if int(self.tempo_sobrevivencia) % intervalo_lava == 0 and not self.lava_manager.ativa and self.lava_manager.aviso_tempo <= 0:
                self.lava_manager.disparar_evento()

        if self.lava_manager.update(self.player, self.dt, self.sounds):
            self._lidar_com_morte()
            return

    elif self.modo_jogo == "TREINO":
        # No modo treino, mantemos a quantidade que o jogador escolheu
        for tid, count in self.inimigos_treino_selecionados.items():
            ativos = sum(1 for ini in self.inimigos if ini.tipo == tid)
            ativos += sum(1 for p in self.portais_inimigos if p["tipo"] == tid)
            
            if ativos < count:
                self._spawn_unitario(tid, 4.5)

def atualizar_menu_interativo(self):
    particulas_ativas = []
    for p in self.particulas:
        p.update()
        if p.raio > 0:
            particulas_ativas.append(p)
    self.particulas = particulas_ativas[-MAX_PARTICULAS:]

    opcoes = self.obter_pads_menu()
    ids_validos = [item["id"] for item in opcoes] + [99]
    if self.botao_selecionado not in ids_validos:
        self.botao_selecionado = ids_validos[0]


def _lidar_com_morte(self):
    self.shake_frames = 15
    self.mortes_total_jogador += 1
    if self.modo_jogo in ["CORRIDA", "TREINO"]:
        self.iniciar_fase()
    elif self.modo_jogo == "CORRIDA_INFINITA":
        self.salvar_ranking(self.modo_jogo, self.fase_atual)
        self.sounds.play_bgm("neon_surge/assets/sounds/trilha_menu.wav", self.volume_musica)
        self.entrar_ranking(veio_de_fim_partida=True)
    elif self.modo_jogo == "LABIRINTO":
        self.salvar_ranking(self.modo_jogo, self.fase_atual)
        self.sounds.play_bgm("neon_surge/assets/sounds/trilha_menu.wav", self.volume_musica)
        self.entrar_ranking(veio_de_fim_partida=True)
    elif self.modo_jogo in ["SOBREVIVENCIA", "HARDCORE"]:
        self.salvar_ranking(self.modo_jogo, self.tempo_sobrevivencia)
        self.sounds.play_bgm("neon_surge/assets/sounds/trilha_menu.wav", self.volume_musica)
        self.entrar_ranking(veio_de_fim_partida=True)

def entrar_ranking(self, veio_de_fim_partida=False):
    """Navega para a tela de ranking e inicia o carregamento global."""
    self.sounds.play('menu_accept')
    self.estado = "RANKING"
    self.botao_selecionado = 0 # Foco no primeiro botão por padrão
    self.ranking_aba = self.modo_jogo if self.modo_jogo != "" else "CORRIDA"
    self.veio_de_fim_partida = veio_de_fim_partida
    self.ranking_global = []
    self.carregando_ranking = True
    
    def fetch():
        # Pequeno delay se veio de fim de partida para dar tempo do POST ser processado pelo Supabase
        if veio_de_fim_partida:
            time.sleep(1.2)
        res = buscar_ranking_global(self.ranking_aba)
        self.ranking_global = res
        self.carregando_ranking = False
        
    threading.Thread(target=fetch, daemon=True).start()

def trocar_aba_ranking(self, nova_aba):
    if self.ranking_aba == nova_aba: return
    self.sounds.play('menu_button')
    self.ranking_aba = nova_aba
    self.ranking_global = []
    self.carregando_ranking = True
    
    def fetch():
        res = buscar_ranking_global(nova_aba)
        self.ranking_global = res
        self.carregando_ranking = False
        
    threading.Thread(target=fetch, daemon=True).start()
