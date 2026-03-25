from __future__ import annotations

from dataclasses import dataclass
import math

import pygame

from game.config import SCREEN_HEIGHT, SCREEN_WIDTH
from game.core.events import AudioContextChanged
from game.modes.mode_config import RaceConfig, RaceInfiniteConfig, SurvivalConfig, SurvivalHardcoreConfig
from game.modes.one_vs_one_mode import OneVsOneMode
from game.modes.labyrinth_mode import LabyrinthMode
from game.modes.race_infinite_mode import RaceInfiniteMode
from game.modes.race_mode import RaceMode
from game.modes.survival_hardcore_mode import SurvivalHardcoreMode
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
        self._mode_card_glow_rect = pygame.Rect(0, 0, 0, 0)

        self.menu_panel = create_centered_panel(
            manager=self.ui_manager,
            screen_size=(SCREEN_WIDTH, SCREEN_HEIGHT),
            config=PanelConfig(size=(SCREEN_WIDTH, SCREEN_HEIGHT), object_id="#menu_panel"),
        )

        self.title_box = create_text_box(
            manager=self.ui_manager,
            container=self.menu_panel,
            config=TextBoxConfig(
                html_text="<font color='#00dcff'><b>NEON SURGE</b></font>",
                rect=pygame.Rect(0, 20, SCREEN_WIDTH, 56),
                object_id="#main_menu_title",
            ),
        )
        self.subtitle_box = create_text_box(
            manager=self.ui_manager,
            container=self.menu_panel,
            config=TextBoxConfig(
                html_text="<font size='4' color='#dfe2ff'><b>ESCOLHA SEU DESAFIO</b></font>",
                rect=pygame.Rect(0, 74, SCREEN_WIDTH, 28),
                object_id="#main_menu_subtitle",
            ),
        )

        card_size = (1040, 220)
        card_left = (SCREEN_WIDTH - card_size[0]) // 2
        card_top = 116
        self.mode_card = create_centered_panel(
            manager=self.ui_manager,
            screen_size=(SCREEN_WIDTH, SCREEN_HEIGHT),
            config=PanelConfig(size=card_size, object_id="#mode_card", container=self.menu_panel),
        )
        self.mode_card.set_relative_position((card_left, card_top))
        self._mode_card_glow_rect = self.mode_card.rect.copy()

        self.mode_title_box = create_text_box(
            manager=self.ui_manager,
            container=self.mode_card,
            config=TextBoxConfig(html_text="", rect=pygame.Rect(20, 16, 1000, 96), object_id="#mode_title"),
        )
        self.mode_description_box = create_text_box(
            manager=self.ui_manager,
            container=self.mode_card,
            config=TextBoxConfig(html_text="", rect=pygame.Rect(28, 122, 984, 78), object_id="#mode_description"),
        )

        grid_padding_x = 24
        grid_padding_y = 20
        button_width = 220
        button_height = 74
        gap_x = 18
        gap_y = 16
        grid_width = (button_width * 4) + (gap_x * 3)
        grid_height = (button_height * 2) + gap_y
        panel_width = grid_width + (grid_padding_x * 2)
        panel_height = grid_height + (grid_padding_y * 2)
        grid_left = (SCREEN_WIDTH - panel_width) // 2
        grid_top = 368
        grid_origin_x = grid_left + grid_padding_x
        grid_origin_y = grid_top + grid_padding_y

        self.grid_panel = create_centered_panel(
            manager=self.ui_manager,
            screen_size=(SCREEN_WIDTH, SCREEN_HEIGHT),
            config=PanelConfig(size=(panel_width, panel_height), object_id="#menu_grid_panel", container=self.menu_panel),
        )
        self.grid_panel.set_relative_position((grid_left, grid_top))

        button_specs = [
            ("CORRIDA", "#mode_button_race", self._start_race),
            ("INFINITA", "#mode_button_infinite", self._start_race_infinite),
            ("SOBREVIVENCIA", "#mode_button_survival", self._start_survival),
            ("HARDCORE", "#mode_button_hardcore", self._start_hardcore),
            ("LABIRINTO", "#mode_button_labyrinth", self._start_labyrinth),
            ("TREINO", "#mode_button_training", self._start_race),
            ("GUIA", "#mode_button_guide", self._open_help),
            ("CONFIG", "#mode_button_config", self._open_settings),
        ]

        self.mode_buttons: list[UIControl] = []
        self._menu_actions = []
        for index, (label, object_id, action) in enumerate(button_specs):
            row = index // 4
            col = index % 4
            rect = pygame.Rect(
                grid_origin_x + col * (button_width + gap_x),
                grid_origin_y + row * (button_height + gap_y),
                button_width,
                button_height,
            )
            self.mode_buttons.append(
                create_button(
                    manager=self.ui_manager,
                    container=self.menu_panel,
                    config=ButtonConfig(text=label, rect=rect, object_id=object_id),
                )
            )
            self._menu_actions.append(action)

        footer_y = SCREEN_HEIGHT - 62
        self.exit_button = create_button(
            manager=self.ui_manager,
            container=self.menu_panel,
            config=ButtonConfig(
                text="[X] SAIR",
                rect=pygame.Rect(grid_left, footer_y, 190, 42),
                object_id="#menu_footer_exit",
            ),
        )
        self.settings_button = create_button(
            manager=self.ui_manager,
            container=self.menu_panel,
            config=ButtonConfig(
                text="SET",
                rect=pygame.Rect(grid_left + panel_width - 66, footer_y, 66, 42),
                object_id="#footer_control_cyan",
            ),
        )

        self._menu_buttons = [
            *self.mode_buttons,
            self.exit_button,
            self.settings_button,
        ]
        self._menu_actions.extend([self._quit, self._open_settings])

        self.set_navigator(
            buttons=self._menu_buttons,
            actions=self._menu_actions,
            on_cancel=self._quit,
            directional_resolver=self._resolve_directional_index,
            use_button_selection_state=True,
        )

        self.mode_cards = [
            ModeCardData(
                title="Corrida",
                description=RaceConfig().description,
                color=NEON_CYAN,
            ),
            ModeCardData(
                title="Infinita",
                description=RaceInfiniteConfig().description,
                color=(166, 88, 255),
            ),
            ModeCardData(
                title="Resistencia",
                description=SurvivalConfig().description,
                color=NEON_MAGENTA,
            ),
            ModeCardData(
                title="Hardcore",
                description=SurvivalHardcoreConfig().description,
                color=(255, 110, 0),
            ),
            ModeCardData(
                title="Labirinto",
                description="Gere labirintos procedurais, colete a chave distante e escape por uma saida bloqueada.",
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
                rect=pygame.Rect(16, 86, 1000, 28),
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

    def _start_race_infinite(self) -> None:
        self.stack.replace(GameScene(self.stack, mode=RaceInfiniteMode()))

    def _start_one_vs_one(self) -> None:
        self.stack.replace(GameScene(self.stack, mode=OneVsOneMode()))

    def _start_labyrinth(self) -> None:
        self.stack.replace(GameScene(self.stack, mode=LabyrinthMode()))

    def _start_hardcore(self) -> None:
        self.stack.replace(GameScene(self.stack, mode=SurvivalHardcoreMode()))

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

        grid_count = 8
        footer_exit = 8
        footer_settings = 9

        if current_index >= grid_count:
            if direction in ("left", "right"):
                return footer_settings if current_index == footer_exit else footer_exit
            if direction == "up":
                return 4 if current_index == footer_exit else 7
            if direction == "down":
                return 0 if current_index == footer_exit else 3
            return current_index

        row = current_index // 4
        col = current_index % 4

        if direction == "left":
            return row * 4 + ((col - 1) % 4)
        if direction == "right":
            return row * 4 + ((col + 1) % 4)
        if direction == "up":
            if row == 0:
                return footer_exit if col < 2 else footer_settings
            return (row - 1) * 4 + col
        if direction == "down":
            if row == 1:
                return footer_exit if col < 2 else footer_settings
            return (row + 1) * 4 + col

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
        self._card_line_2.set_text("<font color='#f1f1f1' size=\"4\"><b>MODO DE JOGO</b></font>")
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
        pulse = 0.6 + 0.4 * math.sin(self.elapsed_time * 4.2)
        pulse_soft = 0.5 + 0.5 * math.sin(self.elapsed_time * 2.6)
        glow_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)

        for index, inflation in enumerate((8, 16, 26)):
            alpha = int((70 - index * 16) * pulse)
            pygame.draw.rect(
                glow_surface,
                (color[0], color[1], color[2], alpha),
                selected_rect.inflate(inflation + int(6 * pulse), inflation + int(6 * pulse)),
                width=2,
                border_radius=12,
            )
        border_alpha = int(140 + 80 * pulse_soft)
        border_width = 2 + int(2 * pulse_soft)
        pygame.draw.rect(
            glow_surface,
            (color[0], color[1], color[2], border_alpha),
            selected_rect.inflate(2 + int(3 * pulse_soft), 2 + int(3 * pulse_soft)),
            width=border_width,
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
        pulse = 0.6 + 0.4 * math.sin(self.elapsed_time * 4.4)
        pulse_soft = 0.5 + 0.5 * math.sin(self.elapsed_time * 2.2)
        inner_alpha = int(120 + 65 * pulse)
        outer_alpha = int(70 + 60 * pulse_soft)
        pygame.draw.rect(
            fill_surface,
            (color[0], color[1], color[2], inner_alpha),
            selected_rect.inflate(-6, -6),
            border_radius=10,
        )
        pygame.draw.rect(
            fill_surface,
            (color[0], color[1], color[2], outer_alpha),
            selected_rect.inflate(6 + int(4 * pulse_soft), 6 + int(4 * pulse_soft)),
            border_radius=12,
            width=2,
        )
        screen.blit(fill_surface, (0, 0))

    @staticmethod
    def _to_hex(color: tuple[int, int, int]) -> str:
        red, green, blue = color
        return f"#{red:02x}{green:02x}{blue:02x}"
