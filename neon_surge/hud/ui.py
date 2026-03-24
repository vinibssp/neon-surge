import math
import time
import pygame

from ..constants import (
    ALTURA_TELA,
    AMARELO_DADO,
    BRANCO,
    CIANO_NEON,
    CINZA_CLARO,
    CINZA_ESCURO,
    COR_PAINEL,
    LARGURA_TELA,
    PRETO_FUNDO,
    ROSA_NEON,
    VERDE_NEON,
    VERMELHO_SANGUE,
)
from ..data import UI_COLORS, UI_ANIMATION, INIMIGOS_DATA


class Button:
    def __init__(self, x, y, largura, altura, texto, fonte, callback=None, id=None, cor=None):
        self.rect = pygame.Rect(x - largura // 2, y - altura // 2, largura, altura)
        self.texto = texto
        self.fonte = fonte
        self.callback = callback
        self.id = id
        self.cor = cor # Cor customizada para o botão
        
        self.is_hovered = False
        self.is_selected = False  # Para navegação via teclado
        self.scale = 1.0
        self.target_scale = 1.0
        
    def update(self, mouse_pos, current_selected_id=None):
        self.is_hovered = self.rect.collidepoint(mouse_pos)
        if current_selected_id is not None:
            self.is_selected = (self.id == current_selected_id)
        
        self.target_scale = UI_ANIMATION["HOVER_SCALE"] if (self.is_hovered or self.is_selected) else 1.0
        self.scale += (self.target_scale - self.scale) * 0.2

    def draw(self, surface):
        is_active = self.is_selected or self.is_hovered
        cor_base = self.cor if self.cor else (UI_COLORS["SELECTED"] if is_active else UI_COLORS["HIGHLIGHT"])
        
        if is_active and not self.cor:
            cor_base = UI_COLORS["SELECTED"]
            
        cor_texto = UI_COLORS["TEXT_SELECTED"] if is_active else UI_COLORS["TEXT_NORMAL"]
        
        draw_rect = self.rect.copy()
        if self.scale != 1.0:
            new_w = int(self.rect.width * self.scale)
            new_h = int(self.rect.height * self.scale)
            draw_rect = pygame.Rect(0, 0, new_w, new_h)
            draw_rect.center = self.rect.center

        # Desenho do botão
        bg_alpha = 255 if is_active else 0
        surf_btn = pygame.Surface((draw_rect.width, draw_rect.height), pygame.SRCALPHA)
        
        if is_active:
            pygame.draw.rect(surf_btn, (*cor_base, bg_alpha), (0, 0, draw_rect.width, draw_rect.height), border_radius=4)
            pygame.draw.rect(surf_btn, BRANCO, (0, 0, draw_rect.width, draw_rect.height), 2, border_radius=4)
        else:
            pygame.draw.rect(surf_btn, (*cor_base, 255), (0, 0, draw_rect.width, draw_rect.height), 2, border_radius=4)
            pygame.draw.rect(surf_btn, (*cor_base, 20), (0, 0, draw_rect.width, draw_rect.height), border_radius=4)
            
        surface.blit(surf_btn, draw_rect.topleft)

        texto_render = f"> {self.texto} <" if is_active else self.texto
        img_texto = self.fonte.render(texto_render, True, cor_texto)
        rect_texto = img_texto.get_rect(center=self.rect.center)
        surface.blit(img_texto, rect_texto)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.is_hovered and self.callback:
                self.callback()
                return True
        return False


class TrainingMenuManager:
    """Gerenciador Avançado para o Menu de Treino - Estética Terminal de Comando."""
    def __init__(self, game):
        self.game = game
        self.row_h = 66
        self.list_w = 700
        self.btn_size = 38
        self.sel_y_smooth = 0
        self.last_aba = ""
        self.scan_line_y = 0
        
    def render(self, surface, mx, my):
        cx, cy = LARGURA_TELA // 2, ALTURA_TELA // 2
        aba = self.game.guia_aba
        is_t = (self.game.modo_jogo == "TREINO")
        items = [t for t in INIMIGOS_DATA.items() if t[1]["categoria"] == aba]
        
        if aba != self.last_aba:
            self.last_aba = aba
            if self.game.botao_selecionado >= 4:
                self.game.botao_selecionado = 4
        
        # 1. Painel Principal (Main Frame)
        pw, ph = LARGURA_TELA - 80, 480
        rect_p = pygame.Rect(cx - pw//2, 155, pw, ph)
        surface.blit(criar_painel_transparente(pw, ph, (10, 15, 25, 230)), rect_p.topleft)
        
        cor_moldura = VERDE_NEON if is_t else VERMELHO_SANGUE
        desenhar_moldura(surface, rect_p, cor_moldura)
        
        # 2. Layout condicional (GUIA vs Outros)
        if aba == "GUIA":
            from ..rendering import Renderer
            Renderer._render_guia_treino(self.game, rect_p)
        else:
            # Divisor Visual apenas se não for GUIA
            divisor_x = rect_p.left + self.list_w + 40
            pygame.draw.line(surface, (*cor_moldura, 60), (divisor_x, rect_p.top + 20), (divisor_x, rect_p.bottom - 60), 1)

            # 3. Lista de Inimigos
            self._render_enemy_list(surface, items, rect_p, mx, my, is_t)
            
            # 4. Módulo de Inteligência (Direita)
            sel_idx = self.game.botao_selecionado - 4
            if 0 <= sel_idx < len(items):
                self._render_tactical_data(surface, items[sel_idx][1], divisor_x + 30, rect_p.top + 40)

        # 5. Rodapé e Botão Principal
        self._render_hotkeys_hint(surface, rect_p)
        self._render_main_button(surface, cx, rect_p.bottom + 50, is_t, mx, my)

    def _render_enemy_list(self, surface, items, rect_p, mx, my, is_t):
        start_y = rect_p.top + 50
        sel_idx = self.game.botao_selecionado - 4
        
        if 0 <= sel_idx < len(items):
            target_y = start_y + sel_idx * self.row_h
            if self.sel_y_smooth == 0: self.sel_y_smooth = target_y
            self.sel_y_smooth += (target_y - self.sel_y_smooth) * 0.22
            
            s_rect = pygame.Rect(rect_p.left + 25, self.sel_y_smooth - self.row_h//2, self.list_w + 20, self.row_h)
            desenhar_brilho_neon(surface, (*AMARELO_DADO, 30), s_rect.centerx, s_rect.centery, 15, 1)
            pygame.draw.rect(surface, (25, 30, 20), s_rect, border_radius=10)
            pygame.draw.rect(surface, AMARELO_DADO, s_rect, 2, border_radius=10)
            
            # Scan Line Animada
            self.scan_line_y = (time.time() * 150) % self.row_h
            scan_y = s_rect.top + self.scan_line_y
            if s_rect.top < scan_y < s_rect.bottom:
                pygame.draw.line(surface, (*AMARELO_DADO, 80), (s_rect.left + 5, scan_y), (s_rect.right - 5, scan_y), 1)

        for i, (tid, data) in enumerate(items):
            ry = start_y + i * self.row_h
            row_rect = pygame.Rect(rect_p.left + 35, ry - self.row_h//2 + 5, self.list_w, self.row_h - 10)
            
            if self.game.mouse_moveu and row_rect.collidepoint(mx, my):
                self.game.botao_selecionado = 4 + i

            is_sel = (self.game.botao_selecionado == 4 + i)
            
            # Nome e ID Técnico
            txt_n = data["nome"].upper()
            cor_n = AMARELO_DADO if is_sel else BRANCO
            desenhar_texto(surface, txt_n, self.game.fonte_sub, cor_n, row_rect.left + 20, row_rect.centery - 8, "esquerda")
            desenhar_texto(surface, tid.upper(), self.game.fonte_desc, (100, 100, 130), row_rect.left + 20, row_rect.centery + 12, "esquerda")

            if is_t:
                qtd = self.game.inimigos_treino_selecionados.get(tid, 0)
                bx = row_rect.right - 160
                
                def dec(t=tid):
                    self.game.inimigos_treino_selecionados[t] = max(0, self.game.inimigos_treino_selecionados.get(t, 0) - 1)
                    self.game.sounds.play('menu_button')
                def inc(t=tid):
                    self.game.inimigos_treino_selecionados[t] = min(10, self.game.inimigos_treino_selecionados.get(t, 0) + 1)
                    self.game.sounds.play('menu_button')

                for d_x, txt, cb, cor in [(0, "-", dec, VERMELHO_SANGUE), (120, "+", inc, VERDE_NEON)]:
                    btn_r = pygame.Rect(bx + d_x - self.btn_size//2, row_rect.centery - self.btn_size//2, self.btn_size, self.btn_size)
                    is_h = btn_r.collidepoint(mx, my)
                    pygame.draw.rect(surface, (15, 20, 30), btn_r, border_radius=6)
                    pygame.draw.rect(surface, cor if is_h else (*cor, 100), btn_r, 2, border_radius=6)
                    desenhar_texto(surface, txt, self.game.fonte_sub, cor if is_h else BRANCO, btn_r.centerx, btn_r.centery)
                    self.game.botoes_menu.append(Button(btn_r.centerx, btn_r.centery, self.btn_size, self.btn_size, txt, self.game.fonte_sub, callback=cb, id=f"act_{tid}_{txt}", cor=cor))

                desenhar_seletor_quantidade(surface, bx + 60, row_rect.centery, qtd, is_sel, self.game.fonte_sub)

    def _render_tactical_data(self, surface, data, dx, dy):
        det_w = 380
        # Painel Tático Simplificado
        pygame.draw.rect(surface, (12, 15, 22, 240), (dx - 10, dy - 10, det_w, 360), border_radius=8)
        pygame.draw.rect(surface, (*data["cor"], 60), (dx - 10, dy - 10, det_w, 360), 1, border_radius=8)
        
        # Header
        desenhar_texto(surface, data["nome"].upper(), self.game.fonte_sub, data["cor"], dx, dy + 10, "esquerda")
        pygame.draw.line(surface, (*data["cor"], 100), (dx, dy + 35), (dx + det_w - 20, dy + 35), 1)
        
        # Descrição principal (com mais espaço agora)
        desc_rect = pygame.Rect(dx, dy + 60, det_w - 20, 280)
        self._desenhar_texto_quebrado(surface, data["desc"], self.game.fonte_texto, (200, 200, 220), desc_rect)






    def _render_main_button(self, surface, x, y, is_t, mx, my):
        txt_f = "INICIAR PROTOCOLO" if is_t else "VOLTAR"
        btn_f = Button(x, y, 500, 60, txt_f, self.game.fonte_sub, callback=self.game.acionar_botao, id=99, cor=VERDE_NEON if is_t else CIANO_NEON)
        btn_f.update((mx, my), self.game.botao_selecionado)
        btn_f.draw(surface)
        self.game.botoes_menu.append(btn_f)

    def _render_hotkeys_hint(self, surface, rect):
        hints = [("[W/S]", "NAVEGAR"), ("[A/D]", "AJUSTE"), ("[Q/E]", "ABAS")]
        hx = rect.left + 30
        for key, act in hints:
            desenhar_texto(surface, key, self.game.fonte_desc, AMARELO_DADO, hx, rect.bottom - 28, "esquerda")
            hx += self.game.fonte_desc.size(key)[0] + 4
            desenhar_texto(surface, act, self.game.fonte_desc, BRANCO, hx, rect.bottom - 28, "esquerda")
            hx += self.game.fonte_desc.size(act)[0] + 18

    def _desenhar_texto_quebrado(self, surface, texto, fonte, cor, rect):
        palavras = texto.split()
        linhas = []
        linha_atual = ""
        for p in palavras:
            if fonte.size(linha_atual + p + " ")[0] < rect.width:
                linha_atual += p + " "
            else:
                linhas.append(linha_atual); linha_atual = p + " "
        linhas.append(linha_atual)
        for i, l in enumerate(linhas):
            desenhar_texto(surface, l, fonte, cor, rect.left, rect.top + i*22, "esquerda")


def desenhar_texto(surface, texto, fonte, cor, x, y, alinhamento="centro"):
    img_texto = fonte.render(texto, True, cor)
    rect_texto = img_texto.get_rect()
    if alinhamento == "centro":
        rect_texto.center = (x, y)
    elif alinhamento == "esquerda":
        rect_texto.midleft = (x, y)
    elif alinhamento == "direita":
        rect_texto.midright = (x, y)
    surface.blit(img_texto, rect_texto)
    return rect_texto


def desenhar_botao_dinamico(surface, texto, fonte, cor_base, cx, cy, is_hovered, largura=500, altura=55):
    """Mantido para compatibilidade legado."""
    texto_display = f"> {texto} <" if is_hovered else texto
    cor_texto = PRETO_FUNDO if is_hovered else BRANCO
    rect_botao = pygame.Rect(0, 0, largura, altura)
    rect_botao.center = (cx, cy)
    if is_hovered:
        pulso = math.sin(time.time() * 10) * 3
        rect_botao = rect_botao.inflate(pulso, pulso)
        pygame.draw.rect(surface, cor_base, rect_botao, border_radius=8)
        pygame.draw.rect(surface, BRANCO, rect_botao, 2, border_radius=8)
    else:
        pygame.draw.rect(surface, (10, 15, 25), rect_botao, border_radius=8)
        pygame.draw.rect(surface, cor_base, rect_botao, 2, border_radius=8)
    img_texto = fonte.render(texto_display, True, cor_texto)
    rect_texto = img_texto.get_rect(center=rect_botao.center)
    surface.blit(img_texto, rect_texto)
    return rect_botao


def desenhar_icone_som(surface, cx, cy, mutado, cor):
    pontos_falante = [
        (cx - 12, cy - 6),
        (cx - 4, cy - 6),
        (cx + 6, cy - 14),
        (cx + 6, cy + 14),
        (cx - 4, cy + 6),
        (cx - 12, cy + 6),
    ]
    pygame.draw.polygon(surface, cor, pontos_falante)
    if mutado:
        pygame.draw.line(surface, VERMELHO_SANGUE, (cx + 12, cy - 8), (cx + 24, cy + 8), 3)
        pygame.draw.line(surface, VERMELHO_SANGUE, (cx + 24, cy - 8), (cx + 12, cy + 8), 3)
    else:
        pygame.draw.arc(surface, cor, (cx - 4, cy - 8, 16, 16), -math.pi / 3, math.pi / 3, 2)
        pygame.draw.arc(surface, cor, (cx - 4, cy - 14, 28, 28), -math.pi / 4, math.pi / 4, 2)


def desenhar_icone_engrenagem(surface, cx, cy, cor):
    pygame.draw.circle(surface, cor, (cx, cy), 10, 3)
    for i in range(8):
        ang = i * (math.pi / 4)
        px1 = cx + math.cos(ang) * 10
        py1 = cy + math.sin(ang) * 10
        px2 = cx + math.cos(ang) * 14
        py2 = cy + math.sin(ang) * 14
        pygame.draw.line(surface, cor, (px1, py1), (px2, py2), 3)


def desenhar_brilho_neon(surface, cor, pos_x, pos_y, raio, intensidade=3):
    for i in range(intensidade, 0, -1):
        c_rgb = cor[:3]
        alpha = cor[3] if len(cor) > 3 else 15
        cor_com_alpha = (*c_rgb, alpha)
        pygame.draw.circle(surface, cor_com_alpha, (int(pos_x), int(pos_y)), int(raio + (i * 4)))


def desenhar_seletor_quantidade(surface, x, y, qtd, selecionado, fonte):
    cor = (20, 20, 30) if selecionado else (VERDE_NEON if qtd > 0 else CINZA_CLARO)
    if selecionado and qtd > 0:
        pulso = math.sin(time.time() * 15) * 4
        desenhar_brilho_neon(surface, AMARELO_DADO, x, y, 12 + pulso, 2)
    img = fonte.render(str(qtd), True, cor)
    rect = img.get_rect(center=(x, y))
    surface.blit(img, rect)
    return rect


def desenhar_fundo_cyberpunk(surface, tempo):
    horizonte_y = int(ALTURA_TELA * 0.6)
    centro_x = LARGURA_TELA // 2
    for y in range(ALTURA_TELA):
        t = y / ALTURA_TELA
        if y <= horizonte_y:
            r = int(12 + (46 * t))
            g = int(8 + (10 * t))
            b = int(34 + (90 * t))
        else:
            t2 = (y - horizonte_y) / max(1, (ALTURA_TELA - horizonte_y))
            r = int(18 + (16 * t2))
            g = int(4 + (14 * t2))
            b = int(30 + (56 * t2))
        pygame.draw.line(surface, (r, g, b), (0, y), (LARGURA_TELA, y))
    estrelas = 85
    for i in range(estrelas):
        x = int((i * 179 + (tempo * (4 + (i % 5)))) % LARGURA_TELA)
        y = int((i * 97) % max(1, int(horizonte_y * 0.9)))
        brilho = 140 + int(100 * (0.5 + 0.5 * math.sin((tempo * 2.4) + i)))
        surface.set_at((x, y), (min(255, brilho), min(255, brilho - 15), 255))
    sol_cx, sol_cy = centro_x, int(horizonte_y * 0.66)
    sol_raio = int(min(LARGURA_TELA, ALTURA_TELA) * 0.12)
    glow_sol = pygame.Surface((LARGURA_TELA, ALTURA_TELA), pygame.SRCALPHA)
    pulso = 0.86 + 0.14 * math.sin(tempo * 1.6)
    for mult, alpha in [(2.3, 18), (1.7, 30), (1.25, 55)]:
        pygame.draw.circle(glow_sol, (255, 60, 175, int(alpha * pulso)), (sol_cx, sol_cy), int(sol_raio * mult))
    surface.blit(glow_sol, (0, 0))
    pygame.draw.circle(surface, (255, 110, 70), (sol_cx, sol_cy), sol_raio)
    pygame.draw.circle(surface, (255, 185, 90), (sol_cx, sol_cy - 2), int(sol_raio * 0.72))
    for i in range(8):
        faixa_h = 5 + i * 2
        y_faixa = sol_cy - sol_raio + 12 + i * int(sol_raio * 0.22)
        pygame.draw.rect(surface, (255, 70, 160), (sol_cx - sol_raio, y_faixa, sol_raio * 2, faixa_h))
    pontos_montanha = []
    for x in range(-80, LARGURA_TELA + 81, 45):
        base = horizonte_y - 12
        altura = 28 + (x % 140)
        y = int(base - altura - 14 * math.sin((x * 0.018) + tempo * 0.35))
        pontos_montanha.append((x, y))
    poligono_montanha = [(0, horizonte_y + 10)] + pontos_montanha + [(LARGURA_TELA, horizonte_y + 10)]
    pygame.draw.polygon(surface, (20, 10, 34), poligono_montanha)
    pygame.draw.lines(surface, ROSA_NEON, False, pontos_montanha, 2)
    pygame.draw.line(surface, ROSA_NEON, (0, horizonte_y), (LARGURA_TELA, horizonte_y), 2)
    deslocamento = (tempo * 180) % 38
    for y in range(horizonte_y + 12, ALTURA_TELA + 42, 38):
        y_linha = int(y + deslocamento)
        if y_linha > ALTURA_TELA: break
        abertura = int((y_linha - horizonte_y) * 2.25)
        pygame.draw.line(surface, (45, 190, 220), (centro_x - abertura, y_linha), (centro_x + abertura, y_linha), 1)
    for i in range(-10, 11):
        x_base, x_final = centro_x + i * 58, int(centro_x + i * 122)
        pygame.draw.line(surface, (30, 140, 190), (x_base, horizonte_y), (x_final, ALTURA_TELA), 1)
    scanline = pygame.Surface((LARGURA_TELA, ALTURA_TELA), pygame.SRCALPHA)
    for y in range(0, ALTURA_TELA, 3):
        pygame.draw.line(scanline, (10, 0, 22, 18), (0, y), (LARGURA_TELA, y))
    surface.blit(scanline, (0, 0))
    vinheta = pygame.Surface((LARGURA_TELA, ALTURA_TELA), pygame.SRCALPHA)
    margem = int(min(LARGURA_TELA, ALTURA_TELA) * 0.07)
    pygame.draw.rect(vinheta, (0, 0, 0, 0), (margem, margem, LARGURA_TELA - margem * 2, ALTURA_TELA - margem * 2))
    for i in range(margem):
        alpha = int(120 * (1 - (i / max(1, margem))))
        pygame.draw.rect(vinheta, (0, 0, 0, alpha), (i, i, LARGURA_TELA - i * 2, ALTURA_TELA - i * 2), 1)
    surface.blit(vinheta, (0, 0))


def desenhar_grade_jogo(surface):
    for x in range(0, LARGURA_TELA, 40):
        pygame.draw.line(surface, (15, 20, 25), (x, 0), (x, ALTURA_TELA), 1)
    for y in range(0, ALTURA_TELA, 40):
        pygame.draw.line(surface, (15, 20, 25), (0, y), (LARGURA_TELA, y), 1)


def criar_painel_transparente(largura, altura, cor=COR_PAINEL):
    surf = pygame.Surface((largura, altura), pygame.SRCALPHA)
    pygame.draw.rect(surf, cor, (0, 0, largura, altura), border_radius=15)
    pygame.draw.rect(surf, CINZA_ESCURO, (0, 0, largura, altura), 3, border_radius=15)
    return surf


def desenhar_moldura(surface, rect, cor, titulo=None, fonte=None):
    pygame.draw.rect(surface, cor, rect, 2, border_radius=12)
    t = 20
    pygame.draw.line(surface, BRANCO, (rect.left, rect.top), (rect.left + t, rect.top), 3)
    pygame.draw.line(surface, BRANCO, (rect.left, rect.top), (rect.left, rect.top + t), 3)
    pygame.draw.line(surface, BRANCO, (rect.right, rect.bottom), (rect.right - t, rect.bottom), 3)
    pygame.draw.line(surface, BRANCO, (rect.right, rect.bottom), (rect.right, rect.bottom - t), 3)
    if titulo and fonte:
        largura_t = fonte.size(titulo)[0] + 40
        pygame.draw.rect(surface, PRETO_FUNDO, (rect.centerx - largura_t//2, rect.top - 15, largura_t, 30))
        pygame.draw.rect(surface, cor, (rect.centerx - largura_t//2, rect.top - 15, largura_t, 30), 2, border_radius=5)
        desenhar_texto(surface, titulo, fonte, BRANCO, rect.centerx, rect.top)
