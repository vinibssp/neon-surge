from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

import pygame

from game.config import SCREEN_HEIGHT, SCREEN_WIDTH
from game.core.events import AudioContextChanged
from game.modes.mode_config import OneVsOneConfig, RaceConfig, SurvivalConfig
from game.modes.one_vs_one_mode import OneVsOneMode
from game.modes.race_mode import RaceMode
from game.modes.survival_mode import SurvivalMode
from game.scenes.base_menu_scene import BaseMenuScene
from game.scenes.game_scene import GameScene
from game.scenes.menu_overlay_scenes import HelpOverlayScene, SettingsOverlayScene
from game.scenes.services import CyberpunkMenuBackgroundRenderer
from game.ui.components.base_widgets import create_button, create_centered_panel, create_text_box
from game.ui.types import UIControl, ButtonConfig, PanelConfig, TextBoxConfig


NEON_CYAN = (0, 220, 255)
NEON_MAGENTA = (255, 55, 220)
NEON_LIME = (150, 255, 70)


@dataclass(frozen=True)
class ModeCardData:
    title: str
    description: str
    color: tuple[int, int, int]


class MainMenuScene(BaseMenuScene):
    def __init__(self, stack) -> None:
        super().__init__(stack)
        self.elapsed_time = 0.0
        self._last_mode_card_index: int | None = None
        self.background_renderer = CyberpunkMenuBackgroundRenderer()
        self._menu_panel_rect = pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT)
        self._mode_card_glow_rect = pygame.Rect(138, 126, 1004, 186)

        self.menu_panel = create_centered_panel(
            manager=self.ui_manager,
            screen_size=(SCREEN_WIDTH, SCREEN_HEIGHT),
            config=PanelConfig(size=(SCREEN_WIDTH, SCREEN_HEIGHT), object_id="#menu_panel"),
        )
        self.mode_card = create_centered_panel(
            manager=self.ui_manager,
            screen_size=(SCREEN_WIDTH, SCREEN_HEIGHT),
            config=PanelConfig(size=(1004, 186), object_id="#mode_card", container=self.menu_panel),
        )
        self.mode_card.set_relative_position((138, 126))

        self.mode_title_box = create_text_box(
            manager=self.ui_manager,
            container=self.mode_card,
            config=TextBoxConfig(html_text="", rect=pygame.Rect(16, 10, 972, 84), object_id="#mode_title"),
        )
        self.mode_description_box = create_text_box(
            manager=self.ui_manager,
            container=self.mode_card,
            config=TextBoxConfig(html_text="", rect=pygame.Rect(16, 94, 972, 78), object_id="#mode_description"),
        )

        self.race_button: UIControl = create_button(
            manager=self.ui_manager,
            container=self.menu_panel,
            config=ButtonConfig(text="CORRIDA", rect=pygame.Rect(130, 370, 240, 92), object_id="#mode_button_race"),
        )
        self.infinite_button: UIControl = create_button(
            manager=self.ui_manager,
            container=self.menu_panel,
            config=ButtonConfig(text="INFINITA", rect=pygame.Rect(390, 370, 240, 92), object_id="#mode_button_infinite"),
        )
        self.survival_button: UIControl = create_button(
            manager=self.ui_manager,
            container=self.menu_panel,
            config=ButtonConfig(text="SOBREVIVENCIA", rect=pygame.Rect(650, 370, 240, 92), object_id="#mode_button_survival"),
        )
        self.hardcore_button: UIControl = create_button(
            manager=self.ui_manager,
            container=self.menu_panel,
            config=ButtonConfig(text="HARDCORE", rect=pygame.Rect(910, 370, 240, 92), object_id="#mode_button_hardcore"),
        )

        self.labyrinth_button: UIControl = create_button(
            manager=self.ui_manager,
            container=self.menu_panel,
            config=ButtonConfig(text="LABIRINTO", rect=pygame.Rect(130, 490, 240, 92), object_id="#mode_button_labyrinth"),
        )
        self.training_button: UIControl = create_button(
            manager=self.ui_manager,
            container=self.menu_panel,
            config=ButtonConfig(text="TREINO", rect=pygame.Rect(390, 490, 240, 92), object_id="#mode_button_training"),
        )
        self.guide_button: UIControl = create_button(
            manager=self.ui_manager,
            container=self.menu_panel,
            config=ButtonConfig(text="GUIA", rect=pygame.Rect(650, 490, 240, 92), object_id="#mode_button_guide"),
        )
        self.one_vs_one_button: UIControl = create_button(
            manager=self.ui_manager,
            container=self.menu_panel,
            config=ButtonConfig(text="CONFIG", rect=pygame.Rect(910, 490, 240, 92), object_id="#mode_button_config"),
        )

        self.exit_button: UIControl = create_button(
            manager=self.ui_manager,
            container=self.menu_panel,
            config=ButtonConfig(text="[X] SAIR", rect=pygame.Rect(20, SCREEN_HEIGHT - 66, 184, 44), object_id="#menu_footer_exit"),
        )

        self.settings_button: UIControl = create_button(
            manager=self.ui_manager,
            container=self.menu_panel,
            config=ButtonConfig(text="⚙", rect=pygame.Rect(SCREEN_WIDTH - 74, SCREEN_HEIGHT - 66, 44, 44), object_id="#footer_control_cyan"),
        )

        self._menu_buttons: list[UIControl] = [
            self.race_button,
            self.infinite_button,
            self.survival_button,
            self.hardcore_button,
            self.labyrinth_button,
            self.training_button,
            self.guide_button,
            self.one_vs_one_button,
            self.exit_button,
            self.settings_button,
        ]

        self._menu_actions: list[Callable[[], None]] = [
            self._start_race,
            self._start_survival,
            self._start_survival,
            self._start_hardcore,
            self._start_one_vs_one,
            self._start_race,
            self._open_help,
            self._open_settings,
            self._quit,
            self._open_settings,
        ]

        self.set_navigator(
            buttons=self._menu_buttons,
            actions=self._menu_actions,
            on_cancel=self._quit,
            directional_resolver=self._resolve_directional_index,
            use_button_selection_state=False,
        )

        self.mode_cards = [
            ModeCardData(
                title="Corrida",
                description=RaceConfig().description,
                color=NEON_CYAN,
            ),
            ModeCardData(
                title="Infinita",
                description="Sobrevivencia infinita com progressao continua e sem fim.",
                color=(166, 88, 255),
            ),
            ModeCardData(
                title="Resistencia",
                description=SurvivalConfig().description,
                color=NEON_MAGENTA,
            ),
            ModeCardData(
                title="Hardcore",
                description="Versao extrema da sobrevivencia, com pressao maxima.",
                color=(255, 110, 0),
            ),
            ModeCardData(
                title="Labirinto",
                description="Combate em arena com rota variavel e pressao de movimento.",
                color=(48, 255, 90),
            ),
            ModeCardData(
                title="Treino",
                description="Modo de aquecimento para praticar dash, movimento e tiro.",
                color=(68, 255, 160),
            ),
            ModeCardData(
                title="Guia",
                description="Veja controles, modos e inimigos antes de jogar.",
                color=(255, 216, 50),
            ),
            ModeCardData(
                title="Config",
                description="Ajustes de jogo, audio e interface.",
                color=(64, 168, 255),
            ),
            None,
            None,
        ]
        self._menu_grid_count = 8

        self._card_line_2 = create_text_box(
            manager=self.ui_manager,
            container=self.mode_card,
            config=TextBoxConfig(
                html_text="",
                rect=pygame.Rect(16, 62, 972, 38),
                object_id="#mode_title_subtitle",
            ),
        )
        self._sync_mode_card()

    def on_enter(self) -> None:
        self.stack.event_bus.publish(AudioContextChanged(context="menu", reason="main_menu_entered"))

    def on_menu_update(self, dt: float) -> None:
        self.elapsed_time += dt
        self._sync_mode_card()

    def render_menu_background(self, screen: pygame.Surface) -> None:
        self.background_renderer.render(screen, self.elapsed_time, SCREEN_WIDTH, SCREEN_HEIGHT)
        if self.navigator is None:
            return
        selected_index = self.navigator.selected_index
        if selected_index < 0 or selected_index >= self._menu_grid_count:
            return
        selected_card = self.mode_cards[selected_index]
        if selected_card is None:
            return
        self._draw_selected_button_fill(screen=screen, color=selected_card.color)

    def render_menu_foreground(self, screen: pygame.Surface) -> None:
        if self.navigator is None:
            return
        selected_index = self.navigator.selected_index
        if selected_index < 0 or selected_index >= len(self.mode_cards):
            return
        selected_card = self.mode_cards[selected_index]
        if selected_card is None:
            return
        self._draw_mode_card_glow(screen=screen, color=selected_card.color)
        self._draw_selected_button_glow(screen=screen, color=selected_card.color)

    def _start_race(self) -> None:
        self.stack.replace(GameScene(self.stack, mode=RaceMode()))

    def _start_survival(self) -> None:
        self.stack.replace(GameScene(self.stack, mode=SurvivalMode()))

    def _start_one_vs_one(self) -> None:
        self.stack.replace(GameScene(self.stack, mode=OneVsOneMode()))

    def _start_hardcore(self) -> None:
        self.stack.replace(GameScene(self.stack, mode=SurvivalMode()))

    def _quit(self) -> None:
        while not self.stack.is_empty():
            self.stack.pop()

    def _open_settings(self) -> None:
        self.stack.push(SettingsOverlayScene(self.stack))

    def _open_help(self) -> None:
        self.stack.push(HelpOverlayScene(self.stack))

    def _resolve_directional_index(self, current_index: int, direction: str, total_buttons: int) -> int:
        if current_index < 0 or current_index >= total_buttons:
            return current_index

        if direction == "left":
            left_map = {
                0: 3,
                1: 0,
                2: 1,
                3: 2,
                4: 7,
                5: 4,
                6: 5,
                7: 6,
                8: 9,
                9: 8,
            }
            return left_map.get(current_index, current_index)

        if direction == "right":
            right_map = {
                0: 1,
                1: 2,
                2: 3,
                3: 0,
                4: 5,
                5: 6,
                6: 7,
                7: 4,
                8: 9,
                9: 8,
            }
            return right_map.get(current_index, current_index)

        if direction == "up":
            up_map = {
                0: 8,
                1: 8,
                2: 9,
                3: 9,
                4: 0,
                5: 1,
                6: 2,
                7: 3,
                8: 4,
                9: 7,
            }
            return up_map.get(current_index, current_index)

        if direction == "down":
            down_map = {
                0: 4,
                1: 5,
                2: 6,
                3: 7,
                4: 8,
                5: 8,
                6: 9,
                7: 9,
                8: 0,
                9: 3,
            }
            return down_map.get(current_index, current_index)

        return current_index

    def _sync_mode_card(self) -> None:
        selected_index = self.navigator.selected_index
        if selected_index < 0:
            self._last_mode_card_index = None
            self.mode_title_box.set_text("")
            self.mode_description_box.set_text("")
            return
        if selected_index >= len(self.mode_cards):
            return
        if self._last_mode_card_index == selected_index:
            return
        selected = self.mode_cards[selected_index]
        if selected is None:
            return
        self.mode_title_box.set_text(
            f"<font color='{self._to_hex(selected.color)}' size=\"7\"><b>{selected.title.upper()}</b></font>"
        )
        self._card_line_2.set_text(f"<font color='#f1f1f1' size=\"5\"><b>EXTREMO</b></font>")
        self.mode_description_box.set_text(selected.description)
        self._last_mode_card_index = selected_index

    def _draw_mode_card_glow(self, screen: pygame.Surface, color: tuple[int, int, int]) -> None:
        pulse = 0.72 + 0.28 * (0.5 + 0.5 * pygame.math.Vector2(1, 0).rotate(self.elapsed_time * 320).x)
        glow_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)

        for index, inflation in enumerate((6, 14, 24)):
            alpha = int((80 - index * 20) * pulse)
            pygame.draw.rect(
                glow_surface,
                (color[0], color[1], color[2], max(0, min(255, alpha))),
                self._mode_card_glow_rect.inflate(inflation, inflation),
                width=2,
                border_radius=18,
            )

        border_alpha = int(180 + 75 * (0.5 + 0.5 * pygame.math.Vector2(1, 0).rotate(self.elapsed_time * 280).x))
        border_width = 2 + int(2 * (0.5 + 0.5 * pygame.math.Vector2(1, 0).rotate(self.elapsed_time * 240).x))
        pygame.draw.rect(
            glow_surface,
            (color[0], color[1], color[2], max(0, min(255, border_alpha))),
            self._mode_card_glow_rect,
            width=border_width,
            border_radius=16,
        )

        screen.blit(glow_surface, (0, 0))

    def _draw_selected_button_glow(self, screen: pygame.Surface, color: tuple[int, int, int]) -> None:
        if self.navigator is None:
            return
        selected_index = self.navigator.selected_index
        if selected_index < 0 or selected_index >= self._menu_grid_count:
            return

        selected_rect = self._menu_buttons[selected_index].rect
        glow_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)

        for index, inflation in enumerate((8, 16)):
            alpha = 70 - index * 18
            pygame.draw.rect(
                glow_surface,
                (color[0], color[1], color[2], alpha),
                selected_rect.inflate(inflation, inflation),
                width=2,
                border_radius=12,
            )
        screen.blit(glow_surface, (0, 0))

    def _draw_selected_button_fill(self, screen: pygame.Surface, color: tuple[int, int, int]) -> None:
        if self.navigator is None:
            return
        selected_index = self.navigator.selected_index
        if selected_index < 0 or selected_index >= self._menu_grid_count:
            return

        selected_rect = self._menu_buttons[selected_index].rect
        fill_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        pygame.draw.rect(
            fill_surface,
            (color[0], color[1], color[2], 165),
            selected_rect.inflate(-8, -8),
            border_radius=10,
        )
        screen.blit(fill_surface, (0, 0))

    @staticmethod
    def _to_hex(color: tuple[int, int, int]) -> str:
        red, green, blue = color
        return f"#{red:02x}{green:02x}{blue:02x}"
