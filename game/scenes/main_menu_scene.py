from __future__ import annotations

from dataclasses import dataclass

import pygame
from pygame import Vector2

from game.config import MENU_MOUNTAIN_FILL_COLOR, SCREEN_HEIGHT, SCREEN_WIDTH
from game.modes.mode_config import OneVsOneConfig, RaceConfig, SurvivalConfig
from game.modes.one_vs_one_mode import OneVsOneMode
from game.modes.race_mode import RaceMode
from game.modes.survival_mode import SurvivalMode
from game.core.scene_stack import Scene
from game.scenes.game_scene import GameScene
from game.scenes.menu_overlay_scenes import HelpOverlayScene, SettingsOverlayScene
from game.scenes.services import CyberpunkMenuBackgroundRenderer
from game.ui.elements import Button, Container, Label
from game.ui.navigation import UINavigationInputHandler, UINavigator


NEON_CYAN = (0, 220, 255)
NEON_MAGENTA = (255, 55, 220)
NEON_LIME = (150, 255, 70)
WHITE = (245, 245, 245)
RED_EXIT = (235, 45, 65)


@dataclass(frozen=True)
class ModeCardData:
    title: str
    description: str
    color: tuple[int, int, int]


class MainMenuScene(Scene):
    def __init__(self, stack) -> None:
        super().__init__(stack)
        self.elapsed_time = 0.0
        self.background_renderer = CyberpunkMenuBackgroundRenderer()
        self.icon_font = pygame.font.Font(None, 38)
        panel_size = Vector2(560, 420)
        panel_pos = Vector2((SCREEN_WIDTH - panel_size.x) * 0.5, (SCREEN_HEIGHT - panel_size.y) * 0.5)
        self.root = Container(position=panel_pos, size=panel_size, orientation="vertical", padding=16, draw_panel=False)
        self.mode_card = Container(
            position=Vector2(),
            size=Vector2(520, 210),
            orientation="vertical",
            padding=12,
            draw_panel=True,
            panel_color=MENU_MOUNTAIN_FILL_COLOR,
            border_color=NEON_CYAN,
        )
        self.mode_title_label = Label(
            position=Vector2(),
            size=Vector2(496, 56),
            text="",
            color=NEON_CYAN,
            font_size=44,
            draw_panel=False,
            margin=8,
        )
        self.mode_description_label = Label(
            position=Vector2(),
            size=Vector2(496, 124),
            text="",
            color=(240, 240, 248),
            font_size=30,
            draw_panel=False,
            margin=0,
        )
        self.mode_card.add_child(self.mode_title_label)
        self.mode_card.add_child(self.mode_description_label)
        self.root.add_child(self.mode_card)
        self.buttons_row = Container(
            position=Vector2(),
            size=Vector2(520, 86),
            orientation="horizontal",
            padding=0,
            draw_panel=False,
        )
        self.race_button = Button(
            position=Vector2(),
            size=Vector2(124, 86),
            text="Corrida",
            callback=self._start_race,
            base_color=MENU_MOUNTAIN_FILL_COLOR,
            hover_color=NEON_CYAN,
            border_color=NEON_CYAN,
            text_color=NEON_CYAN,
            hover_border_color=WHITE,
            hover_text_color=MENU_MOUNTAIN_FILL_COLOR,
            font_size=34,
        )
        self.survival_button = Button(
            position=Vector2(),
            size=Vector2(124, 86),
            text="Resistencia",
            callback=self._start_survival,
            base_color=MENU_MOUNTAIN_FILL_COLOR,
            hover_color=NEON_MAGENTA,
            border_color=NEON_MAGENTA,
            text_color=NEON_MAGENTA,
            hover_border_color=WHITE,
            hover_text_color=MENU_MOUNTAIN_FILL_COLOR,
            font_size=34,
        )
        self.one_vs_one_button = Button(
            position=Vector2(),
            size=Vector2(124, 86),
            text="1v1",
            callback=self._start_one_vs_one,
            base_color=MENU_MOUNTAIN_FILL_COLOR,
            hover_color=NEON_LIME,
            border_color=NEON_LIME,
            text_color=NEON_LIME,
            hover_border_color=WHITE,
            hover_text_color=MENU_MOUNTAIN_FILL_COLOR,
            font_size=34,
        )
        self.buttons_row.add_child(self.race_button)
        self.buttons_row.add_child(self.survival_button)
        self.buttons_row.add_child(self.one_vs_one_button)
        self.root.add_child(self.buttons_row)
        self.ui_input = UINavigationInputHandler()
        self.navigator = UINavigator(
            buttons=[self.race_button, self.survival_button, self.one_vs_one_button],
            on_cancel=self._quit,
        )
        self.mode_cards = [
            ModeCardData(
                title="Corrida",
                description=RaceConfig().description,
                color=NEON_CYAN,
            ),
            ModeCardData(
                title="Resistencia",
                description=SurvivalConfig().description,
                color=NEON_MAGENTA,
            ),
            ModeCardData(
                title="1v1",
                description=OneVsOneConfig().description,
                color=NEON_LIME,
            ),
        ]
        self.exit_button_rect = pygame.Rect(SCREEN_WIDTH - 72, 20, 44, 44)
        self.settings_button_rect = pygame.Rect(SCREEN_WIDTH - 132, SCREEN_HEIGHT - 74, 50, 50)
        self.help_button_rect = pygame.Rect(SCREEN_WIDTH - 72, SCREEN_HEIGHT - 74, 50, 50)
        self._sync_mode_card()

    def handle_input(self, events: list[pygame.event.Event]) -> None:
        filtered_events: list[pygame.event.Event] = []
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                click_position = Vector2(event.pos[0], event.pos[1])
                if self._handle_corner_click(click_position):
                    continue
            filtered_events.append(event)

        commands = self.ui_input.build_commands(filtered_events)
        for command in commands:
            command.execute(self.navigator)

    def update(self, dt: float) -> None:
        self.elapsed_time += dt
        self.root.update(dt)
        self.navigator.sync_hover_state()
        self._sync_mode_card()

    def render(self, screen: pygame.Surface) -> None:
        self.background_renderer.render(screen, self.elapsed_time, SCREEN_WIDTH, SCREEN_HEIGHT)
        self.root.render(screen)
        self._render_corner_controls(screen)

    def _start_race(self) -> None:
        self.stack.replace(GameScene(self.stack, mode=RaceMode()))

    def _start_survival(self) -> None:
        self.stack.replace(GameScene(self.stack, mode=SurvivalMode()))

    def _start_one_vs_one(self) -> None:
        self.stack.replace(GameScene(self.stack, mode=OneVsOneMode()))

    def _quit(self) -> None:
        while not self.stack.is_empty():
            self.stack.pop()

    def _sync_mode_card(self) -> None:
        selected_index = self.navigator.selected_index
        if selected_index < 0 or selected_index >= len(self.mode_cards):
            return
        selected = self.mode_cards[selected_index]
        self.mode_card.border_color = selected.color
        self.mode_title_label.color = selected.color
        self.mode_title_label.text = selected.title
        self.mode_description_label.text = selected.description

    def _handle_corner_click(self, click_position: Vector2) -> bool:
        if self.exit_button_rect.collidepoint(click_position.x, click_position.y):
            self._quit()
            return True
        if self.settings_button_rect.collidepoint(click_position.x, click_position.y):
            self.stack.push(SettingsOverlayScene(self.stack))
            return True
        if self.help_button_rect.collidepoint(click_position.x, click_position.y):
            self.stack.push(HelpOverlayScene(self.stack))
            return True
        return False

    def _render_corner_controls(self, screen: pygame.Surface) -> None:
        self._draw_icon_button(screen, self.exit_button_rect, "X", RED_EXIT, RED_EXIT)
        self._draw_icon_button(screen, self.settings_button_rect, "⚙", NEON_CYAN, WHITE)
        self._draw_icon_button(screen, self.help_button_rect, "?", NEON_MAGENTA, WHITE)

    def _draw_icon_button(
        self,
        screen: pygame.Surface,
        rect: pygame.Rect,
        text: str,
        primary_color: tuple[int, int, int],
        border_color: tuple[int, int, int],
    ) -> None:
        pygame.draw.rect(screen, MENU_MOUNTAIN_FILL_COLOR, rect, border_radius=8)
        pygame.draw.rect(screen, border_color, rect, width=2, border_radius=8)
        icon_surface = self.icon_font.render(text, True, primary_color)
        icon_rect = icon_surface.get_rect(center=rect.center)
        screen.blit(icon_surface, icon_rect)
