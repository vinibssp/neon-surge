from __future__ import annotations

import pygame

from game.config import SCREEN_HEIGHT, SCREEN_WIDTH
from game.scenes.menus._base_menu_scene import BaseMenuScene
from game.scenes.services import CyberpunkMenuBackgroundRenderer
from game.ui.components import ButtonConfig, LabelConfig, create_button, create_label
from game.ui.gui_theme import register_custom_element_themes


class GuideScene(BaseMenuScene):
    def __init__(self, stack) -> None:
        super().__init__(stack)
        self._elapsed_time = 0.0
        self._background_renderer = CyberpunkMenuBackgroundRenderer()
        self._register_guide_themes()

        title = create_label(
            LabelConfig(
                text="GUIA",
                rect=pygame.Rect((SCREEN_WIDTH // 2 - 140, 100), (280, 56)),
                object_id="guide_title_label",
            ),
            manager=self.ui_manager,
        )
        line_1 = create_label(
            LabelConfig(
                text="WASD: mover | SHIFT: dash | ESPACO: parry",
                rect=pygame.Rect((SCREEN_WIDTH // 2 - 300, 220), (600, 42)),
                object_id="guide_line_1_label",
            ),
            manager=self.ui_manager,
        )
        line_2 = create_label(
            LabelConfig(
                text="ESC: pausar | Objetivo depende do modo",
                rect=pygame.Rect((SCREEN_WIDTH // 2 - 280, 264), (560, 42)),
                object_id="guide_line_2_label",
            ),
            manager=self.ui_manager,
        )
        line_3 = create_label(
            LabelConfig(
                text="Treino: selecione inimigos por abas e pratique composicoes especificas",
                rect=pygame.Rect((SCREEN_WIDTH // 2 - 310, 308), (620, 42)),
                object_id="guide_line_3_label",
            ),
            manager=self.ui_manager,
        )
        del title, line_1, line_2, line_3

        back_button = create_button(
            ButtonConfig(
                text="Voltar",
                rect=pygame.Rect((SCREEN_WIDTH // 2 - 130, 480), (260, 56)),
                object_id="guide_back_button",
            ),
            manager=self.ui_manager,
        )

        self.set_navigator(
            buttons=[back_button],
            actions={back_button: self._close},
            on_cancel=self._close,
        )

    def _register_guide_themes(self) -> None:
        register_custom_element_themes(
            self.ui_manager,
            {
                "guide_title_label": {
                    "colours": {
                        "normal_text": "#f7ef87",
                    },
                    "font": {
                        "name": "noto_sans",
                        "size": "48",
                        "bold": "1",
                    },
                },
                "guide_line_1_label": {
                    "colours": {
                        "normal_text": "#ffe4a6",
                    },
                    "font": {
                        "name": "noto_sans",
                        "size": "18",
                        "bold": "1",
                    },
                },
                "guide_line_2_label": {
                    "colours": {
                        "normal_text": "#fff2ce",
                    },
                    "font": {
                        "name": "noto_sans",
                        "size": "16",
                        "bold": "0",
                    },
                },
                "guide_line_3_label": {
                    "colours": {
                        "normal_text": "#fff2ce",
                    },
                    "font": {
                        "name": "noto_sans",
                        "size": "16",
                        "bold": "0",
                    },
                },
                "guide_back_button": {
                    "colours": {
                        "normal_bg": "#3f3805",
                        "hovered_bg": "#5a5009",
                        "selected_bg": "#75680c",
                        "active_bg": "#908110",
                        "normal_text": "#fff1a1",
                        "hovered_text": "#fffbe1",
                        "selected_text": "#fffbe1",
                        "normal_border": "#f1dc3b",
                        "hovered_border": "#f7e570",
                        "selected_border": "#fbef9e",
                    },
                    "font": {
                        "name": "noto_sans",
                        "size": "16",
                        "bold": "1",
                    },
                },
            },
            rebuild_all=True,
        )

    def on_menu_update(self, dt: float) -> None:
        self._elapsed_time += dt

    def render_menu_background(self, screen: pygame.Surface) -> None:
        self._background_renderer.render(
            screen=screen,
            elapsed_time=self._elapsed_time,
            width=SCREEN_WIDTH,
            height=SCREEN_HEIGHT,
        )

    def _close(self) -> None:
        self.stack.pop()
