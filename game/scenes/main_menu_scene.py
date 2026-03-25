from __future__ import annotations

import pygame

from game.config import SCREEN_HEIGHT, SCREEN_WIDTH
from game.modes.labyrinth_mode import LabyrinthMode
from game.modes.race_infinite_mode import RaceInfiniteMode
from game.modes.race_mode import RaceMode
from game.modes.survival_hardcore_mode import SurvivalHardcoreMode
from game.modes.survival_mode import SurvivalMode
from game.scenes.game_scene import GameScene
from game.scenes.menus._base_menu_scene import BaseMenuScene
from game.ui.components import ButtonConfig, LabelConfig
from game.ui.ui_factory import UIFactory


class MainMenuScene(BaseMenuScene):
    def __init__(self, stack) -> None:
        super().__init__(stack)

        title = UIFactory.label(
            LabelConfig(
                text="NEON SURGE 2",
                rect=pygame.Rect((SCREEN_WIDTH // 2 - 180, 120), (360, 64)),
                variant="title",
            ),
            manager=self.ui_manager,
        )
        subtitle = UIFactory.label(
            LabelConfig(
                text="Selecione um modo",
                rect=pygame.Rect((SCREEN_WIDTH // 2 - 150, 180), (300, 40)),
                variant="subtitle",
            ),
            manager=self.ui_manager,
        )
        del title, subtitle

        race_button = UIFactory.button(
            ButtonConfig(
                text="Corrida",
                rect=pygame.Rect((SCREEN_WIDTH // 2 - 140, 270), (280, 56)),
                variant="primary",
            ),
            manager=self.ui_manager,
        )
        survival_button = UIFactory.button(
            ButtonConfig(
                text="Sobrevivencia",
                rect=pygame.Rect((SCREEN_WIDTH // 2 - 140, 340), (280, 56)),
                variant="primary",
            ),
            manager=self.ui_manager,
        )
        labyrinth_button = UIFactory.button(
            ButtonConfig(
                text="Labirinto",
                rect=pygame.Rect((SCREEN_WIDTH // 2 - 140, 410), (280, 56)),
                variant="primary",
            ),
            manager=self.ui_manager,
        )
        quit_button = UIFactory.button(
            ButtonConfig(
                text="Sair",
                rect=pygame.Rect((SCREEN_WIDTH // 2 - 140, 492), (280, 52)),
                variant="danger",
            ),
            manager=self.ui_manager,
        )

        self.set_navigator(
            buttons=[race_button, survival_button, labyrinth_button, quit_button],
            actions={
                race_button: lambda: self.stack.replace(GameScene(self.stack, RaceMode())),
                survival_button: lambda: self.stack.replace(GameScene(self.stack, SurvivalMode())),
                labyrinth_button: lambda: self.stack.replace(GameScene(self.stack, LabyrinthMode())),
                quit_button: self._quit,
            },
            on_cancel=self._quit,
        )

    def _quit(self) -> None:
        self.stack.pop()
