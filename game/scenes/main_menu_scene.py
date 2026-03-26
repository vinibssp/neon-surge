from __future__ import annotations

import pygame

from game.config import SCREEN_HEIGHT, SCREEN_WIDTH
from game.core.events import AudioContextChanged
from game.modes.labyrinth_mode import LabyrinthMode
from game.modes.race_infinite_mode import RaceInfiniteMode
from game.modes.race_mode import RaceMode
from game.modes.survival_hardcore_mode import SurvivalHardcoreMode
from game.modes.survival_mode import SurvivalMode
from game.scenes.game_scene import GameScene
from game.scenes.guide_scene import GuideScene
from game.scenes.menus._base_menu_scene import BaseMenuScene
from game.scenes.settings_scene import SettingsScene
from game.scenes.training_setup_scene import TrainingSetupScene
from game.scenes.services import CyberpunkMenuBackgroundRenderer
from game.ui.components import ButtonConfig, LabelConfig, create_button, create_label


class MainMenuScene(BaseMenuScene):
    def __init__(self, stack) -> None:
        super().__init__(stack)
        self._elapsed_time = 0.0
        self._background_renderer = CyberpunkMenuBackgroundRenderer()

        create_label(
            LabelConfig(
                text="NEON SURGE",
                rect=pygame.Rect((SCREEN_WIDTH // 2 - 430, 100), (860, 120)),
                variant="title",
            ),
            manager=self.ui_manager,
        )

        button_width, button_height = 180, 50
        gap = 15
        columns = 6
        total_grid_w = columns * button_width + (columns - 1) * gap
        start_x = (SCREEN_WIDTH - total_grid_w) // 2
        start_y = 380

        # Game Modes Row
        self._race_btn = create_button(
            ButtonConfig(text="CORRIDA", rect=pygame.Rect((start_x, start_y), (button_width, button_height)), variant="race"),
            manager=self.ui_manager
        )
        self._race_inf_btn = create_button(
            ButtonConfig(text="INFINITA", rect=pygame.Rect((start_x + (button_width + gap), start_y), (button_width, button_height)), variant="race_infinite"),
            manager=self.ui_manager
        )
        self._survival_btn = create_button(
            ButtonConfig(text="SOBREVIVÊNCIA", rect=pygame.Rect((start_x + 2 * (button_width + gap), start_y), (button_width, button_height)), variant="survival"),
            manager=self.ui_manager
        )
        self._hardcore_btn = create_button(
            ButtonConfig(text="HARDCORE", rect=pygame.Rect((start_x + 3 * (button_width + gap), start_y), (button_width, button_height)), variant="hardcore"),
            manager=self.ui_manager
        )
        self._labyrinth_btn = create_button(
            ButtonConfig(text="LABIRINTO", rect=pygame.Rect((start_x + 4 * (button_width + gap), start_y), (button_width, button_height)), variant="labyrinth"),
            manager=self.ui_manager
        )
        self._training_btn = create_button(
            ButtonConfig(text="TREINO", rect=pygame.Rect((start_x + 5 * (button_width + gap), start_y), (button_width, button_height)), variant="training"),
            manager=self.ui_manager
        )

        # Utils Buttons
        from game.scenes.leaderboard_scene import LeaderboardScene
        self._ranking_btn = create_button(
            ButtonConfig(
                text="RANKING",
                rect=pygame.Rect((SCREEN_WIDTH // 2 - 250, 500), (240, 50)),
                variant="primary",
            ),
            manager=self.ui_manager,
        )
        self._guide_btn = create_button(
            ButtonConfig(
                text="MANUAL",
                rect=pygame.Rect((SCREEN_WIDTH // 2 + 10, 500), (240, 50)),
                variant="primary",
            ),
            manager=self.ui_manager,
        )
        
        self._settings_btn = create_button(
            ButtonConfig(
                text="CONFIGURAÇÕES",
                rect=pygame.Rect((SCREEN_WIDTH // 2 - 120, 570), (240, 50)),
                variant="ghost",
            ),
            manager=self.ui_manager,
        )

        self._exit_btn = create_button(
            ButtonConfig(
                text="SAIR DO SISTEMA",
                rect=pygame.Rect((SCREEN_WIDTH // 2 - 120, 640), (240, 50)),
                variant="danger",
            ),
            manager=self.ui_manager,
        )

        self.set_navigator(
            controls=[
                self._race_btn, self._race_inf_btn, self._survival_btn,
                self._hardcore_btn, self._labyrinth_btn, self._training_btn,
                self._ranking_btn, self._guide_btn,
                self._settings_btn, self._exit_btn
            ],
            actions={
                self._race_btn: lambda: self.stack.replace(GameScene(self.stack, RaceMode())),
                self._race_inf_btn: lambda: self.stack.replace(GameScene(self.stack, RaceInfiniteMode())),
                self._survival_btn: lambda: self.stack.replace(GameScene(self.stack, SurvivalMode())),
                self._hardcore_btn: lambda: self.stack.replace(GameScene(self.stack, SurvivalHardcoreMode())),
                self._labyrinth_btn: lambda: self.stack.replace(GameScene(self.stack, LabyrinthMode())),
                self._training_btn: lambda: self.stack.push(TrainingSetupScene(self.stack)),
                self._ranking_btn: lambda: self.stack.push(LeaderboardScene(self.stack)),
                self._guide_btn: lambda: self.stack.push(GuideScene(self.stack)),
                self._settings_btn: lambda: self.stack.push(SettingsScene(self.stack)),
                self._exit_btn: self._quit,
            },
            on_cancel=self._quit,
        )

    def on_enter(self) -> None:
        self.stack.event_bus.publish(AudioContextChanged(context="menu", reason="main_menu_entered"))

    def on_menu_update(self, dt: float) -> None:
        self._elapsed_time += dt

    def render_menu_background(self, screen: pygame.Surface) -> None:
        sunrise_progress = min(1.0, self._elapsed_time / 3.8)
        self._background_renderer.render(
            screen=screen,
            elapsed_time=self._elapsed_time,
            width=SCREEN_WIDTH,
            height=SCREEN_HEIGHT,
            sun_rise_progress=sunrise_progress,
            sun_center_text="2",
        )

    def _quit(self) -> None:
        self.stack.pop()
