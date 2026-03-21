import sys
import time

import pygame

from .config import FPS


def acionar_botao(self):
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
            self.estado = "TELA_INIMIGOS"
            self.botao_selecionado = 0
        elif self.botao_selecionado == 1:
            self.entrar_menu_modo()
            self.botao_selecionado = 0

    elif self.estado == "MENU_MODO":
        if self.botao_selecionado == 0:
            self.modo_jogo = "CORRIDA"
        elif self.botao_selecionado == 1:
            self.modo_jogo = "CORRIDA_HARDCORE"
        elif self.botao_selecionado == 2:
            self.modo_jogo = "SOBREVIVENCIA"
        elif self.botao_selecionado == 3:
            self.modo_jogo = "HARDCORE"
        elif self.botao_selecionado == 5:
            self.modo_jogo = "CORRIDA_INFINITA"
        elif self.botao_selecionado == 4:
            self.estado = "TELA_INFO_MODOS"
            self.botao_selecionado = 0
            return

        self.estado = "TELA_HOTKEYS"
        self.botao_selecionado = 0

    elif self.estado == "TELA_INFO_MODOS" and self.botao_selecionado == 0:
        self.entrar_menu_modo()

    elif self.estado == "TELA_HOTKEYS" and self.botao_selecionado == 0:
        self.estado = "TELA_INIMIGOS"
        self.botao_selecionado = 0

    elif self.estado == "TELA_INIMIGOS" and self.botao_selecionado == 0:
        self.fase_atual = 1
        self.iniciar_fase()

    elif self.estado == "PAUSA":
        if self.botao_selecionado == 0:
            self.estado = "JOGANDO"
        elif self.botao_selecionado == 1:
            self.entrar_menu_modo()

    elif self.estado == "RANKING":
        if self.botao_selecionado == 0:
            self.fase_atual = 1
            self.iniciar_fase()
        elif self.botao_selecionado == 1:
            self.entrar_menu_modo()
            self.botao_selecionado = 0
        elif self.botao_selecionado == 2:
            self.estado = "INPUT_NOME"
            self.nome_jogador = ""
            self.veio_do_game_over = True
            self.botao_selecionado = 0


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
                if event.key in [pygame.K_MINUS, pygame.K_KP_MINUS]:
                    self.alterar_volume(-0.1)
                elif event.key in [pygame.K_PLUS, pygame.K_KP_PLUS, pygame.K_EQUALS]:
                    self.alterar_volume(0.1)
                elif event.key == pygame.K_ESCAPE:
                    if self.estado == "MENU_MODO":
                        self.estado = "INPUT_NOME"
                        self.botao_selecionado = 0
                    elif self.estado == "TELA_INFO_MODOS":
                        self.entrar_menu_modo()
                    elif self.estado == "TELA_HOTKEYS":
                        self.entrar_menu_modo()
                    elif self.estado == "TELA_INIMIGOS":
                        self.estado = "TELA_HOTKEYS"
                        self.botao_selecionado = 0
                    elif self.estado == "PERGUNTA_MODO":
                        self.estado = "INPUT_NOME"
                        self.botao_selecionado = 0
                    elif self.estado == "JOGANDO":
                        self.estado = "PAUSA"
                        self.botao_selecionado = 0
                    elif self.estado == "PAUSA":
                        self.estado = "JOGANDO"
                elif event.key == pygame.K_RETURN:
                    if self.estado == "MENU_MODO":
                        if self.botao_selecionado != -1:
                            self.acionar_botao()
                    else:
                        self.acionar_botao()
                elif event.key == pygame.K_SPACE and self.estado == "MENU_MODO":
                    if self.botao_selecionado != -1:
                        self.acionar_botao()

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = self.obter_posicao_mouse()

                if self.estado not in ["JOGANDO", "PAUSA"]:
                    if self.rect_vol_mute.collidepoint(mx, my):
                        self.alternar_mute()
                        continue
                    elif self.rect_vol_menos.collidepoint(mx, my):
                        self.alterar_volume(-0.1)
                        continue
                    elif self.rect_vol_mais.collidepoint(mx, my):
                        self.alterar_volume(0.1)
                        continue

                if self.estado != "MENU_MODO":
                    for i, rect in enumerate(self.botoes_hitboxes):
                        if rect.collidepoint(mx, my):
                            self.botao_selecionado = i
                            self.acionar_botao()

            if event.type == pygame.KEYDOWN:
                num_botoes = len(self.botoes_hitboxes)

                if num_botoes > 0 and self.estado != "MENU_MODO" and self.botao_selecionado < 0:
                    self.botao_selecionado = 0

                if self.estado == "INPUT_NOME":
                    if event.key == pygame.K_BACKSPACE:
                        self.nome_jogador = self.nome_jogador[:-1]
                    elif event.key != pygame.K_RETURN and len(self.nome_jogador) < 12 and event.unicode.isprintable():
                        self.nome_jogador += event.unicode

                if num_botoes > 0 and self.estado != "MENU_MODO":
                    if event.key in [pygame.K_UP, pygame.K_w, pygame.K_LEFT, pygame.K_a]:
                        self.botao_selecionado = (self.botao_selecionado - 1) % num_botoes
                    elif event.key in [pygame.K_DOWN, pygame.K_s, pygame.K_RIGHT, pygame.K_d]:
                        self.botao_selecionado = (self.botao_selecionado + 1) % num_botoes

                if self.estado in ["TELA_INFO_MODOS", "TELA_HOTKEYS", "TELA_INIMIGOS"] and event.key == pygame.K_SPACE:
                    self.acionar_botao()

        if self.estado == "JOGANDO":
            self.atualizar_jogo()
        elif self.estado == "MENU_MODO":
            self.atualizar_menu_interativo()
        self.desenhar()
