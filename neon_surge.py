import pygame
import sys
import random
import json
import os
import time
import math

# ==========================================
# 1. CONFIGURAÇÕES INICIAIS E RESOLUÇÃO
# ==========================================
pygame.init()
info = pygame.display.Info()

LARGURA_TELA = int(info.current_w * 0.8)
ALTURA_TELA = int(info.current_h * 0.8)
FPS = 60
ARQUIVO_RANKING = "ranking_completo.json"

# CORES
PRETO_FUNDO = (5, 5, 8) 
BRANCO = (255, 255, 255)
VERDE_NEON = (57, 255, 20)
CIANO_NEON = (0, 255, 255)
ROSA_NEON = (255, 20, 147)
LARANJA_NEON = (255, 100, 0)
AMARELO_DADO = (255, 215, 0)
VERMELHO_SANGUE = (255, 30, 30)
ROXO_NEON = (148, 0, 211) 
CINZA_ESCURO = (35, 40, 50)  
CINZA_CLARO = (200, 200, 210) 
AZUL_ESCURO = (15, 20, 30)
COR_PAINEL = (15, 20, 30, 230) 

# ==========================================
# 2. FUNÇÕES AUXILIARES DE UI E GRÁFICOS
# ==========================================
def desenhar_texto(surface, texto, fonte, cor, x, y, alinhamento="centro"):
    img_texto = fonte.render(texto, True, cor)
    rect_texto = img_texto.get_rect()
    if alinhamento == "centro": rect_texto.center = (x, y)
    elif alinhamento == "esquerda": rect_texto.midleft = (x, y) 
    elif alinhamento == "direita": rect_texto.midright = (x, y) 
    surface.blit(img_texto, rect_texto)
    return rect_texto

def desenhar_botao_dinamico(surface, texto, fonte, cor_base, cx, cy, is_hovered, largura=500, altura=55):
    texto_display = f"> {texto} <" if is_hovered else texto
    cor_texto = PRETO_FUNDO if is_hovered else cor_base
    
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
        (cx - 12, cy - 6), (cx - 4, cy - 6), (cx + 6, cy - 14),
        (cx + 6, cy + 14), (cx - 4, cy + 6), (cx - 12, cy + 6)
    ]
    pygame.draw.polygon(surface, cor, pontos_falante)
    if mutado:
        pygame.draw.line(surface, VERMELHO_SANGUE, (cx + 12, cy - 8), (cx + 24, cy + 8), 3)
        pygame.draw.line(surface, VERMELHO_SANGUE, (cx + 24, cy - 8), (cx + 12, cy + 8), 3)
    else:
        pygame.draw.arc(surface, cor, (cx - 4, cy - 8, 16, 16), -math.pi/3, math.pi/3, 2)
        pygame.draw.arc(surface, cor, (cx - 4, cy - 14, 28, 28), -math.pi/4, math.pi/4, 2)

def desenhar_brilho_neon(surface, cor, pos_x, pos_y, raio, intensidade=3):
    for i in range(intensidade, 0, -1):
        cor_com_alpha = (*cor, 15) 
        pygame.draw.circle(surface, cor_com_alpha, (int(pos_x), int(pos_y)), int(raio + (i * 4)))

def desenhar_fundo_cyberpunk(surface, tempo):
    surface.fill(PRETO_FUNDO)
    for x in range(0, LARGURA_TELA + 100, 100):
        pygame.draw.line(surface, (15, 20, 25), (x, 0), (x, ALTURA_TELA), 1)
    
    offset_y = (tempo * 50) % 100
    for y in range(-100, ALTURA_TELA + 100, 100):
        pygame.draw.line(surface, (15, 20, 25), (0, y + offset_y), (LARGURA_TELA, y + offset_y), 1)
        
    surf_fade = pygame.Surface((LARGURA_TELA, 200), pygame.SRCALPHA)
    for i in range(200):
        alpha = int(255 - (i / 200) * 255)
        pygame.draw.line(surf_fade, (*PRETO_FUNDO, alpha), (0, i), (LARGURA_TELA, i))
    surface.blit(surf_fade, (0, 0))

def desenhar_grade_jogo(surface):
    for x in range(0, LARGURA_TELA, 40):
        pygame.draw.line(surface, (15, 20, 25), (x, 0), (x, ALTURA_TELA), 1)
    for y in range(0, ALTURA_TELA, 40):
        pygame.draw.line(surface, (15, 20, 25), (0, y), (LARGURA_TELA, y), 1)

def criar_painel_transparente(largura, altura):
    surf = pygame.Surface((largura, altura), pygame.SRCALPHA)
    pygame.draw.rect(surf, COR_PAINEL, (0, 0, largura, altura), border_radius=15)
    pygame.draw.rect(surf, CINZA_ESCURO, (0, 0, largura, altura), 3, border_radius=15)
    return surf

# ==========================================
# 3. ENTIDADES DO JOGO
# ==========================================
class ParticulaMenu:
    def __init__(self):
        self.pos = pygame.math.Vector2(random.uniform(0, LARGURA_TELA), random.uniform(0, ALTURA_TELA))
        self.vel = pygame.math.Vector2(random.uniform(-0.5, 0.5), random.uniform(-1.5, -0.5))
        self.cor = random.choice([CIANO_NEON, ROSA_NEON, VERDE_NEON, AZUL_ESCURO])
        self.tamanho = random.uniform(1, 3)

    def update(self):
        self.pos += self.vel
        if self.pos.y < -10:
            self.pos.y = ALTURA_TELA + 10
            self.pos.x = random.uniform(0, LARGURA_TELA)

    def draw(self, surface):
        pygame.draw.circle(surface, self.cor, (int(self.pos.x), int(self.pos.y)), int(self.tamanho))

class Particula:
    def __init__(self, x, y, cor):
        self.pos = pygame.math.Vector2(x, y)
        self.vel = pygame.math.Vector2(random.uniform(-3, 3), random.uniform(-3, 3))
        self.raio = random.uniform(4, 7)
        self.cor = cor

    def update(self):
        self.pos += self.vel
        self.raio -= 0.3 

    def draw(self, surface):
        if self.raio > 0:
            desenhar_brilho_neon(surface, self.cor, self.pos.x, self.pos.y, self.raio, intensidade=2)
            pygame.draw.circle(surface, BRANCO, (int(self.pos.x), int(self.pos.y)), int(self.raio // 2))

class Player:
    def __init__(self, x, y):
        self.pos = pygame.math.Vector2(x, y)
        self.vel = pygame.math.Vector2(0, 0)
        self.aceleracao = 1.8
        self.atrito = 0.82
        self.tamanho = 16
        self.dash_cooldown = 0
        self.dash_timer = 0
        self.invencivel = False

    def update(self, teclas, lista_particulas):
        dir_x, dir_y = 0, 0
        if teclas[pygame.K_w] or teclas[pygame.K_UP]: dir_y = -1
        if teclas[pygame.K_s] or teclas[pygame.K_DOWN]: dir_y = 1
        if teclas[pygame.K_a] or teclas[pygame.K_LEFT]: dir_x = -1
        if teclas[pygame.K_d] or teclas[pygame.K_RIGHT]: dir_x = 1

        if dir_x != 0 or dir_y != 0:
            move_vec = pygame.math.Vector2(dir_x, dir_y).normalize()
            self.vel += move_vec * self.aceleracao

        if teclas[pygame.K_SPACE] and self.dash_cooldown <= 0 and self.vel.length() > 0:
            self.vel = self.vel.normalize() * 25
            self.dash_timer = 10
            self.dash_cooldown = 45
            return True

        if self.dash_timer > 0:
            self.dash_timer -= 1
            self.invencivel = True
            for _ in range(3): lista_particulas.append(Particula(self.pos.x, self.pos.y, CIANO_NEON))
        else:
            self.invencivel = False
            
        if self.dash_cooldown > 0: self.dash_cooldown -= 1

        self.vel *= self.atrito
        self.pos += self.vel
        self.pos.x = max(self.tamanho, min(LARGURA_TELA - self.tamanho, self.pos.x))
        self.pos.y = max(60 + self.tamanho, min(ALTURA_TELA - self.tamanho, self.pos.y))
        return False

    def draw(self, surface):
        cor = BRANCO if self.invencivel else CIANO_NEON
        desenhar_brilho_neon(surface, cor, self.pos.x, self.pos.y, self.tamanho // 2, intensidade=4)
        
        rect = pygame.Rect(0, 0, self.tamanho, self.tamanho)
        rect.center = (int(self.pos.x), int(self.pos.y))
        pygame.draw.rect(surface, cor, rect, border_radius=4)
        pygame.draw.rect(surface, BRANCO, rect.inflate(-6, -6), border_radius=2)
        
        raio_anel = 16 
        rect_anel = pygame.Rect(0, 0, raio_anel * 2, raio_anel * 2)
        rect_anel.center = (int(self.pos.x), int(self.pos.y))
        espessura = 5 
        
        if self.dash_cooldown > 0:
            ratio = 1.0 - (self.dash_cooldown / 45.0)
            angulo_inicio = -math.pi / 2
            angulo_fim = angulo_inicio + (math.pi * 2 * ratio)
            pygame.draw.arc(surface, cor, rect_anel, angulo_inicio, angulo_fim, espessura)
        else:
            pygame.draw.circle(surface, cor, rect_anel.center, raio_anel, espessura)

class Inimigo:
    def __init__(self, x, y, tipo, velocidade):
        self.pos = pygame.math.Vector2(x, y)
        self.tipo = tipo
        self.raio = 12
        self.vel = velocidade
        self.dir = pygame.math.Vector2(0, 0)
        self.morto = False
        self.variante = 1 # Para o Boss
        
        self.estado_investida = "ESPERANDO" 
        self.timer_investida = 0.0
        self.alvo_mira = pygame.math.Vector2(x, y) 
        self.travado = False 
        
        self.timer_explosao = 0.0 
        self.explodiu = False
        
        if self.tipo == "boss":
            self.raio = 40
            self.timer_habilidade = 0.0
            self.estado_boss = "PERSEGUINDO"

        if self.tipo == "quique":
            ang = random.uniform(0, math.pi * 2)
            self.dir = pygame.math.Vector2(math.cos(ang), math.sin(ang)) * self.vel

    def update(self, player, lista_inimigos, dt, lista_particulas, interface_principal):
        if self.tipo == "perseguidor":
            pos_futura = player.pos + (player.vel * 12)
            vec_to_player = pos_futura - self.pos
            if vec_to_player.length() > 0:
                direcao_desejada = vec_to_player.normalize() * (self.vel * 0.9)
                onda = math.sin(time.time() * 6) * 40
                direcao_desejada = direcao_desejada.rotate(onda)
                self.dir = self.dir.lerp(direcao_desejada, 0.08) 

        elif self.tipo == "investida":
            self.timer_investida += dt
            if self.estado_investida == "ESPERANDO":
                self.dir = self.dir.lerp(pygame.math.Vector2(0, 0), 0.1) 
                self.travado = False
                if self.timer_investida > 1.2: 
                    self.estado_investida = "MIRANDO"
                    self.timer_investida = 0.0
            
            elif self.estado_investida == "MIRANDO":
                if self.timer_investida < 0.5:
                    self.alvo_mira = pygame.math.Vector2(player.pos.x, player.pos.y) 
                else:
                    self.travado = True 

                if self.timer_investida > 0.9: 
                    vec = self.alvo_mira - self.pos
                    if vec.length() > 0:
                        self.dir = vec.normalize() * (self.vel * 4.0) 
                    self.estado_investida = "ATACANDO"
                    self.timer_investida = 0.0
            
            elif self.estado_investida == "ATACANDO":
                lista_particulas.append(Particula(self.pos.x, self.pos.y, LARANJA_NEON))
                if self.timer_investida > 0.8: 
                    self.morto = True
                    for _ in range(15): lista_particulas.append(Particula(self.pos.x, self.pos.y, LARANJA_NEON))

        elif self.tipo == "explosivo":
            self.timer_explosao += dt
            if self.timer_explosao < 3.5:
                vec_to_player = player.pos - self.pos
                if vec_to_player.length() > 0:
                    self.dir = self.dir.lerp(vec_to_player.normalize() * (self.vel * 0.6), 0.05)
            else:
                self.dir = self.dir * 0.9 
                if self.timer_explosao > 4.5:
                    self.morto = True
                    self.explodiu = True
                    for _ in range(40): lista_particulas.append(Particula(self.pos.x, self.pos.y, AMARELO_DADO))
                    
        elif self.tipo == "boss":
            self.timer_habilidade += dt
            
            if self.estado_boss == "PERSEGUINDO":
                vec_to_player = player.pos - self.pos
                if vec_to_player.length() > 0:
                    self.dir = self.dir.lerp(vec_to_player.normalize() * self.vel, 0.03)
                
                if self.timer_habilidade > 3.0:
                    self.estado_boss = "INVOCANDO"
                    self.timer_habilidade = 0.0
                    
            elif self.estado_boss == "INVOCANDO":
                self.dir *= 0.9 
                
                if self.timer_habilidade > 1.0:
                    # Invocação muda de acordo com a variante do boss (A cada 10 fases)
                    if self.variante % 3 == 1:
                        interface_principal.portais_inimigos.append({"pos": pygame.math.Vector2(self.pos.x, self.pos.y), "tipo": "explosivo", "vel": 3.5, "tempo": 1.5})
                        interface_principal.portais_inimigos.append({"pos": pygame.math.Vector2(self.pos.x, self.pos.y), "tipo": "perseguidor", "vel": 4.5, "tempo": 1.5})
                    elif self.variante % 3 == 2:
                        interface_principal.portais_inimigos.append({"pos": pygame.math.Vector2(self.pos.x, self.pos.y), "tipo": "investida", "vel": 6.0, "tempo": 1.5})
                        interface_principal.portais_inimigos.append({"pos": pygame.math.Vector2(self.pos.x, self.pos.y), "tipo": "investida", "vel": 6.0, "tempo": 1.5})
                    else:
                        interface_principal.portais_inimigos.append({"pos": pygame.math.Vector2(self.pos.x, self.pos.y), "tipo": "quique", "vel": 7.0, "tempo": 1.5})
                        interface_principal.portais_inimigos.append({"pos": pygame.math.Vector2(self.pos.x, self.pos.y), "tipo": "quique", "vel": 7.0, "tempo": 1.5})
                    
                    for _ in range(30): lista_particulas.append(Particula(self.pos.x, self.pos.y, BRANCO))
                    self.estado_boss = "DASH"
                    self.timer_habilidade = 0.0
                    
            elif self.estado_boss == "DASH":
                if self.timer_habilidade < 0.6:
                    self.dir *= 0.8 
                elif self.timer_habilidade < 1.2:
                    if self.timer_habilidade - dt < 0.6: 
                        vec_to_player = player.pos - self.pos
                        if vec_to_player.length() > 0:
                            self.dir = vec_to_player.normalize() * (self.vel * 5.0) 
                        for _ in range(25): lista_particulas.append(Particula(self.pos.x, self.pos.y, VERMELHO_SANGUE))
                else:
                    self.estado_boss = "PERSEGUINDO"
                    self.timer_habilidade = 0.0

        forca_repulsao = pygame.math.Vector2(0, 0)
        for vizinho in lista_inimigos:
            if vizinho != self:
                distancia = self.pos.distance_to(vizinho.pos)
                distancia_segura = self.raio + vizinho.raio + 5
                if 0 < distancia < distancia_segura:
                    if self.tipo == "quique":
                        normal = (self.pos - vizinho.pos).normalize()
                        if self.dir.length() > 0:
                            self.dir = self.dir.reflect(normal)
                        self.pos += normal * 3 
                    else:
                        diferenca = self.pos - vizinho.pos
                        forca_repulsao += diferenca.normalize() * (distancia_segura - distancia) * 0.1
        
        self.pos += self.dir + forca_repulsao

        # Tratamento das Paredes
        if self.pos.x <= self.raio:
            self.pos.x = self.raio
            if self.tipo in ["quique", "explosivo", "boss"]: self.dir.x *= -1
            elif self.tipo == "investida":
                self.dir.x = 0
                if self.estado_investida == "ATACANDO":
                    self.estado_investida = "ESPERANDO"
                    self.timer_investida = 0.0
        elif self.pos.x >= LARGURA_TELA - self.raio:
            self.pos.x = LARGURA_TELA - self.raio
            if self.tipo in ["quique", "explosivo", "boss"]: self.dir.x *= -1
            elif self.tipo == "investida":
                self.dir.x = 0
                if self.estado_investida == "ATACANDO":
                    self.estado_investida = "ESPERANDO"
                    self.timer_investida = 0.0
            
        if self.pos.y <= 60 + self.raio:
            self.pos.y = 60 + self.raio
            if self.tipo in ["quique", "explosivo", "boss"]: self.dir.y *= -1
            elif self.tipo == "investida":
                self.dir.y = 0
                if self.estado_investida == "ATACANDO":
                    self.estado_investida = "ESPERANDO"
                    self.timer_investida = 0.0
        elif self.pos.y >= ALTURA_TELA - self.raio:
            self.pos.y = ALTURA_TELA - self.raio
            if self.tipo in ["quique", "explosivo", "boss"]: self.dir.y *= -1
            elif self.tipo == "investida":
                self.dir.y = 0
                if self.estado_investida == "ATACANDO":
                    self.estado_investida = "ESPERANDO"
                    self.timer_investida = 0.0

    def draw(self, surface):
        cor_base = ROSA_NEON
        if self.tipo == "perseguidor": cor_base = VERMELHO_SANGUE
        elif self.tipo == "investida": cor_base = LARANJA_NEON
        elif self.tipo == "explosivo": cor_base = AMARELO_DADO
        
        if self.tipo == "investida" and self.estado_investida == "MIRANDO":
            cor_linha = VERMELHO_SANGUE if not self.travado else BRANCO
            espessura = 2 if not self.travado else 4
            pygame.draw.line(surface, cor_linha, self.pos, self.alvo_mira, espessura)
            if self.travado: cor_base = BRANCO

        if self.tipo == "explosivo":
            if self.timer_explosao > 2.5:
                if int(self.timer_explosao * 15) % 2 == 0:
                    cor_base = BRANCO
            desenhar_brilho_neon(surface, cor_base, self.pos.x, self.pos.y, self.raio, intensidade=4)
            pygame.draw.circle(surface, cor_base, (int(self.pos.x), int(self.pos.y)), self.raio)
            pygame.draw.circle(surface, BRANCO, (int(self.pos.x), int(self.pos.y)), self.raio // 3)
            if self.timer_explosao > 3.5:
                raio_indicador = min(80, (self.timer_explosao - 3.5) * 80)
                pygame.draw.circle(surface, VERMELHO_SANGUE, (int(self.pos.x), int(self.pos.y)), int(raio_indicador), max(1, int((4.5 - self.timer_explosao)*5)))
                
        elif self.tipo == "boss":
            # Cor do boss varia com a fase
            cor_boss = ROXO_NEON if self.variante % 3 == 1 else (CIANO_NEON if self.variante % 3 == 2 else ROSA_NEON)
            tempo = time.time()
            
            for i in range(3):
                angulo = tempo * 4 + (i * math.pi * 2 / 3)
                distancia_orbe = self.raio + 35 if self.estado_boss == "DASH" else self.raio + 15
                x_orb = self.pos.x + math.cos(angulo) * distancia_orbe
                y_orb = self.pos.y + math.sin(angulo) * distancia_orbe
                
                pygame.draw.line(surface, cor_boss, self.pos, (x_orb, y_orb), 2)
                pygame.draw.circle(surface, VERMELHO_SANGUE, (int(x_orb), int(y_orb)), 8)
                desenhar_brilho_neon(surface, VERMELHO_SANGUE, x_orb, y_orb, 8, 2)
                pygame.draw.circle(surface, BRANCO, (int(x_orb), int(y_orb)), 3)

            if self.estado_boss == "DASH": cor_atual = VERMELHO_SANGUE
            elif self.estado_boss == "INVOCANDO": cor_atual = BRANCO
            else: cor_atual = cor_boss
            
            desenhar_brilho_neon(surface, cor_atual, self.pos.x, self.pos.y, self.raio, intensidade=5)
            pygame.draw.circle(surface, cor_atual, (int(self.pos.x), int(self.pos.y)), self.raio)
            pygame.draw.circle(surface, PRETO_FUNDO, (int(self.pos.x), int(self.pos.y)), self.raio - 6)
            
            pulso = abs(math.sin(tempo * 10)) * (self.raio // 1.5)
            pygame.draw.circle(surface, VERMELHO_SANGUE, (int(self.pos.x), int(self.pos.y)), int(pulso))
            
        else:
            desenhar_brilho_neon(surface, cor_base, self.pos.x, self.pos.y, self.raio, intensidade=3)
            pygame.draw.circle(surface, cor_base, (int(self.pos.x), int(self.pos.y)), self.raio)
            pygame.draw.circle(surface, BRANCO, (int(self.pos.x), int(self.pos.y)), self.raio // 3)

# ==========================================
# 4. MÁQUINA DE ESTADOS E LÓGICA
# ==========================================
class NeonSurge:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        
        self.volume_musica = 0.4 
        self.volume_salvo = 0.4 
        self.mutado = False
        
        try:
            pygame.mixer.music.load("trilha.mp3")
            pygame.mixer.music.set_volume(self.volume_musica)
            pygame.mixer.music.play(-1) 
        except pygame.error:
            pass
            
        self.rect_vol_mute = pygame.Rect(0, 0, 45, 45) 
        self.rect_vol_menos = pygame.Rect(0, 0, 35, 35)
        self.rect_vol_mais = pygame.Rect(0, 0, 35, 35)
        
        self.info = pygame.display.Info()
        self.is_fullscreen = False
        self.tela_real = pygame.display.set_mode((LARGURA_TELA, ALTURA_TELA))
        self.tela = pygame.Surface((LARGURA_TELA, ALTURA_TELA))
        pygame.display.set_caption("Neon Surge - Hardcore Edition")

        self.clock = pygame.time.Clock()
        self.dt = 0.0 
        
        self.crt_overlay = pygame.Surface((LARGURA_TELA, ALTURA_TELA), pygame.SRCALPHA)
        for y in range(0, ALTURA_TELA, 3): 
            pygame.draw.line(self.crt_overlay, (0, 0, 0, 40), (0, y), (LARGURA_TELA, y))

        font_name = "Consolas" if pygame.font.match_font("Consolas") else None
        self.fonte_titulo = pygame.font.SysFont("Impact", 75)
        self.fonte_sub = pygame.font.SysFont(font_name, 26, bold=True)
        self.fonte_texto = pygame.font.SysFont(font_name, 22)
        self.fonte_desc = pygame.font.SysFont(font_name, 19) 
        
        self.estado = "INPUT_NOME"
        self.nome_jogador = ""
        self.modo_jogo = "" 
        self.fase_atual = 1
        self.veio_do_game_over = False  
        
        self.botao_selecionado = -1 
        self.botoes_hitboxes = []  
        
        self.player = None
        self.inimigos = []
        self.portais_inimigos = [] 
        self.coletaveis = []
        self.particulas = []
        self.particulas_menu = [ParticulaMenu() for _ in range(50)]
        self.portal_aberto = False
        
        self.tempo_corrida = 0.0
        self.tempo_sobrevivencia = 0.0
        self.temporizador_spawn = 0.0
        self.shake_frames = 0
        self.tempo_global = 0 
        
        self.tempo_para_lava = 30.0
        self.lava_ativa = False
        self.tempo_lava_restante = 0.0
        self.tipo_lava = 0
        self.lava_hitboxes = []
        self.aviso_lava = 0.0
        
        self.ranking = self.carregar_ranking()
        self.ultima_pos_mouse = (0, 0)
        self.ultima_posicao = 0  
        self.ultimo_tempo = 0.0  

    def alternar_tela_cheia(self):
        self.is_fullscreen = not self.is_fullscreen
        if self.is_fullscreen: 
            self.tela_real = pygame.display.set_mode((self.info.current_w, self.info.current_h), pygame.FULLSCREEN)
        else: 
            self.tela_real = pygame.display.set_mode((LARGURA_TELA, ALTURA_TELA))

    def obter_posicao_mouse(self):
        mx, my = pygame.mouse.get_pos()
        if self.is_fullscreen:
            mx = mx / (self.info.current_w / LARGURA_TELA)
            my = my / (self.info.current_h / ALTURA_TELA)
        return mx, my
        
    def alterar_volume(self, delta):
        if self.mutado: self.alternar_mute()
        self.volume_musica = max(0.0, min(1.0, self.volume_musica + delta))
        try: pygame.mixer.music.set_volume(self.volume_musica)
        except: pass

    def alternar_mute(self):
        self.mutado = not self.mutado
        try:
            if self.mutado:
                self.volume_salvo = self.volume_musica
                self.volume_musica = 0.0
            else:
                self.volume_musica = self.volume_salvo
                if self.volume_musica == 0.0: self.volume_musica = 0.4 
            pygame.mixer.music.set_volume(self.volume_musica)
        except: pass

    def carregar_ranking(self):
        if os.path.exists(ARQUIVO_RANKING):
            with open(ARQUIVO_RANKING, 'r') as f: 
                dados = json.load(f)
                if "Hardcore" not in dados: dados["Hardcore"] = []
                if "Corrida_Hardcore" not in dados: dados["Corrida_Hardcore"] = []
                if "Corrida_Infinita" not in dados: dados["Corrida_Infinita"] = []
                return dados
        return {"Corrida": [], "Corrida_Hardcore": [], "Sobrevivencia": [], "Hardcore": [], "Corrida_Infinita": []}

    def salvar_ranking(self, modo, valor):
        if modo == "CORRIDA": chave_modo = "Corrida"
        elif modo == "CORRIDA_HARDCORE": chave_modo = "Corrida_Hardcore"
        elif modo == "SOBREVIVENCIA": chave_modo = "Sobrevivencia"
        elif modo == "CORRIDA_INFINITA": chave_modo = "Corrida_Infinita"
        else: chave_modo = "Hardcore"
        
        if chave_modo == "Corrida_Infinita":
            novo_registro = {"nome": self.nome_jogador, "fase": int(valor), "id": time.time()}
            self.ranking[chave_modo].append(novo_registro)
            self.ranking[chave_modo] = sorted(self.ranking[chave_modo], key=lambda x: x["fase"], reverse=True)
            self.ultima_posicao = self.ranking[chave_modo].index(novo_registro) + 1
            self.ultimo_tempo = float(valor)
        else:
            tempo_str = f"{valor:.1f}"
            novo_registro = {"nome": self.nome_jogador, "tempo": float(tempo_str), "id": time.time()}
            self.ranking[chave_modo].append(novo_registro)
            if chave_modo in ["Corrida", "Corrida_Hardcore"]: 
                self.ranking[chave_modo] = sorted(self.ranking[chave_modo], key=lambda x: x["tempo"])
            else: 
                self.ranking[chave_modo] = sorted(self.ranking[chave_modo], key=lambda x: x["tempo"], reverse=True)
            self.ultima_posicao = self.ranking[chave_modo].index(novo_registro) + 1
            self.ultimo_tempo = float(tempo_str)
        
        self.ranking[chave_modo] = self.ranking[chave_modo][:50]
        with open(ARQUIVO_RANKING, 'w') as f: json.dump(self.ranking, f, indent=4)

    def entrar_menu_modo(self):
        self.estado = "MENU_MODO"
        self.player = Player(LARGURA_TELA // 2, ALTURA_TELA // 2 + 150)
        self.particulas.clear()
        self.botao_selecionado = -1

    def obter_pads_menu(self):
        cx, cy = LARGURA_TELA // 2, ALTURA_TELA // 2
        dx = min(350, LARGURA_TELA * 0.3)
        dy = min(180, ALTURA_TELA * 0.22)
        return [
            {"id": 0, "modo": "CORRIDA", "texto": "CORRIDA 10 FASES", "pos": (cx - dx, cy - dy), "cor": CIANO_NEON},
            {"id": 5, "modo": "CORRIDA_INFINITA", "texto": "CORRIDA INFINITA", "pos": (cx, cy - dy), "cor": ROXO_NEON},
            {"id": 1, "modo": "CORRIDA_HARDCORE", "texto": "CORRIDA HARDCORE", "pos": (cx + dx, cy - dy), "cor": VERMELHO_SANGUE},
            {"id": 2, "modo": "SOBREVIVENCIA", "texto": "SOBREVIVÊNCIA", "pos": (cx - dx, cy + dy), "cor": ROSA_NEON},
            {"id": 4, "modo": "INFO", "texto": "TUTORIAL / INFO", "pos": (cx, cy + dy), "cor": AMARELO_DADO},
            {"id": 3, "modo": "HARDCORE", "texto": "SOBREV. HARDCORE", "pos": (cx + dx, cy + dy), "cor": LARANJA_NEON}
        ]

    def iniciar_fase(self):
        self.player = Player(LARGURA_TELA // 2, ALTURA_TELA // 2)
        self.inimigos.clear()
        self.portais_inimigos.clear()
        self.coletaveis.clear()
        self.particulas.clear() 
        self.portal_aberto = False
        
        self.tempo_para_lava = 30.0
        self.lava_ativa = False
        self.tempo_lava_restante = 0.0
        self.tipo_lava = 0
        self.lava_hitboxes = []
        self.aviso_lava = 0.0
        
        if self.fase_atual == 1:
            self.tempo_corrida = 0.0
            self.tempo_sobrevivencia = 0.0
            self.temporizador_spawn = 0.0
        
        if self.modo_jogo in ["CORRIDA", "CORRIDA_HARDCORE", "CORRIDA_INFINITA"]:
            eh_fase_boss = (self.modo_jogo in ["CORRIDA", "CORRIDA_HARDCORE"] and self.fase_atual == 10) or \
                           (self.modo_jogo == "CORRIDA_INFINITA" and self.fase_atual > 0 and self.fase_atual % 10 == 0)

            if eh_fase_boss:
                for _ in range(8):
                    x = random.randint(50, LARGURA_TELA - 50)
                    y = random.randint(110, ALTURA_TELA - 50)
                    self.coletaveis.append(pygame.math.Vector2(x, y))
                
                ex, ey = LARGURA_TELA // 2, 120
                while abs(ex - self.player.pos.x) < 300 and abs(ey - self.player.pos.y) < 300:
                    ex = random.randint(50, LARGURA_TELA - 50)
                    ey = random.randint(110, ALTURA_TELA - 50)
                
                variante_boss = (self.fase_atual // 10) if self.modo_jogo == "CORRIDA_INFINITA" else 1
                self.portais_inimigos.append({"pos": pygame.math.Vector2(ex, ey), "tipo": "boss", "vel": 4.0 + (variante_boss * 0.2), "tempo": 2.0, "variante": variante_boss})
                self._spawn_inimigos(3 + variante_boss, 4.5 + (variante_boss * 0.3)) 
                
            else:
                for _ in range(5):
                    x = random.randint(50, LARGURA_TELA - 50)
                    y = random.randint(110, ALTURA_TELA - 50)
                    self.coletaveis.append(pygame.math.Vector2(x, y))

                limite_inimigos = 3 + min(self.fase_atual, 20)
                vel_inimigo = 4 + min((self.fase_atual * 0.25), 8.0)
                self._spawn_inimigos(limite_inimigos, vel_inimigo)
            
        elif self.modo_jogo == "SOBREVIVENCIA":
            self._spawn_inimigos(2, 4)
            
        elif self.modo_jogo == "HARDCORE":
            self._spawn_inimigos(4, 6)

        self.estado = "JOGANDO"

    def _spawn_inimigos(self, quantidade, velocidade):
        for _ in range(quantidade):
            tipo = random.choice(["quique", "perseguidor", "investida", "explosivo"])
            ex, ey = self.player.pos.x, self.player.pos.y
            while abs(ex - self.player.pos.x) < 300 and abs(ey - self.player.pos.y) < 300:
                ex = random.randint(50, LARGURA_TELA - 50)
                ey = random.randint(110, ALTURA_TELA - 50)
            
            self.portais_inimigos.append({
                "pos": pygame.math.Vector2(ex, ey),
                "tipo": tipo,
                "vel": velocidade,
                "tempo": 1.5
            })

    def atualizar_jogo(self):
        teclas = pygame.key.get_pressed()
        if self.player.update(teclas, self.particulas): self.shake_frames = 6

        for p in self.particulas[:]:
            p.update()
            if p.raio <= 0: self.particulas.remove(p)

        for p in self.portais_inimigos[:]:
            p["tempo"] -= self.dt
            if p["tempo"] <= 0:
                inimigo = Inimigo(p["pos"].x, p["pos"].y, p["tipo"], p["vel"])
                if "variante" in p:
                    inimigo.variante = p["variante"]
                if inimigo.tipo == "boss":
                    inimigo.raio = 40 + (inimigo.variante * 5)
                self.inimigos.append(inimigo)
                self.portais_inimigos.remove(p)
                self.shake_frames = 3
                for _ in range(15): self.particulas.append(Particula(p["pos"].x, p["pos"].y, VERMELHO_SANGUE))

        inimigos_atuais = self.inimigos.copy()
        novos_inimigos = []
        for ini in self.inimigos:
            ini.update(self.player, self.inimigos, self.dt, self.particulas, self)
            
            if ini.morto:
                if getattr(ini, 'explodiu', False):
                    self.shake_frames = 15
                    if not self.player.invencivel and ini.pos.distance_to(self.player.pos) < 80:
                        self._lidar_com_morte()
                        return
                continue 
                
            dist = ini.pos.distance_to(self.player.pos)
            if not self.player.invencivel and dist < (ini.raio + self.player.tamanho//2 - 2):
                self._lidar_com_morte()
                return
                
            novos_inimigos.append(ini)
            
        for ini in self.inimigos:
            if ini not in inimigos_atuais:
                novos_inimigos.append(ini)
                
        self.inimigos = novos_inimigos

        if self.modo_jogo in ["CORRIDA", "CORRIDA_HARDCORE", "CORRIDA_INFINITA"]:
            self.tempo_corrida += self.dt
            for d in self.coletaveis[:]:
                if self.player.pos.distance_to(d) < 20:
                    self.coletaveis.remove(d)
                    self.shake_frames = 2 
                    for _ in range(10): self.particulas.append(Particula(d.x, d.y, AMARELO_DADO))
            
            if len(self.coletaveis) == 0 and not self.portal_aberto:
                self.portal_aberto = True
                
                margem_x, margem_y = 100, 100
                px = random.randint(margem_x, LARGURA_TELA - margem_x)
                py = random.randint(margem_y + 60, ALTURA_TELA - margem_y)
                
                self.portal_pos = pygame.math.Vector2(px, py)
                self.shake_frames = 10

            if self.portal_aberto and self.player.pos.distance_to(self.portal_pos) < 30:
                if self.modo_jogo == "CORRIDA_INFINITA":
                    self.fase_atual += 1
                    self.iniciar_fase()
                elif self.fase_atual < 10:
                    self.fase_atual += 1
                    self.iniciar_fase() 
                else:
                    self.salvar_ranking(self.modo_jogo, self.tempo_corrida)
                    self.estado = "RANKING"
                    self.botao_selecionado = -1
                    
        elif self.modo_jogo in ["SOBREVIVENCIA", "HARDCORE"]:
            self.tempo_sobrevivencia += self.dt
            self.temporizador_spawn += self.dt
            
            if not self.lava_ativa:
                self.tempo_para_lava -= self.dt
                if self.tempo_para_lava <= 3.0:
                    if self.tipo_lava == 0:
                        self.tipo_lava = random.randint(1, 3)
                    self.aviso_lava = self.tempo_para_lava
                if self.tempo_para_lava <= 0.0:
                    self.lava_ativa = True
                    self.tempo_lava_restante = 10.0
                    self.aviso_lava = 0.0
                    self.shake_frames = 15
            else:
                self.tempo_lava_restante -= self.dt
                if self.tempo_lava_restante <= 0.0:
                    self.lava_ativa = False
                    self.tempo_para_lava = 30.0
                    self.tipo_lava = 0
                    self.lava_hitboxes = []
                    
            self.lava_hitboxes = []
            if self.tipo_lava != 0:
                tempo_simulado = self.tempo_lava_restante if self.lava_ativa else 10.0
                if self.tipo_lava == 1: 
                    margem = 180
                    self.lava_hitboxes.append(pygame.Rect(0, 60, LARGURA_TELA, margem))
                    self.lava_hitboxes.append(pygame.Rect(0, ALTURA_TELA - margem, LARGURA_TELA, margem))
                    self.lava_hitboxes.append(pygame.Rect(0, 60, margem, ALTURA_TELA))
                    self.lava_hitboxes.append(pygame.Rect(LARGURA_TELA - margem, 60, margem, ALTURA_TELA))
                elif self.tipo_lava == 2: 
                    cx, cy = LARGURA_TELA // 2, (ALTURA_TELA + 60) // 2
                    w, h = 500, 350
                    self.lava_hitboxes.append(pygame.Rect(cx - w//2, cy - h//2, w, h))
                elif self.tipo_lava == 3: 
                    desloc_y = (10.0 - tempo_simulado) * 150 
                    largura_p = 250
                    p_y = (desloc_y % (ALTURA_TELA + largura_p)) - largura_p
                    self.lava_hitboxes.append(pygame.Rect(0, p_y, LARGURA_TELA, largura_p))
                    
                    desloc_x = ((10.0 - tempo_simulado) * 200)
                    p_x = (desloc_x % (LARGURA_TELA + largura_p)) - largura_p
                    self.lava_hitboxes.append(pygame.Rect(p_x, 60, largura_p, ALTURA_TELA))

            if self.lava_ativa and not self.player.invencivel:
                p_rect = pygame.Rect(self.player.pos.x - self.player.tamanho//2, self.player.pos.y - self.player.tamanho//2, self.player.tamanho, self.player.tamanho)
                for r in self.lava_hitboxes:
                    if r.colliderect(p_rect):
                        self._lidar_com_morte()
                        return

            limite_spawn = 3.0 if self.modo_jogo == "SOBREVIVENCIA" else 1.5
            taxa_vel = 0.05 if self.modo_jogo == "SOBREVIVENCIA" else 0.1
            vel_base = 4 if self.modo_jogo == "SOBREVIVENCIA" else 6
            vel_max = 8 if self.modo_jogo == "SOBREVIVENCIA" else 12
            
            if self.temporizador_spawn > limite_spawn:
                vel_progressiva = min(vel_max, vel_base + (self.tempo_sobrevivencia * taxa_vel)) 
                self._spawn_inimigos(1, vel_progressiva)
                self.temporizador_spawn = 0.0 
                self.shake_frames = 3 

    def atualizar_menu_interativo(self):
        teclas = pygame.key.get_pressed()
        self.player.update(teclas, self.particulas)
        
        for p in self.particulas[:]:
            p.update()
            if p.raio <= 0: self.particulas.remove(p)
            
        pads = self.obter_pads_menu()
        self.botao_selecionado = -1
        dist_min = 180 
        
        for pad in pads:
            pad_vec = pygame.math.Vector2(pad["pos"])
            dist = self.player.pos.distance_to(pad_vec)
            
            # Física de repulsão leve
            raio_colisao = 55
            if dist < raio_colisao + self.player.tamanho:
                if self.player.dash_timer > 0:
                    self.shake_frames = 20
                    for _ in range(50): self.particulas.append(Particula(pad["pos"][0], pad["pos"][1], pad["cor"]))
                    self.botao_selecionado = pad["id"]
                    self.acionar_botao()
                    return
                elif dist > 0:
                    normal = (self.player.pos - pad_vec).normalize()
                    self.player.vel += normal * 2 

            # Seleciona automaticamente o pad mais próximo para possibilitar o uso do Enter
            if dist < dist_min:
                dist_min = dist
                self.botao_selecionado = pad["id"]

    def _lidar_com_morte(self):
        self.shake_frames = 15
        if self.modo_jogo == "CORRIDA": 
            self.iniciar_fase() 
        elif self.modo_jogo == "CORRIDA_HARDCORE":
            self.salvar_ranking(self.modo_jogo, self.tempo_corrida)
            self.estado = "RANKING"
            self.botao_selecionado = -1
        elif self.modo_jogo == "CORRIDA_INFINITA":
            self.salvar_ranking(self.modo_jogo, self.fase_atual)
            self.estado = "RANKING"
            self.botao_selecionado = -1
        elif self.modo_jogo in ["SOBREVIVENCIA", "HARDCORE"]:
            self.salvar_ranking(self.modo_jogo, self.tempo_sobrevivencia)
            self.estado = "RANKING"
            self.botao_selecionado = -1

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
        desenhar_texto(self.tela, "-", self.fonte_sub, BRANCO, self.rect_vol_menos.centerx, self.rect_vol_menos.centery, alinhamento="centro")
        
        hover_mais = self.rect_vol_mais.collidepoint(mx, my)
        pygame.draw.rect(self.tela, CINZA_ESCURO if hover_mais else (10, 15, 25), self.rect_vol_mais, border_radius=6)
        pygame.draw.rect(self.tela, CIANO_NEON if hover_mais else CINZA_ESCURO, self.rect_vol_mais, 2, border_radius=6)
        desenhar_texto(self.tela, "+", self.fonte_sub, BRANCO, self.rect_vol_mais.centerx, self.rect_vol_mais.centery, alinhamento="centro")

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
            
            btn_rect = desenhar_botao_dinamico(self.tela, "CONFIRMAR DADOS", self.fonte_sub, VERDE_NEON, cx, cy + 150, self.botao_selecionado == 0)
            self.botoes_hitboxes.append(btn_rect)

        elif self.estado == "PERGUNTA_MODO":
            desenhar_texto(self.tela, "NOVO PILOTO REGISTRADO", self.fonte_titulo, VERDE_NEON, cx, cy - 100)
            modo_formatado = self.modo_jogo.replace('_', ' ')
            btn_manter_modo = desenhar_botao_dinamico(self.tela, f"CONTINUAR EM: {modo_formatado}", self.fonte_sub, CIANO_NEON, cx, cy + 30, self.botao_selecionado == 0)
            btn_mudar_modo = desenhar_botao_dinamico(self.tela, "ESCOLHER NOVO MODO", self.fonte_sub, ROSA_NEON, cx, cy + 110, self.botao_selecionado == 1)
            self.botoes_hitboxes.extend([btn_manter_modo, btn_mudar_modo])

        elif self.estado == "MENU_MODO":
            offset_x = random.randint(-4, 4) if self.shake_frames > 0 else 0
            offset_y = random.randint(-4, 4) if self.shake_frames > 0 else 0
            if self.shake_frames > 0: self.shake_frames -= 1
            
            desenhar_texto(self.tela, "SISTEMA PRINCIPAL", self.fonte_titulo, BRANCO, cx + offset_x, 60 + offset_y)
            desenhar_texto(self.tela, "USE SEU DASH [ ESPAÇO ] NO NÓDULO OU APERTE [ ENTER ] PARA SELECIONAR", self.fonte_texto, VERDE_NEON, cx + offset_x, 120 + offset_y)
            
            pads = self.obter_pads_menu()
            
            for pad in pads:
                px, py = pad["pos"]
                cor = pad["cor"]
                dist = self.player.pos.distance_to(pygame.math.Vector2(px, py))
                
                is_hovered = (self.botao_selecionado == pad["id"])
                
                if is_hovered or dist < 300:
                    espessura = max(1, int(6 - (dist / 60))) if dist < 300 else 2
                    pygame.draw.line(self.tela, (*cor[:3], 150), self.player.pos, (px, py), espessura)
                    
            for pad in pads:
                px, py = pad["pos"]
                cor = pad["cor"]
                is_hovered = (self.botao_selecionado == pad["id"])
                
                raio_pad = 45 + (math.sin(time.time() * 12) * 8 if is_hovered else math.sin(time.time() * 4) * 3)
                
                desenhar_brilho_neon(self.tela, cor, px, py, raio_pad, 4)
                pygame.draw.circle(self.tela, PRETO_FUNDO, (int(px), int(py)), int(raio_pad - 6))
                pygame.draw.circle(self.tela, cor, (int(px), int(py)), int(raio_pad), 5)
                
                if is_hovered:
                    pygame.draw.circle(self.tela, cor, (int(px), int(py)), int(raio_pad // 2))
                
                desenhar_texto(self.tela, pad["texto"], self.fonte_sub, BRANCO if is_hovered else cor, px, py - 80)

            for p in self.particulas: p.draw(self.tela)
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
            desenhar_texto(self.tela, "Complete 10 fases no menor tempo. No Hardcore, a morte devolve-o para a fase 1.", self.fonte_desc, BRANCO, x_esq, y_base + 35, alinhamento="esquerda")
            
            y_base = painel_rect.top + 130
            desenhar_texto(self.tela, "CORRIDA INFINITA:", self.fonte_sub, ROXO_NEON, x_esq, y_base, alinhamento="esquerda")
            desenhar_texto(self.tela, "Fases não têm fim. A cada 10 fases o Boss muda de forma, cor e dificuldade!", self.fonte_desc, BRANCO, x_esq, y_base + 35, alinhamento="esquerda")
            
            y_base = painel_rect.top + 230
            desenhar_texto(self.tela, "SOBREVIVÊNCIA / HARDCORE:", self.fonte_sub, ROSA_NEON, x_esq, y_base, alinhamento="esquerda")
            desenhar_texto(self.tela, "A cada 30 segundos, o cenário vai ser invadido por LAVA! Fuja das zonas de aviso.", self.fonte_desc, BRANCO, x_esq, y_base + 35, alinhamento="esquerda")
            
            y_base = painel_rect.top + 330
            desenhar_texto(self.tela, "OS PORTAIS VERMELHOS (Aviso de Inimigo):", self.fonte_sub, VERMELHO_SANGUE, x_esq, y_base, alinhamento="esquerda")
            desenhar_texto(self.tela, "Antes de um inimigo materializar-se, um portal indica onde ele vai surgir, permitindo que escape.", self.fonte_desc, BRANCO, x_esq, y_base + 35, alinhamento="esquerda")
            
            btn_voltar = desenhar_botao_dinamico(self.tela, "VOLTAR PARA O MENU", self.fonte_sub, VERDE_NEON, cx, cy + 300, self.botao_selecionado == 0)
            self.botoes_hitboxes.append(btn_voltar)

        elif self.estado == "TELA_HOTKEYS":
            desenhar_texto(self.tela, "CONTROLES DO SISTEMA", self.fonte_titulo, VERDE_NEON, cx, 100)
            comandos = [
                ("W A S D / SETAS", "Mover a Nave"),
                ("BARRA DE ESPAÇO", "DASH (Invencibilidade Rápida)"),
                ("TECLA ESC", "Pausar ou Voltar Menus"),
                ("TECLA F11", "Ativar/Desativar Ecrã Inteiro")
            ]
            for i, (tecla, desc) in enumerate(comandos):
                y_pos = 240 + (i * 70) 
                desenhar_texto(self.tela, tecla, self.fonte_sub, CIANO_NEON, cx - 40, y_pos, alinhamento="direita")
                desenhar_texto(self.tela, "- " + desc, self.fonte_texto, BRANCO, cx + 40, y_pos, alinhamento="esquerda")
                
            btn_prox = desenhar_botao_dinamico(self.tela, "AVANÇAR PARA AMEAÇAS", self.fonte_sub, ROSA_NEON, cx, cy + 240, self.botao_selecionado == 0)
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
            desenhar_texto(self.tela, "Patrulha rebatendo nas paredes. Cuidado com o efeito manada,", self.fonte_desc, BRANCO, espacamento, y_base + 35, alinhamento="esquerda")
            desenhar_texto(self.tela, "pois eles ricocheteiam uns nos outros.", self.fonte_desc, CINZA_CLARO, espacamento, y_base + 60, alinhamento="esquerda")

            y_base += espaco_y
            desenhar_brilho_neon(self.tela, VERMELHO_SANGUE, painel_rect.left + 80, y_base + 20, 18, 2)
            pygame.draw.circle(self.tela, VERMELHO_SANGUE, (painel_rect.left + 80, y_base + 20), 18)
            pygame.draw.circle(self.tela, BRANCO, (painel_rect.left + 80, y_base + 20), 6)
            desenhar_texto(self.tela, "CAÇADOR (A Sanguessuga):", self.fonte_sub, VERMELHO_SANGUE, espacamento, y_base, alinhamento="esquerda")
            desenhar_texto(self.tela, "Persegue a sua posição futura. Ele vai tentar prever os seus", self.fonte_desc, BRANCO, espacamento, y_base + 35, alinhamento="esquerda")
            desenhar_texto(self.tela, "movimentos e bloquear a sua fuga em ziguezague.", self.fonte_desc, CINZA_CLARO, espacamento, y_base + 60, alinhamento="esquerda")

            y_base += espaco_y
            desenhar_brilho_neon(self.tela, LARANJA_NEON, painel_rect.left + 80, y_base + 20, 18, 2)
            pygame.draw.circle(self.tela, LARANJA_NEON, (painel_rect.left + 80, y_base + 20), 18)
            pygame.draw.circle(self.tela, BRANCO, (painel_rect.left + 80, y_base + 20), 6)
            desenhar_texto(self.tela, "SNIPER (O Fuzil):", self.fonte_sub, LARANJA_NEON, espacamento, y_base, alinhamento="esquerda")
            desenhar_texto(self.tela, "Aguarde o feixe de mira, use o Dash no momento exato do disparo.", self.fonte_desc, BRANCO, espacamento, y_base + 35, alinhamento="esquerda")
            desenhar_texto(self.tela, "Ele destrói-se automaticamente após a investida.", self.fonte_desc, CINZA_CLARO, espacamento, y_base + 60, alinhamento="esquerda")

            y_base += espaco_y
            desenhar_brilho_neon(self.tela, AMARELO_DADO, painel_rect.left + 80, y_base + 20, 18, 2)
            pygame.draw.circle(self.tela, AMARELO_DADO, (painel_rect.left + 80, y_base + 20), 18)
            pygame.draw.circle(self.tela, BRANCO, (painel_rect.left + 80, y_base + 20), 6)
            desenhar_texto(self.tela, "A BOMBA (O Relógio):", self.fonte_sub, AMARELO_DADO, espacamento, y_base, alinhamento="esquerda")
            desenhar_texto(self.tela, "Segue-o e detona num raio gigantesco quando o relógio expirar.", self.fonte_desc, BRANCO, espacamento, y_base + 35, alinhamento="esquerda")
            desenhar_texto(self.tela, "Saia de perto assim que ela parar e começar a piscar!", self.fonte_desc, CINZA_CLARO, espacamento, y_base + 60, alinhamento="esquerda")

            btn_iniciar = desenhar_botao_dinamico(self.tela, "INICIAR SEQUÊNCIA", self.fonte_sub, VERDE_NEON, cx, cy + 300, self.botao_selecionado == 0)
            self.botoes_hitboxes.append(btn_iniciar)

        elif self.estado in ["JOGANDO", "PAUSA"]:
            offset_x = random.randint(-8, 8) if self.shake_frames > 0 else 0
            offset_y = random.randint(-8, 8) if self.shake_frames > 0 else 0
            if self.shake_frames > 0 and self.estado == "JOGANDO": self.shake_frames -= 1

            self.tela.fill(PRETO_FUNDO)
            surf_jogo = pygame.Surface((LARGURA_TELA, ALTURA_TELA), pygame.SRCALPHA)
            desenhar_grade_jogo(surf_jogo)
            
            # --- PORTAIS DE AVISO (SPAWN WARNING) ---
            for p in self.portais_inimigos:
                raio = 15 + math.sin(time.time() * 15) * 5
                cor_portal = ROXO_NEON if p["tipo"] == "boss" else VERMELHO_SANGUE
                pygame.draw.circle(surf_jogo, (*cor_portal[:3], 150), (int(p["pos"].x), int(p["pos"].y)), int(raio))
                pygame.draw.circle(surf_jogo, cor_portal, (int(p["pos"].x), int(p["pos"].y)), int(raio), 2)
                desenhar_brilho_neon(surf_jogo, cor_portal, p["pos"].x, p["pos"].y, raio, 2)
            
            # --- EFEITOS DA LAVA (SOBREVIVÊNCIA) ---
            if self.modo_jogo in ["SOBREVIVENCIA", "HARDCORE"]:
                # Desenho do PREVISTO (Zonas de aviso antes do dano)
                if self.aviso_lava > 0.0 and self.tipo_lava != 0:
                    for r in self.lava_hitboxes:
                        aviso_surf = pygame.Surface((r.width, r.height), pygame.SRCALPHA)
                        alpha = int(100 + math.sin(time.time() * 20) * 50)
                        aviso_surf.fill((255, 150, 0, alpha))
                        pygame.draw.rect(aviso_surf, AMARELO_DADO, (0, 0, r.width, r.height), 4)
                        surf_jogo.blit(aviso_surf, (r.x, r.y))
                    desenhar_texto(surf_jogo, f"ALERTA DE LAVA EM {int(self.aviso_lava)+1}s!", self.fonte_titulo, VERMELHO_SANGUE, LARGURA_TELA // 2, 140)

                # Desenho da LAVA MORTAL ATIVA
                if getattr(self, 'lava_ativa', False):
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

                    desenhar_texto(surf_jogo, f"LAVA ATIVA: {self.tempo_lava_restante:.1f}s", self.fonte_sub, LARANJA_NEON, LARGURA_TELA // 2, 90)

            for d in self.coletaveis:
                desenhar_brilho_neon(surf_jogo, AMARELO_DADO, d.x, d.y, 6, 2)
                pygame.draw.rect(surf_jogo, AMARELO_DADO, (int(d.x)-6, int(d.y)-6, 12, 12), border_radius=2)

            if self.portal_aberto:
                raio = 20 + math.sin(time.time() * 10) * 5 
                desenhar_brilho_neon(surf_jogo, VERDE_NEON, self.portal_pos.x, self.portal_pos.y, raio, 4)
                pygame.draw.circle(surf_jogo, VERDE_NEON, (int(self.portal_pos.x), int(self.portal_pos.y)), int(raio), 3)

            for p in self.particulas: p.draw(surf_jogo)
            for ini in self.inimigos: ini.draw(surf_jogo)
            self.player.draw(surf_jogo)

            self.tela.blit(surf_jogo, (offset_x, offset_y))

            pygame.draw.rect(self.tela, PRETO_FUNDO, (0, 0, LARGURA_TELA, 60))
            pygame.draw.line(self.tela, CIANO_NEON, (0, 60), (LARGURA_TELA, 60), 2)
            
            if self.modo_jogo in ["CORRIDA", "CORRIDA_HARDCORE", "CORRIDA_INFINITA"]:
                texto_tempo = f"{self.tempo_corrida:.1f}s"
                desc_hud = self.modo_jogo.replace('_', ' ')
                eh_fase_boss = (self.modo_jogo in ["CORRIDA", "CORRIDA_HARDCORE"] and self.fase_atual == 10) or \
                               (self.modo_jogo == "CORRIDA_INFINITA" and self.fase_atual > 0 and self.fase_atual % 10 == 0)
                if eh_fase_boss:
                    desenhar_texto(self.tela, f"{desc_hud} - FASE FINAL (O SOBERANO!)", self.fonte_sub, ROXO_NEON, 20, 30, alinhamento="esquerda")
                else:
                    desenhar_texto(self.tela, f"{desc_hud} - FASE {self.fase_atual}", self.fonte_sub, BRANCO, 20, 30, alinhamento="esquerda")
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
                btn_cont = desenhar_botao_dinamico(self.tela, "CONTINUAR [ESC]", self.fonte_sub, VERDE_NEON, cx, cy + 30, self.botao_selecionado == 0)
                btn_sair = desenhar_botao_dinamico(self.tela, "ABANDONAR PARTIDA", self.fonte_sub, VERMELHO_SANGUE, cx, cy + 110, self.botao_selecionado == 1)
                
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
            pygame.draw.line(self.tela, CINZA_ESCURO, (rect_ranking.left + 50, rect_ranking.top + 85), (rect_ranking.right - 50, rect_ranking.top + 85), 2)
            desenhar_texto(self.tela, f"--- TOP 5 {self.modo_jogo.replace('_', ' ')} ---", self.fonte_sub, CIANO_NEON, cx, rect_ranking.top + 115)
            
            if self.modo_jogo == "CORRIDA": chave_modo = "Corrida"
            elif self.modo_jogo == "CORRIDA_HARDCORE": chave_modo = "Corrida_Hardcore"
            elif self.modo_jogo == "SOBREVIVENCIA": chave_modo = "Sobrevivencia"
            elif self.modo_jogo == "CORRIDA_INFINITA": chave_modo = "Corrida_Infinita"
            else: chave_modo = "Hardcore"
            top5 = self.ranking.get(chave_modo, [])
            
            margem_esq = rect_ranking.left + 80
            margem_dir = rect_ranking.right - 80
            
            for i, reg in enumerate(top5[:5]):
                cor = AMARELO_DADO if reg.get('id', 0) == self.ranking[chave_modo][self.ultima_posicao-1].get('id', 0) else BRANCO
                y_pos = rect_ranking.top + 155 + (i * 35) 
                desenhar_texto(self.tela, f"{i+1}º {reg['nome']}", self.fonte_sub, cor, margem_esq, y_pos, alinhamento="esquerda")
                
                texto_valor = f"Fase {reg.get('fase', 0)}" if chave_modo == "Corrida_Infinita" else f"{reg.get('tempo', 0):.1f}s"
                desenhar_texto(self.tela, texto_valor, self.fonte_sub, cor, margem_dir, y_pos, alinhamento="direita")
            
            espaco_y = 65 
            y_botoes = rect_ranking.bottom + 40
            
            btn_replay = desenhar_botao_dinamico(self.tela, "JOGAR NOVAMENTE", self.fonte_sub, VERDE_NEON, cx, y_botoes, self.botao_selecionado == 0)
            btn_manter = desenhar_botao_dinamico(self.tela, "MANTER PILOTO (MENU)", self.fonte_sub, CIANO_NEON, cx, y_botoes + espaco_y, self.botao_selecionado == 1)
            btn_novo = desenhar_botao_dinamico(self.tela, "CRIAR NOVO PILOTO", self.fonte_sub, ROSA_NEON, cx, y_botoes + (espaco_y * 2), self.botao_selecionado == 2)
            
            self.botoes_hitboxes.extend([btn_replay, btn_manter, btn_novo])

        if self.is_fullscreen:
            w, h = self.tela_real.get_size()
            tela_redimensionada = pygame.transform.scale(self.tela, (w, h))
            self.tela_real.blit(tela_redimensionada, (0, 0))
        else:
            self.tela_real.blit(self.tela, (0, 0))

        pygame.display.flip()

    def acionar_botao(self):
        if self.estado == "INPUT_NOME" and self.botao_selecionado == 0:
            if len(self.nome_jogador) > 0: 
                if self.veio_do_game_over and self.modo_jogo != "":
                    self.estado = "PERGUNTA_MODO"
                else:
                    self.entrar_menu_modo()
                self.botao_selecionado = -1
                
        elif self.estado == "PERGUNTA_MODO":
            self.veio_do_game_over = False
            if self.botao_selecionado == 0:
                self.estado = "TELA_INIMIGOS" 
            elif self.botao_selecionado == 1:
                self.entrar_menu_modo()
            self.botao_selecionado = -1

        elif self.estado == "MENU_MODO":
            if self.botao_selecionado == 0: self.modo_jogo = "CORRIDA"
            elif self.botao_selecionado == 1: self.modo_jogo = "CORRIDA_HARDCORE"
            elif self.botao_selecionado == 2: self.modo_jogo = "SOBREVIVENCIA"
            elif self.botao_selecionado == 3: self.modo_jogo = "HARDCORE"
            elif self.botao_selecionado == 5: self.modo_jogo = "CORRIDA_INFINITA"
            elif self.botao_selecionado == 4: 
                self.estado = "TELA_INFO_MODOS"
                self.botao_selecionado = -1
                return

            self.estado = "TELA_HOTKEYS"
            self.botao_selecionado = -1

        elif self.estado == "TELA_INFO_MODOS" and self.botao_selecionado == 0:
            self.entrar_menu_modo()
                
        elif self.estado == "TELA_HOTKEYS" and self.botao_selecionado == 0:
            self.estado = "TELA_INIMIGOS"
            self.botao_selecionado = -1
            
        elif self.estado == "TELA_INIMIGOS" and self.botao_selecionado == 0:
            self.fase_atual = 1
            self.iniciar_fase()
            
        elif self.estado == "PAUSA":
            if self.botao_selecionado == 0: self.estado = "JOGANDO"
            elif self.botao_selecionado == 1: 
                self.entrar_menu_modo()
                
        elif self.estado == "RANKING":
            if self.botao_selecionado == 0: 
                self.fase_atual = 1
                self.iniciar_fase()
            elif self.botao_selecionado == 1: 
                self.entrar_menu_modo()
            elif self.botao_selecionado == 2: 
                self.estado = "INPUT_NOME"
                self.nome_jogador = ""
                self.veio_do_game_over = True
            self.botao_selecionado = -1

    def executar(self):
        while True:
            self.tempo_global = time.time()
            self.dt = self.clock.tick(FPS) / 1000.0 
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                    
                if event.type == pygame.KEYDOWN and event.key == pygame.K_F11: self.alternar_tela_cheia()
                if event.type == pygame.KEYDOWN:
                    if event.key in [pygame.K_MINUS, pygame.K_KP_MINUS]: self.alterar_volume(-0.1)
                    elif event.key in [pygame.K_PLUS, pygame.K_KP_PLUS, pygame.K_EQUALS]: self.alterar_volume(0.1)
                    elif event.key == pygame.K_ESCAPE:
                        if self.estado == "MENU_MODO": self.estado = "INPUT_NOME"
                        elif self.estado == "TELA_INFO_MODOS": self.entrar_menu_modo()
                        elif self.estado == "TELA_HOTKEYS": self.entrar_menu_modo()
                        elif self.estado == "TELA_INIMIGOS": self.estado = "TELA_HOTKEYS"
                        elif self.estado == "PERGUNTA_MODO": self.estado = "INPUT_NOME"
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
                            
                    # Sem cliques no ecrã para escolher o modo (Uso exclusivo da nave)
                    if self.estado != "MENU_MODO":
                        for i, rect in enumerate(self.botoes_hitboxes):
                            if rect.collidepoint(mx, my):
                                self.botao_selecionado = i
                                self.acionar_botao()
                
                if event.type == pygame.KEYDOWN:
                    num_botoes = len(self.botoes_hitboxes)
                    
                    if self.estado == "INPUT_NOME":
                        if event.key == pygame.K_BACKSPACE: self.nome_jogador = self.nome_jogador[:-1]
                        elif event.key != pygame.K_RETURN and len(self.nome_jogador) < 12 and event.unicode.isprintable():
                            self.nome_jogador += event.unicode
                    
                    if num_botoes > 0 and self.estado != "MENU_MODO":
                        if event.key in [pygame.K_UP, pygame.K_w, pygame.K_LEFT, pygame.K_a]:
                            self.botao_selecionado = (self.botao_selecionado - 1) % num_botoes
                        elif event.key in [pygame.K_DOWN, pygame.K_s, pygame.K_RIGHT, pygame.K_d]:
                            self.botao_selecionado = (self.botao_selecionado + 1) % num_botoes
                            
                    if self.estado in ["TELA_INFO_MODOS", "TELA_HOTKEYS", "TELA_INIMIGOS"] and event.key == pygame.K_SPACE: 
                        self.acionar_botao()

            if self.estado == "JOGANDO": self.atualizar_jogo()
            elif self.estado == "MENU_MODO": self.atualizar_menu_interativo()
            self.desenhar()

if __name__ == "__main__":
    jogo = NeonSurge()
    jogo.executar()