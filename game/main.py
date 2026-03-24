from __future__ import annotations

import pygame

from game.audio import (
    AudioDirector,
    AudioRouter,
    MixerBackend,
    build_default_audio_catalog,
    build_default_audio_settings,
)
from game.config import SCREEN_HEIGHT, SCREEN_WIDTH, WINDOW_TITLE
from game.core.game import Game
from game.core.scene_stack import SceneStack
from game.scenes.main_menu_scene import MainMenuScene


def main() -> None:
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption(WINDOW_TITLE)

    stack = SceneStack()

    audio_settings = build_default_audio_settings()
    audio_catalog = build_default_audio_catalog()
    audio_router = AudioRouter(catalog=audio_catalog, settings=audio_settings)
    audio_backend = MixerBackend(settings=audio_settings)
    audio_director = AudioDirector(
        event_bus=stack.event_bus,
        router=audio_router,
        backend=audio_backend,
        catalog=audio_catalog,
        settings=audio_settings,
    )
    audio_director.initialize()

    stack.push(MainMenuScene(stack))

    game = Game(screen=screen, scene_stack=stack)
    game.run()

    audio_director.shutdown()

    pygame.quit()


if __name__ == "__main__":
    main()
