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
    desenhar_texto, desenhar_moldura
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
            if (mx, my) != self.ultima_pos_mouse:
                for i, btn in enumerate(self.botoes_hitboxes):
                    if btn.collidepoint(mx, my):
                        self.botao_selecionado = i
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

        # Escalonamento para tela cheia
        if self.is_fullscreen:
            w, h = self.tela_real.get_size()
            self.tela_real.blit(pygame.transform.scale(self.tela, (w, h)), (0, 0))
        else:
            self.tela_real.blit(self.tela, (0, 0))
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
        self.botoes_hitboxes.append(btn)

    @staticmethod
    def _render_pergunta_modo(self, mx, my):
        cx, cy = LARGURA_TELA // 2, ALTURA_TELA // 2
        desenhar_texto(self.tela, "PLAYER RECONHECIDO", self.fonte_titulo, VERDE_NEON, cx, cy - 120)
        modo = self.modo_jogo.replace("_", " ")
        
        b1 = desenhar_botao_dinamico(self.tela, f"CONTINUAR EM {modo}", self.fonte_sub, CIANO_NEON, cx, cy + 20, self.botao_selecionado == 0)
        b2 = desenhar_botao_dinamico(self.tela, "ALTERAR MODO DE JOGO", self.fonte_sub, ROSA_NEON, cx, cy + 100, self.botao_selecionado == 1)
        self.botoes_hitboxes.extend([b1, b2])

    @staticmethod
    def _render_menu_modo(self, mx, my):
        cx, cy = LARGURA_TELA // 2, ALTURA_TELA // 2
        modos = self.obter_pads_menu()
        
        # Info do Modo
        sel = next((m for m in modos if m["id"] == self.botao_selecionado), None)
        if self.botao_selecionado == 99:
            sel = {"texto": "OPÇÕES DE TELA", "tag": "FULLSCREEN / WINDOWED", "descricao": "Alterne entre modo janela ou tela cheia (F11).", "cor": AMARELO_DADO}
        if not sel: sel = modos[0]

        # Painel Descritivo
        pw, ph = 960, 180
        rect_desc = pygame.Rect(cx - pw//2, cy - 240, pw, ph)
        self.tela.blit(criar_painel_transparente(pw, ph), rect_desc.topleft)
        desenhar_moldura(self.tela, rect_desc, sel["cor"])
        
        desenhar_texto(self.tela, sel["texto"], self.fonte_titulo, sel["cor"], cx, rect_desc.top + 50)
        desenhar_texto(self.tela, sel["tag"], self.fonte_sub, BRANCO, cx, rect_desc.top + 105)
        desenhar_texto(self.tela, sel["descricao"], self.fonte_texto, BRANCO, cx, rect_desc.top + 145)

        # Grid
        cw, ch = 240, 95
        gx, gy = 25, 20
        cols = 3
        total_w = (cols * cw) + ((cols-1) * gx)
        sx = cx - total_w // 2
        sy = cy - 20

        for i, m in enumerate(modos):
            r, c = i // cols, i % cols
            rect = pygame.Rect(sx + c*(cw+gx), sy + r*(ch+gy), cw, ch)
            ativo = (self.botao_selecionado == m["id"])
            
            cf = m["cor"] if ativo else (15, 20, 30)
            ct = PRETO_FUNDO if ativo else BRANCO
            
            pygame.draw.rect(self.tela, cf, rect, border_radius=12)
            pygame.draw.rect(self.tela, m["cor"] if not ativo else BRANCO, rect, 2, border_radius=12)
            
            desenhar_texto(self.tela, m["texto"], self.fonte_sub, ct, rect.centerx, rect.top + 35)
            desenhar_texto(self.tela, m["tag"], self.fonte_desc, PRETO_FUNDO if ativo else m["cor"], rect.centerx, rect.top + 65)
            self.botoes_hitboxes.append(rect)

        # Botão de Tela
        txt_t = "FECHAR TELA CHEIA" if self.is_fullscreen else "ATIVAR TELA CHEIA"
        btn_t = desenhar_botao_dinamico(self.tela, txt_t, self.fonte_sub, AMARELO_DADO, cx, sy + (3*(ch+gy)) - 10, self.botao_selecionado == 99, 450, 50)
        self.botoes_hitboxes.append(btn_t)

    @staticmethod
    def _render_info_modos(self, mx, my):
        cx, cy = LARGURA_TELA // 2, ALTURA_TELA // 2
        aba = getattr(self, "guia_aba", "MODOS")
        
        # Abas
        b1 = desenhar_botao_dinamico(self.tela, "GUIA DE SISTEMA", self.fonte_texto, AMARELO_DADO if aba=="MODOS" else CINZA_CLARO, cx - 160, 130, self.botao_selecionado == 0, 280, 45)
        b2 = desenhar_botao_dinamico(self.tela, "MAPEAMENTO DE TECLAS", self.fonte_texto, VERDE_NEON if aba=="HOTKEYS" else CINZA_CLARO, cx + 160, 130, self.botao_selecionado == 1, 280, 45)
        self.botoes_hitboxes.extend([b1, b2])

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
        self.botoes_hitboxes.append(btn_v)

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
            self.botoes_hitboxes.append(btn)

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
            self.botoes_hitboxes.append(ir)

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
        btn_f = desenhar_botao_dinamico(self.tela, txt_b, self.fonte_sub, cor_t if is_t else CIANO_NEON, cx, rect.bottom + 65, self.botao_selecionado == len(self.botoes_hitboxes))
        self.botoes_hitboxes.append(btn_f)

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
        self.botoes_hitboxes.append(desenhar_botao_dinamico(self.tela, "REPETIR", self.fonte_sub, VERDE_NEON, cx - 240, by, self.botao_selecionado == 0, 220, 50))
        self.botoes_hitboxes.append(desenhar_botao_dinamico(self.tela, "MENU", self.fonte_sub, CIANO_NEON, cx, by, self.botao_selecionado == 1, 220, 50))
        self.botoes_hitboxes.append(desenhar_botao_dinamico(self.tela, "NOVO PLAYER", self.fonte_sub, ROSA_NEON, cx + 240, by, self.botao_selecionado == 2, 220, 50))

    @staticmethod
    def _render_configuracoes(self, mx, my):
        cx, cy = LARGURA_TELA // 2, ALTURA_TELA // 2
        pw, ph = 680, 460
        rect = pygame.Rect(cx - pw//2, cy - ph//2, pw, ph)
        self.tela.blit(criar_painel_transparente(pw, ph), rect.topleft)
        desenhar_moldura(self.tela, rect, CIANO_NEON, "AJUSTES DE ÁUDIO", self.fonte_sub)

        def draw_bar(label, y, vol, idx, cor):
            foc = (self.botao_selecionado == idx)
            if foc: pygame.draw.rect(self.tela, (*cor, 60), (rect.left+30, y-30, pw-60, 60), border_radius=12)
            desenhar_texto(self.tela, label, self.fonte_sub, BRANCO if foc else CINZA_CLARO, cx - 220, y, "esquerda")
            
            # Barra de volume
            bx, bw = cx, 240
            pygame.draw.rect(self.tela, CINZA_ESCURO, (bx, y-12, bw, 24), border_radius=6)
            pygame.draw.rect(self.tela, cor, (bx, y-12, int(bw * vol), 24), border_radius=6)
            for i in range(1, 10):
                pygame.draw.line(self.tela, PRETO_FUNDO, (bx + i*(bw/10), y-12), (bx + i*(bw/10), y+11), 1)
            
            # Hitboxes para botões - e +
            self.botoes_hitboxes.append(pygame.Rect(bx - 50, y-20, 40, 40))
            self.botoes_hitboxes.append(pygame.Rect(bx + bw + 10, y-20, 40, 40))

        draw_bar("VOLUME MÚSICA", cy - 40, self.sounds.volume_musica, 0, CIANO_NEON)
        draw_bar("EFEITOS SONOROS", cy + 60, self.sounds.volume_sfx, 1, ROSA_NEON)
        
        btn = desenhar_botao_dinamico(self.tela, "CONFIRMAR E SAIR", self.fonte_sub, AMARELO_DADO, cx, rect.bottom - 70, self.botao_selecionado == 2, 350, 50)
        self.botoes_hitboxes.append(btn)

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

        # Lava (Survival)
        if self.modo_jogo in ["SOBREVIVENCIA", "HARDCORE"]:
            Renderer._render_lava(self, surf)

        # Entidades
        for d in self.coletaveis:
            desenhar_brilho_neon(surf, AMARELO_DADO, d.x, d.y, 6, 2)
            pygame.draw.rect(surf, AMARELO_DADO, (int(d.x)-6, int(d.y)-6, 12, 12), border_radius=2)

        if self.portal_aberto: Renderer._render_portal_saida(self, surf)

        for p in self.particulas: p.draw(surf)
        for i in self.inimigos: i.draw(surf)
        for b in self.buracos_negros: b.draw(surf)
        Renderer._render_projeteis(self, surf)
        
        self.player.draw(surf)
        self.tela.blit(surf, (off_x, off_y))

        # HUD Gameplay
        Renderer._render_hud_gameplay(self)

        # Menu de Pausa Overlay
        if self.estado == "PAUSA":
            Renderer._render_pausa(self)

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
    def _render_lava(self, surf):
        if self.aviso_lava > 0.0 and self.tipo_lava != 0:
            for r in self.lava_hitboxes:
                s = pygame.Surface((r.width, r.height), pygame.SRCALPHA)
                al = int(100 + math.sin(time.time()*20)*50)
                s.fill((255, 150, 0, al))
                pygame.draw.rect(s, AMARELO_DADO, (0,0,r.width,r.height), 4)
                surf.blit(s, (r.x, r.y))
            desenhar_texto(surf, f"ALERTA DE LAVA: {int(self.aviso_lava)+1}s!", self.fonte_titulo, VERMELHO_SANGUE, LARGURA_TELA//2, 140)

        if getattr(self, "lava_ativa", False):
            if (self.tempo_lava_restante > 1.5) or (int(time.time()*8)%2 == 0):
                for r in self.lava_hitboxes:
                    s = pygame.Surface((r.width, r.height), pygame.SRCALPHA)
                    s.fill((255, 60, 0, 140))
                    pygame.draw.rect(s, VERMELHO_SANGUE, (0,0,r.width,r.height), 4)
                    surf.blit(s, (r.x, r.y))
            desenhar_texto(surf, f"LAVA ATIVA: {self.tempo_lava_restante:.1f}s", self.fonte_sub, LARANJA_NEON, LARGURA_TELA//2, 90)

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
    def _render_pausa(self):
        cx, cy = LARGURA_TELA // 2, ALTURA_TELA // 2
        overlay = pygame.Surface((LARGURA_TELA, ALTURA_TELA), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.tela.blit(overlay, (0, 0))
        
        desenhar_texto(self.tela, "SISTEMA EM PAUSA", self.fonte_titulo, BRANCO, cx, cy - 120)
        
        btns = [("CONTINUAR OPERAÇÃO", VERDE_NEON), ("AJUSTES DE ÁUDIO", AMARELO_DADO)]
        if self.modo_jogo == "CORRIDA": btns.append(("REINICIAR CORRIDA", CIANO_NEON))
        btns.append(("ABANDONAR MISSÃO", VERMELHO_SANGUE))
        
        for i, (t, c) in enumerate(btns):
            y = cy + i * 70
            rect = desenhar_botao_dinamico(self.tela, t, self.fonte_sub, c, cx, y, self.botao_selecionado == i, 400, 50)
            self.botoes_hitboxes.append(rect)

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
        rx, ry = LARGURA_TELA - 360, ALTURA_TELA - 70
        self.tela.blit(criar_painel_transparente(340, 50), (rx, ry))
        
        vol = "MUDO" if self.mutado else f"{int(self.volume_musica * 100)}%"
        desenhar_texto(self.tela, vol, self.fonte_sub, VERDE_NEON if not self.mutado else CINZA_CLARO, rx+20, ry+25, "esquerda")
        
        # Botões de volume simplificados
        Renderer._draw_vol_btn(self, "-", rx+200, ry+25, self.rect_vol_menos, mx, my)
        Renderer._draw_vol_btn(self, "+", rx+310, ry+25, self.rect_vol_mais, mx, my)
        Renderer._draw_mute_btn(self, rx+255, ry+25, mx, my)

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

# Atalhos globais para facilitar o registro no NeonSurge
def desenhar(self): Renderer.desenhar(self)
def desenhar_controle_volume(self, mx, my): Renderer._desenhar_controle_volume(self, mx, my)
def desenhar_menu_configuracoes(self, mx, my): Renderer._render_configuracoes(self, mx, my)
