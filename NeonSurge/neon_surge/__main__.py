"""Allows running with: python -m neon_surge"""
import pygame
from .game import Game

pygame.init()
Game().run()
