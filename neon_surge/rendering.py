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


def _desenhar_teclas_menu(self, cx, cy):
    base_y = cy + 10
    key_w, key_h = 38, 32
    esp = 8

    def tecla(txt, x, y, largura=key_w, altura=key_h, cor=CIANO_NEON):
        rect = pygame.Rect(0, 0, largura, altura)
        rect.center = (x, y)
        pygame.draw.rect(self.tela, (10, 16, 24), rect, border_radius=6)
        pygame.draw.rect(self.tela, cor, rect, 2, border_radius=6)
        desenhar_texto(self.tela, txt, self.fonte_desc, BRANCO, rect.centerx, rect.centery)

    tecla("W", cx, base_y - (key_h + esp))
    tecla("A", cx - (key_w + esp), base_y)
    tecla("S", cx, base_y)
    tecla("D", cx + (key_w + esp), base_y)
    tecla("SPACE", cx, base_y + (key_h + 24), largura=132, altura=30, cor=AMARELO_DADO)


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

        # desenhar_texto(self.tela, "SISTEMA PRINCIPAL", self.fonte_titulo, BRANCO, cx + offset_x, 60 + offset_y)
        # desenhar_texto(
        #     self.tela,
        #     "SELECIONE UM MODO PELO CÍRCULO E USE SPACE PARA DASH/CONFIRMAR",
        #     self.fonte_texto,
        #     VERDE_NEON,
        #     cx + offset_x,
        #     120 + offset_y,
        # )

        pads = self.obter_pads_menu()
        centro_menu = pygame.math.Vector2(cx, cy + 10)
        _desenhar_teclas_menu(self, cx, cy + 8)
        # desenhar_texto(self.tela, "Mover", self.fonte_desc, CINZA_CLARO, cx, cy + 66)
        # desenhar_texto(self.tela, "SPACE: dash / selecionar", self.fonte_desc, AMARELO_DADO, cx, cy + 88)

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

            vetor = pygame.math.Vector2(px, py) - centro_menu
            if vetor.length() > 0:
                vetor = vetor.normalize()
            label_x = px + (vetor.x * 78)
            label_y = py + (vetor.y * 78)
            desenhar_texto(self.tela, pad["texto"], self.fonte_sub, BRANCO if is_hovered else cor, label_x, label_y)

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
        desenhar_texto(self.tela, "CORRIDA:", self.fonte_sub, CIANO_NEON, x_esq, y_base, alinhamento="esquerda")
        desenhar_texto(
            self.tela,
            "Complete 10 fases no menor tempo possível.",
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

        x_icone = painel_rect.left + 65
        x_texto = painel_rect.left + 120
        y_base = painel_rect.top + 30
        espaco_y = 70

        ameacas = [
            (ROSA_NEON, "SENTINELA", "Ricocheteia no cenário e em outros inimigos."),
            (VERMELHO_SANGUE, "CAÇADOR", "Prevê sua rota e fecha espaço para fuga."),
            (LARANJA_NEON, "INVESTIDA", "Trava mira e dispara em linha reta."),
            (AMARELO_DADO, "BOMBA", "Explode em área grande ao final da contagem."),
            (ROXO_NEON, "ATIRADOR", "Fica parado, dura 10s e atira padrão aleatório."),
            (LARANJA_NEON, "LAVA SETORIAL", "Avança pelas bordas e elimina ao toque."),
            (VERMELHO_SANGUE, "PORTAIS", "Avisam o ponto de spawn inimigo."),
        ]

        for i, (cor_ameaca, titulo, descricao) in enumerate(ameacas):
            y_item = y_base + (i * espaco_y)
            desenhar_brilho_neon(self.tela, cor_ameaca, x_icone, y_item + 16, 14, 2)
            pygame.draw.circle(self.tela, cor_ameaca, (x_icone, y_item + 16), 14)
            pygame.draw.circle(self.tela, BRANCO, (x_icone, y_item + 16), 4)
            desenhar_texto(self.tela, titulo + ":", self.fonte_sub, cor_ameaca, x_texto, y_item, alinhamento="esquerda")
            desenhar_texto(self.tela, descricao, self.fonte_desc, BRANCO, x_texto, y_item + 28, alinhamento="esquerda")

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
            cor_portal = ROXO_NEON if p["tipo"] == "boss" else VERMELHO_SANGUE
            centro = (int(p["pos"].x), int(p["pos"].y))
            raio_base = 20 if p["tipo"] == "boss" else 16
            pulso = abs(math.sin(time.time() * 6)) * 3
            raio = raio_base + pulso

            desenhar_brilho_neon(surf_jogo, cor_portal, centro[0], centro[1], raio + 2, 3)
            pygame.draw.circle(surf_jogo, (*cor_portal, 128), centro, int(raio + 3))
            pygame.draw.circle(surf_jogo, PRETO_FUNDO, centro, int(raio - 4))
            pygame.draw.circle(surf_jogo, cor_portal, centro, int(raio), 3)

            angulo_inicio = (time.time() * 6) % (math.pi * 2)
            angulo_fim = angulo_inicio + (math.pi * 1.3)
            rect_loading = pygame.Rect(0, 0, int(raio * 2), int(raio * 2))
            rect_loading.center = centro
            pygame.draw.arc(surf_jogo, BRANCO, rect_loading, angulo_inicio, angulo_fim, 4)

            dot_x = centro[0] + math.cos(angulo_inicio) * raio
            dot_y = centro[1] + math.sin(angulo_inicio) * raio
            pygame.draw.circle(surf_jogo, BRANCO, (int(dot_x), int(dot_y)), 4)

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
                janela_piscada = 1.5
                periodo_piscada = 0.25
                em_piscada_final = self.tempo_lava_restante <= janela_piscada

                if em_piscada_final:
                    fase = (janela_piscada - max(0.0, self.tempo_lava_restante)) % periodo_piscada
                    lava_visivel = fase < (periodo_piscada / 2)
                else:
                    lava_visivel = True

                if lava_visivel:
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

                texto_lava = f"LAVA DESATIVANDO: {self.tempo_lava_restante:.1f}s" if em_piscada_final else f"LAVA ATIVA: {self.tempo_lava_restante:.1f}s"
                cor_lava = VERMELHO_SANGUE if em_piscada_final else LARANJA_NEON
                desenhar_texto(
                    surf_jogo,
                    texto_lava,
                    self.fonte_sub,
                    cor_lava,
                    LARGURA_TELA // 2,
                    90,
                )

        for d in self.coletaveis:
            desenhar_brilho_neon(surf_jogo, AMARELO_DADO, d.x, d.y, 6, 2)
            pygame.draw.rect(surf_jogo, AMARELO_DADO, (int(d.x) - 6, int(d.y) - 6, 12, 12), border_radius=2)

        if self.portal_aberto:
            centro_saida = (int(self.portal_pos.x), int(self.portal_pos.y))
            raio_saida = 22 + abs(math.sin(time.time() * 5)) * 4

            desenhar_brilho_neon(surf_jogo, VERDE_NEON, centro_saida[0], centro_saida[1], raio_saida + 2, 4)
            pygame.draw.circle(surf_jogo, (*VERDE_NEON, 200), centro_saida, int(raio_saida + 3))
            pygame.draw.circle(surf_jogo, PRETO_FUNDO, centro_saida, int(raio_saida - 5))
            pygame.draw.circle(surf_jogo, VERDE_NEON, centro_saida, int(raio_saida), 3)

            ang_ini_saida = (time.time() * 5) % (math.pi * 2)
            ang_fim_saida = ang_ini_saida + (math.pi * 1.25)
            rect_saida = pygame.Rect(0, 0, int(raio_saida * 2), int(raio_saida * 2))
            rect_saida.center = centro_saida
            pygame.draw.arc(surf_jogo, BRANCO, rect_saida, ang_ini_saida, ang_fim_saida, 4)

            orb_x = centro_saida[0] + math.cos(ang_ini_saida) * raio_saida
            orb_y = centro_saida[1] + math.sin(ang_ini_saida) * raio_saida
            pygame.draw.circle(surf_jogo, BRANCO, (int(orb_x), int(orb_y)), 4)

        for p in self.particulas:
            p.draw(surf_jogo)
        for ini in self.inimigos:
            ini.draw(surf_jogo)
<<<<<<< HEAD
        for b in self.buracos_negros:
            b.draw(surf_jogo)
=======
        for proj in self.projeteis_inimigos:
            cor_proj = proj.get("cor", LARANJA_NEON)
            raio = int(proj.get("raio", 4))
            desenhar_brilho_neon(surf_jogo, cor_proj, proj["pos"].x, proj["pos"].y, raio + 2, 2)
            pygame.draw.circle(surf_jogo, cor_proj, (int(proj["pos"].x), int(proj["pos"].y)), raio)
            pygame.draw.circle(surf_jogo, BRANCO, (int(proj["pos"].x), int(proj["pos"].y)), max(1, raio // 2))
>>>>>>> 7ff9806 (varias coisas)
        self.player.draw(surf_jogo)

        self.tela.blit(surf_jogo, (offset_x, offset_y))

        if self.modo_jogo == "CORRIDA":
            atual = self.tempo_corrida
            chave_modo = "Corrida"
            melhor = self.ranking.get(chave_modo, [{}])[0].get("tempo", atual) if self.ranking.get(chave_modo) else atual
            texto_atual = f"{atual:.1f}s/"
            texto_melhor = f"{melhor:.1f}s"
        elif self.modo_jogo == "SOBREVIVENCIA":
            atual = self.tempo_sobrevivencia
            chave_modo = "Sobrevivencia"
            melhor = self.ranking.get(chave_modo, [{}])[0].get("tempo", atual) if self.ranking.get(chave_modo) else atual
            texto_atual = f"{atual:.1f}s/"
            texto_melhor = f"{melhor:.1f}s"
        elif self.modo_jogo == "HARDCORE":
            atual = self.tempo_sobrevivencia
            chave_modo = "Hardcore"
            melhor = self.ranking.get(chave_modo, [{}])[0].get("tempo", atual) if self.ranking.get(chave_modo) else atual
            texto_atual = f"{atual:.1f}s/"
            texto_melhor = f"{melhor:.1f}s"
        else:
            atual = int(self.fase_atual)
            chave_modo = "Corrida_Infinita"
            melhor = self.ranking.get(chave_modo, [{}])[0].get("fase", atual) if self.ranking.get(chave_modo) else atual
            texto_atual = f"{atual}/"
            texto_melhor = f"{melhor}"

        surf_melhor = self.fonte_sub.render(texto_melhor, True, BRANCO)
        surf_atual = self.fonte_sub.render(texto_atual, True, VERDE_NEON)
        y_hud = 18
        margem_direita = 20

        rect_melhor = surf_melhor.get_rect()
        rect_melhor.top = y_hud
        rect_melhor.right = LARGURA_TELA - margem_direita
        self.tela.blit(surf_melhor, rect_melhor)

        rect_atual = surf_atual.get_rect()
        rect_atual.top = y_hud
        rect_atual.right = rect_melhor.left
        self.tela.blit(surf_atual, rect_atual)

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
