from __future__ import annotations

import pygame
import pygame_gui

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
from game.services.ranking_service import RankingService
from game.ui.components import ButtonConfig, LabelConfig, PanelConfig, create_button, create_label, create_panel

class MainMenuScene(BaseMenuScene):
    def __init__(self, stack) -> None:
        super().__init__(stack)
        self._elapsed_time = 0.0
        self._background_renderer = CyberpunkMenuBackgroundRenderer()
        self._selected_mode_tag: str | None = None
        self._btn_to_mode_tag: dict[object, str] = {}
        self._init_ui()

    def _init_ui(self) -> None:
        self._btn_to_mode_tag.clear()
        self._selected_mode_tag = None

        mode_info = {
            "race": (
                self.t("mode.race"),
                self.t("mode.race.desc"),
                self.t("mode.race.meta"),
            ),
            "race_infinite": (
                self.t("mode.race_infinite"),
                self.t("mode.race_infinite.desc"),
                self.t("mode.race_infinite.meta"),
            ),
            "survival": (
                self.t("mode.survival"),
                self.t("mode.survival.desc"),
                self.t("mode.survival.meta"),
            ),
            "hardcore": (
                self.t("mode.hardcore"),
                self.t("mode.hardcore.desc"),
                self.t("mode.hardcore.meta"),
            ),
            "labyrinth": (
                self.t("mode.labyrinth"),
                self.t("mode.labyrinth.desc"),
                self.t("mode.labyrinth.meta"),
            ),
            "training": (
                self.t("mode.training"),
                self.t("mode.training.desc"),
                self.t("mode.training.meta"),
            ),
        }

        # 1. Header
        create_label(
            LabelConfig(
                text=self.t("main.title"),
                rect=pygame.Rect((SCREEN_WIDTH // 2 - 400, 40), (800, 100)),
                variant="title",
            ),
            manager=self.ui_manager,
        )

        self._player_panel = create_panel(
            PanelConfig(rect=pygame.Rect((20, 20), (300, 68)), variant="hud"),
            manager=self.ui_manager,
        )

        create_label(
            LabelConfig(
                text=self._resolve_player_name(),
                rect=pygame.Rect((14, 18), (272, 28)),
                variant="value",
            ),
            manager=self.ui_manager,
            container=self._player_panel,
        )

        # 2. Corner Buttons
        # Top Right: Exit
        self._exit_btn = create_button(
            ButtonConfig(text="X", rect=pygame.Rect((SCREEN_WIDTH - 70, 20), (50, 50)), variant="danger"),
            manager=self.ui_manager
        )
        
        # Bottom Right: Help and Settings
        self._settings_btn = create_button(
            ButtonConfig(text="*", rect=pygame.Rect((SCREEN_WIDTH - 70, SCREEN_HEIGHT - 70), (50, 50)), variant="ghost"),
            manager=self.ui_manager
        )
        self._guide_btn = create_button(
            ButtonConfig(text="?", rect=pygame.Rect((SCREEN_WIDTH - 130, SCREEN_HEIGHT - 70), (50, 50)), variant="primary"),
            manager=self.ui_manager
        )
        self._language_btn = create_button(
            ButtonConfig(
                text=self._language_button_text(),
                rect=pygame.Rect((20, SCREEN_HEIGHT - 70), (80, 50)),
                variant="ghost",
            ),
            manager=self.ui_manager,
        )

        # 3. Mode Grid (Original Aesthetics - Centralized)
        btn_w, btn_h = 190, 60
        gap = 15
        cols = 6
        total_w = cols * btn_w + (cols - 1) * gap
        start_x = (SCREEN_WIDTH - total_w) // 2
        start_y = 320

        modes_list = [
            (self.t("mode.race"), "race", RaceMode(), "race"),
            (self.t("mode.race_infinite"), "race_infinite", RaceInfiniteMode(), "race_infinite"),
            (self.t("mode.survival"), "survival", SurvivalMode(), "survival"),
            (self.t("mode.hardcore"), "hardcore", SurvivalHardcoreMode(), "hardcore"),
            (self.t("mode.labyrinth"), "labyrinth", LabyrinthMode(), "labyrinth"),
            (self.t("mode.training"), "training", None, "training"),
        ]

        self._mode_btns = []
        for i, (name, tag, mode_obj, variant) in enumerate(modes_list):
            rect = pygame.Rect((start_x + i * (btn_w + gap), start_y), (btn_w, btn_h))
            btn = create_button(
                ButtonConfig(text=name, rect=rect, variant=variant),
                manager=self.ui_manager
            )
            self._mode_btns.append((btn, mode_obj, tag))
            self._btn_to_mode_tag[btn] = tag

        # 4. Info Card (Below Grid)
        self._info_panel = create_panel(
            PanelConfig(rect=pygame.Rect((SCREEN_WIDTH // 2 - 450, 420), (900, 140)), variant="hud"),
            manager=self.ui_manager
        )
        self._info_title = create_label(
            LabelConfig(text=self.t("main.info.select"), rect=pygame.Rect((20, 15), (860, 30)), variant="header"),
            manager=self.ui_manager, container=self._info_panel
        )
        self._info_desc = create_label(
            LabelConfig(
                text=self.t("main.info.default_desc"),
                rect=pygame.Rect((20, 50), (860, 70)),
                variant="guide_body"
            ),
            manager=self.ui_manager, container=self._info_panel
        )
        self._info_meta = create_label(
            LabelConfig(
                text=self.t("main.info.default_meta"),
                rect=pygame.Rect((20, 105), (860, 24)),
                variant="guide_accent"
            ),
            manager=self.ui_manager, container=self._info_panel
        )

        # 5. Global Ranking (Center Bottom)
        self._ranking_btn = create_button(
            ButtonConfig(
                text=self.t("main.ranking"),
                rect=pygame.Rect((SCREEN_WIDTH // 2 - 200, 580), (400, 50)),
                variant="primary"
            ),
            manager=self.ui_manager
        )

        # 6. Navigation
        from game.scenes.leaderboard_scene import LeaderboardScene
        controls = [b[0] for b in self._mode_btns] + [self._ranking_btn, self._guide_btn, self._settings_btn, self._exit_btn]
        
        actions = {
            self._ranking_btn: lambda: self.stack.push(LeaderboardScene(self.stack)),
            self._guide_btn: lambda: self.stack.push(GuideScene(self.stack)),
            self._settings_btn: lambda: self.stack.push(SettingsScene(self.stack)),
            self._language_btn: self._toggle_language,
            self._exit_btn: self._quit,
        }
        for btn, mode_obj, tag in self._mode_btns:
            if tag == "training":
                actions[btn] = lambda: self.stack.push(TrainingSetupScene(self.stack))
            else:
                actions[btn] = lambda m=mode_obj: self.stack.replace(GameScene(self.stack, m))

        controls.append(self._language_btn)
        self.set_navigator(controls=controls, actions=actions, on_cancel=self._quit)
        self._mode_info = mode_info
        self._sync_info_card_with_navigator()

    def _update_info_card(self, tag: str | None) -> None:
        if tag == self._selected_mode_tag:
            return
        if tag in self._mode_info:
            title, desc, meta = self._mode_info[tag]
            self._info_title.set_text(title)
            self._info_desc.set_text(desc)
            self._info_meta.set_text(meta)
            self._selected_mode_tag = tag
        else:
            self._info_title.set_text(self.t("main.info.ui_title"))
            self._info_desc.set_text(self.t("main.info.ui_desc"))
            self._info_meta.set_text(self.t("main.info.ui_meta"))
            self._selected_mode_tag = None

    def _sync_info_card_with_navigator(self) -> None:
        if self.navigator is None:
            return
        selected_control = self.navigator.selected_control
        selected_tag = self._btn_to_mode_tag.get(selected_control)
        self._update_info_card(selected_tag)

    def handle_input(self, events: list[pygame.event.Event]) -> None:
        for event in events:
            # Update on Hover
            if event.type == pygame.USEREVENT and event.user_type == pygame_gui.UI_BUTTON_ON_HOVERED:
                self._update_info_card(self._btn_to_mode_tag.get(event.ui_element))

        super().handle_input(events)
        self._sync_info_card_with_navigator()

    def on_enter(self) -> None:
        self.stack.event_bus.publish(AudioContextChanged(context="menu", reason="main_menu_entered"))

    def on_menu_update(self, dt: float) -> None:
        self._elapsed_time += dt

    def render_menu_background(self, screen: pygame.Surface) -> None:
        self._background_renderer.render(
            screen=screen,
            elapsed_time=self._elapsed_time,
            width=SCREEN_WIDTH,
            height=SCREEN_HEIGHT,
            sun_rise_progress=min(1.0, self._elapsed_time / 3.8),
        )

    def _quit(self) -> None:
        self.stack.pop()

    def _toggle_language(self) -> None:
        manager = self.stack.localization_manager
        if manager is None:
            return
        new_language = "en_US" if manager.language == "pt_BR" else "pt_BR"
        manager.set_language(new_language)
        self.ui_manager.clear_and_reset()
        self._init_ui()

    def _language_button_text(self) -> str:
        manager = self.stack.localization_manager
        if manager is None:
            return "PT"
        return "PT" if manager.language == "pt_BR" else "EN"

    def _resolve_player_name(self) -> str:
        player_name = (RankingService().get_player_name() or self.t("main.unknown_player")).strip()
        if not player_name:
            return self.t("main.unknown_player")
        return player_name[:24]
