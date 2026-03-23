import pygame

from .constants import ALTURA_TELA, LARGURA_TELA
from .entities import ParticulaMenu
from .systems.gameplay import (
    _atualizar_fantasmas_labirinto,
    _colide_com_paredes_labirinto,
    _gerar_layout_labirinto,
    _lidar_com_morte,
    _resolver_colisao_labirinto,
    _spawn_inimigos,
    _spawn_unitario,
    atualizar_jogo,
    atualizar_menu_interativo,
    entrar_menu_modo,
    iniciar_fase,
    obter_pads_menu,
)
from .services.ranking import carregar_ranking, salvar_ranking
from .rendering import desenhar, desenhar_controle_volume, desenhar_menu_configuracoes
from .runtime import acionar_botao, executar, voltar_configuracoes
from .services.audio import SoundManager


class NeonSurge:
    carregar_ranking = carregar_ranking
    salvar_ranking = salvar_ranking
    entrar_menu_modo = entrar_menu_modo
    obter_pads_menu = obter_pads_menu
    iniciar_fase = iniciar_fase
    _colide_com_paredes_labirinto = _colide_com_paredes_labirinto
    _atualizar_fantasmas_labirinto = _atualizar_fantasmas_labirinto
    _gerar_layout_labirinto = _gerar_layout_labirinto
    _resolver_colisao_labirinto = _resolver_colisao_labirinto
    _spawn_inimigos = _spawn_inimigos
    _spawn_unitario = _spawn_unitario
    atualizar_jogo = atualizar_jogo
    atualizar_menu_interativo = atualizar_menu_interativo
    _lidar_com_morte = _lidar_com_morte
    desenhar_controle_volume = desenhar_controle_volume
    desenhar_menu_configuracoes = desenhar_menu_configuracoes
    desenhar = desenhar
    acionar_botao = acionar_botao
    voltar_configuracoes = voltar_configuracoes
    executar = executar

    def __init__(self):
        pygame.init()
        pygame.mixer.init()

        self.volume_musica = 0.20
        self.volume_salvo = 0.20
        self.mutado = False
        self.sounds = SoundManager()
        self.sounds.set_sfx_volume(self.volume_musica)
        self.sounds.play_bgm("neon_surge/assets/sounds/trilha_menu.wav", self.volume_musica)

        self.rect_vol_mute = pygame.Rect(0, 0, 45, 45)
        self.rect_vol_config = pygame.Rect(0, 0, 45, 45)
        self.rect_vol_menos = pygame.Rect(0, 0, 35, 35)
        self.rect_vol_mais = pygame.Rect(0, 0, 35, 35)
        self.estado_anterior_config = "MENU_MODO"

        # Configurações de Vídeo
        self.info = pygame.display.Info()
        self.res_nativa = (self.info.current_w, self.info.current_h)
        self.is_fullscreen = False
        
        # Lista de resoluções e detecção da nativa
        self.resolucoes = [(1280, 720), (1366, 768), (1600, 900), (1920, 1080), (2560, 1440)]
        if self.res_nativa not in self.resolucoes:
            self.resolucoes.append(self.res_nativa)
            self.resolucoes.sort()
        
        self.res_idx = self.resolucoes.index((1280, 720)) if (1280, 720) in self.resolucoes else 0
        
        # Inicialização da tela
        self.aplicar_configuracoes_video()
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
        self.inimigos_treino_selecionados = {} # { type: count }
        self.fase_atual = 1
        self.veio_do_game_over = False

        self.botao_selecionado = 0
        self.botoes_hitboxes = []
        self.guia_aba = "MODOS"

        self.player = None
        self.inimigos = []
        self.projeteis_inimigos = []
        self.portais_inimigos = []
        self.coletaveis = []
        self.particulas = []
        self.particulas_menu = [ParticulaMenu() for _ in range(50)]
        self.portal_aberto = False

        self.tempo_corrida = 0.0
        self.tempo_sobrevivencia = 0.0
        self.temporizador_spawn = 0.0
        self.tempo_renascer_corrida = 0.0
        self.limite_inimigos_corrida = 0
        self.temporizador_buraco_negro = 8.0
        self.buracos_negros = []
        from .entities.hazards import LavaManager
        self.lava_manager = LavaManager()
        self.labirinto_paredes = []

        self.ranking = self.carregar_ranking()
        self.ultima_pos_mouse = (0, 0)
        self.ultima_posicao = 0
        self.ultimo_tempo = 0.0
        self.mortes_total_jogador = 0
        self.shake_frames = 0
        self.tempo_global = 0.0

    def calcular_rect_tela(self):
        """Calcula o retângulo de destino mantendo a proporção 16:9 (Letterboxing)."""
        largura_real, altura_real = self.tela_real.get_size()
        proporcao_alvo = LARGURA_TELA / ALTURA_TELA
        proporcao_real = largura_real / altura_real

        if proporcao_real > proporcao_alvo:
            # Tela mais larga que 16:9 (Pillarbox)
            nova_largura = int(altura_real * proporcao_alvo)
            nova_altura = altura_real
            off_x = (largura_real - nova_largura) // 2
            off_y = 0
        else:
            # Tela mais alta que 16:9 (Letterbox)
            nova_largura = largura_real
            nova_altura = int(largura_real / proporcao_alvo)
            off_x = 0
            off_y = (altura_real - nova_altura) // 2

        return pygame.Rect(off_x, off_y, nova_largura, nova_altura)

    def aplicar_configuracoes_video(self):
        """Centraliza a lógica de alteração de modo de vídeo."""
        res = self.resolucoes[self.res_idx]
        flags = pygame.DOUBLEBUF | pygame.HWSURFACE
        
        if self.is_fullscreen:
            flags |= pygame.FULLSCREEN
            # Em fullscreen, se a resolução escolhida for a nativa, usamos (0,0) para otimização do SO
            if res == self.res_nativa:
                self.tela_real = pygame.display.set_mode((0, 0), flags)
            else:
                self.tela_real = pygame.display.set_mode(res, flags)
        else:
            self.tela_real = pygame.display.set_mode(res, flags)

    def alternar_tela_cheia(self):
        self.is_fullscreen = not self.is_fullscreen
        self.aplicar_configuracoes_video()

    def alterar_resolucao(self, delta):
        self.res_idx = (self.res_idx + delta) % len(self.resolucoes)
        self.aplicar_configuracoes_video()
        self.sounds.play('menu_button')

    def obter_posicao_mouse(self):
        mx, my = pygame.mouse.get_pos()
        rect = self.calcular_rect_tela()
        
        mx -= rect.x
        my -= rect.y
        
        if rect.width > 0 and rect.height > 0:
            mx = mx * (LARGURA_TELA / rect.width)
            my = my * (ALTURA_TELA / rect.height)
            
        return mx, my

    def alterar_volume(self, delta):
        if self.mutado:
            self.alternar_mute()
        self.volume_musica = max(0.0, min(1.0, self.volume_musica + delta))
        self.sounds.set_bgm_volume(self.volume_musica)
        self.sounds.set_sfx_volume(self.volume_musica)

    def alterar_volume_musica(self, delta):
        if self.mutado:
            self.alternar_mute()
        novo = max(0.0, min(1.0, self.sounds.volume_musica + delta))
        self.volume_musica = novo
        self.sounds.set_bgm_volume(novo)

    def alterar_volume_sfx(self, delta):
        if self.mutado:
            self.alternar_mute()
        novo = max(0.0, min(1.0, self.sounds.volume_sfx + delta))
        self.sounds.set_sfx_volume(novo)
        self.sounds.play('menu_button')

    def alternar_mute(self):
        self.mutado = not self.mutado
        try:
            if self.mutado:
                self.volume_salvo = self.volume_musica
                self.volume_musica = 0.0
            else:
                self.volume_musica = self.volume_salvo
                if self.volume_musica == 0.0:
                    self.volume_musica = 0.4
            pygame.mixer.music.set_volume(self.volume_musica)
            self.sounds.set_sfx_volume(self.volume_musica)
        except:
            pass

    
