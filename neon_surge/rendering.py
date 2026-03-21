import math
import random
import time

import pygame

from .config import (
    ALTURA_TELA,
    AMARELO_DADO,
    AZUL_ESCURO,
    BRANCO,
    CIANO_NEON,
    CINZA_CLARO,
    CINZA_ESCURO,
    LARGURA_TELA,
    LARANJA_NEON,
    PRETO_FUNDO,
    ROSA_NEON,
    ROXO_NEON,
    VERDE_NEON,
    VERMELHO_SANGUE,
)
from .entities import Particula
from .ui import (
    criar_painel_transparente,
    desenhar_botao_dinamico,
    desenhar_brilho_neon,
    desenhar_fundo_cyberpunk,
    desenhar_grade_jogo,
    desenhar_icone_som,
    desenhar_texto,
)


def desenhar_controle_volume(self, mx, my):
    largura_painel = 280
    altura_painel = 56
    x_painel = LARGURA_TELA - largura_painel - 20
    y_painel = ALTURA_TELA - altura_painel - 20

    rect_painel = pygame.Rect(x_painel, y_painel, largura_painel, altura_painel)
    surf_vol = criar_painel_transparente(largura_painel, altura_painel)
    self.tela.blit(surf_vol, (x_painel, y_painel))

    vol_str = "MUDO" if self.mutado else f"{int(self.volume_musica * 100)}%"
    cor_texto = CINZA_CLARO if self.mutado else VERDE_NEON
    desenhar_texto(self.tela, vol_str, self.fonte_sub, cor_texto, x_painel + 20, rect_painel.centery, alinhamento="esquerda")

    cx_mais = x_painel + largura_painel - 30
    cx_menos = cx_mais - 45
    cx_mute = cx_menos - 55

    self.rect_vol_mais.center = (cx_mais, rect_painel.centery)
    self.rect_vol_menos.center = (cx_menos, rect_painel.centery)
    self.rect_vol_mute.center = (cx_mute, rect_painel.centery)

    hover_mute = self.rect_vol_mute.collidepoint(mx, my)
    pygame.draw.rect(self.tela, CINZA_ESCURO if hover_mute else (10, 15, 25), self.rect_vol_mute, border_radius=6)
    pygame.draw.rect(self.tela, ROSA_NEON if hover_mute else CINZA_ESCURO, self.rect_vol_mute, 2, border_radius=6)
    desenhar_icone_som(self.tela, self.rect_vol_mute.centerx, self.rect_vol_mute.centery, self.mutado, BRANCO)

    hover_menos = self.rect_vol_menos.collidepoint(mx, my)
    pygame.draw.rect(self.tela, CINZA_ESCURO if hover_menos else (10, 15, 25), self.rect_vol_menos, border_radius=6)
    pygame.draw.rect(self.tela, CIANO_NEON if hover_menos else CINZA_ESCURO, self.rect_vol_menos, 2, border_radius=6)
    desenhar_texto(
        self.tela,
        "-",
        self.fonte_sub,
        BRANCO,
        self.rect_vol_menos.centerx,
        self.rect_vol_menos.centery,
        alinhamento="centro",
    )

    hover_mais = self.rect_vol_mais.collidepoint(mx, my)
    pygame.draw.rect(self.tela, CINZA_ESCURO if hover_mais else (10, 15, 25), self.rect_vol_mais, border_radius=6)
    pygame.draw.rect(self.tela, CIANO_NEON if hover_mais else CINZA_ESCURO, self.rect_vol_mais, 2, border_radius=6)
    desenhar_texto(
        self.tela,
        "+",
        self.fonte_sub,
        BRANCO,
        self.rect_vol_mais.centerx,
        self.rect_vol_mais.centery,
        alinhamento="centro",
    )


def desenhar(self):
    mx, my = self.obter_posicao_mouse()

    if self.estado != "MENU_MODO":
        if (mx, my) != self.ultima_pos_mouse:
            for i, btn in enumerate(self.botoes_hitboxes):
                if btn.collidepoint(mx, my):
                    self.botao_selecionado = i
            self.ultima_pos_mouse = (mx, my)

    cx, cy = LARGURA_TELA // 2, ALTURA_TELA // 2
    self.botoes_hitboxes = []

    if self.estado in ["INPUT_NOME", "MENU_MODO", "TELA_INFO_MODOS", "TELA_HOTKEYS", "TELA_INIMIGOS", "RANKING", "PERGUNTA_MODO"]:
        desenhar_fundo_cyberpunk(self.tela, self.tempo_global)

        for p in self.particulas_menu:
            p.update()
            p.draw(self.tela)

        self.desenhar_controle_volume(mx, my)
        if self.estado in ["TELA_INFO_MODOS", "TELA_HOTKEYS", "TELA_INIMIGOS", "PERGUNTA_MODO"]:
            pygame.draw.rect(self.tela, CINZA_ESCURO, (20, 20, 140, 40), border_radius=5)
            desenhar_texto(self.tela, "< ESC VOLTAR", self.fonte_texto, BRANCO, 90, 40, alinhamento="centro")

    if self.estado == "INPUT_NOME":
        desenhar_texto(self.tela, "NEON SURGE", self.fonte_titulo, CIANO_NEON, cx, cy - 120)
        desenhar_texto(self.tela, "IDENTIFICAÇÃO DO PILOTO:", self.fonte_texto, BRANCO, cx, cy)

        caixa_texto = pygame.Rect(0, 0, 400, 60)
        caixa_texto.center = (cx, cy + 50)
        pygame.draw.rect(self.tela, AZUL_ESCURO, caixa_texto, border_radius=10)
        pygame.draw.rect(self.tela, VERDE_NEON, caixa_texto, 2, border_radius=10)

        cursor = "_" if int(time.time() * 2) % 2 == 0 else ""
        desenhar_texto(self.tela, self.nome_jogador + cursor, self.fonte_sub, VERDE_NEON, cx, cy + 50)

        btn_rect = desenhar_botao_dinamico(
            self.tela, "CONFIRMAR DADOS", self.fonte_sub, VERDE_NEON, cx, cy + 150, self.botao_selecionado == 0
        )
        self.botoes_hitboxes.append(btn_rect)

    elif self.estado == "PERGUNTA_MODO":
        desenhar_texto(self.tela, "NOVO PILOTO REGISTRADO", self.fonte_titulo, VERDE_NEON, cx, cy - 100)
        modo_formatado = self.modo_jogo.replace("_", " ")
        btn_manter_modo = desenhar_botao_dinamico(
            self.tela,
            f"CONTINUAR EM: {modo_formatado}",
            self.fonte_sub,
            CIANO_NEON,
            cx,
            cy + 30,
            self.botao_selecionado == 0,
        )
        btn_mudar_modo = desenhar_botao_dinamico(
            self.tela, "ESCOLHER NOVO MODO", self.fonte_sub, ROSA_NEON, cx, cy + 110, self.botao_selecionado == 1
        )
        self.botoes_hitboxes.extend([btn_manter_modo, btn_mudar_modo])

    elif self.estado == "MENU_MODO":
        offset_x = random.randint(-4, 4) if self.shake_frames > 0 else 0
        offset_y = random.randint(-4, 4) if self.shake_frames > 0 else 0
        if self.shake_frames > 0:
            self.shake_frames -= 1

        desenhar_texto(self.tela, "SISTEMA PRINCIPAL", self.fonte_titulo, BRANCO, cx + offset_x, 60 + offset_y)
        desenhar_texto(
            self.tela,
            "USE SEU DASH [ ESPAÇO ] NO NÓDULO OU APERTE [ ENTER ] PARA SELECIONAR",
            self.fonte_texto,
            VERDE_NEON,
            cx + offset_x,
            120 + offset_y,
        )

        pads = self.obter_pads_menu()

        for pad in pads:
            px, py = pad["pos"]
            cor = pad["cor"]
            dist = self.player.pos.distance_to(pygame.math.Vector2(px, py))

            is_hovered = self.botao_selecionado == pad["id"]

            if is_hovered or dist < 300:
                espessura = max(1, int(6 - (dist / 60))) if dist < 300 else 2
                pygame.draw.line(self.tela, (*cor[:3], 150), self.player.pos, (px, py), espessura)

        for pad in pads:
            px, py = pad["pos"]
            cor = pad["cor"]
            is_hovered = self.botao_selecionado == pad["id"]

            raio_pad = 45 + (math.sin(time.time() * 12) * 8 if is_hovered else math.sin(time.time() * 4) * 3)

            desenhar_brilho_neon(self.tela, cor, px, py, raio_pad, 4)
            pygame.draw.circle(self.tela, PRETO_FUNDO, (int(px), int(py)), int(raio_pad - 6))
            pygame.draw.circle(self.tela, cor, (int(px), int(py)), int(raio_pad), 5)

            if is_hovered:
                pygame.draw.circle(self.tela, cor, (int(px), int(py)), int(raio_pad // 2))

            desenhar_texto(self.tela, pad["texto"], self.fonte_sub, BRANCO if is_hovered else cor, px, py - 80)

        for p in self.particulas:
            p.draw(self.tela)
        if self.player:
            self.player.draw(self.tela)

    elif self.estado == "TELA_INFO_MODOS":
        desenhar_texto(self.tela, "MANUAL DOS MODOS DE JOGO", self.fonte_titulo, AMARELO_DADO, cx, 80)
        largura_painel, altura_painel = min(1150, LARGURA_TELA - 40), min(500, ALTURA_TELA - 160)
        surf_painel = criar_painel_transparente(largura_painel, altura_painel)
        painel_rect = pygame.Rect(0, 0, largura_painel, altura_painel)
        painel_rect.center = (cx, cy - 10)
        self.tela.blit(surf_painel, painel_rect.topleft)
        x_esq = painel_rect.left + 50

        y_base = painel_rect.top + 30
        desenhar_texto(self.tela, "CORRIDA / CORRIDA HARDCORE:", self.fonte_sub, CIANO_NEON, x_esq, y_base, alinhamento="esquerda")
        desenhar_texto(
            self.tela,
            "Complete 10 fases no menor tempo. No Hardcore, a morte devolve-o para a fase 1.",
            self.fonte_desc,
            BRANCO,
            x_esq,
            y_base + 35,
            alinhamento="esquerda",
        )

        y_base = painel_rect.top + 130
        desenhar_texto(self.tela, "CORRIDA INFINITA:", self.fonte_sub, ROXO_NEON, x_esq, y_base, alinhamento="esquerda")
        desenhar_texto(
            self.tela,
            "Fases não têm fim. A cada 10 fases o Boss muda de forma, cor e dificuldade!",
            self.fonte_desc,
            BRANCO,
            x_esq,
            y_base + 35,
            alinhamento="esquerda",
        )

        y_base = painel_rect.top + 230
        desenhar_texto(self.tela, "SOBREVIVÊNCIA / HARDCORE:", self.fonte_sub, ROSA_NEON, x_esq, y_base, alinhamento="esquerda")
        desenhar_texto(
            self.tela,
            "A cada 30 segundos, o cenário vai ser invadido por LAVA! Fuja das zonas de aviso.",
            self.fonte_desc,
            BRANCO,
            x_esq,
            y_base + 35,
            alinhamento="esquerda",
        )

        y_base = painel_rect.top + 330
        desenhar_texto(
            self.tela,
            "OS PORTAIS VERMELHOS (Aviso de Inimigo):",
            self.fonte_sub,
            VERMELHO_SANGUE,
            x_esq,
            y_base,
            alinhamento="esquerda",
        )
        desenhar_texto(
            self.tela,
            "Antes de um inimigo materializar-se, um portal indica onde ele vai surgir, permitindo que escape.",
            self.fonte_desc,
            BRANCO,
            x_esq,
            y_base + 35,
            alinhamento="esquerda",
        )

        btn_voltar = desenhar_botao_dinamico(
            self.tela, "VOLTAR PARA O MENU", self.fonte_sub, VERDE_NEON, cx, cy + 300, self.botao_selecionado == 0
        )
        self.botoes_hitboxes.append(btn_voltar)

    elif self.estado == "TELA_HOTKEYS":
        desenhar_texto(self.tela, "CONTROLES DO SISTEMA", self.fonte_titulo, VERDE_NEON, cx, 100)
        comandos = [
            ("W A S D / SETAS", "Mover a Nave"),
            ("BARRA DE ESPAÇO", "DASH (Invencibilidade Rápida)"),
            ("TECLA ESC", "Pausar ou Voltar Menus"),
            ("TECLA F11", "Ativar/Desativar Ecrã Inteiro"),
        ]
        for i, (tecla, desc) in enumerate(comandos):
            y_pos = 240 + (i * 70)
            desenhar_texto(self.tela, tecla, self.fonte_sub, CIANO_NEON, cx - 40, y_pos, alinhamento="direita")
            desenhar_texto(self.tela, "- " + desc, self.fonte_texto, BRANCO, cx + 40, y_pos, alinhamento="esquerda")

        btn_prox = desenhar_botao_dinamico(
            self.tela, "AVANÇAR PARA AMEAÇAS", self.fonte_sub, ROSA_NEON, cx, cy + 240, self.botao_selecionado == 0
        )
        self.botoes_hitboxes.append(btn_prox)

    elif self.estado == "TELA_INIMIGOS":
        desenhar_texto(self.tela, "ARQUIVO DE AMEAÇAS", self.fonte_titulo, VERMELHO_SANGUE, cx, 60)

        largura_painel, altura_painel = min(1100, LARGURA_TELA - 40), min(540, ALTURA_TELA - 160)
        surf_painel = criar_painel_transparente(largura_painel, altura_painel)
        painel_rect = pygame.Rect(0, 0, largura_painel, altura_painel)
        painel_rect.center = (cx, cy - 20)
        self.tela.blit(surf_painel, painel_rect.topleft)

        espacamento = painel_rect.left + 150
        espaco_y = 115

        y_base = painel_rect.top + 45
        desenhar_brilho_neon(self.tela, ROSA_NEON, painel_rect.left + 80, y_base + 20, 18, 2)
        pygame.draw.circle(self.tela, ROSA_NEON, (painel_rect.left + 80, y_base + 20), 18)
        pygame.draw.circle(self.tela, BRANCO, (painel_rect.left + 80, y_base + 20), 6)
        desenhar_texto(self.tela, "SENTINELA (O Básico):", self.fonte_sub, ROSA_NEON, espacamento, y_base, alinhamento="esquerda")
        desenhar_texto(
            self.tela,
            "Patrulha rebatendo nas paredes. Cuidado com o efeito manada,",
            self.fonte_desc,
            BRANCO,
            espacamento,
            y_base + 35,
            alinhamento="esquerda",
        )
        desenhar_texto(
            self.tela,
            "pois eles ricocheteiam uns nos outros.",
            self.fonte_desc,
            CINZA_CLARO,
            espacamento,
            y_base + 60,
            alinhamento="esquerda",
        )

        y_base += espaco_y
        desenhar_brilho_neon(self.tela, VERMELHO_SANGUE, painel_rect.left + 80, y_base + 20, 18, 2)
        pygame.draw.circle(self.tela, VERMELHO_SANGUE, (painel_rect.left + 80, y_base + 20), 18)
        pygame.draw.circle(self.tela, BRANCO, (painel_rect.left + 80, y_base + 20), 6)
        desenhar_texto(
            self.tela,
            "CAÇADOR (A Sanguessuga):",
            self.fonte_sub,
            VERMELHO_SANGUE,
            espacamento,
            y_base,
            alinhamento="esquerda",
        )
        desenhar_texto(
            self.tela,
            "Persegue a sua posição futura. Ele vai tentar prever os seus",
            self.fonte_desc,
            BRANCO,
            espacamento,
            y_base + 35,
            alinhamento="esquerda",
        )
        desenhar_texto(
            self.tela,
            "movimentos e bloquear a sua fuga em ziguezague.",
            self.fonte_desc,
            CINZA_CLARO,
            espacamento,
            y_base + 60,
            alinhamento="esquerda",
        )

        y_base += espaco_y
        desenhar_brilho_neon(self.tela, LARANJA_NEON, painel_rect.left + 80, y_base + 20, 18, 2)
        pygame.draw.circle(self.tela, LARANJA_NEON, (painel_rect.left + 80, y_base + 20), 18)
        pygame.draw.circle(self.tela, BRANCO, (painel_rect.left + 80, y_base + 20), 6)
        desenhar_texto(self.tela, "SNIPER (O Fuzil):", self.fonte_sub, LARANJA_NEON, espacamento, y_base, alinhamento="esquerda")
        desenhar_texto(
            self.tela,
            "Aguarde o feixe de mira, use o Dash no momento exato do disparo.",
            self.fonte_desc,
            BRANCO,
            espacamento,
            y_base + 35,
            alinhamento="esquerda",
        )
        desenhar_texto(
            self.tela,
            "Ele destrói-se automaticamente após a investida.",
            self.fonte_desc,
            CINZA_CLARO,
            espacamento,
            y_base + 60,
            alinhamento="esquerda",
        )

        y_base += espaco_y
        desenhar_brilho_neon(self.tela, AMARELO_DADO, painel_rect.left + 80, y_base + 20, 18, 2)
        pygame.draw.circle(self.tela, AMARELO_DADO, (painel_rect.left + 80, y_base + 20), 18)
        pygame.draw.circle(self.tela, BRANCO, (painel_rect.left + 80, y_base + 20), 6)
        desenhar_texto(self.tela, "A BOMBA (O Relógio):", self.fonte_sub, AMARELO_DADO, espacamento, y_base, alinhamento="esquerda")
        desenhar_texto(
            self.tela,
            "Segue-o e detona num raio gigantesco quando o relógio expirar.",
            self.fonte_desc,
            BRANCO,
            espacamento,
            y_base + 35,
            alinhamento="esquerda",
        )
        desenhar_texto(
            self.tela,
            "Saia de perto assim que ela parar e começar a piscar!",
            self.fonte_desc,
            CINZA_CLARO,
            espacamento,
            y_base + 60,
            alinhamento="esquerda",
        )

        btn_iniciar = desenhar_botao_dinamico(
            self.tela, "INICIAR SEQUÊNCIA", self.fonte_sub, VERDE_NEON, cx, cy + 300, self.botao_selecionado == 0
        )
        self.botoes_hitboxes.append(btn_iniciar)

    elif self.estado in ["JOGANDO", "PAUSA"]:
        offset_x = random.randint(-8, 8) if self.shake_frames > 0 else 0
        offset_y = random.randint(-8, 8) if self.shake_frames > 0 else 0
        if self.shake_frames > 0 and self.estado == "JOGANDO":
            self.shake_frames -= 1

        self.tela.fill(PRETO_FUNDO)
        surf_jogo = pygame.Surface((LARGURA_TELA, ALTURA_TELA), pygame.SRCALPHA)
        desenhar_grade_jogo(surf_jogo)

        for p in self.portais_inimigos:
            raio = 15 + math.sin(time.time() * 15) * 5
            cor_portal = ROXO_NEON if p["tipo"] == "boss" else VERMELHO_SANGUE
            pygame.draw.circle(surf_jogo, (*cor_portal[:3], 150), (int(p["pos"].x), int(p["pos"].y)), int(raio))
            pygame.draw.circle(surf_jogo, cor_portal, (int(p["pos"].x), int(p["pos"].y)), int(raio), 2)
            desenhar_brilho_neon(surf_jogo, cor_portal, p["pos"].x, p["pos"].y, raio, 2)

        if self.modo_jogo in ["SOBREVIVENCIA", "HARDCORE"]:
            if self.aviso_lava > 0.0 and self.tipo_lava != 0:
                for r in self.lava_hitboxes:
                    aviso_surf = pygame.Surface((r.width, r.height), pygame.SRCALPHA)
                    alpha = int(100 + math.sin(time.time() * 20) * 50)
                    aviso_surf.fill((255, 150, 0, alpha))
                    pygame.draw.rect(aviso_surf, AMARELO_DADO, (0, 0, r.width, r.height), 4)
                    surf_jogo.blit(aviso_surf, (r.x, r.y))
                desenhar_texto(
                    surf_jogo,
                    f"ALERTA DE LAVA EM {int(self.aviso_lava) + 1}s!",
                    self.fonte_titulo,
                    VERMELHO_SANGUE,
                    LARGURA_TELA // 2,
                    140,
                )

            if getattr(self, "lava_ativa", False):
                for r in self.lava_hitboxes:
                    lava_surf = pygame.Surface((r.width, r.height), pygame.SRCALPHA)
                    lava_surf.fill((255, 60, 0, 140))
                    pygame.draw.rect(lava_surf, VERMELHO_SANGUE, (0, 0, r.width, r.height), 4)
                    for i in range(0, r.width + r.height, 40):
                        pygame.draw.line(lava_surf, (255, 100, 0, 100), (i, 0), (0, i), 3)
                    surf_jogo.blit(lava_surf, (r.x, r.y))
                    if random.random() < 0.2:
                        px = random.randint(r.left, r.right)
                        py = random.randint(r.top, r.bottom)
                        self.particulas.append(Particula(px, py, LARANJA_NEON))

                desenhar_texto(
                    surf_jogo,
                    f"LAVA ATIVA: {self.tempo_lava_restante:.1f}s",
                    self.fonte_sub,
                    LARANJA_NEON,
                    LARGURA_TELA // 2,
                    90,
                )

        for d in self.coletaveis:
            desenhar_brilho_neon(surf_jogo, AMARELO_DADO, d.x, d.y, 6, 2)
            pygame.draw.rect(surf_jogo, AMARELO_DADO, (int(d.x) - 6, int(d.y) - 6, 12, 12), border_radius=2)

        if self.portal_aberto:
            raio = 20 + math.sin(time.time() * 10) * 5
            desenhar_brilho_neon(surf_jogo, VERDE_NEON, self.portal_pos.x, self.portal_pos.y, raio, 4)
            pygame.draw.circle(surf_jogo, VERDE_NEON, (int(self.portal_pos.x), int(self.portal_pos.y)), int(raio), 3)

        for p in self.particulas:
            p.draw(surf_jogo)
        for ini in self.inimigos:
            ini.draw(surf_jogo)
        self.player.draw(surf_jogo)

        self.tela.blit(surf_jogo, (offset_x, offset_y))

        pygame.draw.rect(self.tela, PRETO_FUNDO, (0, 0, LARGURA_TELA, 60))
        pygame.draw.line(self.tela, CIANO_NEON, (0, 60), (LARGURA_TELA, 60), 2)

        if self.modo_jogo in ["CORRIDA", "CORRIDA_HARDCORE", "CORRIDA_INFINITA"]:
            texto_tempo = f"{self.tempo_corrida:.1f}s"
            desc_hud = self.modo_jogo.replace("_", " ")
            eh_fase_boss = (self.modo_jogo in ["CORRIDA", "CORRIDA_HARDCORE"] and self.fase_atual == 10) or (
                self.modo_jogo == "CORRIDA_INFINITA" and self.fase_atual > 0 and self.fase_atual % 10 == 0
            )
            if eh_fase_boss:
                desenhar_texto(
                    self.tela,
                    f"{desc_hud} - FASE FINAL (O SOBERANO!)",
                    self.fonte_sub,
                    ROXO_NEON,
                    20,
                    30,
                    alinhamento="esquerda",
                )
            else:
                desenhar_texto(
                    self.tela,
                    f"{desc_hud} - FASE {self.fase_atual}",
                    self.fonte_sub,
                    BRANCO,
                    20,
                    30,
                    alinhamento="esquerda",
                )
        else:
            texto_tempo = f"{self.tempo_sobrevivencia:.1f}s"
            titulo_hud = "MODO SOBREVIVÊNCIA" if self.modo_jogo == "SOBREVIVENCIA" else "SOBREVIVÊNCIA HARDCORE"
            cor_hud = BRANCO if self.modo_jogo == "SOBREVIVENCIA" else VERMELHO_SANGUE
            desenhar_texto(self.tela, titulo_hud, self.fonte_sub, cor_hud, 20, 30, alinhamento="esquerda")

        desenhar_texto(self.tela, texto_tempo, self.fonte_sub, VERDE_NEON, LARGURA_TELA - 20, 30, alinhamento="direita")

        if self.estado == "PAUSA":
            overlay = pygame.Surface((LARGURA_TELA, ALTURA_TELA), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            self.tela.blit(overlay, (0, 0))

            desenhar_texto(self.tela, "SISTEMA PAUSADO", self.fonte_titulo, BRANCO, cx, cy - 100)
            btn_cont = desenhar_botao_dinamico(
                self.tela, "CONTINUAR [ESC]", self.fonte_sub, VERDE_NEON, cx, cy + 30, self.botao_selecionado == 0
            )
            btn_sair = desenhar_botao_dinamico(
                self.tela, "ABANDONAR PARTIDA", self.fonte_sub, VERMELHO_SANGUE, cx, cy + 110, self.botao_selecionado == 1
            )

            self.botoes_hitboxes.append(btn_cont)
            self.botoes_hitboxes.append(btn_sair)

    elif self.estado == "RANKING":
        titulo = f"GAME OVER - {self.modo_jogo.replace('_', ' ')}"
        cor_titulo = VERMELHO_SANGUE if "HARDCORE" in self.modo_jogo else (VERDE_NEON if "CORRIDA" in self.modo_jogo else ROSA_NEON)
        desenhar_texto(self.tela, titulo, self.fonte_titulo, cor_titulo, cx, 50)

        largura_rank = min(800, LARGURA_TELA - 40)
        altura_rank = 340
        surf_rank = criar_painel_transparente(largura_rank, altura_rank)
        rect_ranking = pygame.Rect(0, 0, largura_rank, altura_rank)
        rect_ranking.center = (cx, cy - 60)

        self.tela.blit(surf_rank, rect_ranking.topleft)
        desenhar_texto(self.tela, "DESEMPENHO DA MISSÃO:", self.fonte_sub, VERDE_NEON, cx, rect_ranking.top + 20)

        if self.modo_jogo == "CORRIDA_INFINITA":
            texto_desempenho = f"Fase Alcançada: {int(self.ultimo_tempo)}    |    Sua Posição: {self.ultima_posicao}º Lugar"
        else:
            texto_desempenho = f"Tempo: {self.ultimo_tempo:.1f}s    |    Sua Posição: {self.ultima_posicao}º Lugar"

        desenhar_texto(self.tela, texto_desempenho, self.fonte_sub, BRANCO, cx, rect_ranking.top + 55)
        pygame.draw.line(
            self.tela,
            CINZA_ESCURO,
            (rect_ranking.left + 50, rect_ranking.top + 85),
            (rect_ranking.right - 50, rect_ranking.top + 85),
            2,
        )
        desenhar_texto(
            self.tela,
            f"--- TOP 5 {self.modo_jogo.replace('_', ' ')} ---",
            self.fonte_sub,
            CIANO_NEON,
            cx,
            rect_ranking.top + 115,
        )

        if self.modo_jogo == "CORRIDA":
            chave_modo = "Corrida"
        elif self.modo_jogo == "CORRIDA_HARDCORE":
            chave_modo = "Corrida_Hardcore"
        elif self.modo_jogo == "SOBREVIVENCIA":
            chave_modo = "Sobrevivencia"
        elif self.modo_jogo == "CORRIDA_INFINITA":
            chave_modo = "Corrida_Infinita"
        else:
            chave_modo = "Hardcore"
        top5 = self.ranking.get(chave_modo, [])

        margem_esq = rect_ranking.left + 80
        margem_dir = rect_ranking.right - 80

        for i, reg in enumerate(top5[:5]):
            cor = AMARELO_DADO if reg.get("id", 0) == self.ranking[chave_modo][self.ultima_posicao - 1].get("id", 0) else BRANCO
            y_pos = rect_ranking.top + 155 + (i * 35)
            desenhar_texto(self.tela, f"{i + 1}º {reg['nome']}", self.fonte_sub, cor, margem_esq, y_pos, alinhamento="esquerda")

            texto_valor = f"Fase {reg.get('fase', 0)}" if chave_modo == "Corrida_Infinita" else f"{reg.get('tempo', 0):.1f}s"
            desenhar_texto(self.tela, texto_valor, self.fonte_sub, cor, margem_dir, y_pos, alinhamento="direita")

        espaco_y = 65
        y_botoes = rect_ranking.bottom + 40

        btn_replay = desenhar_botao_dinamico(
            self.tela, "JOGAR NOVAMENTE", self.fonte_sub, VERDE_NEON, cx, y_botoes, self.botao_selecionado == 0
        )
        btn_manter = desenhar_botao_dinamico(
            self.tela, "MANTER PILOTO (MENU)", self.fonte_sub, CIANO_NEON, cx, y_botoes + espaco_y, self.botao_selecionado == 1
        )
        btn_novo = desenhar_botao_dinamico(
            self.tela,
            "CRIAR NOVO PILOTO",
            self.fonte_sub,
            ROSA_NEON,
            cx,
            y_botoes + (espaco_y * 2),
            self.botao_selecionado == 2,
        )

        self.botoes_hitboxes.extend([btn_replay, btn_manter, btn_novo])

    if self.is_fullscreen:
        w, h = self.tela_real.get_size()
        tela_redimensionada = pygame.transform.scale(self.tela, (w, h))
        self.tela_real.blit(tela_redimensionada, (0, 0))
    else:
        self.tela_real.blit(self.tela, (0, 0))

    pygame.display.flip()
