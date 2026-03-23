import sys
import time

import pygame

from .constants import FPS


def acionar_botao(self):
    self.sounds.play('menu_accept')
    if self.estado == "INPUT_NOME" and self.botao_selecionado == 0:
        if len(self.nome_jogador) > 0:
            if self.veio_do_game_over and self.modo_jogo != "":
                self.estado = "PERGUNTA_MODO"
                self.botao_selecionado = 0
            else:
                self.entrar_menu_modo()
                self.botao_selecionado = 0

    elif self.estado == "PERGUNTA_MODO":
        self.veio_do_game_over = False
        if self.botao_selecionado == 0:
            if self.modo_jogo == "TREINO":
                self.estado = "TELA_INIMIGOS"
                self.botao_selecionado = 0
            else:
                self.iniciar_fase()
                self.estado = "JOGANDO"
        elif self.botao_selecionado == 1:
            self.entrar_menu_modo()
            self.botao_selecionado = 0

    elif self.estado == "MENU_MODO":
        if self.botao_selecionado == 0:
            self.modo_jogo = "CORRIDA"
        elif self.botao_selecionado == 1:
            self.modo_jogo = "TREINO"
        elif self.botao_selecionado == 2:
            self.modo_jogo = "SOBREVIVENCIA"
        elif self.botao_selecionado == 3:
            self.modo_jogo = "HARDCORE"
        elif self.botao_selecionado == 5:
            self.modo_jogo = "CORRIDA_INFINITA"
        elif self.botao_selecionado == 6:
            self.modo_jogo = "LABIRINTO"
        elif self.botao_selecionado == 4:
            self.estado = "TELA_INFO_MODOS"
            self.guia_aba = "MODOS"
            self.botao_selecionado = 0
            return
        elif self.botao_selecionado == 99:
            self.estado_anterior_config = "MENU_MODO"
            self.estado = "CONFIGURACOES"
            self.botao_selecionado = 2 # Foca na resolução por padrão quando vem do menu
            return

        if self.modo_jogo == "TREINO":
            self.estado = "TELA_INIMIGOS"
            self.botao_selecionado = 0
        else:
            self.fase_atual = 1
            self.iniciar_fase()
            self.estado = "JOGANDO"

    elif self.estado == "TELA_INFO_MODOS":
        if self.botao_selecionado == 0:
            self.guia_aba = "MODOS"
        elif self.botao_selecionado == 1:
            self.guia_aba = "HOTKEYS"
        elif self.botao_selecionado == 2:
            self.entrar_menu_modo()

    elif self.estado == "TELA_HOTKEYS":
        self.estado = "TELA_INFO_MODOS"
        self.guia_aba = "HOTKEYS"
        self.botao_selecionado = 1


    elif self.estado == "TELA_INIMIGOS":
        if self.botao_selecionado < 3:
            # Trocar de Aba
            categorias = ["COMUNS", "MINIBOSSES", "BOSSES"]
            self.guia_aba = categorias[self.botao_selecionado]
            self.botao_selecionado = 3 # Foca no primeiro inimigo da aba
        elif self.botao_selecionado == len(self.botoes_hitboxes) - 1:
            # Botão Iniciar / Voltar
            if self.modo_jogo == "TREINO":
                # No modo treino, se não escolheu nada, coloca um quique por padrão
                tem_selecao = any(v > 0 for v in self.inimigos_treino_selecionados.values())
                if not tem_selecao:
                    self.inimigos_treino_selecionados["quique"] = 1
                self.fase_atual = 1
                self.iniciar_fase()
            else:
                self.entrar_menu_modo()
        else:
            # Seleção de inimigo (Apenas visual ou incremento no treino)
            if self.modo_jogo == "TREINO":
                aba_atual = getattr(self, "guia_aba", "COMUNS")
                from .data import INIMIGOS_DATA
                inimigos_aba = [tid for tid, data in INIMIGOS_DATA.items() if data["categoria"] == aba_atual]
                sel_idx = self.botao_selecionado - 3
                if 0 <= sel_idx < len(inimigos_aba):
                    tid = inimigos_aba[sel_idx]
                    self.inimigos_treino_selecionados[tid] = self.inimigos_treino_selecionados.get(tid, 0) + 1
                    if self.inimigos_treino_selecionados[tid] > 10:
                        self.inimigos_treino_selecionados[tid] = 0
                    self.sounds.play('menu_button')

    elif self.estado == "PAUSA":
        if self.botao_selecionado == 0:
            self.estado = "JOGANDO"
        elif self.botao_selecionado == 1:
            self.estado_anterior_config = "PAUSA"
            self.estado = "CONFIGURACOES"
            self.botao_selecionado = -1
        elif self.modo_jogo == "CORRIDA" and self.botao_selecionado == 2:
            self.fase_atual = 1
            self.tempo_corrida = 0.0
            self.iniciar_fase()
        elif (self.modo_jogo == "CORRIDA" and self.botao_selecionado == 3) or (
            self.modo_jogo != "CORRIDA" and self.botao_selecionado == 2
        ):
            self.entrar_menu_modo()

    elif self.estado == "RANKING":
        if self.botao_selecionado == 0:
            self.fase_atual = 1
            self.iniciar_fase()
        elif self.botao_selecionado == 1:
            self.entrar_menu_modo()
            self.botao_selecionado = 0
        elif self.botao_selecionado == 2:
            self.sounds.play_bgm("neon_surge/assets/sounds/trilha_menu.wav", self.volume_musica)
            self.estado = "INPUT_NOME"
            self.nome_jogador = ""
            self.veio_do_game_over = True
            self.mortes_total_jogador = 0
            self.botao_selecionado = 0


    elif self.estado == "CONFIGURACOES":
        if self.botao_selecionado == 2: # Botão Voltar
            self.voltar_configuracoes()

def voltar_configuracoes(self):
    origem = getattr(self, "estado_anterior_config", "MENU_MODO")
    if origem == "PAUSA":
        self.estado = "PAUSA"
        self.botao_selecionado = 1
    else:
        self.entrar_menu_modo()
    self.estado_anterior_config = "MENU_MODO"

def executar(self):
    while True:
        self.tempo_global = time.time()
        self.dt = self.clock.tick(FPS) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN and event.key == pygame.K_F11:
                self.alternar_tela_cheia()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.sounds.play('menu_reject')
                    if self.estado == "MENU_MODO":
                        self.estado = "INPUT_NOME"
                        self.botao_selecionado = 0
                    elif self.estado in ["TELA_INFO_MODOS", "TELA_INIMIGOS", "PERGUNTA_MODO"]:
                        self.entrar_menu_modo()
                    elif self.estado == "CONFIGURACOES":
                        self.voltar_configuracoes()
                    elif self.estado == "TELA_HOTKEYS":
                        self.estado = "TELA_INFO_MODOS"
                        self.guia_aba = "HOTKEYS"
                        self.botao_selecionado = 1
                    elif self.estado == "JOGANDO":
                        self.estado = "PAUSA"
                        self.botao_selecionado = 0
                    elif self.estado == "PAUSA":
                        self.estado = "JOGANDO"
                elif event.key in [pygame.K_RETURN, pygame.K_SPACE]:
                    estados_menu_interacao = [
                        "INPUT_NOME",
                        "PERGUNTA_MODO",
                        "MENU_MODO",
                        "TELA_INFO_MODOS",
                        "TELA_HOTKEYS",
                        "TELA_INIMIGOS",
                        "PAUSA",
                        "RANKING",
                        "CONFIGURACOES",
                    ]
                    if self.estado in estados_menu_interacao:
                        if self.estado == "MENU_MODO":
                            if self.botao_selecionado != -1:
                                self.acionar_botao()
                        else:
                            self.acionar_botao()

                # Lógica de setas/WASD para estados específicos
                if self.estado == "CONFIGURACOES":
                    if event.key in [pygame.K_LEFT, pygame.K_a]:
                        if self.botao_selecionado == 0: self.alterar_volume_musica(-0.1)
                        elif self.botao_selecionado == 1: self.alterar_volume_sfx(-0.1)
                        elif self.botao_selecionado == 2: self.alterar_resolucao(-1)
                    elif event.key in [pygame.K_RIGHT, pygame.K_d]:
                        if self.botao_selecionado == 0: self.alterar_volume_musica(0.1)
                        elif self.botao_selecionado == 1: self.alterar_volume_sfx(0.1)
                        elif self.botao_selecionado == 2: self.alterar_resolucao(1)
                    elif event.key in [pygame.K_UP, pygame.K_w]:
                        self.sounds.play('menu_button')
                        self.botao_selecionado = (self.botao_selecionado - 1) % 4
                    elif event.key in [pygame.K_DOWN, pygame.K_s]:
                        self.sounds.play('menu_button')
                        self.botao_selecionado = (self.botao_selecionado + 1) % 4
                
                elif self.estado == "TELA_INFO_MODOS":
                    if event.key in [pygame.K_LEFT, pygame.K_a]:
                        self.sounds.play('menu_button')
                        self.botao_selecionado = 0
                        self.guia_aba = "MODOS"
                    elif event.key in [pygame.K_RIGHT, pygame.K_d]:
                        self.sounds.play('menu_button')
                        self.botao_selecionado = 1
                        self.guia_aba = "HOTKEYS"
                    elif event.key in [pygame.K_DOWN, pygame.K_s]:
                        self.sounds.play('menu_button')
                        self.botao_selecionado = 2
                    elif event.key in [pygame.K_UP, pygame.K_w]:
                        self.sounds.play('menu_button')
                        self.botao_selecionado = 0 # Foca na aba
                    elif event.key == pygame.K_TAB:
                        self.sounds.play('menu_button')
                        self.guia_aba = "HOTKEYS" if self.guia_aba == "MODOS" else "MODOS"
                        self.botao_selecionado = 1 if self.guia_aba == "HOTKEYS" else 0

                elif self.estado == "TELA_INIMIGOS":
                    if event.key == pygame.K_TAB:
                        self.sounds.play('menu_button')
                        categorias = ["COMUNS", "MINIBOSSES", "BOSSES"]
                        idx = (categorias.index(getattr(self, "guia_aba", "COMUNS")) + 1) % 3
                        self.guia_aba = categorias[idx]
                        self.botao_selecionado = idx
                    elif self.modo_jogo == "TREINO" and self.botao_selecionado >= 3:
                        aba_atual = getattr(self, "guia_aba", "COMUNS")
                        from .data import INIMIGOS_DATA
                        inimigos_aba = [tid for tid, data in INIMIGOS_DATA.items() if data["categoria"] == aba_atual]
                        sel_idx = self.botao_selecionado - 3
                        if 0 <= sel_idx < len(inimigos_aba):
                            tid = inimigos_aba[sel_idx]
                            if event.key in [pygame.K_LEFT, pygame.K_a]:
                                self.inimigos_treino_selecionados[tid] = max(0, self.inimigos_treino_selecionados.get(tid, 0) - 1)
                                self.sounds.play('menu_button')
                            elif event.key in [pygame.K_RIGHT, pygame.K_d]:
                                self.inimigos_treino_selecionados[tid] = min(10, self.inimigos_treino_selecionados.get(tid, 0) + 1)
                                self.sounds.play('menu_button')

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = self.obter_posicao_mouse()

                if self.estado not in ["JOGANDO", "PAUSA", "CONFIGURACOES"]:
                    if self.rect_vol_mute.collidepoint(mx, my):
                        self.sounds.play('menu_accept')
                        self.alternar_mute()
                        continue
                    elif self.rect_vol_config.collidepoint(mx, my):
                        self.sounds.play('menu_accept')
                        self.estado_anterior_config = "MENU_MODO"
                        self.estado = "CONFIGURACOES"
                        self.botao_selecionado = 0
                        continue
                    elif self.rect_vol_menos.collidepoint(mx, my):
                        self.sounds.play('menu_accept')
                        self.alterar_volume(-0.1)
                        continue
                    elif self.rect_vol_mais.collidepoint(mx, my):
                        self.sounds.play('menu_accept')
                        self.alterar_volume(0.1)
                        continue

                if self.estado != "JOGANDO":
                    # Mapeamento especial para cliques no menu de áudio/sistema
                    if self.estado == "CONFIGURACOES":
                        # Botoes_hitboxes em CONFIG: [mus_-, mus_+, sfx_-, sfx_+, res_-, res_+, voltar]
                        if len(self.botoes_hitboxes) >= 7:
                            if self.botoes_hitboxes[0].collidepoint(mx, my): self.alterar_volume_musica(-0.1)
                            elif self.botoes_hitboxes[1].collidepoint(mx, my): self.alterar_volume_musica(0.1)
                            elif self.botoes_hitboxes[2].collidepoint(mx, my): self.alterar_volume_sfx(-0.1)
                            elif self.botoes_hitboxes[3].collidepoint(mx, my): self.alterar_volume_sfx(0.1)
                            elif self.botoes_hitboxes[4].collidepoint(mx, my): self.alterar_resolucao(-1)
                            elif self.botoes_hitboxes[5].collidepoint(mx, my): self.alterar_resolucao(1)
                            elif self.botoes_hitboxes[6].collidepoint(mx, my):
                                self.botao_selecionado = 3 # Botão Confirmar
                                self.acionar_botao()
                        continue

                    for i, rect in enumerate(self.botoes_hitboxes):
                        if rect.collidepoint(mx, my):
                            self.botao_selecionado = i
                            self.acionar_botao()


            if event.type == pygame.KEYDOWN:
                num_botoes = len(self.botoes_hitboxes)

                # Evita sobrescrever a lógica customizada acima para CONFIG e INFO
                if self.estado in ["CONFIGURACOES", "TELA_INFO_MODOS"]:
                    continue

                if num_botoes > 0 and self.estado != "MENU_MODO" and self.botao_selecionado < 0:
                    self.botao_selecionado = 0

                if self.estado == "INPUT_NOME":
                    if event.key == pygame.K_BACKSPACE:
                        self.nome_jogador = self.nome_jogador[:-1]
                    elif event.key not in [pygame.K_RETURN, pygame.K_SPACE] and len(self.nome_jogador) < 12 and event.unicode.isprintable():
                        self.nome_jogador += event.unicode

                if self.estado == "MENU_MODO":
                    ids_menu = [item["id"] for item in self.obter_pads_menu()]
                    if self.botao_selecionado not in ids_menu:
                        self.botao_selecionado = ids_menu[0]

                    indice_atual = ids_menu.index(self.botao_selecionado)
                    cols_menu = 4
                    linha_atual = indice_atual // cols_menu
                    col_atual = indice_atual % cols_menu
                    total_linhas = (len(ids_menu) + cols_menu - 1) // cols_menu

                    if event.key in [pygame.K_LEFT, pygame.K_a]:
                        self.sounds.play('menu_button')
                        novo_indice = (indice_atual - 1) % len(ids_menu)
                        self.botao_selecionado = ids_menu[novo_indice]
                    elif event.key in [pygame.K_RIGHT, pygame.K_d]:
                        self.sounds.play('menu_button')
                        novo_indice = (indice_atual + 1) % len(ids_menu)
                        self.botao_selecionado = ids_menu[novo_indice]
                    elif event.key in [pygame.K_UP, pygame.K_w]:
                        self.sounds.play('menu_button')
                        if linha_atual > 0:
                            novo_indice = (linha_atual - 1) * cols_menu + col_atual
                            if novo_indice < len(ids_menu):
                                self.botao_selecionado = ids_menu[novo_indice]
                    elif event.key in [pygame.K_DOWN, pygame.K_s]:
                        self.sounds.play('menu_button')
                        if linha_atual < total_linhas - 1:
                            novo_indice = (linha_atual + 1) * cols_menu + col_atual
                            if novo_indice < len(ids_menu):
                                self.botao_selecionado = ids_menu[novo_indice]

                if num_botoes > 0 and self.estado != "MENU_MODO":
                    if event.key in [pygame.K_UP, pygame.K_w, pygame.K_LEFT, pygame.K_a]:
                        self.sounds.play('menu_button')
                        self.botao_selecionado = (self.botao_selecionado - 1) % num_botoes
                    elif event.key in [pygame.K_DOWN, pygame.K_s, pygame.K_RIGHT, pygame.K_d]:
                        self.sounds.play('menu_button')
                        self.botao_selecionado = (self.botao_selecionado + 1) % num_botoes


        if self.estado == "JOGANDO":
            self.atualizar_jogo()
        elif self.estado == "MENU_MODO":
            self.atualizar_menu_interativo()
        self.desenhar()
