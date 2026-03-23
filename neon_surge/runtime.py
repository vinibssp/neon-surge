import sys
import time

import pygame

from .constants import FPS
from .data import INIMIGOS_DATA


def acionar_botao(self):
    self.sounds.play('menu_accept')
    if self.estado == "INPUT_NOME" and self.botao_selecionado == 0:
        if len(self.nome_jogador) > 0:
            if getattr(self, "veio_do_game_over", False) and self.modo_jogo != "":
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
                self.guia_aba = "COMUNS"
                self.botao_selecionado = 0
            else:
                self.iniciar_fase()
                self.estado = "JOGANDO"
        elif self.botao_selecionado == 1:
            self.entrar_menu_modo()
            self.botao_selecionado = 0

    elif self.estado == "MENU_MODO":
        if self.botao_selecionado == "IR_RANKING":
            self.entrar_ranking()
            return
            
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
            self.botao_selecionado = 2 
            return
        elif self.botao_selecionado == "SAIR_JOGO":
            pygame.quit()
            sys.exit()

        if self.modo_jogo == "TREINO":
            self.estado = "TELA_INIMIGOS"
            self.guia_aba = "COMUNS"
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

    elif self.estado == "TELA_INIMIGOS":
        if isinstance(self.botao_selecionado, int) and self.botao_selecionado < 4:
            categorias = ["COMUNS", "MINIBOSSES", "BOSSES", "GUIA"]
            self.guia_aba = categorias[self.botao_selecionado]
            if self.guia_aba != "GUIA":
                self.botao_selecionado = 4 
        elif self.botao_selecionado == 99:
            if self.modo_jogo == "TREINO":
                tem_selecao = any(v > 0 for v in self.inimigos_treino_selecionados.values())
                if not tem_selecao:
                    self.inimigos_treino_selecionados["quique"] = 1
                self.fase_atual = 1
                self.iniciar_fase()
                self.estado = "JOGANDO"
            else:
                self.entrar_menu_modo()

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
        if isinstance(self.botao_selecionado, str) and self.botao_selecionado.startswith("ABA_RANK_"):
            nova_aba = self.botao_selecionado.replace("ABA_RANK_", "")
            self.trocar_aba_ranking(nova_aba)
        elif self.botao_selecionado == 0:
            if getattr(self, "veio_de_fim_partida", False):
                self.iniciar_fase()
                self.estado = "JOGANDO"
            else:
                self.entrar_menu_modo()
                self.botao_selecionado = 0
        elif self.botao_selecionado == 1:
            if getattr(self, "veio_de_fim_partida", False):
                self.entrar_menu_modo()
                self.botao_selecionado = 0
        elif self.botao_selecionado == 2:
            if getattr(self, "veio_de_fim_partida", False):
                self.sounds.play_bgm("neon_surge/assets/sounds/trilha_menu.wav", self.volume_musica)
                self.estado = "INPUT_NOME"
                self.nome_jogador = ""
                self.veio_do_game_over = True
                self.mortes_total_jogador = 0
                self.botao_selecionado = 0

    elif self.estado == "CONFIGURACOES":
        if self.botao_selecionado == 3:
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
        mx, my = self.obter_posicao_mouse()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if self.estado != "JOGANDO":
                for btn in self.botoes_menu:
                    if btn.handle_event(event):
                        break

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F11:
                    self.alternar_tela_cheia()
                
                if event.key in [pygame.K_q, pygame.K_e]:
                    direcao = -1 if event.key == pygame.K_q else 1
                    if self.estado == "TELA_INFO_MODOS":
                        abas = ["MODOS", "HOTKEYS"]
                        idx = (abas.index(self.guia_aba) + direcao) % len(abas)
                        self.guia_aba = abas[idx]
                        self.botao_selecionado = idx
                        self.sounds.play('menu_button')
                        continue
                    elif self.estado == "TELA_INIMIGOS":
                        cats = ["COMUNS", "MINIBOSSES", "BOSSES", "GUIA"]
                        idx = (cats.index(self.guia_aba) + direcao) % len(cats)
                        self.guia_aba = cats[idx]
                        self.botao_selecionado = idx
                        self.sounds.play('menu_button')
                        continue
                    elif self.estado == "RANKING" and not getattr(self, "veio_de_fim_partida", False):
                        modos_rank = ["CORRIDA", "SOBREVIVENCIA", "HARDCORE", "LABIRINTO", "CORRIDA_INFINITA"]    
                        idx = (modos_rank.index(self.ranking_aba) + direcao) % len(modos_rank)
                        self.trocar_aba_ranking(modos_rank[idx])
                        self.botao_selecionado = f"ABA_RANK_{modos_rank[idx]}"
                        continue

                if event.key == pygame.K_ESCAPE:
                    self.sounds.play('menu_reject')
                    if self.estado == "MENU_MODO":
                        self.estado = "INPUT_NOME"
                        self.botao_selecionado = 0
                    elif self.estado in ["TELA_INFO_MODOS", "TELA_INIMIGOS", "PERGUNTA_MODO"]:
                        self.entrar_menu_modo()
                    elif self.estado == "CONFIGURACOES":
                        self.voltar_configuracoes()
                    elif self.estado == "JOGANDO":
                        self.estado = "PAUSA"
                        self.botao_selecionado = 0
                    elif self.estado == "PAUSA":
                        self.estado = "JOGANDO"

                elif event.key in [pygame.K_RETURN, pygame.K_SPACE]:
                    callback_executado = False
                    for btn in self.botoes_menu:
                        if btn.is_selected and btn.callback:
                            btn.callback()
                            callback_executado = True
                            break
                    if not callback_executado:
                        self.acionar_botao()

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
                
                elif self.estado == "MENU_MODO":
                    if event.key == pygame.K_r: 
                        self.entrar_ranking()
                        continue
                    
                    ids_menu = [item["id"] for item in self.obter_pads_menu()]
                    if self.botao_selecionado not in ids_menu and self.botao_selecionado not in ["IR_RANKING", "SAIR_JOGO"]:
                         self.botao_selecionado = ids_menu[0]
                    
                    cols = 4
                    if self.botao_selecionado == "IR_RANKING":
                        if event.key in [pygame.K_DOWN, pygame.K_s]:
                            self.botao_selecionado = ids_menu[0]
                            self.sounds.play('menu_button')
                        elif event.key in [pygame.K_LEFT, pygame.K_a]:
                            self.botao_selecionado = ids_menu[3] # Canto superior direito do grid
                            self.sounds.play('menu_button')
                    elif self.botao_selecionado == "SAIR_JOGO":
                        if event.key in [pygame.K_UP, pygame.K_w]:
                            self.botao_selecionado = ids_menu[4] # Canto inferior esquerdo do grid
                            self.sounds.play('menu_button')
                        elif event.key in [pygame.K_RIGHT, pygame.K_d]:
                            self.botao_selecionado = ids_menu[4]
                            self.sounds.play('menu_button')
                    elif self.botao_selecionado in ids_menu:
                        idx_atual = ids_menu.index(self.botao_selecionado)
                        if event.key in [pygame.K_LEFT, pygame.K_a]:
                            if idx_atual % cols == 0: # Borda esquerda
                                if idx_atual == 4: # Se estiver no LABIRINTO (2,1), vai para SAIR
                                    self.botao_selecionado = "SAIR_JOGO"
                                else:
                                    self.botao_selecionado = ids_menu[idx_atual + cols - 1] # Wrap na linha
                            else:
                                self.botao_selecionado = ids_menu[idx_atual - 1]
                            self.sounds.play('menu_button')
                        elif event.key in [pygame.K_RIGHT, pygame.K_d]:
                            if idx_atual % cols == cols - 1: # Borda direita
                                if idx_atual == 3: # Se estiver no HARDCORE (1,4), vai para RANKING
                                    self.botao_selecionado = "IR_RANKING"
                                else:
                                    self.botao_selecionado = ids_menu[idx_atual - cols + 1] # Wrap na linha
                            else:
                                self.botao_selecionado = ids_menu[idx_atual + 1]
                            self.sounds.play('menu_button')
                        elif event.key in [pygame.K_UP, pygame.K_w]:
                            if idx_atual >= cols: 
                                self.botao_selecionado = ids_menu[idx_atual - cols]
                            else:
                                self.botao_selecionado = "IR_RANKING"
                            self.sounds.play('menu_button')
                        elif event.key in [pygame.K_DOWN, pygame.K_s]:
                            if idx_atual < len(ids_menu) - cols:
                                self.botao_selecionado = ids_menu[idx_atual + cols]
                            else:
                                self.botao_selecionado = "SAIR_JOGO"
                            self.sounds.play('menu_button')

                elif self.estado == "TELA_INIMIGOS":
                    # Ajuste de Quantidade (A/D) - Somente se um inimigo estiver selecionado
                    if event.key in [pygame.K_a, pygame.K_d]:
                        if isinstance(self.botao_selecionado, int) and self.botao_selecionado >= 4:
                            items = [t for t in INIMIGOS_DATA.items() if t[1]["categoria"] == self.guia_aba]
                            idx_inim = self.botao_selecionado - 4
                            if 0 <= idx_inim < len(items):
                                tid = items[idx_inim][0]
                                delta = -1 if event.key == pygame.K_a else 1
                                self.inimigos_treino_selecionados[tid] = max(0, min(10, self.inimigos_treino_selecionados.get(tid, 0) + delta))
                                self.sounds.play('menu_button')
                                continue # Impede que A/D naveguem

                    ids_disponiveis = []
                    for btn in self.botoes_menu:
                        if isinstance(btn.id, int) and btn.id not in ids_disponiveis:
                            ids_disponiveis.append(btn.id)
                    ids_disponiveis.sort()

                    if ids_disponiveis:
                        if not isinstance(self.botao_selecionado, int):
                            self.botao_selecionado = ids_disponiveis[0]
                        
                        if event.key in [pygame.K_UP, pygame.K_w]:
                            self.sounds.play('menu_button')
                            idx_atual = ids_disponiveis.index(self.botao_selecionado) if self.botao_selecionado in ids_disponiveis else 0
                            self.botao_selecionado = ids_disponiveis[(idx_atual - 1) % len(ids_disponiveis)]
                        elif event.key in [pygame.K_DOWN, pygame.K_s]:
                            self.sounds.play('menu_button')
                            idx_atual = ids_disponiveis.index(self.botao_selecionado) if self.botao_selecionado in ids_disponiveis else 0
                            self.botao_selecionado = ids_disponiveis[(idx_atual + 1) % len(ids_disponiveis)]

                elif self.estado in ["PAUSA", "RANKING"]:
                    ids_disponiveis = []
                    for btn in self.botoes_menu:
                        if isinstance(btn.id, int) and btn.id not in ids_disponiveis:
                            ids_disponiveis.append(btn.id)
                    ids_disponiveis.sort()
                    if ids_disponiveis:
                        if not isinstance(self.botao_selecionado, int):
                            self.botao_selecionado = ids_disponiveis[0]
                        if event.key in [pygame.K_UP, pygame.K_w, pygame.K_LEFT, pygame.K_a]:
                            self.sounds.play('menu_button')
                            idx_atual = ids_disponiveis.index(self.botao_selecionado) if self.botao_selecionado in ids_disponiveis else 0
                            self.botao_selecionado = ids_disponiveis[(idx_atual - 1) % len(ids_disponiveis)]
                        elif event.key in [pygame.K_DOWN, pygame.K_s, pygame.K_RIGHT, pygame.K_d]:
                            self.sounds.play('menu_button')
                            idx_atual = ids_disponiveis.index(self.botao_selecionado) if self.botao_selecionado in ids_disponiveis else 0
                            self.botao_selecionado = ids_disponiveis[(idx_atual + 1) % len(ids_disponiveis)]

                if self.estado == "INPUT_NOME":
                    if event.key == pygame.K_BACKSPACE:
                        self.nome_jogador = self.nome_jogador[:-1]
                    elif event.key not in [pygame.K_RETURN, pygame.K_SPACE] and len(self.nome_jogador) < 12 and event.unicode.isprintable():
                        self.nome_jogador += event.unicode

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 4: self.alterar_volume(0.05)
                elif event.button == 5: self.alterar_volume(-0.05)

        if self.estado == "JOGANDO":
            self.atualizar_jogo()
        elif self.estado == "MENU_MODO":
            self.atualizar_menu_interativo()
        self.desenhar()
