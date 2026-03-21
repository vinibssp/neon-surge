import random

import pygame

from .config import ALTURA_TELA, AMARELO_DADO, CIANO_NEON, LARGURA_TELA, LARANJA_NEON, ROSA_NEON, ROXO_NEON, VERMELHO_SANGUE
from .entities import Inimigo, Particula, Player


def entrar_menu_modo(self):
    self.estado = "MENU_MODO"
    self.player = Player(LARGURA_TELA // 2, ALTURA_TELA // 2 + 150)
    self.particulas.clear()
    self.botao_selecionado = -1


def obter_pads_menu(self):
    cx, cy = LARGURA_TELA // 2, ALTURA_TELA // 2
    dx = min(350, LARGURA_TELA * 0.3)
    dy = min(180, ALTURA_TELA * 0.22)
    return [
        {"id": 0, "modo": "CORRIDA", "texto": "CORRIDA 10 FASES", "pos": (cx - dx, cy - dy), "cor": CIANO_NEON},
        {"id": 5, "modo": "CORRIDA_INFINITA", "texto": "CORRIDA INFINITA", "pos": (cx, cy - dy), "cor": ROXO_NEON},
        {"id": 1, "modo": "CORRIDA_HARDCORE", "texto": "CORRIDA HARDCORE", "pos": (cx + dx, cy - dy), "cor": VERMELHO_SANGUE},
        {"id": 2, "modo": "SOBREVIVENCIA", "texto": "SOBREVIVÊNCIA", "pos": (cx - dx, cy + dy), "cor": ROSA_NEON},
        {"id": 4, "modo": "INFO", "texto": "TUTORIAL / INFO", "pos": (cx, cy + dy), "cor": AMARELO_DADO},
        {"id": 3, "modo": "HARDCORE", "texto": "SOBREV. HARDCORE", "pos": (cx + dx, cy + dy), "cor": LARANJA_NEON},
    ]


def iniciar_fase(self):
    self.player = Player(LARGURA_TELA // 2, ALTURA_TELA // 2)
    self.inimigos.clear()
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

    if self.fase_atual == 1:
        self.tempo_corrida = 0.0
        self.tempo_sobrevivencia = 0.0
        self.temporizador_spawn = 0.0

    if self.modo_jogo in ["CORRIDA", "CORRIDA_HARDCORE", "CORRIDA_INFINITA"]:
        eh_fase_boss = (self.modo_jogo in ["CORRIDA", "CORRIDA_HARDCORE"] and self.fase_atual == 10) or (
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
                    "tempo": 2.0,
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
    for _ in range(quantidade):
        tipo = random.choice(["quique", "perseguidor", "investida", "explosivo"])
        ex, ey = self.player.pos.x, self.player.pos.y
        while abs(ex - self.player.pos.x) < 300 and abs(ey - self.player.pos.y) < 300:
            ex = random.randint(50, LARGURA_TELA - 50)
            ey = random.randint(110, ALTURA_TELA - 50)

        self.portais_inimigos.append({"pos": pygame.math.Vector2(ex, ey), "tipo": tipo, "vel": velocidade, "tempo": 1.5})


def atualizar_jogo(self):
    teclas = pygame.key.get_pressed()
    if self.player.update(teclas, self.particulas):
        self.shake_frames = 6

    for p in self.particulas[:]:
        p.update()
        if p.raio <= 0:
            self.particulas.remove(p)

    for p in self.portais_inimigos[:]:
        p["tempo"] -= self.dt
        if p["tempo"] <= 0:
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

    if self.modo_jogo in ["CORRIDA", "CORRIDA_HARDCORE", "CORRIDA_INFINITA"]:
        self.tempo_corrida += self.dt
        for d in self.coletaveis[:]:
            if self.player.pos.distance_to(d) < 20:
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
                self.botao_selecionado = -1

    elif self.modo_jogo in ["SOBREVIVENCIA", "HARDCORE"]:
        self.tempo_sobrevivencia += self.dt
        self.temporizador_spawn += self.dt

        if not self.lava_ativa:
            self.tempo_para_lava -= self.dt
            if self.tempo_para_lava <= 3.0:
                if self.tipo_lava == 0:
                    self.tipo_lava = random.randint(1, 3)
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

        self.lava_hitboxes = []
        if self.tipo_lava != 0:
            tempo_simulado = self.tempo_lava_restante if self.lava_ativa else 10.0
            if self.tipo_lava == 1:
                margem = 180
                self.lava_hitboxes.append(pygame.Rect(0, 60, LARGURA_TELA, margem))
                self.lava_hitboxes.append(pygame.Rect(0, ALTURA_TELA - margem, LARGURA_TELA, margem))
                self.lava_hitboxes.append(pygame.Rect(0, 60, margem, ALTURA_TELA))
                self.lava_hitboxes.append(pygame.Rect(LARGURA_TELA - margem, 60, margem, ALTURA_TELA))
            elif self.tipo_lava == 2:
                cx, cy = LARGURA_TELA // 2, (ALTURA_TELA + 60) // 2
                w, h = 500, 350
                self.lava_hitboxes.append(pygame.Rect(cx - w // 2, cy - h // 2, w, h))
            elif self.tipo_lava == 3:
                desloc_y = (10.0 - tempo_simulado) * 150
                largura_p = 250
                p_y = (desloc_y % (ALTURA_TELA + largura_p)) - largura_p
                self.lava_hitboxes.append(pygame.Rect(0, p_y, LARGURA_TELA, largura_p))

                desloc_x = (10.0 - tempo_simulado) * 200
                p_x = (desloc_x % (LARGURA_TELA + largura_p)) - largura_p
                self.lava_hitboxes.append(pygame.Rect(p_x, 60, largura_p, ALTURA_TELA))

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

        raio_colisao = 55
        if dist < raio_colisao + self.player.tamanho:
            if self.player.dash_timer > 0:
                self.shake_frames = 20
                for _ in range(50):
                    self.particulas.append(Particula(pad["pos"][0], pad["pos"][1], pad["cor"]))
                self.botao_selecionado = pad["id"]
                self.acionar_botao()
                return
            elif dist > 0:
                normal = (self.player.pos - pad_vec).normalize()
                self.player.vel += normal * 2

        if dist < dist_min:
            dist_min = dist
            self.botao_selecionado = pad["id"]


def _lidar_com_morte(self):
    self.shake_frames = 15
    if self.modo_jogo == "CORRIDA":
        self.iniciar_fase()
    elif self.modo_jogo == "CORRIDA_HARDCORE":
        self.salvar_ranking(self.modo_jogo, self.tempo_corrida)
        self.estado = "RANKING"
        self.botao_selecionado = -1
    elif self.modo_jogo == "CORRIDA_INFINITA":
        self.salvar_ranking(self.modo_jogo, self.fase_atual)
        self.estado = "RANKING"
        self.botao_selecionado = -1
    elif self.modo_jogo in ["SOBREVIVENCIA", "HARDCORE"]:
        self.salvar_ranking(self.modo_jogo, self.tempo_sobrevivencia)
        self.estado = "RANKING"
        self.botao_selecionado = -1
