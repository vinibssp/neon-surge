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
    atualizar_jogo,
    atualizar_menu_interativo,
    entrar_menu_modo,
    iniciar_fase,
    obter_pads_menu,
)
from .services.ranking import carregar_ranking, salvar_ranking
from .rendering import desenhar, desenhar_controle_volume
from .runtime import acionar_botao, executar
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
    atualizar_jogo = atualizar_jogo
    atualizar_menu_interativo = atualizar_menu_interativo
    _lidar_com_morte = _lidar_com_morte
    desenhar_controle_volume = desenhar_controle_volume
    desenhar = desenhar
    acionar_botao = acionar_botao
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
        self.rect_vol_menos = pygame.Rect(0, 0, 35, 35)
        self.rect_vol_mais = pygame.Rect(0, 0, 35, 35)

        self.info = pygame.display.Info()
        self.is_fullscreen = True
        self.tela_real = pygame.display.set_mode((self.info.current_w, self.info.current_h), pygame.FULLSCREEN)
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
        self.labirinto_paredes = []
        self.labirinto_area = None
        self.labirinto_info = {}
        self.labirinto_armadilhas = []
        self.labirinto_fantasmas = []
        self.labirinto_tempo_restante = 0.0
        self.labirinto_tempo_max = 0.0
        self.shake_frames = 0
        self.tempo_global = 0

        self.tempo_para_lava = 30
        self.lava_ativa = False
        self.tempo_lava_restante = 0.0
        self.tipo_lava = 0
        self.lava_hitboxes = []
        self.aviso_lava = 0.0
        self.lava_lado_horizontal = None
        self.lava_lado_vertical = None

        self.ranking = self.carregar_ranking()
        self.ultima_pos_mouse = (0, 0)
        self.ultima_posicao = 0
        self.ultimo_tempo = 0.0
        self.mortes_total_jogador = 0

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
        if self.mutado:
            self.alternar_mute()
        self.volume_musica = max(0.0, min(1.0, self.volume_musica + delta))
        try:
            pygame.mixer.music.set_volume(self.volume_musica)
            self.sounds.set_sfx_volume(self.volume_musica)
        except:
            pass

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

    
