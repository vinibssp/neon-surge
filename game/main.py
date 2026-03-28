from __future__ import annotations

import pygame

from game.audio import (
    AudioDirector,
    AudioRouter,
    AudioSettingsManager,
    MixerBackend,
    build_default_audio_catalog,
    build_default_audio_settings,
)
from game.config import SCREEN_HEIGHT, SCREEN_WIDTH, WINDOW_TITLE
from game.core.display_settings import DisplaySettingsManager
from game.core.game import Game
from game.core.input_settings import InputSettingsManager
from game.core.localization import LocalizationManager
from game.core.scene_stack import SceneStack
from game.scenes.main_menu_scene import MainMenuScene
from game.scenes.player_name_scene import PlayerNameScene
from game.services.ranking_service import RankingService


def main() -> None:
    pygame.init()
    pygame.joystick.init()
    # Initial joystick count check
    _ = pygame.joystick.get_count()
        
    display_settings_manager = DisplaySettingsManager()
    screen = display_settings_manager.apply_display_mode()
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
    audio_settings_manager = AudioSettingsManager(
        settings=audio_settings,
        backend=audio_backend,
        is_ducked_provider=lambda: audio_director.state.is_ducked,
    )
    stack.audio_settings_manager = audio_settings_manager
    stack.display_settings_manager = display_settings_manager
    stack.input_settings_manager = InputSettingsManager()
    stack.localization_manager = LocalizationManager()
    audio_director.initialize()
    audio_backend.apply_runtime_settings(is_ducked=False)

    if RankingService().get_player_name() is None:
        stack.push(PlayerNameScene(stack, is_first_time=True))
    else:
        stack.push(MainMenuScene(stack))

    game = Game(screen=screen, scene_stack=stack)
    game.run()

    audio_director.shutdown()

    pygame.quit()


if __name__ == "__main__":
    main()
