import pygame

pygame.init()
info = pygame.display.Info()

LARGURA_TELA = int(info.current_w * 0.8)
ALTURA_TELA = int(info.current_h * 0.8)
FPS = 60
ARQUIVO_RANKING = "ranking_completo.json"

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
