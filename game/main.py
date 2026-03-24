from __future__ import annotations

import pygame

from game.config import SCREEN_HEIGHT, SCREEN_WIDTH, WINDOW_TITLE
from game.core.game import Game
from game.core.scene_stack import SceneStack
from game.scenes.main_menu_scene import MainMenuScene


def main() -> None:
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption(WINDOW_TITLE)

    stack = SceneStack()
    stack.push(MainMenuScene(stack))

    game = Game(screen=screen, scene_stack=stack)
    game.run()

    pygame.quit()


if __name__ == "__main__":
    main()
