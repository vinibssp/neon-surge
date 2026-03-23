import math
import random
import time
import pygame

from .constants import (
    ALTURA_TELA, AMARELO_DADO, AZUL_ESCURO, BRANCO, CIANO_NEON, 
    CINZA_CLARO, CINZA_ESCURO, LARGURA_TELA, LARANJA_NEON, 
    PRETO_FUNDO, ROSA_NEON, ROXO_NEON, VERDE_NEON, VERMELHO_SANGUE
)
from .entities import Particula
from .hud.ui import (
    criar_painel_transparente, desenhar_botao_dinamico, desenhar_brilho_neon,
    desenhar_fundo_cyberpunk, desenhar_grade_jogo, desenhar_icone_som, 
    desenhar_icone_engrenagem, desenhar_texto, desenhar_moldura, Button
)
from .data import INIMIGOS_DATA

class Renderer:
    """Namespace para funções de renderização organizada."""
    
    @staticmethod
    def desenhar(self):
        """Método principal delegado do NeonSurge."""
        mx, my = self.obter_posicao_mouse()
        self.botoes_hitboxes = []
        self.botoes_menu = [] # Reinicia a cada frame para reconstrução dinâmica
        
        # Fundo base para menus
        if self.estado not in ["JOGANDO", "PAUSA"]:
            desenhar_fundo_cyberpunk(self.tela, self.tempo_global)
            for p in self.particulas_menu:
                p.update()
                p.draw(self.tela)
            
            if self.estado != "CONFIGURACOES":
                Renderer._desenhar_controle_volume(self, mx, my)

        # Seleção de renderizador por estado
        render_map = {
            "INPUT_NOME": Renderer._render_input_nome,
            "MENU_MODO": Renderer._render_menu_modo,
            "TELA_INFO_MODOS": Renderer._render_info_modos,
            "TELA_INIMIGOS": Renderer._render_tela_inimigos,
            "RANKING": Renderer._render_ranking,
            "PERGUNTA_MODO": Renderer._render_pergunta_modo,
            "CONFIGURACOES": Renderer._render_configuracoes,
            "JOGANDO": Renderer._render_gameplay,
            "PAUSA": Renderer._render_gameplay,
        }

        if self.estado in render_map:
            render_map[self.estado](self, mx, my)

        # Sincronizar mouse com seleção (híbrido) - DEPOIS de renderizar para ter os botões na lista
        if self.estado not in ["JOGANDO"]:
            mouse_moveu = (mx, my) != getattr(self, "ultima_pos_mouse", (0, 0))
            if mouse_moveu:
                self.ultima_pos_mouse = (mx, my)
                # Primeiro checa botões da nova classe (precedência)
                for btn in self.botoes_menu:
                    if btn.rect.collidepoint(mx, my) and btn.id is not None:
                        if isinstance(btn.id, int):
                            self.botao_selecionado = btn.id
                
                # Depois checa hitboxes legadas
                for item in self.botoes_hitboxes:
                    if isinstance(item, tuple) and len(item) >= 2:
                        rect, val = item[:2]
                        if rect.collidepoint(mx, my):
                            self.botao_selecionado = val

        # HUD Topo (Sempre visível em menus/jogo)
        Renderer._render_hud_topo(self)

        # Escalonamento inteligente mantendo proporção (Letterbox/Pillarbox)
        rect_destino = self.calcular_rect_tela()
        self.tela_real.fill((0, 0, 0)) # Limpa com preto para as barras laterais
        
        if rect_destino.size != self.tela.get_size():
            # Redimensionamento suave para evitar serrilhado em resoluções não nativas
            self.tela_real.blit(pygame.transform.smoothscale(self.tela, rect_destino.size), rect_destino)
        else:
            self.tela_real.blit(self.tela, rect_destino)
            
        pygame.display.flip()

    @staticmethod
    def _render_hud_topo(self):
        """Desenha contadores persistentes no topo da tela."""
        estados_v = ["INPUT_NOME", "MENU_MODO", "TELA_INFO_MODOS", "TELA_INIMIGOS", "PERGUNTA_MODO", "JOGANDO", "PAUSA", "RANKING", "CONFIGURACOES"]
        if self.estado not in estados_v: return

        x = 170 if self.estado in ["TELA_INFO_MODOS", "TELA_INIMIGOS", "PERGUNTA_MODO", "CONFIGURACOES"] else 20
        y = 16
        
        txt_m = f"💀 {int(getattr(self, 'mortes_total_jogador', 0))}"
        surf_m = self.fonte_sub.render(txt_m, True, VERMELHO_SANGUE)
        self.tela.blit(surf_m, (x, y))

        if self.modo_jogo == "CORRIDA":
            txt_f = f"FASE: {int(self.fase_atual)}/10"
            desenhar_texto(self.tela, txt_f, self.fonte_sub, BRANCO, x + surf_m.get_width() + 40, y + 12, "esquerda")

    @staticmethod
    def _render_input_nome(self, mx, my):
        cx, cy = LARGURA_TELA // 2, ALTURA_TELA // 2
        desenhar_texto(self.tela, "NEON SURGE", self.fonte_titulo, CIANO_NEON, cx, cy - 140)
        desenhar_texto(self.tela, "IDENTIFICAÇÃO DO PLAYER:", self.fonte_texto, BRANCO, cx, cy - 20)

        caixa = pygame.Rect(0, 0, 420, 70)
        caixa.center = (cx, cy + 40)
        pygame.draw.rect(self.tela, AZUL_ESCURO, caixa, border_radius=12)
        pygame.draw.rect(self.tela, VERDE_NEON, caixa, 2, border_radius=12)

        cursor = "_" if int(time.time() * 2) % 2 == 0 else ""
        desenhar_texto(self.tela, self.nome_jogador + cursor, self.fonte_sub, VERDE_NEON, cx, cy + 40)

        btn = Button(cx, cy + 160, 400, 55, "INICIAR PROTOCOLO", self.fonte_sub, callback=self.acionar_botao, id=0)
        btn.update((mx, my), self.botao_selecionado)
        btn.draw(self.tela)
        self.botoes_menu.append(btn)

    @staticmethod
    def _render_pergunta_modo(self, mx, my):
        cx, cy = LARGURA_TELA // 2, ALTURA_TELA // 2
        desenhar_texto(self.tela, "PLAYER RECONHECIDO", self.fonte_titulo, VERDE_NEON, cx, cy - 120)
        modo = self.modo_jogo.replace("_", " ")
        
        def cont():
            self.botao_selecionado = 0
            self.acionar_botao()
        def alt():
            self.botao_selecionado = 1
            self.acionar_botao()

        b1 = Button(cx, cy + 20, 500, 55, f"CONTINUAR EM {modo}", self.fonte_sub, callback=cont, id=0)
        b2 = Button(cx, cy + 100, 500, 55, "ALTERAR MODO DE JOGO", self.fonte_sub, callback=alt, id=1)
        
        for b in [b1, b2]:
            b.update((mx, my), self.botao_selecionado)
            b.draw(self.tela)
            self.botoes_menu.append(b)

    @staticmethod
    def _render_menu_modo(self, mx, my):
        cx, cy = LARGURA_TELA // 2, ALTURA_TELA // 2
        modos = self.obter_pads_menu()
        
        # Botão Ranking (Superior Direito)
        def ir_rank():
            self.botao_selecionado = "IR_RANKING"
            self.acionar_botao()
        
        btn_rank = Button(LARGURA_TELA - 110, 42, 180, 45, "🏆 RANKING", self.fonte_sub, callback=ir_rank, id="IR_RANKING")
        btn_rank.update((mx, my), self.botao_selecionado)
        btn_rank.draw(self.tela)
        self.botoes_menu.append(btn_rank)

        # Botão Sair (Canto Inferior Esquerdo)
        def sair():
            self.botao_selecionado = "SAIR_JOGO"
            self.acionar_botao()
            
        btn_sair = Button(110, ALTURA_TELA - 42, 180, 45, "🚪 SAIR", self.fonte_sub, callback=sair, id="SAIR_JOGO")
        btn_sair.update((mx, my), self.botao_selecionado)
        btn_sair.draw(self.tela)
        self.botoes_menu.append(btn_sair)

        id_busca = self.botao_selecionado if isinstance(self.botao_selecionado, int) else 0
        sel = next((m for m in modos if m["id"] == id_busca), modos[0])

        pw, ph = 1000, 190
        rect_desc = pygame.Rect(cx - pw//2, cy - 230, pw, ph)
        self.tela.blit(criar_painel_transparente(pw, ph), rect_desc.topleft)
        desenhar_moldura(self.tela, rect_desc, sel["cor"])
        
        desenhar_texto(self.tela, sel["texto"], self.fonte_titulo, sel["cor"], cx, rect_desc.top + 55)
        desenhar_texto(self.tela, sel["tag"], self.fonte_sub, BRANCO, cx, rect_desc.top + 110)
        desenhar_texto(self.tela, sel["descricao"], self.fonte_texto, BRANCO, cx, rect_desc.top + 155)

        cw, ch = 240, 95
        gx, gy = 20, 20
        cols = 4
        rows = 2
        total_w = (cols * cw) + ((cols-1) * gx)
        total_h = (rows * ch) + ((rows-1) * gy)
        
        sx = cx - total_w // 2
        sy = cy + 10

        for i, m in enumerate(modos):
            r, c = i // cols, i % cols
            bx, by = sx + c*(cw+gx) + cw//2, sy + r*(ch+gy) + ch//2
            
            def select_mode(val=m["id"]):
                self.botao_selecionado = val
                self.acionar_botao()

            btn = Button(bx, by, cw, ch, m["texto"], self.fonte_sub, callback=select_mode, id=m["id"])
            btn.update((mx, my), self.botao_selecionado)
            btn.draw(self.tela)
            self.botoes_menu.append(btn)

    @staticmethod
    def _render_info_modos(self, mx, my):
        cx, cy = LARGURA_TELA // 2, ALTURA_TELA // 2
        aba = getattr(self, "guia_aba", "MODOS")
        
        def set_aba_modos():
            self.guia_aba = "MODOS"
            self.botao_selecionado = 0
        def set_aba_keys():
            self.guia_aba = "HOTKEYS"
            self.botao_selecionado = 1

        b1 = Button(cx - 160, 130, 280, 45, "GUIA DE SISTEMA", self.fonte_texto, callback=set_aba_modos, id=0)
        b2 = Button(cx + 160, 130, 280, 45, "MAPEAMENTO DE TECLAS", self.fonte_texto, callback=set_aba_keys, id=1)
        
        for b in [b1, b2]:
            b.update((mx, my), self.botao_selecionado)
            b.draw(self.tela)
            self.botoes_menu.append(b)

        pw, ph = LARGURA_TELA - 100, 420
        rect = pygame.Rect(50, 175, pw, ph)
        self.tela.blit(criar_painel_transparente(pw, ph), rect.topleft)
        desenhar_moldura(self.tela, rect, AMARELO_DADO if aba=="MODOS" else VERDE_NEON)

        if aba == "HOTKEYS":
            items = [("WASD / SETAS", "Movimentação da Nave"), ("SPACE / L-SHIFT", "DASH: Impulso e Invencibilidade"), ("TECLA ESC", "Menu de Pausa / Retornar"), ("TECLA F11", "Alternar Visualização de Tela"), ("TECLAS + / -", "Ajuste Dinâmico de Volume")]
            for i, (k, d) in enumerate(items):
                y = rect.top + 60 + i * 70
                desenhar_texto(self.tela, k, self.fonte_sub, CIANO_NEON, cx - 60, y, "direita")
                desenhar_texto(self.tela, d, self.fonte_texto, BRANCO, cx + 60, y, "esquerda")
        else:
            regras = [("OBJETIVOS", "Avance eliminando ameaças e coletando núcleos de energia."), ("AMEAÇAS", "Analise os padrões de ataque no banco de dados antes de iniciar."), ("PONTUAÇÃO", "Tempo de sobrevivência e precisão definem sua posição no ranking."), ("MODO TREINO", "Customize o ambiente para dominar as mecânicas de combate.")]
            for i, (t, d) in enumerate(regras):
                y = rect.top + 50 + i * 90
                desenhar_texto(self.tela, t + ":", self.fonte_sub, AMARELO_DADO, rect.left + 60, y, "esquerda")
                desenhar_texto(self.tela, d, self.fonte_texto, BRANCO, rect.left + 60, y + 35, "esquerda")

        def voltar():
            self.botao_selecionado = 2
            self.acionar_botao()
        btn_v = Button(cx, cy + 300, 400, 55, "RETORNAR AO MENU", self.fonte_sub, callback=voltar, id=2)
        btn_v.update((mx, my), self.botao_selecionado)
        btn_v.draw(self.tela)
        self.botoes_menu.append(btn_v)

    @staticmethod
    def _render_tela_inimigos(self, mx, my):
        cx, cy = LARGURA_TELA // 2, ALTURA_TELA // 2
        is_t = (self.modo_jogo == "TREINO")
        aba = getattr(self, "guia_aba", "COMUNS")
        cor_t = VERDE_NEON if is_t else VERMELHO_SANGUE
        
        # Abas de Categoria
        cats = ["COMUNS", "MINIBOSSES", "BOSSES"]
        if is_t: cats.append("GUIA")
        
        n_abas = len(cats)
        tw = n_abas * 240
        start_x = cx - tw // 2
        
        for i, c in enumerate(cats):
            bx = start_x + (i * 240) + 120
            def change_tab(val=i):
                self.botao_selecionado = val
                self.acionar_botao()

            btn = Button(bx, 130, 220, 45, c, self.fonte_texto, callback=change_tab, id=i)
            btn.update((mx, my), self.botao_selecionado)
            btn.draw(self.tela)
            self.botoes_menu.append(btn)

        # Painel Principal
        pw, ph = LARGURA_TELA - 80, 440
        rect_p = pygame.Rect(40, 175, pw, ph)
        self.tela.blit(criar_painel_transparente(pw, ph), rect_p.topleft)
        desenhar_moldura(self.tela, rect_p, cor_t)

        if aba == "GUIA":
            Renderer._render_guia_treino(self, rect_p)
        else:
            items = [t for t in INIMIGOS_DATA.items() if t[1]["categoria"] == aba]
            
            # Lista de Inimigos (Esquerda)
            for i, (tid, data) in enumerate(items):
                iy = rect_p.top + 30 + i * 65
                ix = rect_p.left + 240
                
                def select_enemy(idx=4+i):
                    self.botao_selecionado = idx
                    self.acionar_botao()

                btn_inim = Button(ix, iy + 27, 420, 55, data["nome"], self.fonte_sub, callback=select_enemy, id=4+i)
                btn_inim.update((mx, my), self.botao_selecionado)
                btn_inim.draw(self.tela)
                self.botoes_menu.append(btn_inim)

                pygame.draw.circle(self.tela, data["cor"], (rect_p.left + 60, iy + 27), 10)
                
                if is_t:
                    qtd = self.inimigos_treino_selecionados.get(tid, 0)
                    bx_q = rect_p.left + 350
                    
                    def dec_enemy(t=tid):
                        self.inimigos_treino_selecionados[t] = max(0, self.inimigos_treino_selecionados.get(t, 0) - 1)
                        self.sounds.play('menu_button')

                    btn_m = Button(bx_q - 45, iy + 27, 35, 35, "-", self.fonte_sub, callback=dec_enemy, id=f"dec_{tid}")
                    btn_m.update((mx, my))
                    btn_m.draw(self.tela)
                    self.botoes_menu.append(btn_m)

                    desenhar_texto(self.tela, str(qtd), self.fonte_sub, VERDE_NEON if qtd > 0 else CINZA_CLARO, bx_q, iy + 27)

                    def inc_enemy(t=tid):
                        self.inimigos_treino_selecionados[t] = min(10, self.inimigos_treino_selecionados.get(t, 0) + 1)
                        self.sounds.play('menu_button')

                    btn_p = Button(bx_q + 25, iy + 27, 35, 35, "+", self.fonte_sub, callback=inc_enemy, id=f"inc_{tid}")
                    btn_p.update((mx, my))
                    btn_p.draw(self.tela)
                    self.botoes_menu.append(btn_p)

            # Detalhes (Direita)
            sel_idx = self.botao_selecionado - 4
            if 0 <= sel_idx < len(items):
                tid, data = items[sel_idx]
                dx = rect_p.left + 480
                desenhar_texto(self.tela, data["nome"], self.fonte_titulo, data["cor"], dx, rect_p.top + 70, "esquerda")
                pygame.draw.line(self.tela, data["cor"], (dx, rect_p.top + 130), (rect_p.right - 40, rect_p.top + 130), 3)
                
                palavras = data["desc"].split()
                linhas, curr = [], ""
                for p in palavras:
                    if len(curr + p) < 40: curr += p + " "
                    else: linhas.append(curr); curr = p + " "
                linhas.append(curr)
                for i, l in enumerate(linhas):
                    desenhar_texto(self.tela, l, self.fonte_texto, BRANCO, dx, rect_p.top + 160 + i*35, "esquerda")

        txt_b = "INICIAR SIMULAÇÃO" if is_t else "VOLTAR AO MENU"
        def final_action():
            self.botao_selecionado = 99
            self.acionar_botao()

        btn_f = Button(cx, rect_p.bottom + 65, 400, 55, txt_b, self.fonte_sub, callback=final_action, id=99)
        btn_f.update((mx, my), self.botao_selecionado)
        btn_f.draw(self.tela)
        self.botoes_menu.append(btn_f)

    @staticmethod
    def _render_guia_treino(self, rect):
        cx = rect.centerx
        desenhar_texto(self.tela, "PROTOCOLOS DE TREINAMENTO", self.fonte_sub, VERDE_NEON, cx, rect.top + 50)
        
        instrucoes = [
            ("PERSONALIZAÇÃO", "Selecione a quantidade de cada inimigo usando os botões [+] e [-]."),
            ("COMBATE REALISTA", "Inimigos manterão seus comportamentos e danos originais."),
            ("IMORTALIDADE", "Neste modo, sua nave não é destruída. Use para aprender padrões."),
            ("CONTROLES", "Use as setas para navegar e clique ou use ENTER para ajustar."),
            ("EXPERIMENTAL", "Você pode spawnar até 10 unidades de cada tipo simultaneamente.")
        ]
        
        for i, (tit, desc) in enumerate(instrucoes):
            y = rect.top + 110 + i * 65
            desenhar_texto(self.tela, f"• {tit}:", self.fonte_texto, VERDE_NEON, rect.left + 60, y, "esquerda")
            desenhar_texto(self.tela, desc, self.fonte_desc, BRANCO, rect.left + 60, y + 25, "esquerda")


    @staticmethod
    def _render_ranking(self, mx, my):
        cx, cy = LARGURA_TELA // 2, ALTURA_TELA // 2
        aba_atual = getattr(self, "ranking_aba", "CORRIDA")
        veio_de_fim = getattr(self, "veio_de_fim_partida", False)
        
        desenhar_texto(self.tela, "LEADERBOARDS MULTIVERSAIS", self.fonte_titulo, AMARELO_DADO, cx, 60)
        
        if not veio_de_fim:
            modos_rank = ["CORRIDA", "SOBREVIVENCIA", "HARDCORE", "LABIRINTO", "CORRIDA_INFINITA"]
            for i, m in enumerate(modos_rank):
                rx = cx - 440 + (i * 220)
                def change_rank(val=m):
                    self.trocar_aba_ranking(val)
                    self.botao_selecionado = f"ABA_RANK_{val}"
                
                btn = Button(rx, 115, 200, 40, m.replace("_", " "), self.fonte_desc, callback=change_rank, id=f"ABA_RANK_{m}")
                btn.update((mx, my), self.botao_selecionado)
                btn.draw(self.tela)
                self.botoes_menu.append(btn)
        else:
            desenhar_texto(self.tela, f"MODO: {aba_atual.replace('_', ' ')}", self.fonte_sub, CIANO_NEON, cx, 115)

        pw, ph = LARGURA_TELA - 100, 460
        rect = pygame.Rect(50, 155, pw, ph)
        self.tela.blit(criar_painel_transparente(pw, ph), rect.topleft)
        desenhar_moldura(self.tela, rect, CIANO_NEON)

        w_metade = (pw - 60) // 2
        rect_local = pygame.Rect(rect.left + 20, rect.top + 20, w_metade, ph - 40)
        rect_global = pygame.Rect(rect.centerx + 10, rect.top + 20, w_metade, ph - 40)
        
        def draw_rank_list(r_area, titulo, dados, is_global):
            pygame.draw.rect(self.tela, (15, 25, 45), r_area, border_radius=12)
            desenhar_texto(self.tela, titulo, self.fonte_sub, VERDE_NEON, r_area.centerx, r_area.top + 35)
            pygame.draw.line(self.tela, VERDE_NEON, (r_area.left + 40, r_area.top + 60), (r_area.right - 40, r_area.top + 60), 2)
            
            if not dados and not (is_global and getattr(self, "carregando_ranking", False)):
                desenhar_texto(self.tela, "NENHUM DADO ENCONTRADO", self.fonte_desc, CINZA_CLARO, r_area.centerx, r_area.centery)
                return

            if is_global and getattr(self, "carregando_ranking", False):
                desenhar_texto(self.tela, "CARREGANDO DADOS...", self.fonte_desc, AMARELO_DADO, r_area.centerx, r_area.centery)
                return

            for i, item in enumerate(dados[:10]):
                y = r_area.top + 95 + i * 34
                is_current = False
                nome = item.get("nome") or item.get("player_name", "???")
                score = item.get("tempo") or item.get("fase") or item.get("score", 0)
                
                if veio_de_fim:
                    if str(nome).upper() == getattr(self, "nome_jogador", "").upper():
                        if f"{float(score):.1f}" == f"{getattr(self, 'ultimo_tempo', -1.0):.1f}":
                            is_current = True
                
                cor = VERDE_NEON if is_current else (AMARELO_DADO if i == 0 else BRANCO)
                desenhar_texto(self.tela, f"{i+1}º", self.fonte_desc, cor, r_area.left + 35, y, "esquerda")
                desenhar_texto(self.tela, str(nome).upper(), self.fonte_desc, cor, r_area.left + 85, y, "esquerda")
                txt_score = f"{float(score):.1f}s"
                if "INFINITA" in aba_atual or "LABIRINTO" in aba_atual: txt_score = f"F{int(score)}"
                desenhar_texto(self.tela, txt_score, self.fonte_desc, cor, r_area.right - 35, y, "direita")

        chave_local = aba_atual.capitalize()
        if aba_atual == "LABIRINTO": chave_local = "Labirinto_Infinito"
        elif aba_atual == "CORRIDA_INFINITA": chave_local = "Corrida_Infinita"
        dados_locais = self.ranking.get(chave_local, [])
        
        draw_rank_list(rect_local, "💾 RECORDS LOCAIS", dados_locais, False)
        draw_rank_list(rect_global, "🌐 TOP 10 GLOBAL", getattr(self, "ranking_global", []), True)

        by = rect.bottom + 65
        def ir_menu():
            self.botao_selecionado = 1 if veio_de_fim else 0
            self.acionar_botao()
        def tentar():
            self.botao_selecionado = 0
            self.acionar_botao()
        def novo():
            self.botao_selecionado = 2
            self.acionar_botao()

        if veio_de_fim:
            b1 = Button(cx - 280, by, 250, 45, "TENTAR NOVAMENTE", self.fonte_sub, callback=tentar, id=0)
            b2 = Button(cx, by, 250, 45, "MENU PRINCIPAL", self.fonte_sub, callback=ir_menu, id=1)
            b3 = Button(cx + 280, by, 250, 45, "NOVO JOGADOR", self.fonte_sub, callback=novo, id=2)
            for b in [b1, b2, b3]:
                b.update((mx, my), self.botao_selecionado)
                b.draw(self.tela)
                self.botoes_menu.append(b)
        else:
            btn = Button(cx, by, 350, 50, "VOLTAR AO MENU", self.fonte_sub, callback=ir_menu, id=0)
            btn.update((mx, my), self.botao_selecionado)
            btn.draw(self.tela)
            self.botoes_menu.append(btn)

    @staticmethod
    def _render_configuracoes(self, mx, my):
        cx, cy = LARGURA_TELA // 2, ALTURA_TELA // 2
        pw, ph = 840, 620
        rect = pygame.Rect(cx - pw//2, cy - ph//2, pw, ph)
        self.tela.blit(criar_painel_transparente(pw, ph), rect.topleft)
        desenhar_moldura(self.tela, rect, CIANO_NEON, "CONFIGURAÇÕES DE SISTEMA", self.fonte_sub)

        def draw_neon_bar(label, y, vol, idx, cor):
            foc = (self.botao_selecionado == idx)
            lx, bx = rect.left + 60, cx - 40
            bw, bh = 340, 32
            desenhar_texto(self.tela, label, self.fonte_sub, BRANCO if foc else CINZA_CLARO, lx, y, "esquerda")
            rect_bg = pygame.Rect(bx, y - bh//2, bw, bh)
            pygame.draw.rect(self.tela, (12, 22, 40), rect_bg, border_radius=10)
            pygame.draw.rect(self.tela, cor if foc else CINZA_ESCURO, rect_bg, 2, border_radius=10)
            
            num_seg, pad = 10, 6
            seg_w = (bw - (pad * 2)) // num_seg
            pre = int(vol * num_seg)
            for i in range(num_seg):
                sr = pygame.Rect(bx + pad + i*seg_w + 2, y - bh//2 + 6, seg_w - 4, bh - 12)
                if i < pre:
                    pygame.draw.rect(self.tela, cor, sr, border_radius=3)
                    if foc: desenhar_brilho_neon(self.tela, cor, sr.centerx, sr.centery, 10, 1)
                else: pygame.draw.rect(self.tela, (25, 35, 55), sr, border_radius=3)

            def m_vol(): self.alterar_volume_musica(-0.1) if idx==0 else self.alterar_volume_sfx(-0.1)
            def p_vol(): self.alterar_volume_musica(0.1) if idx==0 else self.alterar_volume_sfx(0.1)
            
            bm = Button(bx - 42, y, 44, 44, "-", self.fonte_sub, callback=m_vol, id=f"v{idx}_-")
            bp = Button(bx + bw + 42, y, 44, 44, "+", self.fonte_sub, callback=p_vol, id=f"v{idx}_+")
            for b in [bm, bp]:
                b.update((mx, my))
                b.draw(self.tela)
                self.botoes_menu.append(b)

        draw_neon_bar("VOLUME MÚSICA", rect.top + 140, self.sounds.volume_musica, 0, CIANO_NEON)
        draw_neon_bar("EFEITOS SONOROS", rect.top + 250, self.sounds.volume_sfx, 1, ROSA_NEON)
        
        ry = rect.top + 360
        foc_res = (self.botao_selecionado == 2)
        rect_res = pygame.Rect(rect.left + 50, ry - 45, pw - 100, 90)
        pygame.draw.rect(self.tela, (18, 28, 48), rect_res, border_radius=15)
        pygame.draw.rect(self.tela, VERDE_NEON if foc_res else CINZA_ESCURO, rect_res, 2, border_radius=15)
        desenhar_texto(self.tela, "RESOLUÇÃO DE VÍDEO", self.fonte_sub, BRANCO if foc_res else CINZA_CLARO, rect.left + 80, ry, "esquerda")
        
        res_txt = f"{self.resolucoes[self.res_idx][0]}x{self.resolucoes[self.res_idx][1]}"
        if self.is_fullscreen: res_txt = f"FULLSCREEN [{res_txt}]"
        tx_pos = rect.left + 560
        desenhar_texto(self.tela, res_txt, self.fonte_sub, VERDE_NEON, tx_pos, ry)
        
        def res_m(): self.alterar_resolucao(-1)
        def res_p(): self.alterar_resolucao(1)
        bl = Button(tx_pos - 160, ry, 44, 44, "<", self.fonte_sub, callback=res_m, id="res_-")
        br = Button(tx_pos + 115, ry, 44, 44, ">", self.fonte_sub, callback=res_p, id="res_+")
        for b in [bl, br]:
            b.update((mx, my))
            b.draw(self.tela)
            self.botoes_menu.append(b)

        btn_c = Button(cx, rect.bottom - 80, 450, 60, "SALVAR E RETORNAR AO MENU", self.fonte_sub, callback=self.acionar_botao, id=3)
        btn_c.update((mx, my), self.botao_selecionado)
        btn_c.draw(self.tela)
        self.botoes_menu.append(btn_c)

    @staticmethod
    def _render_gameplay(self, mx, my):
        off_x = random.randint(-8, 8) if self.shake_frames > 0 else 0
        off_y = random.randint(-8, 8) if self.shake_frames > 0 else 0
        if self.shake_frames > 0 and self.estado == "JOGANDO": self.shake_frames -= 1
        self.tela.fill(PRETO_FUNDO)
        surf = pygame.Surface((LARGURA_TELA, ALTURA_TELA), pygame.SRCALPHA)
        desenhar_grade_jogo(surf)
        if self.modo_jogo == "LABIRINTO":
            for w in self.labirinto_paredes:
                pygame.draw.rect(surf, (22, 34, 58), w)
                pygame.draw.rect(surf, CIANO_NEON, w, 1)
            Renderer._render_lab_ui(self, surf)
        Renderer._render_portais(self, surf)
        for d in self.coletaveis:
            desenhar_brilho_neon(surf, AMARELO_DADO, d.x, d.y, 6, 2)
            pygame.draw.rect(surf, AMARELO_DADO, (int(d.x)-6, int(d.y)-6, 12, 12), border_radius=2)
        if self.portal_aberto: Renderer._render_portal_saida(self, surf)
        for p in self.particulas: p.draw(surf)
        for i in self.inimigos: i.draw(surf)
        for b in self.buracos_negros: b.draw(surf)
        if self.modo_jogo in ["SOBREVIVENCIA", "HARDCORE"]:
            self.lava_manager.draw(surf, self.fonte_titulo, self.fonte_sub)
        Renderer._render_projeteis(self, surf)
        self.player.draw(surf)
        self.tela.blit(surf, (off_x, off_y))
        Renderer._render_hud_gameplay(self)
        if self.estado == "PAUSA": Renderer._render_pausa(self, mx, my)

    @staticmethod
    def _render_pausa(self, mx, my):
        cx, cy = LARGURA_TELA // 2, ALTURA_TELA // 2
        overlay = pygame.Surface((LARGURA_TELA, ALTURA_TELA), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.tela.blit(overlay, (0, 0))
        desenhar_texto(self.tela, "SISTEMA EM PAUSA", self.fonte_titulo, BRANCO, cx, cy - 120)
        
        btns_data = [("CONTINUAR OPERAÇÃO", VERDE_NEON), ("AJUSTES DE SISTEMA", AMARELO_DADO)]
        if self.modo_jogo == "CORRIDA": btns_data.append(("REINICIAR CORRIDA", CIANO_NEON))
        btns_data.append(("ABANDONAR MISSÃO", VERMELHO_SANGUE))
        
        for i, (t, c) in enumerate(btns_data):
            def cb(idx=i):
                self.botao_selecionado = idx
                self.acionar_botao()
            btn = Button(cx, cy + i * 70, 400, 50, t, self.fonte_sub, callback=cb, id=i)
            btn.update((mx, my), self.botao_selecionado)
            btn.draw(self.tela)
            self.botoes_menu.append(btn)

    @staticmethod
    def _render_lab_ui(self, surf):
        t = max(0.0, float(getattr(self, "labirinto_tempo_restante", 0.0)))
        cor = VERMELHO_SANGUE if t < 8 else (AMARELO_DADO if t < 15 else CIANO_NEON)
        desenhar_texto(surf, f"TEMPO: {t:04.1f}s", self.fonte_sub, cor, LARGURA_TELA // 2, 90)
        for a in self.labirinto_armadilhas:
            p = abs(math.sin((time.time()*8) + a.get("fase",0)))
            r = a["raio"] + p*2.5
            desenhar_brilho_neon(surf, VERMELHO_SANGUE, a["pos"].x, a["pos"].y, r+4, 2)
            pygame.draw.circle(surf, VERMELHO_SANGUE, (int(a["pos"].x), int(a["pos"].y)), int(r))
            pygame.draw.circle(surf, BRANCO, (int(a["pos"].x), int(a["pos"].y)), max(1, int(r//3)))
        for g in self.labirinto_fantasmas:
            Renderer._draw_fancy_circle(surf, g["pos"], g.get("raio",10), g.get("cor", ROSA_NEON))

    @staticmethod
    def _render_portais(self, surf):
        for p in self.portais_inimigos:
            cor = ROXO_NEON if p["tipo"] in ["boss", "boss_artilharia", "boss_caotico"] else (AMARELO_DADO if "miniboss" in p["tipo"] else VERMELHO_SANGUE)
            r_base = 20 if "boss" in p["tipo"] else (18 if "miniboss" in p["tipo"] else 16)
            pulso = abs(math.sin(time.time()*6)) * 3
            r = r_base + pulso
            c = (int(p["pos"].x), int(p["pos"].y))
            desenhar_brilho_neon(surf, cor, c[0], c[1], r+2, 3)
            pygame.draw.circle(surf, (*cor, 120), c, int(r+3))
            pygame.draw.circle(surf, PRETO_FUNDO, c, int(r-4))
            pygame.draw.circle(surf, cor, c, int(r), 3)
            ang = (time.time()*6) % (math.pi*2)
            pygame.draw.arc(surf, BRANCO, pygame.Rect(c[0]-r, c[1]-r, r*2, r*2), ang, ang+math.pi*1.3, 4)

    @staticmethod
    def _render_projeteis(self, surf):
        for pr in self.projeteis_inimigos:
            pos = pr.get("pos_visual", (pr["pos"].x, pr["pos"].y))
            cor = pr.get("cor", LARANJA_NEON)
            if pr.get("tipo") == "bomba":
                alvo, re = pr["alvo_final"], pr["raio_explosao"]
                alpha = int(80 + math.sin(time.time()*15)*40)
                aviso = pygame.Surface((re*2, re*2), pygame.SRCALPHA)
                pygame.draw.circle(aviso, (*cor, alpha), (re, re), re)
                pygame.draw.circle(aviso, (*cor, 255), (re, re), re, 2)
                surf.blit(aviso, (alvo.x - re, alvo.y - re))
                Renderer._draw_fancy_circle(surf, pygame.math.Vector2(pos[0], pos[1]), 10, cor)
            else:
                r = int(pr.get("raio", 4))
                Renderer._draw_fancy_circle(surf, pygame.math.Vector2(pos[0], pos[1]), r, cor)

    @staticmethod
    def _render_hud_gameplay(self):
        m = self.modo_jogo
        if m == "CORRIDA":
            cur, key = self.tempo_corrida, "Corrida"
            best = self.ranking.get(key, [{}])[0].get("tempo", cur) if self.ranking.get(key) else cur
            txt = f"{cur:.1f}s / MELHOR: {best:.1f}s"
        elif m == "TREINO": txt = f"MORTES: {int(self.mortes_total_jogador)}"
        elif m in ["SOBREVIVENCIA", "HARDCORE"]:
            cur, key = self.tempo_sobrevivencia, m.capitalize()
            best = self.ranking.get(key, [{}])[0].get("tempo", cur) if self.ranking.get(key) else cur
            txt = f"{cur:.1f}s / RECORDE: {best:.1f}s"
        else:
            cur = int(self.fase_atual)
            key = "Labirinto_Infinito" if m=="LABIRINTO" else "Corrida_Infinita"
            best = self.ranking.get(key, [{}])[0].get("fase", cur) if self.ranking.get(key) else cur
            txt = f"FASE: {cur} / RECORDE: {best}"
        desenhar_texto(self.tela, txt, self.fonte_sub, VERDE_NEON, LARGURA_TELA - 20, 20, "direita")

    @staticmethod
    def _render_portal_saida(self, surf):
        c = (int(self.portal_pos.x), int(self.portal_pos.y))
        r = 22 + abs(math.sin(time.time()*5)) * 4
        desenhar_brilho_neon(surf, VERDE_NEON, c[0], c[1], r+2, 4)
        pygame.draw.circle(surf, (*VERDE_NEON, 180), c, int(r+3))
        pygame.draw.circle(surf, PRETO_FUNDO, c, int(r-5))
        pygame.draw.circle(surf, VERDE_NEON, c, int(r), 3)
        ang = (time.time()*5) % (math.pi*2)
        pygame.draw.arc(surf, BRANCO, pygame.Rect(c[0]-r, c[1]-r, r*2, r*2), ang, ang+math.pi*1.25, 4)

    @staticmethod
    def _draw_fancy_circle(surf, pos, r, cor):
        desenhar_brilho_neon(surf, cor, pos.x, pos.y, r+2, 2)
        pygame.draw.circle(surf, cor, (int(pos.x), int(pos.y)), int(r))
        pygame.draw.circle(surf, BRANCO, (int(pos.x), int(pos.y)), max(1, int(r//2.5)))

    @staticmethod
    def _desenhar_controle_volume(self, mx, my):
        rx, ry = LARGURA_TELA - 410, ALTURA_TELA - 70
        self.tela.blit(criar_painel_transparente(390, 50), (rx, ry))
        vol = "MUDO" if self.mutado else f"{int(self.volume_musica * 100)}%"
        desenhar_texto(self.tela, vol, self.fonte_sub, VERDE_NEON if not self.mutado else CINZA_CLARO, rx+20, ry+25, "esquerda")
        
        def m_vol(): self.alterar_volume(-0.1)
        def p_vol(): self.alterar_volume(0.1)
        def t_mute(): self.alternar_mute()
        def ir_cfg(): self.estado_anterior_config = self.estado; self.estado = "CONFIGURACOES"; self.botao_selecionado = 0

        b_m = Button(rx+180, ry+25, 40, 40, "-", self.fonte_sub, callback=m_vol, id="vol_-")
        b_p = Button(rx+290, ry+25, 40, 40, "+", self.fonte_sub, callback=p_vol, id="vol_+")
        b_mu = Button(rx+235, ry+25, 40, 40, "", self.fonte_sub, callback=t_mute, id="vol_mute")
        b_cfg = Button(rx+350, ry+25, 40, 40, "", self.fonte_sub, callback=ir_cfg, id="vol_cfg")
        
        for b in [b_m, b_p, b_mu, b_cfg]:
            b.update((mx, my))
            b.draw(self.tela)
            if b.id == "vol_mute": desenhar_icone_som(self.tela, b.rect.centerx, b.rect.centery, self.mutado, BRANCO)
            elif b.id == "vol_cfg": desenhar_icone_engrenagem(self.tela, b.rect.centerx, b.rect.centery, BRANCO)
            self.botoes_menu.append(b)

# Atalhos
def desenhar(self): Renderer.desenhar(self)
def desenhar_controle_volume(self, mx, my): Renderer._desenhar_controle_volume(self, mx, my)
def desenhar_menu_configuracoes(self, mx, my): Renderer._render_configuracoes(self, mx, my)
