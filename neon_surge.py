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
# Inicia o pygame primeiro para conseguirmos pegar a resolução do monitor
pygame.init()
info = pygame.display.Info()

# Define a resolução do jogo sempre para o tamanho exato do PC do jogador
LARGURA_TELA = info.current_w
ALTURA_TELA = info.current_h
FPS = 60
ARQUIVO_RANKING = "ranking_completo.json"

# MELHORIA DE CONTRASTE: Fundo mais escuro para os neons brilharem mais
PRETO_FUNDO = (5, 5, 8) 
BRANCO = (255, 255, 255)
VERDE_NEON = (57, 255, 20)
CIANO_NEON = (0, 255, 255)
ROSA_NEON = (255, 20, 147)
LARANJA_NEON = (255, 100, 0)
AMARELO_DADO = (255, 215, 0)
VERMELHO_SANGUE = (255, 30, 30)
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

def desenhar_botao_dinamico(surface, texto, fonte, cor_base, cx, cy, is_hovered):
    texto_display = f"> {texto} <" if is_hovered else texto
    cor_texto = PRETO_FUNDO if is_hovered else cor_base
    
    img_texto = fonte.render(texto_display, True, cor_texto)
    rect_texto = img_texto.get_rect(center=(cx, cy))
    
    rect_botao = rect_texto.inflate(80, 40) 
    
    if is_hovered:
        pulso = math.sin(time.time() * 10) * 3
        rect_botao = rect_botao.inflate(pulso, pulso)
        pygame.draw.rect(surface, cor_base, rect_botao, border_radius=8)
        pygame.draw.rect(surface, BRANCO, rect_botao, 2, border_radius=8)
    else:
        pygame.draw.rect(surface, (10, 15, 25), rect_botao, border_radius=8)
        pygame.draw.rect(surface, cor_base, rect_botao, 2, border_radius=8)
        
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
        pygame.draw.line(surface, (20, 25, 35), (x, 0), (x, ALTURA_TELA), 1)
    offset_y = (tempo * 50) % 100
    for y in range(-100, ALTURA_TELA + 100, 100):
        pygame.draw.line(surface, (20, 25, 35), (0, y + offset_y), (LARGURA_TELA, y + offset_y), 1)
    surf_fade = pygame.Surface((LARGURA_TELA, 300), pygame.SRCALPHA)
    for i in range(300):
        alpha = int(255 - (i / 300) * 255)
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

class Inimigo:
    def __init__(self, x, y, tipo, velocidade):
        self.pos = pygame.math.Vector2(x, y)
        self.tipo = tipo
        self.raio = 12
        self.vel = velocidade
        self.dir = pygame.math.Vector2(0, 0)
        
        self.estado_investida = "ESPERANDO" 
        self.timer_investida = 0.0
        self.alvo_mira = pygame.math.Vector2(x, y) 
        self.travado = False # Controle de trava de mira (Kamikaze)

        if self.tipo == "quique":
            ang = random.uniform(0, math.pi * 2)
            self.dir = pygame.math.Vector2(math.cos(ang), math.sin(ang)) * self.vel

    def update(self, player_pos, lista_inimigos, dt, lista_particulas):
        if self.tipo == "perseguidor":
            vec_to_player = player_pos - self.pos
            if vec_to_player.length() > 0:
                direcao_desejada = vec_to_player.normalize() * (self.vel * 0.7)
                self.dir = self.dir.lerp(direcao_desejada, 0.1) 

        elif self.tipo == "investida":
            self.timer_investida += dt
            if self.estado_investida == "ESPERANDO":
                self.dir = self.dir.lerp(pygame.math.Vector2(0, 0), 0.1) 
                self.travado = False
                if self.timer_investida > 1.2: 
                    self.estado_investida = "MIRANDO"
                    self.timer_investida = 0.0
            
            elif self.estado_investida == "MIRANDO":
                # Segue o jogador pela primeira metade do tempo
                if self.timer_investida < 0.5:
                    self.alvo_mira = pygame.math.Vector2(player_pos.x, player_pos.y) 
                else:
                    self.travado = True # Trava a mira no último local conhecido

                if self.timer_investida > 0.9: 
                    vec = self.alvo_mira - self.pos
                    if vec.length() > 0:
                        self.dir = vec.normalize() * (self.vel * 4.0) # Investida muito mais rápida
                    self.estado_investida = "ATACANDO"
                    self.timer_investida = 0.0
            
            elif self.estado_investida == "ATACANDO":
                lista_particulas.append(Particula(self.pos.x, self.pos.y, LARANJA_NEON))
                if self.timer_investida > 0.6: 
                    self.estado_investida = "ESPERANDO"
                    self.timer_investida = 0.0

        forca_repulsao = pygame.math.Vector2(0, 0)
        for vizinho in lista_inimigos:
            if vizinho != self:
                distancia = self.pos.distance_to(vizinho.pos)
                distancia_segura = self.raio + vizinho.raio + 5
                if 0 < distancia < distancia_segura:
                    diferenca = self.pos - vizinho.pos
                    forca_repulsao += diferenca.normalize() * (distancia_segura - distancia) * 0.1
        
        self.pos += self.dir + forca_repulsao

        if self.pos.x <= self.raio:
            self.pos.x = self.raio
            if self.tipo == "quique": self.dir.x *= -1
            elif self.tipo == "investida": self.estado_investida = "ESPERANDO"
        elif self.pos.x >= LARGURA_TELA - self.raio:
            self.pos.x = LARGURA_TELA - self.raio
            if self.tipo == "quique": self.dir.x *= -1
            elif self.tipo == "investida": self.estado_investida = "ESPERANDO"
            
        if self.pos.y <= 60 + self.raio:
            self.pos.y = 60 + self.raio
            if self.tipo == "quique": self.dir.y *= -1
            elif self.tipo == "investida": self.estado_investida = "ESPERANDO"
        elif self.pos.y >= ALTURA_TELA - self.raio:
            self.pos.y = ALTURA_TELA - self.raio
            if self.tipo == "quique": self.dir.y *= -1
            elif self.tipo == "investida": self.estado_investida = "ESPERANDO"

    def draw(self, surface):
        cor_base = ROSA_NEON
        if self.tipo == "perseguidor": cor_base = VERMELHO_SANGUE
        elif self.tipo == "investida": cor_base = LARANJA_NEON
        
        if self.tipo == "investida" and self.estado_investida == "MIRANDO":
            cor_linha = VERMELHO_SANGUE if not self.travado else BRANCO
            espessura = 2 if not self.travado else 4
            pygame.draw.line(surface, cor_linha, self.pos, self.alvo_mira, espessura)
            if self.travado: cor_base = BRANCO

        desenhar_brilho_neon(surface, cor_base, self.pos.x, self.pos.y, self.raio, intensidade=3)
        pygame.draw.circle(surface, cor_base, (int(self.pos.x), int(self.pos.y)), self.raio)
        pygame.draw.circle(surface, BRANCO, (int(self.pos.x), int(self.pos.y)), self.raio // 3)

# ==========================================
# 4. MÁQUINA DE ESTADOS E LÓGICA
# ==========================================
class NeonSurge:
    def __init__(self):
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
        
        # Agora inicializa por padrão em Tela Cheia (Borderless Window no tamanho do monitor)
        self.is_fullscreen = True
        self.tela_real = pygame.display.set_mode((LARGURA_TELA, ALTURA_TELA), pygame.FULLSCREEN)
        self.tela = pygame.Surface((LARGURA_TELA, ALTURA_TELA))
        pygame.display.set_caption("Neon Surge - Hardcore Edition")

        self.clock = pygame.time.Clock()
        self.dt = 0.0 
        
        self.blur_surf = pygame.Surface((LARGURA_TELA, ALTURA_TELA))
        self.blur_surf.set_alpha(80) 
        self.blur_surf.fill(PRETO_FUNDO)

        self.crt_overlay = pygame.Surface((LARGURA_TELA, ALTURA_TELA), pygame.SRCALPHA)
        for y in range(0, ALTURA_TELA, 3): 
            pygame.draw.line(self.crt_overlay, (0, 0, 0, 40), (0, y), (LARGURA_TELA, y))

        font_name = "Consolas" if pygame.font.match_font("Consolas") else None
        self.fonte_titulo = pygame.font.SysFont("Impact", 85)
        self.fonte_sub = pygame.font.SysFont(font_name, 30, bold=True)
        self.fonte_texto = pygame.font.SysFont(font_name, 22)
        self.fonte_desc = pygame.font.SysFont(font_name, 19) 
        
        self.estado = "INPUT_NOME"
        self.nome_jogador = ""
        self.modo_jogo = "" 
        self.fase_atual = 1
        self.veio_do_game_over = False  
        
        self.botao_selecionado = 0 
        self.botoes_hitboxes = []  
        
        self.player = None
        self.inimigos = []
        self.coletaveis = []
        self.particulas = []
        self.portal_aberto = False
        
        self.tempo_corrida = 0.0
        self.tempo_sobrevivencia = 0.0
        self.temporizador_spawn = 0.0
        self.shake_frames = 0
        self.tempo_global = 0 
        
        self.ranking = self.carregar_ranking()
        self.ultima_pos_mouse = (0, 0)
        self.ultima_posicao = 0  
        self.ultimo_tempo = 0.0  

    def alternar_tela_cheia(self):
        self.is_fullscreen = not self.is_fullscreen
        if self.is_fullscreen: 
            self.tela_real = pygame.display.set_mode((LARGURA_TELA, ALTURA_TELA), pygame.FULLSCREEN)
        else: 
            # Em modo janela, usa 80% da tela para não cortar as margens na barra de tarefas
            win_w, win_h = int(LARGURA_TELA * 0.8), int(ALTURA_TELA * 0.8)
            self.tela_real = pygame.display.set_mode((win_w, win_h))

    def obter_posicao_mouse(self):
        mx, my = pygame.mouse.get_pos()
        # Ajusta a escala do mouse se estiver em modo janela (80%)
        if not self.is_fullscreen:
            mx = mx / 0.8
            my = my / 0.8
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
                return dados
        return {"Corrida": [], "Corrida_Hardcore": [], "Sobrevivencia": [], "Hardcore": []}

    def salvar_ranking(self, modo, tempo):
        tempo_str = f"{tempo:.1f}"
        novo_registro = {"nome": self.nome_jogador, "tempo": float(tempo_str), "id": time.time()}
        
        if modo == "CORRIDA": chave_modo = "Corrida"
        elif modo == "CORRIDA_HARDCORE": chave_modo = "Corrida_Hardcore"
        elif modo == "SOBREVIVENCIA": chave_modo = "Sobrevivencia"
        else: chave_modo = "Hardcore"
        
        self.ranking[chave_modo].append(novo_registro)
        
        if chave_modo in ["Corrida", "Corrida_Hardcore"]: 
            self.ranking[chave_modo] = sorted(self.ranking[chave_modo], key=lambda x: x["tempo"])
        else: 
            self.ranking[chave_modo] = sorted(self.ranking[chave_modo], key=lambda x: x["tempo"], reverse=True)
            
        self.ultima_posicao = self.ranking[chave_modo].index(novo_registro) + 1
        self.ultimo_tempo = float(tempo_str)
        
        self.ranking[chave_modo] = self.ranking[chave_modo][:50]
            
        with open(ARQUIVO_RANKING, 'w') as f: json.dump(self.ranking, f, indent=4)

    def iniciar_fase(self):
        self.player = Player(LARGURA_TELA // 2, ALTURA_TELA // 2)
        self.inimigos.clear()
        self.coletaveis.clear()
        self.particulas.clear() 
        self.portal_aberto = False
        
        if self.fase_atual == 1:
            self.tempo_corrida = 0.0
            self.tempo_sobrevivencia = 0.0
            self.temporizador_spawn = 0.0
        
        if self.modo_jogo in ["CORRIDA", "CORRIDA_HARDCORE"]:
            for _ in range(5):
                x = random.randint(50, LARGURA_TELA - 50)
                y = random.randint(110, ALTURA_TELA - 50)
                self.coletaveis.append(pygame.math.Vector2(x, y))

            qtd_inimigos = 3 + self.fase_atual
            vel_inimigo = 4 + (self.fase_atual * 0.3)
            self._spawn_inimigos(qtd_inimigos, vel_inimigo)
            
        elif self.modo_jogo == "SOBREVIVENCIA":
            self._spawn_inimigos(2, 4)
            
        elif self.modo_jogo == "HARDCORE":
            self._spawn_inimigos(4, 6)

        self.estado = "JOGANDO"

    def _spawn_inimigos(self, quantidade, velocidade):
        for _ in range(quantidade):
            tipo = random.choice(["quique", "perseguidor", "investida"])
            ex, ey = self.player.pos.x, self.player.pos.y
            while abs(ex - self.player.pos.x) < 300 and abs(ey - self.player.pos.y) < 300:
                ex = random.randint(50, LARGURA_TELA - 50)
                ey = random.randint(110, ALTURA_TELA - 50)
            self.inimigos.append(Inimigo(ex, ey, tipo, velocidade))

    def atualizar_jogo(self):
        teclas = pygame.key.get_pressed()
        if self.player.update(teclas, self.particulas): self.shake_frames = 6

        for p in self.particulas[:]:
            p.update()
            if p.raio <= 0: self.particulas.remove(p)

        for ini in self.inimigos:
            ini.update(self.player.pos, self.inimigos, self.dt, self.particulas)
            dist = ini.pos.distance_to(self.player.pos)
            if not self.player.invencivel and dist < (ini.raio + self.player.tamanho//2 - 2):
                self._lidar_com_morte()
                return

        if self.modo_jogo in ["CORRIDA", "CORRIDA_HARDCORE"]:
            self.tempo_corrida += self.dt
            for d in self.coletaveis[:]:
                if self.player.pos.distance_to(d) < 20:
                    self.coletaveis.remove(d)
                    self.shake_frames = 2 
                    for _ in range(10): self.particulas.append(Particula(d.x, d.y, AMARELO_DADO))
            
            if len(self.coletaveis) == 0 and not self.portal_aberto:
                self.portal_aberto = True
                self.portal_pos = pygame.math.Vector2(LARGURA_TELA//2, 100)
                self.shake_frames = 10

            if self.portal_aberto and self.player.pos.distance_to(self.portal_pos) < 30:
                if self.fase_atual < 10:
                    self.fase_atual += 1
                    self.iniciar_fase() 
                else:
                    self.salvar_ranking(self.modo_jogo, self.tempo_corrida)
                    self.estado = "RANKING"
                    self.botao_selecionado = 0
                    
        elif self.modo_jogo == "SOBREVIVENCIA":
            self.tempo_sobrevivencia += self.dt
            self.temporizador_spawn += self.dt
            if self.temporizador_spawn > 3.0:
                vel_progressiva = min(8, 4 + (self.tempo_sobrevivencia * 0.05)) 
                self._spawn_inimigos(1, vel_progressiva)
                self.temporizador_spawn = 0.0 
                self.shake_frames = 3 
                
        elif self.modo_jogo == "HARDCORE":
            self.tempo_sobrevivencia += self.dt
            self.temporizador_spawn += self.dt
            if self.temporizador_spawn > 1.5: 
                vel_progressiva = min(12, 6 + (self.tempo_sobrevivencia * 0.1)) 
                self._spawn_inimigos(1, vel_progressiva)
                self.temporizador_spawn = 0.0 
                self.shake_frames = 5 

    def _lidar_com_morte(self):
        self.shake_frames = 15
        if self.modo_jogo == "CORRIDA": 
            self.iniciar_fase() 
        elif self.modo_jogo == "CORRIDA_HARDCORE":
            self.salvar_ranking(self.modo_jogo, self.tempo_corrida)
            self.estado = "RANKING"
            self.botao_selecionado = 0
        elif self.modo_jogo in ["SOBREVIVENCIA", "HARDCORE"]:
            self.salvar_ranking(self.modo_jogo, self.tempo_sobrevivencia)
            self.estado = "RANKING"
            self.botao_selecionado = 0

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
        
        if (mx, my) != self.ultima_pos_mouse:
            for i, btn in enumerate(self.botoes_hitboxes):
                if btn.collidepoint(mx, my): 
                    self.botao_selecionado = i
            self.ultima_pos_mouse = (mx, my)

        cx, cy = LARGURA_TELA // 2, ALTURA_TELA // 2
        self.botoes_hitboxes = []

        if self.estado in ["INPUT_NOME", "MENU_MODO", "TELA_INFO_MODOS", "TELA_HOTKEYS", "TELA_INIMIGOS", "RANKING", "PERGUNTA_MODO"]:
            desenhar_fundo_cyberpunk(self.tela, self.tempo_global)
            self.desenhar_controle_volume(mx, my)
            if self.estado in ["MENU_MODO", "TELA_INFO_MODOS", "TELA_HOTKEYS", "TELA_INIMIGOS", "PERGUNTA_MODO"]:
                pygame.draw.rect(self.tela, CINZA_ESCURO, (20, 20, 140, 40), border_radius=5)
                desenhar_texto(self.tela, "< ESC VOLTAR", self.fonte_texto, BRANCO, 90, 40, alinhamento="centro")

        if self.estado == "INPUT_NOME":
            desenhar_texto(self.tela, "NEON SURGE", self.fonte_titulo, CIANO_NEON, cx, cy - 140)
            desenhar_texto(self.tela, "IDENTIFICAÇÃO DO PILOTO:", self.fonte_texto, BRANCO, cx, cy - 20)
            
            caixa_texto = pygame.Rect(0, 0, 400, 60)
            caixa_texto.center = (cx, cy + 40)
            pygame.draw.rect(self.tela, AZUL_ESCURO, caixa_texto, border_radius=10)
            pygame.draw.rect(self.tela, VERDE_NEON, caixa_texto, 2, border_radius=10)
            
            cursor = "_" if int(time.time() * 2) % 2 == 0 else ""
            desenhar_texto(self.tela, self.nome_jogador + cursor, self.fonte_sub, VERDE_NEON, cx, cy + 40)
            
            btn_rect = desenhar_botao_dinamico(self.tela, "CONFIRMAR DADOS", self.fonte_texto, VERDE_NEON, cx, cy + 180, self.botao_selecionado == 0)
            self.botoes_hitboxes.append(btn_rect)

        elif self.estado == "PERGUNTA_MODO":
            desenhar_texto(self.tela, "NOVO PILOTO REGISTRADO", self.fonte_titulo, VERDE_NEON, cx, cy - 100)
            
            modo_formatado = self.modo_jogo.replace('_', ' ')
            btn_manter_modo = desenhar_botao_dinamico(self.tela, f"CONTINUAR EM: {modo_formatado}", self.fonte_sub, CIANO_NEON, cx, cy + 30, self.botao_selecionado == 0)
            btn_mudar_modo = desenhar_botao_dinamico(self.tela, "ESCOLHER NOVO MODO", self.fonte_sub, ROSA_NEON, cx, cy + 120, self.botao_selecionado == 1)
            
            self.botoes_hitboxes.extend([btn_manter_modo, btn_mudar_modo])

        elif self.estado == "MENU_MODO":
            desenhar_texto(self.tela, "SISTEMA PRINCIPAL", self.fonte_titulo, BRANCO, cx, cy - 230)
            
            btn_corrida = desenhar_botao_dinamico(self.tela, "CORRIDA (SPEEDRUN)", self.fonte_sub, CIANO_NEON, cx, cy - 110, self.botao_selecionado == 0)
            btn_corrida_hard = desenhar_botao_dinamico(self.tela, "CORRIDA HARDCORE (PERMADEATH)", self.fonte_sub, CIANO_NEON, cx, cy - 40, self.botao_selecionado == 1)
            btn_sobre = desenhar_botao_dinamico(self.tela, "SOBREVIVÊNCIA (INFINITO)", self.fonte_sub, ROSA_NEON, cx, cy + 30, self.botao_selecionado == 2)
            btn_hard = desenhar_botao_dinamico(self.tela, "SOBREVIVÊNCIA HARDCORE (BRUTAL)", self.fonte_sub, VERMELHO_SANGUE, cx, cy + 100, self.botao_selecionado == 3)
            btn_info = desenhar_botao_dinamico(self.tela, "? ENTENDER OS MODOS ?", self.fonte_sub, AMARELO_DADO, cx, cy + 190, self.botao_selecionado == 4)
            
            self.botoes_hitboxes.extend([btn_corrida, btn_corrida_hard, btn_sobre, btn_hard, btn_info])
            desenhar_texto(self.tela, "Navegue com Mouse ou Setas + Enter", self.fonte_texto, CINZA_CLARO, cx, ALTURA_TELA - 40)

        elif self.estado == "TELA_INFO_MODOS":
            desenhar_texto(self.tela, "MANUAL DOS MODOS DE JOGO", self.fonte_titulo, AMARELO_DADO, cx, 60)
            
            largura_painel, altura_painel = min(1150, LARGURA_TELA - 40), min(460, ALTURA_TELA - 200)
            surf_painel = criar_painel_transparente(largura_painel, altura_painel)
            
            painel_rect = pygame.Rect(0, 0, largura_painel, altura_painel)
            painel_rect.center = (cx, cy - 20)
            self.tela.blit(surf_painel, painel_rect.topleft)
            
            x_esq = painel_rect.left + 50
            
            y_base = painel_rect.top + 40
            desenhar_texto(self.tela, "MODO CORRIDA:", self.fonte_sub, CIANO_NEON, x_esq, y_base, alinhamento="esquerda")
            desenhar_texto(self.tela, "Complete 10 fases no menor tempo. Se morrer, você repete apenas a fase atual.", self.fonte_desc, BRANCO, x_esq, y_base + 35, alinhamento="esquerda")
            
            y_base = painel_rect.top + 140
            desenhar_texto(self.tela, "MODO CORRIDA HARDCORE:", self.fonte_sub, CIANO_NEON, x_esq, y_base, alinhamento="esquerda")
            desenhar_texto(self.tela, "Complete 10 fases. Se a nave for destruída, VOCÊ VOLTA PARA A FASE 1 e o tempo zera!", self.fonte_desc, BRANCO, x_esq, y_base + 35, alinhamento="esquerda")
            
            y_base = painel_rect.top + 240
            desenhar_texto(self.tela, "MODO SOBREVIVÊNCIA:", self.fonte_sub, ROSA_NEON, x_esq, y_base, alinhamento="esquerda")
            desenhar_texto(self.tela, "Sobreviva o máximo que puder. Inimigos surgem e ficam mais rápidos com o tempo.", self.fonte_desc, BRANCO, x_esq, y_base + 35, alinhamento="esquerda")
            
            y_base = painel_rect.top + 340
            desenhar_texto(self.tela, "MODO SOBREVIVÊNCIA HARDCORE:", self.fonte_sub, VERMELHO_SANGUE, x_esq, y_base, alinhamento="esquerda")
            desenhar_texto(self.tela, "Inimigos nascem o dobro de rápido e a velocidade de movimento cresce drasticamente.", self.fonte_desc, BRANCO, x_esq, y_base + 35, alinhamento="esquerda")
            
            btn_voltar = desenhar_botao_dinamico(self.tela, "VOLTAR PARA O MENU", self.fonte_sub, VERDE_NEON, cx, cy + 280, self.botao_selecionado == 0)
            self.botoes_hitboxes.append(btn_voltar)

        elif self.estado == "TELA_HOTKEYS":
            desenhar_texto(self.tela, "CONTROLES DO SISTEMA", self.fonte_titulo, VERDE_NEON, cx, 100)
            
            comandos = [
                ("W A S D / SETAS", "Mover a Nave"),
                ("BARRA DE ESPAÇO", "DASH (Invencibilidade Rápida)"),
                ("TECLA ESC", "Pausar ou Voltar Menus"),
                ("TECLA F11", "Ativar/Desativar Tela Cheia")
            ]
            for i, (tecla, desc) in enumerate(comandos):
                y_pos = 240 + (i * 70) 
                desenhar_texto(self.tela, tecla, self.fonte_sub, CIANO_NEON, cx - 40, y_pos, alinhamento="direita")
                desenhar_texto(self.tela, "- " + desc, self.fonte_texto, BRANCO, cx + 40, y_pos, alinhamento="esquerda")
                
            btn_prox = desenhar_botao_dinamico(self.tela, "AVANÇAR PARA AMEAÇAS", self.fonte_sub, ROSA_NEON, cx, cy + 240, self.botao_selecionado == 0)
            self.botoes_hitboxes.append(btn_prox)

        elif self.estado == "TELA_INIMIGOS":
            desenhar_texto(self.tela, "ARQUIVO DE AMEAÇAS", self.fonte_titulo, VERMELHO_SANGUE, cx, 60)
            
            largura_painel, altura_painel = min(1100, LARGURA_TELA - 40), min(480, ALTURA_TELA - 200)
            surf_painel = criar_painel_transparente(largura_painel, altura_painel)
            
            painel_rect = pygame.Rect(0, 0, largura_painel, altura_painel)
            painel_rect.center = (cx, cy - 10)
            self.tela.blit(surf_painel, painel_rect.topleft)
            
            espacamento_horizontal = painel_rect.left + 150 

            y_base = painel_rect.top + 50
            desenhar_brilho_neon(self.tela, ROSA_NEON, painel_rect.left + 80, y_base + 20, 18, 2)
            pygame.draw.circle(self.tela, ROSA_NEON, (painel_rect.left + 80, y_base + 20), 18)
            pygame.draw.circle(self.tela, BRANCO, (painel_rect.left + 80, y_base + 20), 6)
            desenhar_texto(self.tela, "SENTINELA (O Básico):", self.fonte_sub, ROSA_NEON, espacamento_horizontal, y_base, alinhamento="esquerda")
            desenhar_texto(self.tela, "Patrulha a área rebatendo nas paredes.", self.fonte_desc, BRANCO, espacamento_horizontal, y_base + 35, alinhamento="esquerda")
            desenhar_texto(self.tela, "Cuidado com o efeito manada quando eles se agrupam.", self.fonte_desc, CINZA_CLARO, espacamento_horizontal, y_base + 65, alinhamento="esquerda")

            y_base = painel_rect.top + 190
            desenhar_brilho_neon(self.tela, VERMELHO_SANGUE, painel_rect.left + 80, y_base + 20, 18, 2)
            pygame.draw.circle(self.tela, VERMELHO_SANGUE, (painel_rect.left + 80, y_base + 20), 18)
            pygame.draw.circle(self.tela, BRANCO, (painel_rect.left + 80, y_base + 20), 6)
            desenhar_texto(self.tela, "CAÇADOR (A Sanguessuga):", self.fonte_sub, VERMELHO_SANGUE, espacamento_horizontal, y_base, alinhamento="esquerda")
            desenhar_texto(self.tela, "Possui navegação autônoma avançada.", self.fonte_desc, BRANCO, espacamento_horizontal, y_base + 35, alinhamento="esquerda")
            desenhar_texto(self.tela, "Persegue sua assinatura de calor continuamente, tente despistá-lo.", self.fonte_desc, CINZA_CLARO, espacamento_horizontal, y_base + 65, alinhamento="esquerda")

            y_base = painel_rect.top + 330
            desenhar_brilho_neon(self.tela, LARANJA_NEON, painel_rect.left + 80, y_base + 20, 18, 2)
            pygame.draw.circle(self.tela, LARANJA_NEON, (painel_rect.left + 80, y_base + 20), 18)
            pygame.draw.circle(self.tela, BRANCO, (painel_rect.left + 80, y_base + 20), 6)
            desenhar_texto(self.tela, "KAMIKAZE (O Fuzil):", self.fonte_sub, LARANJA_NEON, espacamento_horizontal, y_base, alinhamento="esquerda")
            desenhar_texto(self.tela, "Aguarde o feixe de mira vermelho aparecer, indicando que ele travou no alvo.", self.fonte_desc, BRANCO, espacamento_horizontal, y_base + 35, alinhamento="esquerda")
            desenhar_texto(self.tela, "Espere o disparo e use o Dash (Espaço) no momento exato para esquivar!", self.fonte_desc, CINZA_CLARO, espacamento_horizontal, y_base + 65, alinhamento="esquerda")

            btn_iniciar = desenhar_botao_dinamico(self.tela, "INICIAR SEQUÊNCIA DE JOGO", self.fonte_sub, VERDE_NEON, cx, cy + 290, self.botao_selecionado == 0)
            self.botoes_hitboxes.append(btn_iniciar)

        elif self.estado in ["JOGANDO", "PAUSA"]:
            offset_x = random.randint(-8, 8) if self.shake_frames > 0 else 0
            offset_y = random.randint(-8, 8) if self.shake_frames > 0 else 0
            if self.shake_frames > 0 and self.estado == "JOGANDO": self.shake_frames -= 1

            self.tela.blit(self.blur_surf, (0, 0))
            surf_jogo = pygame.Surface((LARGURA_TELA, ALTURA_TELA), pygame.SRCALPHA)
            desenhar_grade_jogo(surf_jogo)

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
            
            if self.modo_jogo in ["CORRIDA", "CORRIDA_HARDCORE"]:
                texto_tempo = f"{self.tempo_corrida:.1f}s"
                desc_hud = "CORRIDA HARDCORE" if self.modo_jogo == "CORRIDA_HARDCORE" else "CORRIDA"
                desenhar_texto(self.tela, f"{desc_hud} - FASE {self.fase_atual}/10", self.fonte_sub, BRANCO, 20, 30, alinhamento="esquerda")
            else:
                texto_tempo = f"{self.tempo_sobrevivencia:.1f}s"
                titulo_hud = "MODO SOBREVIVÊNCIA" if self.modo_jogo == "SOBREVIVENCIA" else "SOBREVIVÊNCIA HARDCORE"
                cor_hud = BRANCO if self.modo_jogo == "SOBREVIVENCIA" else VERMELHO_SANGUE
                desenhar_texto(self.tela, titulo_hud, self.fonte_sub, cor_hud, 20, 30, alinhamento="esquerda")
            
            desenhar_texto(self.tela, texto_tempo, self.fonte_sub, VERDE_NEON, LARGURA_TELA - 20, 30, alinhamento="direita")

            cor_dash = VERDE_NEON if self.player.dash_cooldown == 0 else ROSA_NEON
            largura_dash = 100 * (1 - (self.player.dash_cooldown / 45))
            pygame.draw.rect(self.tela, cor_dash, (cx - 50, 25, largura_dash, 10))
            pygame.draw.rect(self.tela, BRANCO, (cx - 50, 25, 100, 10), 1)

            if self.estado == "PAUSA":
                overlay = pygame.Surface((LARGURA_TELA, ALTURA_TELA), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 180)) 
                self.tela.blit(overlay, (0, 0))
                
                desenhar_texto(self.tela, "SISTEMA PAUSADO", self.fonte_titulo, BRANCO, cx, cy - 100)
                
                btn_cont = desenhar_botao_dinamico(self.tela, "CONTINUAR [ESC]", self.fonte_sub, VERDE_NEON, cx, cy + 30, self.botao_selecionado == 0)
                btn_sair = desenhar_botao_dinamico(self.tela, "ABANDONAR PARTIDA", self.fonte_sub, VERMELHO_SANGUE, cx, cy + 120, self.botao_selecionado == 1)
                
                self.botoes_hitboxes.append(btn_cont)
                self.botoes_hitboxes.append(btn_sair)

        elif self.estado == "RANKING":
            titulo = f"GAME OVER - {self.modo_jogo.replace('_', ' ')}" 
            cor_titulo = VERMELHO_SANGUE if "HARDCORE" in self.modo_jogo else (VERDE_NEON if "CORRIDA" in self.modo_jogo else ROSA_NEON)
            desenhar_texto(self.tela, titulo, self.fonte_titulo, cor_titulo, cx, 50)
            
            largura_rank, altura_rank = 700, 410
            surf_rank = criar_painel_transparente(largura_rank, altura_rank)
            rect_ranking = pygame.Rect(0, 0, largura_rank, altura_rank)
            rect_ranking.center = (cx, cy - 50)
            
            self.tela.blit(surf_rank, rect_ranking.topleft)
            
            # --- INFO DA PARTIDA ATUAL ---
            desenhar_texto(self.tela, "DESEMPENHO DA MISSÃO:", self.fonte_sub, VERDE_NEON, cx, rect_ranking.top + 25)
            texto_desempenho = f"Tempo: {self.ultimo_tempo:.1f}s    |    Sua Posição: {self.ultima_posicao}º Lugar"
            desenhar_texto(self.tela, texto_desempenho, self.fonte_sub, BRANCO, cx, rect_ranking.top + 60)
            
            # Linha divisória
            pygame.draw.line(self.tela, CINZA_ESCURO, (rect_ranking.left + 50, rect_ranking.top + 95), (rect_ranking.right - 50, rect_ranking.top + 95), 2)
            
            # --- TOP 5 ---
            desenhar_texto(self.tela, f"--- TOP 5 {self.modo_jogo.replace('_', ' ')} ---", self.fonte_sub, CIANO_NEON, cx, rect_ranking.top + 130)
            
            if self.modo_jogo == "CORRIDA": chave_modo = "Corrida"
            elif self.modo_jogo == "CORRIDA_HARDCORE": chave_modo = "Corrida_Hardcore"
            elif self.modo_jogo == "SOBREVIVENCIA": chave_modo = "Sobrevivencia"
            else: chave_modo = "Hardcore"
            top5 = self.ranking.get(chave_modo, [])
            
            for i, reg in enumerate(top5[:5]):
                cor = AMARELO_DADO if reg.get('id', 0) == self.ranking[chave_modo][self.ultima_posicao-1].get('id', 0) else BRANCO
                y_pos = rect_ranking.top + 180 + (i * 40)
                desenhar_texto(self.tela, f"{i+1}º {reg['nome']}", self.fonte_sub, cor, rect_ranking.left + 80, y_pos, alinhamento="esquerda")
                desenhar_texto(self.tela, f"{reg['tempo']:.1f}s", self.fonte_sub, cor, rect_ranking.right - 80, y_pos, alinhamento="direita")
            
            btn_replay = desenhar_botao_dinamico(self.tela, "JOGAR NOVAMENTE (MESMO MODO)", self.fonte_sub, VERDE_NEON, cx, rect_ranking.bottom + 40, self.botao_selecionado == 0)
            btn_manter = desenhar_botao_dinamico(self.tela, "MANTER PILOTO (MUDAR MODO)", self.fonte_sub, CIANO_NEON, cx, rect_ranking.bottom + 110, self.botao_selecionado == 1)
            btn_novo = desenhar_botao_dinamico(self.tela, "CRIAR NOVO PILOTO", self.fonte_sub, ROSA_NEON, cx, rect_ranking.bottom + 180, self.botao_selecionado == 2)
            
            self.botoes_hitboxes.extend([btn_replay, btn_manter, btn_novo])

        self.tela.blit(self.crt_overlay, (0, 0))

        if self.is_fullscreen:
            self.tela_real.blit(self.tela, (0, 0))
        else:
            # Pega o novo tamanho da janela caso tenha mudado via alternar_tela_cheia
            w, h = self.tela_real.get_size()
            tela_redimensionada = pygame.transform.scale(self.tela, (w, h))
            self.tela_real.blit(tela_redimensionada, (0, 0))

        pygame.display.flip()

    def acionar_botao(self):
        if self.estado == "INPUT_NOME" and self.botao_selecionado == 0:
            if len(self.nome_jogador) > 0: 
                if self.veio_do_game_over and self.modo_jogo != "":
                    self.estado = "PERGUNTA_MODO"
                else:
                    self.estado = "MENU_MODO"
                self.botao_selecionado = 0
                
        elif self.estado == "PERGUNTA_MODO":
            self.veio_do_game_over = False
            if self.botao_selecionado == 0:
                self.estado = "TELA_INIMIGOS" 
            elif self.botao_selecionado == 1:
                self.estado = "MENU_MODO"
            self.botao_selecionado = 0

        elif self.estado == "MENU_MODO":
            if self.botao_selecionado == 0: self.modo_jogo = "CORRIDA"
            elif self.botao_selecionado == 1: self.modo_jogo = "CORRIDA_HARDCORE"
            elif self.botao_selecionado == 2: self.modo_jogo = "SOBREVIVENCIA"
            elif self.botao_selecionado == 3: self.modo_jogo = "HARDCORE" 
            elif self.botao_selecionado == 4: 
                self.estado = "TELA_INFO_MODOS"
                self.botao_selecionado = 0
                return

            self.estado = "TELA_HOTKEYS"
            self.botao_selecionado = 0

        elif self.estado == "TELA_INFO_MODOS" and self.botao_selecionado == 0:
            self.estado = "MENU_MODO"
            self.botao_selecionado = 0
                
        elif self.estado == "TELA_HOTKEYS" and self.botao_selecionado == 0:
            self.estado = "TELA_INIMIGOS"
            self.botao_selecionado = 0
            
        elif self.estado == "TELA_INIMIGOS" and self.botao_selecionado == 0:
            self.fase_atual = 1
            self.iniciar_fase()
            
        elif self.estado == "PAUSA":
            if self.botao_selecionado == 0: self.estado = "JOGANDO"
            elif self.botao_selecionado == 1: 
                self.estado = "MENU_MODO"
                self.botao_selecionado = 0
                
        elif self.estado == "RANKING":
            if self.botao_selecionado == 0: # JOGAR NOVAMENTE
                self.fase_atual = 1
                self.iniciar_fase()
            elif self.botao_selecionado == 1: # MANTER PILOTO (MUDAR MODO)
                self.estado = "MENU_MODO"
            elif self.botao_selecionado == 2: # NOVO PILOTO
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
                    
                if event.type == pygame.KEYDOWN and event.key == pygame.K_F11: self.alternar_tela_cheia()
                if event.type == pygame.KEYDOWN:
                    if event.key in [pygame.K_MINUS, pygame.K_KP_MINUS]: self.alterar_volume(-0.1)
                    elif event.key in [pygame.K_PLUS, pygame.K_KP_PLUS, pygame.K_EQUALS]: self.alterar_volume(0.1)
                    elif event.key == pygame.K_ESCAPE:
                        if self.estado == "MENU_MODO": self.estado = "INPUT_NOME"
                        elif self.estado == "TELA_INFO_MODOS": self.estado = "MENU_MODO"
                        elif self.estado == "TELA_HOTKEYS": self.estado = "MENU_MODO"
                        elif self.estado == "TELA_INIMIGOS": self.estado = "TELA_HOTKEYS"
                        elif self.estado == "PERGUNTA_MODO": self.estado = "INPUT_NOME"
                        elif self.estado == "JOGANDO":
                            self.estado = "PAUSA"
                            self.botao_selecionado = 0
                        elif self.estado == "PAUSA":
                            self.estado = "JOGANDO"
                
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
                    
                    if num_botoes > 0:
                        if event.key in [pygame.K_UP, pygame.K_w, pygame.K_LEFT, pygame.K_a]:
                            self.botao_selecionado = (self.botao_selecionado - 1) % num_botoes
                        elif event.key in [pygame.K_DOWN, pygame.K_s, pygame.K_RIGHT, pygame.K_d]:
                            self.botao_selecionado = (self.botao_selecionado + 1) % num_botoes
                            
                    if event.key == pygame.K_RETURN: self.acionar_botao()
                    if self.estado in ["TELA_INFO_MODOS", "TELA_HOTKEYS", "TELA_INIMIGOS"] and event.key == pygame.K_SPACE: 
                        self.acionar_botao()

            if self.estado == "JOGANDO": self.atualizar_jogo()
            self.desenhar()

if __name__ == "__main__":
    jogo = NeonSurge()
    jogo.executar()