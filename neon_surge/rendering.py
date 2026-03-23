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
    desenhar_icone_engrenagem, desenhar_texto, desenhar_moldura
)
from .data import INIMIGOS_DATA

class Renderer:
    """Namespace para funções de renderização organizada."""
    
    @staticmethod
    def desenhar(self):
        """Método principal delegado do NeonSurge."""
        mx, my = self.obter_posicao_mouse()

        # Sincronizar mouse com botões (exceto em gameplay fluido)
        if self.estado not in ["JOGANDO"]:
            if (mx, my) != getattr(self, "ultima_pos_mouse", (0, 0)):
                for item in self.botoes_hitboxes:
                    if isinstance(item, tuple) and len(item) >= 2:
                        rect, val = item[:2]
                        if rect.collidepoint(mx, my):
                            if isinstance(val, int):
                                self.botao_selecionado = val
                    elif hasattr(item, "collidepoint") and item.collidepoint(mx, my):
                        # Fallback para quando ainda for apenas Rect
                        pass 
                self.ultima_pos_mouse = (mx, my)

        self.botoes_hitboxes = []
        
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

        btn = desenhar_botao_dinamico(self.tela, "INICIAR PROTOCOLO", self.fonte_sub, VERDE_NEON, cx, cy + 160, self.botao_selecionado == 0)
        self.botoes_hitboxes.append((btn, 0))

    @staticmethod
    def _render_pergunta_modo(self, mx, my):
        cx, cy = LARGURA_TELA // 2, ALTURA_TELA // 2
        desenhar_texto(self.tela, "PLAYER RECONHECIDO", self.fonte_titulo, VERDE_NEON, cx, cy - 120)
        modo = self.modo_jogo.replace("_", " ")
        
        b1 = desenhar_botao_dinamico(self.tela, f"CONTINUAR EM {modo}", self.fonte_sub, CIANO_NEON, cx, cy + 20, self.botao_selecionado == 0)
        b2 = desenhar_botao_dinamico(self.tela, "ALTERAR MODO DE JOGO", self.fonte_sub, ROSA_NEON, cx, cy + 100, self.botao_selecionado == 1)
        self.botoes_hitboxes.extend([(b1, 0), (b2, 1)])

    @staticmethod
    def _render_menu_modo(self, mx, my):
        cx, cy = LARGURA_TELA // 2, ALTURA_TELA // 2
        modos = self.obter_pads_menu()
        
        # Info do Modo (Painel Superior)
        sel = next((m for m in modos if m["id"] == self.botao_selecionado), modos[0])

        # Painel Descritivo - Refinado
        pw, ph = 1000, 190
        rect_desc = pygame.Rect(cx - pw//2, cy - 230, pw, ph)
        self.tela.blit(criar_painel_transparente(pw, ph), rect_desc.topleft)
        desenhar_moldura(self.tela, rect_desc, sel["cor"])
        
        desenhar_texto(self.tela, sel["texto"], self.fonte_titulo, sel["cor"], cx, rect_desc.top + 55)
        desenhar_texto(self.tela, sel["tag"], self.fonte_sub, BRANCO, cx, rect_desc.top + 110)
        desenhar_texto(self.tela, sel["descricao"], self.fonte_texto, BRANCO, cx, rect_desc.top + 155)

        # Grid de 4 Colunas x 2 Linhas (Total 8 itens)
        cw, ch = 240, 95
        gx, gy = 20, 20
        cols = 4
        total_w = (cols * cw) + ((cols-1) * gx)
        sx = cx - total_w // 2
        sy = cy + 10

        for i, m in enumerate(modos):
            r, c = i // cols, i % cols
            rect = pygame.Rect(sx + c*(cw+gx), sy + r*(ch+gy), cw, ch)
            ativo = (self.botao_selecionado == m["id"])
            
            # Cores dinâmicas para botões
            cf = m["cor"] if ativo else (15, 20, 30)
            ct = PRETO_FUNDO if ativo else BRANCO
            
            pygame.draw.rect(self.tela, cf, rect, border_radius=12)
            pygame.draw.rect(self.tela, m["cor"] if not ativo else BRANCO, rect, 2, border_radius=12)
            
            desenhar_texto(self.tela, m["texto"], self.fonte_sub, ct, rect.centerx, rect.top + 35)
            desenhar_texto(self.tela, m["tag"], self.fonte_desc, PRETO_FUNDO if ativo else m["cor"], rect.centerx, rect.top + 65)
            self.botoes_hitboxes.append((rect, m["id"]))

    @staticmethod
    def _render_info_modos(self, mx, my):
        cx, cy = LARGURA_TELA // 2, ALTURA_TELA // 2
        aba = getattr(self, "guia_aba", "MODOS")
        
        # Abas
        b1 = desenhar_botao_dinamico(self.tela, "GUIA DE SISTEMA", self.fonte_texto, AMARELO_DADO if aba=="MODOS" else CINZA_CLARO, cx - 160, 130, self.botao_selecionado == 0, 280, 45)
        b2 = desenhar_botao_dinamico(self.tela, "MAPEAMENTO DE TECLAS", self.fonte_texto, VERDE_NEON if aba=="HOTKEYS" else CINZA_CLARO, cx + 160, 130, self.botao_selecionado == 1, 280, 45)
        self.botoes_hitboxes.extend([(b1, 0), (b2, 1)])

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

        btn_v = desenhar_botao_dinamico(self.tela, "RETORNAR AO MENU", self.fonte_sub, VERDE_NEON, cx, cy + 300, self.botao_selecionado == 2)
        self.botoes_hitboxes.append((btn_v, 2))

    @staticmethod
    def _render_tela_inimigos(self, mx, my):
        cx, cy = LARGURA_TELA // 2, ALTURA_TELA // 2
        is_t = (self.modo_jogo == "TREINO")
        aba = getattr(self, "guia_aba", "COMUNS")
        cor_t = VERDE_NEON if is_t else VERMELHO_SANGUE
        
        # Abas
        cats = ["COMUNS", "MINIBOSSES", "BOSSES"]
        for i, c in enumerate(cats):
            bx = cx - 280 + (i * 280)
            btn = desenhar_botao_dinamico(self.tela, c, self.fonte_texto, cor_t if aba==c else CINZA_CLARO, bx, 130, self.botao_selecionado == i, 260, 45)
            self.botoes_hitboxes.append((btn, i))

        # Painel
        pw, ph = LARGURA_TELA - 80, 440
        rect = pygame.Rect(40, 175, pw, ph)
        self.tela.blit(criar_painel_transparente(pw, ph), rect.topleft)
        desenhar_moldura(self.tela, rect, cor_t)

        items = [t for t in INIMIGOS_DATA.items() if t[1]["categoria"] == aba]
        
        # Lista (Esquerda)
        for i, (tid, data) in enumerate(items):
            iy = rect.top + 30 + i * 65
            ir = pygame.Rect(rect.left + 30, iy, 380, 55)
            foc = (self.botao_selecionado == 3 + i)
            
            pygame.draw.rect(self.tela, (*data["cor"], 50 if foc else 15), ir, border_radius=10)
            pygame.draw.rect(self.tela, data["cor"] if foc else CINZA_ESCURO, ir, 2, border_radius=10)
            
            pygame.draw.circle(self.tela, data["cor"], (ir.left + 30, ir.centery), 10)
            desenhar_texto(self.tela, data["nome"], self.fonte_sub, BRANCO, ir.left + 65, ir.centery, "esquerda")
            
            if is_t:
                qtd = self.inimigos_treino_selecionados.get(tid, 0)
                desenhar_texto(self.tela, f"QTD: {qtd}", self.fonte_sub, VERDE_NEON if qtd>0 else CINZA_CLARO, ir.right - 60, ir.centery)
            self.botoes_hitboxes.append((ir, 3 + i))

        # Detalhes (Direita)
        sel_idx = self.botao_selecionado - 3
        if 0 <= sel_idx < len(items):
            tid, data = items[sel_idx]
            dx = rect.left + 460
            desenhar_texto(self.tela, data["nome"], self.fonte_titulo, data["cor"], dx, rect.top + 70, "esquerda")
            pygame.draw.line(self.tela, data["cor"], (dx, rect.top + 130), (rect.right - 40, rect.top + 130), 3)
            
            # Descrição Wrap
            palavras = data["desc"].split()
            linhas, curr = [], ""
            for p in palavras:
                if len(curr + p) < 45: curr += p + " "
                else: linhas.append(curr); curr = p + " "
            linhas.append(curr)
            for i, l in enumerate(linhas):
                desenhar_texto(self.tela, l, self.fonte_texto, BRANCO, dx, rect.top + 160 + i*35, "esquerda")

        txt_b = "INICIAR SIMULAÇÃO" if is_t else "VOLTAR AO MENU"
        last_idx = 3 + len(items)
        btn_f = desenhar_botao_dinamico(self.tela, txt_b, self.fonte_sub, cor_t if is_t else CIANO_NEON, cx, rect.bottom + 65, self.botao_selecionado == last_idx)
        self.botoes_hitboxes.append((btn_f, last_idx))

    @staticmethod
    def _render_ranking(self, mx, my):
        cx, cy = LARGURA_TELA // 2, ALTURA_TELA // 2
        desenhar_texto(self.tela, "SISTEMA DESATIVADO", self.fonte_titulo, VERMELHO_SANGUE, cx, 70)
        
        pw, ph = 840, 380
        rect = pygame.Rect(cx - pw//2, 150, pw, ph)
        self.tela.blit(criar_painel_transparente(pw, ph), rect.topleft)
        desenhar_moldura(self.tela, rect, CIANO_NEON)
        
        res = f"SCORE: {self.ultimo_tempo:.1f}s | POSIÇÃO: {self.ultima_posicao}º"
        if self.modo_jogo in ["CORRIDA_INFINITA", "LABIRINTO"]:
            res = f"FASE ALCANÇADA: {int(self.ultimo_tempo)} | POSIÇÃO: {self.ultima_posicao}º"
        desenhar_texto(self.tela, res, self.fonte_sub, VERDE_NEON, cx, rect.top + 45)

        chave = self.modo_jogo.capitalize()
        if self.modo_jogo == "LABIRINTO": chave = "Labirinto_Infinito"
        elif self.modo_jogo == "CORRIDA_INFINITA": chave = "Corrida_Infinita"
        
        top = self.ranking.get(chave, [])[:5]
        for i, r in enumerate(top):
            y = rect.top + 120 + i*45
            cor = AMARELO_DADO if (i+1 == self.ultima_posicao) else BRANCO
            desenhar_texto(self.tela, f"{i+1}º {r['nome']}", self.fonte_sub, cor, rect.left + 100, y, "esquerda")
            val = f"Fase {r.get('fase',0)}" if "fase" in r else f"{r.get('tempo',0):.1f}s"
            desenhar_texto(self.tela, val, self.fonte_sub, cor, rect.right - 100, y, "direita")

        by = rect.bottom + 70
        self.botoes_hitboxes.append((desenhar_botao_dinamico(self.tela, "REPETIR", self.fonte_sub, VERDE_NEON, cx - 240, by, self.botao_selecionado == 0, 220, 50), 0))
        self.botoes_hitboxes.append((desenhar_botao_dinamico(self.tela, "MENU", self.fonte_sub, CIANO_NEON, cx, by, self.botao_selecionado == 1, 220, 50), 1))
        self.botoes_hitboxes.append((desenhar_botao_dinamico(self.tela, "NOVO PLAYER", self.fonte_sub, ROSA_NEON, cx + 240, by, self.botao_selecionado == 2, 220, 50), 2))

    @staticmethod
    def _render_configuracoes(self, mx, my):
        cx, cy = LARGURA_TELA // 2, ALTURA_TELA // 2
        pw, ph = 800, 580
        rect = pygame.Rect(cx - pw//2, cy - ph//2, pw, ph)
        
        # Fundo e Moldura
        self.tela.blit(criar_painel_transparente(pw, ph), rect.topleft)
        desenhar_moldura(self.tela, rect, CIANO_NEON, "CONFIGURAÇÕES DE SISTEMA", self.fonte_sub)

        def draw_neon_bar(label, y, vol, idx, cor):
            foc = (self.botao_selecionado == idx)
            bx, bw, bh = cx + 20, 320, 30
            
            # Label com destaque se focado
            cor_label = BRANCO if foc else CINZA_CLARO
            desenhar_texto(self.tela, label, self.fonte_sub, cor_label, cx - 120, y, "direita")
            
            # Container da barra
            rect_bg = pygame.Rect(bx, y - bh//2, bw, bh)
            pygame.draw.rect(self.tela, (10, 20, 35), rect_bg, border_radius=8)
            pygame.draw.rect(self.tela, cor if foc else CINZA_ESCURO, rect_bg, 2, border_radius=8)
            
            # Preenchimento Segmentado
            num_segmentos = 10
            seg_w = (bw - 10) // num_segmentos
            preenchidos = int(vol * num_segmentos)
            
            for i in range(num_segmentos):
                seg_rect = pygame.Rect(bx + 5 + i*seg_w, y - bh//2 + 5, seg_w - 4, bh - 10)
                if i < preenchidos:
                    # Segmento ativo com glow se focado
                    alpha = 255 if foc else 180
                    pygame.draw.rect(self.tela, (*cor, alpha), seg_rect, border_radius=3)
                    if foc:
                        desenhar_brilho_neon(self.tela, cor, seg_rect.centerx, seg_rect.centery, 8, 1)
                else:
                    pygame.draw.rect(self.tela, (20, 30, 50), seg_rect, border_radius=3)

            # Hitboxes (Mapeadas para controle fino)
            h_menos = pygame.Rect(bx - 55, y - 20, 40, 40)
            h_mais = pygame.Rect(bx + bw + 15, y - 20, 40, 40)
            
            # Botões de ajuste minimalistas
            def draw_adj_btn(r, txt, active):
                h = r.collidepoint(mx, my)
                c = cor if h else (cor if active else (40, 50, 70))
                pygame.draw.rect(self.tela, c, r, border_radius=6 if h else 4, width=0 if h else 2)
                desenhar_texto(self.tela, txt, self.fonte_sub, PRETO_FUNDO if h else BRANCO, r.centerx, r.centery)

            draw_adj_btn(h_menos, "-", foc)
            draw_adj_btn(h_mais, "+", foc)
            
            self.botoes_hitboxes.append((h_menos, f"val_{idx}_-"))
            self.botoes_hitboxes.append((h_mais, f"val_{idx}_+"))
            self.botoes_hitboxes.append((pygame.Rect(cx - 380, y-30, 760, 60), idx))

        # Volumes
        draw_neon_bar("ÁUDIO BGM", cy - 120, self.sounds.volume_musica, 0, CIANO_NEON)
        draw_neon_bar("EFEITOS SFX", cy - 30, self.sounds.volume_sfx, 1, ROSA_NEON)
        
        # Resolução (Estilo Card)
        ry = cy + 90
        foc_res = (self.botao_selecionado == 2)
        rect_res = pygame.Rect(cx - 360, ry - 35, 720, 70)
        
        pygame.draw.rect(self.tela, (15, 25, 45), rect_res, border_radius=10)
        pygame.draw.rect(self.tela, VERDE_NEON if foc_res else CINZA_ESCURO, rect_res, 2, border_radius=10)
        
        desenhar_texto(self.tela, "RESOLUÇÃO DE VÍDEO", self.fonte_sub, BRANCO if foc_res else CINZA_CLARO, cx - 120, ry, "direita")
        
        res_txt = f"{self.resolucoes[self.res_idx][0]}x{self.resolucoes[self.res_idx][1]}"
        if self.is_fullscreen: res_txt = f"FULLSCREEN [{res_txt}]"
        
        desenhar_texto(self.tela, res_txt, self.fonte_sub, VERDE_NEON, cx + 180, ry)
        
        # Setas de Resolução
        btn_l = pygame.Rect(cx + 20, ry - 20, 40, 40)
        btn_r = pygame.Rect(cx + 335, ry - 20, 40, 40)
        
        for r, t, act in [(btn_l, "<", "res_-"), (btn_r, ">", "res_+")]:
            h = r.collidepoint(mx, my)
            pygame.draw.rect(self.tela, VERDE_NEON if h else (40, 50, 70), r, border_radius=6, width=0 if h else 2)
            desenhar_texto(self.tela, t, self.fonte_sub, PRETO_FUNDO if h else BRANCO, r.centerx, r.centery)
            self.botoes_hitboxes.append((r, act))
        
        self.botoes_hitboxes.append((rect_res, 2))

        # Botão Confirmar
        btn_c = desenhar_botao_dinamico(self.tela, "SALVAR E RETORNAR", self.fonte_sub, AMARELO_DADO, cx, rect.bottom - 70, self.botao_selecionado == 3, 400, 55)
        self.botoes_hitboxes.append((btn_c, 3))

    @staticmethod
    def _render_gameplay(self, mx, my):
        # Shake de tela
        off_x = random.randint(-8, 8) if self.shake_frames > 0 else 0
        off_y = random.randint(-8, 8) if self.shake_frames > 0 else 0
        if self.shake_frames > 0 and self.estado == "JOGANDO": self.shake_frames -= 1

        self.tela.fill(PRETO_FUNDO)
        surf = pygame.Surface((LARGURA_TELA, ALTURA_TELA), pygame.SRCALPHA)
        desenhar_grade_jogo(surf)

        # Labirinto
        if self.modo_jogo == "LABIRINTO":
            for w in self.labirinto_paredes:
                pygame.draw.rect(surf, (22, 34, 58), w)
                pygame.draw.rect(surf, CIANO_NEON, w, 1)
            Renderer._render_lab_ui(self, surf)

        # Portais
        Renderer._render_portais(self, surf)

        # Entidades
        for d in self.coletaveis:
            desenhar_brilho_neon(surf, AMARELO_DADO, d.x, d.y, 6, 2)
            pygame.draw.rect(surf, AMARELO_DADO, (int(d.x)-6, int(d.y)-6, 12, 12), border_radius=2)

        if self.portal_aberto: Renderer._render_portal_saida(self, surf)

        for p in self.particulas: p.draw(surf)
        for i in self.inimigos: i.draw(surf)
        for b in self.buracos_negros: b.draw(surf)
        
        # Lava (Survival)
        if self.modo_jogo in ["SOBREVIVENCIA", "HARDCORE"]:
            self.lava_manager.draw(surf, self.fonte_titulo, self.fonte_sub)

        Renderer._render_projeteis(self, surf)
        
        self.player.draw(surf)
        self.tela.blit(surf, (off_x, off_y))

        # HUD Gameplay
        Renderer._render_hud_gameplay(self)

        # Menu de Pausa Overlay
        if self.estado == "PAUSA":
            Renderer._render_pausa(self)

    @staticmethod
    def _render_pausa(self):
        cx, cy = LARGURA_TELA // 2, ALTURA_TELA // 2
        overlay = pygame.Surface((LARGURA_TELA, ALTURA_TELA), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.tela.blit(overlay, (0, 0))
        
        desenhar_texto(self.tela, "SISTEMA EM PAUSA", self.fonte_titulo, BRANCO, cx, cy - 120)
        
        btns = [("CONTINUAR OPERAÇÃO", VERDE_NEON), ("AJUSTES DE SISTEMA", AMARELO_DADO)]
        if self.modo_jogo == "CORRIDA": btns.append(("REINICIAR CORRIDA", CIANO_NEON))
        btns.append(("ABANDONAR MISSÃO", VERMELHO_SANGUE))
        
        for i, (t, c) in enumerate(btns):
            y = cy + i * 70
            rect = desenhar_botao_dinamico(self.tela, t, self.fonte_sub, c, cx, y, self.botao_selecionado == i, 400, 50)
            self.botoes_hitboxes.append((rect, i))

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
                alvo = pr["alvo_final"]
                re = pr["raio_explosao"]
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
        # Lógica de Score e Recorde
        m = self.modo_jogo
        if m == "CORRIDA":
            cur, key = self.tempo_corrida, "Corrida"
            best = self.ranking.get(key, [{}])[0].get("tempo", cur) if self.ranking.get(key) else cur
            txt = f"{cur:.1f}s / MELHOR: {best:.1f}s"
        elif m == "TREINO":
            txt = f"MORTES: {int(self.mortes_total_jogador)}"
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
        # Re-usando lógica original mas com visual limpo
        rx, ry = LARGURA_TELA - 410, ALTURA_TELA - 70
        self.tela.blit(criar_painel_transparente(390, 50), (rx, ry))
        
        vol = "MUDO" if self.mutado else f"{int(self.volume_musica * 100)}%"
        desenhar_texto(self.tela, vol, self.fonte_sub, VERDE_NEON if not self.mutado else CINZA_CLARO, rx+20, ry+25, "esquerda")
        
        # Botões de volume simplificados
        Renderer._draw_vol_btn(self, "-", rx+180, ry+25, self.rect_vol_menos, mx, my)
        Renderer._draw_vol_btn(self, "+", rx+290, ry+25, self.rect_vol_mais, mx, my)
        Renderer._draw_mute_btn(self, rx+235, ry+25, mx, my)
        Renderer._draw_config_btn(self, rx+350, ry+25, mx, my)

    @staticmethod
    def _draw_vol_btn(self, txt, cx, cy, rect, mx, my):
        rect.center = (cx, cy)
        h = rect.collidepoint(mx, my)
        pygame.draw.rect(self.tela, CIANO_NEON if h else (20,30,40), rect, border_radius=6)
        desenhar_texto(self.tela, txt, self.fonte_sub, BRANCO, cx, cy)

    @staticmethod
    def _draw_mute_btn(self, cx, cy, mx, my):
        self.rect_vol_mute.center = (cx, cy)
        h = self.rect_vol_mute.collidepoint(mx, my)
        pygame.draw.rect(self.tela, ROSA_NEON if h else (20,30,40), self.rect_vol_mute, border_radius=6)
        desenhar_icone_som(self.tela, cx, cy, self.mutado, BRANCO)

    @staticmethod
    def _draw_config_btn(self, cx, cy, mx, my):
        self.rect_vol_config.center = (cx, cy)
        h = self.rect_vol_config.collidepoint(mx, my)
        pygame.draw.rect(self.tela, AMARELO_DADO if h else (20,30,40), self.rect_vol_config, border_radius=6)
        desenhar_icone_engrenagem(self.tela, cx, cy, BRANCO)

# Atalhos globais para facilitar o registro no NeonSurge
def desenhar(self): Renderer.desenhar(self)
def desenhar_controle_volume(self, mx, my): Renderer._desenhar_controle_volume(self, mx, my)
def desenhar_menu_configuracoes(self, mx, my): Renderer._render_configuracoes(self, mx, my)
