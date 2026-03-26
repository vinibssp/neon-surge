from __future__ import annotations

import pygame
import pygame_gui
from dataclasses import dataclass

from game.config import SCREEN_HEIGHT, SCREEN_WIDTH
from game.scenes.menus._base_menu_scene import BaseMenuScene
from game.scenes.services import CyberpunkMenuBackgroundRenderer
from game.ui.components import ButtonConfig, LabelConfig, PanelConfig, create_button, create_label, create_panel


@dataclass(frozen=True)
class GuideSection:
    title: str
    content: list[str]


class GuideScene(BaseMenuScene):
    def __init__(self, stack) -> None:
        super().__init__(stack)
        self._elapsed_time = 0.0
        self._background_renderer = CyberpunkMenuBackgroundRenderer()
        
        self._sections: tuple[GuideSection, ...] = (
            GuideSection(
                title="SISTEMA DE MOVIMENTAÇÃO",
                content=[
                    "WASD ou SETAS: Navegar pelo espaço.",
                    "SHIFT ESQUERDO: Dash tático (invulnerabilidade curta).",
                    "ESPAÇO: Ativar campo de PARRY.",
                    "DICA: Dash consome energia, use com sabedoria.",
                ],
            ),
            GuideSection(
                title="MECÂNICAS DE COMBATE",
                content=[
                    "PARRY: Reflete projéteis e atordoa (stagger) inimigos.",
                    "STAGGER: Inimigos atordoados não causam dano por contato.",
                    "COMBO: Eliminar inimigos em sequência aumenta o multiplicador.",
                    "DICA: O parry é sua principal ferramenta de defesa.",
                ],
            ),
            GuideSection(
                title="MODOS DE SIMULAÇÃO",
                content=[
                    "CORRIDA: Atravesse portais para avançar de nível.",
                    "SOBREVIVÊNCIA: Resista a hordas infinitas e eventos.",
                    "TREINO: Configure hordas personalizadas para praticar.",
                    "DICA: Use o treino para aprender padrões de chefes.",
                ],
            ),
            GuideSection(
                title="INTERFACE E ATALHOS",
                content=[
                    "ESC: Abrir menu de pausa ou voltar.",
                    "1 / 2 / 3 / 4: Trocar abas em menus complexos.",
                    "Q / E: Alternar entre seções adjacentes.",
                    "MOUSE WHEEL: Rolar listas e trocar páginas.",
                ],
            ),
        )
        self._active_index = 0
        
        self._init_ui()
        self._refresh_content()

    def _init_ui(self) -> None:
        # Header
        create_label(
            LabelConfig(
                text="MANUAL DO OPERADOR",
                rect=pygame.Rect((SCREEN_WIDTH // 2 - 400, 40), (800, 80)),
                variant="title",
            ),
            manager=self.ui_manager,
        )

        # Content Panel
        self._content_panel = create_panel(
            PanelConfig(
                rect=pygame.Rect((SCREEN_WIDTH // 2 - 450, 180), (900, 320)),
                variant="card",
            ),
            manager=self.ui_manager,
        )

        self._section_title_label = create_label(
            LabelConfig(
                text="",
                rect=pygame.Rect((50, 20), (800, 50)),
                variant="guide_section",
            ),
            manager=self.ui_manager,
            container=self._content_panel,
        )

        self._content_labels: list[object] = []
        for i in range(4):
            lbl = create_label(
                LabelConfig(
                    text="",
                    rect=pygame.Rect((50, 80 + i * 45), (800, 40)),
                    variant="guide_body",
                ),
                manager=self.ui_manager,
                container=self._content_panel,
            )
            self._content_labels.append(lbl)

        # Footer / Navigation
        self._prev_button = create_button(
            ButtonConfig(
                text="ANTERIOR (Q)",
                rect=pygame.Rect((SCREEN_WIDTH // 2 - 350, 530), (200, 50)),
                variant="ghost",
            ),
            manager=self.ui_manager,
        )
        
        self._section_counter_label = create_label(
            LabelConfig(
                text="",
                rect=pygame.Rect((SCREEN_WIDTH // 2 - 100, 535), (200, 40)),
                variant="header",
            ),
            manager=self.ui_manager,
        )

        self._next_button = create_button(
            ButtonConfig(
                text="PRÓXIMO (E)",
                rect=pygame.Rect((SCREEN_WIDTH // 2 + 150, 530), (200, 50)),
                variant="ghost",
            ),
            manager=self.ui_manager,
        )

        self._back_button = create_button(
            ButtonConfig(
                text="VOLTAR AO MENU",
                rect=pygame.Rect((SCREEN_WIDTH // 2 - 150, 620), (300, 60)),
                variant="danger",
            ),
            manager=self.ui_manager,
        )

        self.set_navigator(
            controls=[self._prev_button, self._next_button, self._back_button],
            actions={
                self._prev_button: lambda: self._change_section(-1),
                self._next_button: lambda: self._change_section(1),
                self._back_button: self._close,
            },
            on_cancel=self._close,
        )

    def _refresh_content(self) -> None:
        section = self._sections[self._active_index]
        self._section_title_label.set_text(section.title)
        
        for i, text in enumerate(section.content):
            if i < len(self._content_labels):
                self._content_labels[i].set_text(text)
        
        self._section_counter_label.set_text(f"MÓDULO {self._active_index + 1} / {len(self._sections)}")

    def _change_section(self, delta: int) -> None:
        self._active_index = (self._active_index + delta) % len(self._sections)
        self._refresh_content()

    def handle_input(self, events: list[pygame.event.Event]) -> None:
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_q, pygame.K_LEFT, pygame.K_PAGEUP):
                    self._change_section(-1)
                elif event.key in (pygame.K_e, pygame.K_RIGHT, pygame.K_PAGEDOWN):
                    self._change_section(1)
                elif pygame.K_1 <= event.key <= pygame.K_4:
                    self._active_index = min(event.key - pygame.K_1, len(self._sections) - 1)
                    self._refresh_content()
            elif event.type == pygame.MOUSEWHEEL:
                self._change_section(-event.y)
        super().handle_input(events)

    def on_menu_update(self, dt: float) -> None:
        self._elapsed_time += dt

    def render_menu_background(self, screen: pygame.Surface) -> None:
        self._background_renderer.render(screen, self._elapsed_time, SCREEN_WIDTH, SCREEN_HEIGHT)

    def _close(self) -> None:
        self.stack.pop()
