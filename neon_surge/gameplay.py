import math
import random

import pygame

from .config import ALTURA_TELA, AMARELO_DADO, CIANO_NEON, LARGURA_TELA, LARANJA_NEON, ROSA_NEON, ROXO_NEON, VERMELHO_SANGUE
from .entities import BlackHole, Inimigo, Particula, Player


def entrar_menu_modo(self):
    self.estado = "MENU_MODO"
    self.player = Player(LARGURA_TELA // 2, ALTURA_TELA // 2 + 150)
    self.particulas.clear()
    self.botao_selecionado = -1


def obter_pads_menu(self):
    cx, cy = LARGURA_TELA // 2, ALTURA_TELA // 2 + 10
    raio = min(LARGURA_TELA, ALTURA_TELA) * 0.34

    modos = [
        {"id": 5, "modo": "CORRIDA_INFINITA", "texto": "CORRIDA INFINITA", "cor": ROXO_NEON},
        {"id": 3, "modo": "HARDCORE", "texto": "SOBREV. HARDCORE", "cor": LARANJA_NEON},
        {"id": 4, "modo": "INFO", "texto": "TUTORIAL / INFO", "cor": AMARELO_DADO},
        {"id": 2, "modo": "SOBREVIVENCIA", "texto": "SOBREVIVÊNCIA", "cor": ROSA_NEON},
        {"id": 0, "modo": "CORRIDA", "texto": "CORRIDA 10 FASES", "cor": CIANO_NEON},
    ]

    for i, pad in enumerate(modos):
        angulo = (-math.pi / 2) + (i * (2 * math.pi / len(modos)))
        px = cx + math.cos(angulo) * raio
        py = cy + math.sin(angulo) * raio
        pad["pos"] = (px, py)

    return modos


def iniciar_fase(self):
    self.player = Player(LARGURA_TELA // 2, ALTURA_TELA // 2)
    self.inimigos.clear()
    self.projeteis_inimigos.clear()
    self.portais_inimigos.clear()
    self.coletaveis.clear()
    self.particulas.clear()
    self.portal_aberto = False

    self.tempo_para_lava = 30.0
    self.lava_ativa = False
    self.tempo_lava_restante = 0.0
    self.tipo_lava = 0
    self.lava_hitboxes = []
    self.aviso_lava = 0.0
    self.lava_lado_horizontal = None
    self.lava_lado_vertical = None

    if self.fase_atual == 1:
        self.tempo_corrida = 0.0
        self.tempo_sobrevivencia = 0.0
        self.temporizador_spawn = 0.0
        self.temporizador_buraco_negro = 8.0
        self.buracos_negros.clear()

    if self.modo_jogo in ["CORRIDA", "CORRIDA_INFINITA"]:
        eh_fase_boss = (self.modo_jogo == "CORRIDA" and self.fase_atual == 10) or (
            self.modo_jogo == "CORRIDA_INFINITA" and self.fase_atual > 0 and self.fase_atual % 10 == 0
        )

        if eh_fase_boss:
            for _ in range(8):
                x = random.randint(50, LARGURA_TELA - 50)
                y = random.randint(110, ALTURA_TELA - 50)
                self.coletaveis.append(pygame.math.Vector2(x, y))

            ex, ey = LARGURA_TELA // 2, 120
            while abs(ex - self.player.pos.x) < 300 and abs(ey - self.player.pos.y) < 300:
                ex = random.randint(50, LARGURA_TELA - 50)
                ey = random.randint(110, ALTURA_TELA - 50)

            variante_boss = (self.fase_atual // 10) if self.modo_jogo == "CORRIDA_INFINITA" else 1
            self.portais_inimigos.append(
                {
                    "pos": pygame.math.Vector2(ex, ey),
                    "tipo": "boss",
                    "vel": 4.0 + (variante_boss * 0.2),
                    "tempo": 1.1,
                    "variante": variante_boss,
                }
            )
            self._spawn_inimigos(3 + variante_boss, 4.5 + (variante_boss * 0.3))

        else:
            for _ in range(5):
                x = random.randint(50, LARGURA_TELA - 50)
                y = random.randint(110, ALTURA_TELA - 50)
                self.coletaveis.append(pygame.math.Vector2(x, y))

            limite_inimigos = 3 + min(self.fase_atual, 20)
            vel_inimigo = 4 + min((self.fase_atual * 0.25), 8.0)
            self._spawn_inimigos(limite_inimigos, vel_inimigo)

    elif self.modo_jogo == "SOBREVIVENCIA":
        self._spawn_inimigos(2, 4)

    elif self.modo_jogo == "HARDCORE":
        self._spawn_inimigos(4, 6)

    self.estado = "JOGANDO"


def _spawn_inimigos(self, quantidade, velocidade):
    tipos_spawn = ["quique", "perseguidor", "investida", "explosivo", "metralhadora", "metralhadora"]
    tipos_sem_atirador = ["quique", "perseguidor", "investida", "explosivo"]
    for _ in range(quantidade):
        tipo = random.choice(tipos_spawn)

        if tipo == "metralhadora":
            atiradores_ativos = sum(1 for ini in self.inimigos if ini.tipo == "metralhadora")
            atiradores_em_portal = sum(1 for portal in self.portais_inimigos if portal.get("tipo") == "metralhadora")
            if atiradores_ativos + atiradores_em_portal >= 2:
                tipo = random.choice(tipos_sem_atirador)

        ex, ey = self.player.pos.x, self.player.pos.y
        while abs(ex - self.player.pos.x) < 300 and abs(ey - self.player.pos.y) < 300:
            ex = random.randint(50, LARGURA_TELA - 50)
            ey = random.randint(110, ALTURA_TELA - 50)

        self.portais_inimigos.append({"pos": pygame.math.Vector2(ex, ey), "tipo": tipo, "vel": velocidade, "tempo": 0.8})


def atualizar_jogo(self):
    teclas = pygame.key.get_pressed()
    if self.player.update(teclas, self.particulas):
        self.shake_frames = 6

    for p in self.particulas[:]:
        p.update()
        if p.raio <= 0:
            self.particulas.remove(p)

    projeteis_ativos = []
    for proj in self.projeteis_inimigos:
        proj["pos"] += proj["vel"]
        proj["tempo"] -= self.dt

        fora_tela = (
            proj["pos"].x < -30
            or proj["pos"].x > LARGURA_TELA + 30
            or proj["pos"].y < 30
            or proj["pos"].y > ALTURA_TELA + 30
        )
        if proj["tempo"] <= 0 or fora_tela:
            continue

        if random.random() < 0.25:
            self.particulas.append(Particula(proj["pos"].x, proj["pos"].y, proj.get("cor", LARANJA_NEON)))

        if not self.player.invencivel:
            raio_colisao = proj.get("raio", 4) + (self.player.tamanho * 0.45)
            if proj["pos"].distance_to(self.player.pos) < raio_colisao:
                self._lidar_com_morte()
                return

        projeteis_ativos.append(proj)

    self.projeteis_inimigos = projeteis_ativos

    for p in self.portais_inimigos[:]:
        p["tempo"] -= self.dt
        if p["tempo"] <= 0:
            if p.get("tipo") == "metralhadora":
                atiradores_ativos = sum(1 for ini in self.inimigos if ini.tipo == "metralhadora")
                if atiradores_ativos >= 2:
                    self.portais_inimigos.remove(p)
                    continue

            inimigo = Inimigo(p["pos"].x, p["pos"].y, p["tipo"], p["vel"])
            if "variante" in p:
                inimigo.variante = p["variante"]
            if inimigo.tipo == "boss":
                inimigo.raio = 40 + (inimigo.variante * 5)
            self.inimigos.append(inimigo)
            self.portais_inimigos.remove(p)
            self.shake_frames = 3
            for _ in range(15):
                self.particulas.append(Particula(p["pos"].x, p["pos"].y, VERMELHO_SANGUE))

    inimigos_atuais = self.inimigos.copy()
    novos_inimigos = []
    for ini in self.inimigos:
        ini.update(self.player, self.inimigos, self.dt, self.particulas, self)

        if ini.morto:
            if getattr(ini, "explodiu", False):
                self.shake_frames = 15
                if not self.player.invencivel and ini.pos.distance_to(self.player.pos) < 80:
                    self._lidar_com_morte()
                    return
            continue

        dist = ini.pos.distance_to(self.player.pos)
        if not self.player.invencivel and dist < (ini.raio + self.player.tamanho // 2 - 2):
            self._lidar_com_morte()
            return

        novos_inimigos.append(ini)

    for ini in self.inimigos:
        if ini not in inimigos_atuais:
            novos_inimigos.append(ini)

    self.inimigos = novos_inimigos

    # -- Atualização do Buraco Negro --
    self.temporizador_buraco_negro -= self.dt
    if self.temporizador_buraco_negro <= 0:
        bx = random.randint(100, LARGURA_TELA - 100)
        by = random.randint(110, ALTURA_TELA - 100)
        self.buracos_negros.append(BlackHole(bx, by))
        # Tempo de spawn entre 8 e 15 segundos
        self.temporizador_buraco_negro = random.uniform(8.0, 15.0)

    for b in self.buracos_negros:
        b.update(self.player, self.dt, self._lidar_com_morte)
    
    self.buracos_negros = [b for b in self.buracos_negros if not b.expirado]

    if self.modo_jogo in ["CORRIDA", "CORRIDA_INFINITA"]:
        self.tempo_corrida += self.dt
        raio_coleta = 28 if self.modo_jogo == "CORRIDA" else 20
        for d in self.coletaveis[:]:
            if self.player.pos.distance_to(d) < raio_coleta:
                self.coletaveis.remove(d)
                self.shake_frames = 2
                for _ in range(10):
                    self.particulas.append(Particula(d.x, d.y, AMARELO_DADO))

        if len(self.coletaveis) == 0 and not self.portal_aberto:
            self.portal_aberto = True

            margem_x, margem_y = 100, 100
            px = random.randint(margem_x, LARGURA_TELA - margem_x)
            py = random.randint(margem_y + 60, ALTURA_TELA - margem_y)

            self.portal_pos = pygame.math.Vector2(px, py)
            self.shake_frames = 10

        if self.portal_aberto and self.player.pos.distance_to(self.portal_pos) < 30:
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
        self.temporizador_spawn += self.dt

        if not self.lava_ativa:
            self.tempo_para_lava -= self.dt
            if self.tempo_para_lava <= 3.0:
                if self.tipo_lava == 0:
                    self.tipo_lava = 1
                    self.lava_lado_horizontal = random.choice(["esquerda", "direita"])
                    self.lava_lado_vertical = random.choice(["cima", "baixo"])
                self.aviso_lava = self.tempo_para_lava
            if self.tempo_para_lava <= 0.0:
                self.lava_ativa = True
                self.tempo_lava_restante = 10.0
                self.aviso_lava = 0.0
                self.shake_frames = 15
        else:
            self.tempo_lava_restante -= self.dt
            if self.tempo_lava_restante <= 0.0:
                self.lava_ativa = False
                self.tempo_para_lava = 30.0
                self.tipo_lava = 0
                self.lava_hitboxes = []
                self.lava_lado_horizontal = None
                self.lava_lado_vertical = None

        self.lava_hitboxes = []
        if self.tipo_lava != 0:
            tempo_simulado = self.tempo_lava_restante if self.lava_ativa else 10.0
            progresso = max(0.0, min(1.0, (10.0 - tempo_simulado) / 10.0))

            metade_largura = int(LARGURA_TELA * 0.5)
            metade_altura = int((ALTURA_TELA - 60) * 0.5)
            largura_h = max(32, int(metade_largura * progresso))
            altura_v = max(32, int(metade_altura * progresso))
            altura_area = ALTURA_TELA - 60

            lado_h = self.lava_lado_horizontal or "esquerda"
            if lado_h == "esquerda":
                rect_h = pygame.Rect(0, 60, largura_h, altura_area)
            else:
                rect_h = pygame.Rect(LARGURA_TELA - largura_h, 60, largura_h, altura_area)
            self.lava_hitboxes.append(rect_h)

            lado_v = self.lava_lado_vertical or "cima"
            if lado_v == "cima":
                rect_v = pygame.Rect(0, 60, LARGURA_TELA, altura_v)
            else:
                rect_v = pygame.Rect(0, ALTURA_TELA - altura_v, LARGURA_TELA, altura_v)
            self.lava_hitboxes.append(rect_v)

        if self.lava_ativa and not self.player.invencivel:
            p_rect = pygame.Rect(
                self.player.pos.x - self.player.tamanho // 2,
                self.player.pos.y - self.player.tamanho // 2,
                self.player.tamanho,
                self.player.tamanho,
            )
            for r in self.lava_hitboxes:
                if r.colliderect(p_rect):
                    self._lidar_com_morte()
                    return

        limite_spawn = 3.0 if self.modo_jogo == "SOBREVIVENCIA" else 1.5
        taxa_vel = 0.05 if self.modo_jogo == "SOBREVIVENCIA" else 0.1
        vel_base = 4 if self.modo_jogo == "SOBREVIVENCIA" else 6
        vel_max = 8 if self.modo_jogo == "SOBREVIVENCIA" else 12

        if self.temporizador_spawn > limite_spawn:
            vel_progressiva = min(vel_max, vel_base + (self.tempo_sobrevivencia * taxa_vel))
            self._spawn_inimigos(1, vel_progressiva)
            self.temporizador_spawn = 0.0
            self.shake_frames = 3


def atualizar_menu_interativo(self):
    teclas = pygame.key.get_pressed()
    self.player.update(teclas, self.particulas)

    for p in self.particulas[:]:
        p.update()
        if p.raio <= 0:
            self.particulas.remove(p)

    pads = self.obter_pads_menu()
    self.botao_selecionado = -1
    dist_min = 180

    for pad in pads:
        pad_vec = pygame.math.Vector2(pad["pos"])
        dist = self.player.pos.distance_to(pad_vec)

        if dist < dist_min:
            dist_min = dist
            self.botao_selecionado = pad["id"]


def _lidar_com_morte(self):
    self.shake_frames = 15
    self.mortes_total_jogador += 1
    if self.modo_jogo == "CORRIDA":
        self.iniciar_fase()
    elif self.modo_jogo == "CORRIDA_INFINITA":
        self.salvar_ranking(self.modo_jogo, self.fase_atual)
        self.estado = "RANKING"
        self.botao_selecionado = 0
    elif self.modo_jogo in ["SOBREVIVENCIA", "HARDCORE"]:
        self.salvar_ranking(self.modo_jogo, self.tempo_sobrevivencia)
        self.estado = "RANKING"
        self.botao_selecionado = 0
