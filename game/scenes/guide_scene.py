from __future__ import annotations

import pygame
from dataclasses import dataclass

from game.config import SCREEN_HEIGHT, SCREEN_WIDTH
from game.scenes.menus._base_menu_scene import BaseMenuScene
from game.scenes.services import CyberpunkMenuBackgroundRenderer
from game.ui.components import ButtonConfig, LabelConfig, create_button, create_label
from game.ui.gui_theme import register_custom_element_themes


@dataclass(frozen=True)
class GuideSection:
    title: str
    lines: tuple[str, str, str]


class GuideScene(BaseMenuScene):
    def __init__(self, stack) -> None:
        super().__init__(stack)
        self._elapsed_time = 0.0
        self._background_renderer = CyberpunkMenuBackgroundRenderer()
        self._sections: tuple[GuideSection, ...] = (
            GuideSection(
                title="Controles",
                lines=(
                    "WASD: mover | SHIFT: dash | ESPACO: parry",
                    "ESC: pausar/retomar overlays",
                    "No menu: setas, TAB e ENTER para navegar",
                ),
            ),
            GuideSection(
                title="Modos",
                lines=(
                    "Corrida: coletar energia e atravessar portais",
                    "Sobrevivencia: resistir ao caos progressivo",
                    "Treino: montar composicoes por abas e quantidade",
                ),
            ),
            GuideSection(
                title="Dicas",
                lines=(
                    "Parry interrompe pressao e aplica stagger",
                    "Use dash para reposicionar antes de bursts",
                    "Treino: 1/2/3 troca abas, +/- ajusta linha focada",
                ),
            ),
        )
        self._active_section_index = 0
        self._register_guide_themes()

        title = create_label(
            LabelConfig(
                text="GUIA",
                rect=pygame.Rect((SCREEN_WIDTH // 2 - 140, 100), (280, 56)),
                object_id="guide_title_label",
            ),
            manager=self.ui_manager,
        )
        self._section_title_label = create_label(
            LabelConfig(
                text="",
                rect=pygame.Rect((SCREEN_WIDTH // 2 - 300, 220), (600, 42)),
                object_id="guide_section_title_label",
            ),
            manager=self.ui_manager,
        )
        self._line_1_label = create_label(
            LabelConfig(
                text="",
                rect=pygame.Rect((SCREEN_WIDTH // 2 - 280, 264), (560, 42)),
                object_id="guide_line_1_label",
            ),
            manager=self.ui_manager,
        )
        self._line_2_label = create_label(
            LabelConfig(
                text="",
                rect=pygame.Rect((SCREEN_WIDTH // 2 - 310, 308), (620, 42)),
                object_id="guide_line_2_label",
            ),
            manager=self.ui_manager,
        )
        self._line_3_label = create_label(
            LabelConfig(
                text="",
                rect=pygame.Rect((SCREEN_WIDTH // 2 - 320, 352), (640, 42)),
                object_id="guide_line_3_label",
            ),
            manager=self.ui_manager,
        )
        self._hotkeys_label = create_label(
            LabelConfig(
                text="Atalhos: 1/2/3 secoes | Q/E alterna | PgUp/PgDn alterna",
                rect=pygame.Rect((SCREEN_WIDTH // 2 - 360, 414), (720, 34)),
                object_id="guide_hotkeys_label",
            ),
            manager=self.ui_manager,
        )
        del title

        self._prev_button = create_button(
            ButtonConfig(
                text="Anterior",
                rect=pygame.Rect((SCREEN_WIDTH // 2 - 280, 470), (180, 50)),
                object_id="guide_prev_button",
            ),
            manager=self.ui_manager,
        )
        self._next_button = create_button(
            ButtonConfig(
                text="Proximo",
                rect=pygame.Rect((SCREEN_WIDTH // 2 + 100, 470), (180, 50)),
                object_id="guide_next_button",
            ),
            manager=self.ui_manager,
        )
        self._section_counter_label = create_label(
            LabelConfig(
                text="",
                rect=pygame.Rect((SCREEN_WIDTH // 2 - 90, 480), (180, 34)),
                object_id="guide_section_counter_label",
            ),
            manager=self.ui_manager,
        )

        back_button = create_button(
            ButtonConfig(
                text="Voltar",
                rect=pygame.Rect((SCREEN_WIDTH // 2 - 130, 548), (260, 56)),
                object_id="guide_back_button",
            ),
            manager=self.ui_manager,
        )
        self._back_button = back_button

        self.set_navigator(
            controls=[self._prev_button, self._next_button, self._back_button],
            actions={
                self._prev_button: lambda: self._change_section(-1),
                self._next_button: lambda: self._change_section(1),
                self._back_button: self._close,
            },
            on_cancel=self._close,
        )
        self._refresh_content()

    def handle_input(self, events: list[pygame.event.Event]) -> None:
        forwarded_events: list[pygame.event.Event] = []
        for event in events:
            if event.type != pygame.KEYDOWN:
                forwarded_events.append(event)
                continue
            if not self._handle_keyboard_shortcut(event):
                forwarded_events.append(event)
        super().handle_input(forwarded_events)

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
                "guide_section_title_label": {
                    "colours": {
                        "normal_text": "#f6de75",
                    },
                    "font": {
                        "name": "noto_sans",
                        "size": "26",
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
                "guide_hotkeys_label": {
                    "colours": {
                        "normal_text": "#f8e6bb",
                    },
                    "font": {
                        "name": "noto_sans",
                        "size": "14",
                        "bold": "0",
                    },
                },
                "guide_section_counter_label": {
                    "colours": {
                        "normal_text": "#f8e6bb",
                    },
                    "font": {
                        "name": "noto_sans",
                        "size": "15",
                        "bold": "1",
                    },
                },
                "guide_prev_button": {
                    "colours": {
                        "normal_bg": "#2e2a08",
                        "hovered_bg": "#494211",
                        "selected_bg": "#655a16",
                        "active_bg": "#7f731c",
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
                "guide_next_button": {
                    "colours": {
                        "normal_bg": "#2e2a08",
                        "hovered_bg": "#494211",
                        "selected_bg": "#655a16",
                        "active_bg": "#7f731c",
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

    def _handle_keyboard_shortcut(self, event: pygame.event.Event) -> bool:
        key = event.key
        if key in (pygame.K_1, pygame.K_KP1):
            self._set_section_index(0)
            return True
        if key in (pygame.K_2, pygame.K_KP2):
            self._set_section_index(1)
            return True
        if key in (pygame.K_3, pygame.K_KP3):
            self._set_section_index(2)
            return True
        if key in (pygame.K_q, pygame.K_PAGEUP):
            self._change_section(-1)
            return True
        if key in (pygame.K_e, pygame.K_PAGEDOWN):
            self._change_section(1)
            return True
        return False

    def _set_section_index(self, section_index: int) -> None:
        bounded_index = max(0, min(len(self._sections) - 1, section_index))
        if bounded_index == self._active_section_index:
            return
        self._active_section_index = bounded_index
        self._refresh_content()

    def _change_section(self, direction: int) -> None:
        section_count = len(self._sections)
        if section_count <= 0:
            return
        next_index = (self._active_section_index + direction) % section_count
        self._active_section_index = next_index
        self._refresh_content()

    def _refresh_content(self) -> None:
        section = self._sections[self._active_section_index]
        self._section_title_label.set_text(section.title)
        self._line_1_label.set_text(section.lines[0])
        self._line_2_label.set_text(section.lines[1])
        self._line_3_label.set_text(section.lines[2])
        self._section_counter_label.set_text(f"{self._active_section_index + 1}/{len(self._sections)}")

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
