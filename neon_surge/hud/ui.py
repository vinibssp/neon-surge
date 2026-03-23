import math
import time

import pygame

from ..constants import (
    ALTURA_TELA,
    BRANCO,
    CINZA_ESCURO,
    COR_PAINEL,
    LARGURA_TELA,
    PRETO_FUNDO,
    ROSA_NEON,
    VERMELHO_SANGUE,
)
from ..data import UI_COLORS, UI_ANIMATION


class Button:
    def __init__(self, x, y, largura, altura, texto, fonte, callback=None, id=None):
        self.rect = pygame.Rect(x - largura // 2, y - altura // 2, largura, altura)
        self.texto = texto
        self.fonte = fonte
        self.callback = callback
        self.id = id
        
        self.is_hovered = False
        self.is_selected = False  # Para navegação via teclado
        self.scale = 1.0
        self.target_scale = 1.0
        
    def update(self, mouse_pos, current_selected_id=None):
        # Hover via mouse
        self.is_hovered = self.rect.collidepoint(mouse_pos)
        
        # Seleção via teclado (sincronizada por ID)
        if current_selected_id is not None:
            self.is_selected = (self.id == current_selected_id)
        
        # Animação de escala
        self.target_scale = UI_ANIMATION["HOVER_SCALE"] if (self.is_hovered or self.is_selected) else 1.0
        self.scale += (self.target_scale - self.scale) * 0.2

    def draw(self, surface):
        # Cores baseadas no estado
        # Selecionado ou Hovered: Amarelo preenchido, texto escuro
        # Inativo: Outline Ciano, texto claro
        is_active = self.is_selected or self.is_hovered
        cor_base = UI_COLORS["SELECTED"] if is_active else UI_COLORS["HIGHLIGHT"]
        cor_texto = UI_COLORS["TEXT_SELECTED"] if is_active else UI_COLORS["TEXT_NORMAL"]
        
        # Rect animado
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
            # Bloco preenchido Amarelo
            pygame.draw.rect(surf_btn, (*cor_base, bg_alpha), (0, 0, draw_rect.width, draw_rect.height), border_radius=4)
            # Brilho extra se selecionado
            pulso = math.sin(time.time() * UI_ANIMATION["PULSE_SPEED"]) * 2
            pygame.draw.rect(surf_btn, BRANCO, (0, 0, draw_rect.width, draw_rect.height), 2, border_radius=4)
        else:
            # Apenas outline Ciano Neon
            pygame.draw.rect(surf_btn, (*cor_base, 255), (0, 0, draw_rect.width, draw_rect.height), 2, border_radius=4)
            # Leve preenchimento transparente para profundidade
            pygame.draw.rect(surf_btn, (*cor_base, 20), (0, 0, draw_rect.width, draw_rect.height), border_radius=4)
            
        surface.blit(surf_btn, draw_rect.topleft)

        # Texto
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
    """Mantido para compatibilidade legado, mas usa lógica similar ao Button."""
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
    """Desenha um ícone de engrenagem simplificado para configurações."""
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
        cor_com_alpha = (*cor, 15)
        pygame.draw.circle(surface, cor_com_alpha, (int(pos_x), int(pos_y)), int(raio + (i * 4)))


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

    sol_cx = centro_x
    sol_cy = int(horizonte_y * 0.66)
    sol_raio = int(min(LARGURA_TELA, ALTURA_TELA) * 0.12)

    glow_sol = pygame.Surface((LARGURA_TELA, ALTURA_TELA), pygame.SRCALPHA)
    pulso = 0.86 + 0.14 * math.sin(tempo * 1.6)
    for mult, alpha in [(2.3, 18), (1.7, 30), (1.25, 55)]:
        pygame.draw.circle(
            glow_sol,
            (255, 60, 175, int(alpha * pulso)),
            (sol_cx, sol_cy),
            int(sol_raio * mult),
        )
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
        if y_linha > ALTURA_TELA:
            break
        abertura = int((y_linha - horizonte_y) * 2.25)
        pygame.draw.line(
            surface,
            (45, 190, 220),
            (centro_x - abertura, y_linha),
            (centro_x + abertura, y_linha),
            1,
        )

    for i in range(-10, 11):
        x_base = centro_x + i * 58
        x_final = int(centro_x + i * 122)
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
    """Desenha uma moldura neon estilizada com um título opcional."""
    pygame.draw.rect(surface, cor, rect, 2, border_radius=12)
    
    # Cantos acentuados
    t = 20
    pygame.draw.line(surface, BRANCO, (rect.left, rect.top), (rect.left + t, rect.top), 3)
    pygame.draw.line(surface, BRANCO, (rect.left, rect.top), (rect.left, rect.top + t), 3)
    pygame.draw.line(surface, BRANCO, (rect.right, rect.bottom), (rect.right - t, rect.bottom), 3)
    pygame.draw.line(surface, BRANCO, (rect.right, rect.bottom), (rect.right, rect.bottom - t), 3)

    if titulo and fonte:
        # Fundo para o texto do título
        largura_t = fonte.size(titulo)[0] + 40
        pygame.draw.rect(surface, PRETO_FUNDO, (rect.centerx - largura_t//2, rect.top - 15, largura_t, 30))
        pygame.draw.rect(surface, cor, (rect.centerx - largura_t//2, rect.top - 15, largura_t, 30), 2, border_radius=5)
        desenhar_texto(surface, titulo, fonte, BRANCO, rect.centerx, rect.top)
