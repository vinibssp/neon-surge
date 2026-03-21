"""
main.py — entry point
=====================
Run from the project root:

    python main.py
    # or
    python -m neon_surge
"""
import pygame
from neon_surge import Game

if __name__ == "__main__":
    pygame.init()
    game = Game()
    game.run()
