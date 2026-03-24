from __future__ import annotations

import pygame
from pygame_gui.elements import UITextBox

from game.config import PAUSE_OVERLAY_COLOR, SCREEN_HEIGHT, SCREEN_WIDTH
from game.scenes.base_menu_scene import BaseMenuScene
from game.scenes.overlay_scene_factory import OverlayActionBinding, OverlaySceneFactory
from game.ui.components.base_widgets import create_button, create_centered_panel, create_text_box, create_title
from game.ui.components.overlay_builder import draw_overlay_backdrop
from game.ui.components.tab_builder import TabController, create_tab_controller
from game.ui.types import (
    UIControl,
    ButtonConfig,
    PanelConfig,
    TabBarConfig,
    TitleConfig,
    TextBoxConfig,
)


class MenuOverlayScene(BaseMenuScene):
    transparent = True

    def __init__(
        self,
        stack,
        title: str,
        panel_object_id: str,
        body_text: str = "Painel em construcao...",
    ) -> None:
        super().__init__(stack)
        overlay = OverlaySceneFactory.build(
            screen_size=(SCREEN_WIDTH, SCREEN_HEIGHT),
            ui_manager=self.ui_manager,
            title=title,
            panel_object_id=panel_object_id,
            panel_size=(560, 320),
            body_text=body_text,
            body_rect=pygame.Rect(14, 78, 530, 160),
            action_bindings=(
                OverlayActionBinding(
                    key="close",
                    text="x",
                    rect=pygame.Rect(14, 248, 530, 58),
                    object_id="#overlay_close_button",
                    handler=self._close,
                ),
            ),
            on_cancel_key="close",
        )
        self.panel = overlay.panel
        self.body_text_box: UITextBox | None = overlay.body
        self.close_button: UIControl = overlay.controls["close"]

        self.set_navigator(
            buttons=overlay.navigation_buttons,
            actions=overlay.navigation_actions,
            on_cancel=overlay.cancel_action,
        )

    def render_menu_background(self, screen: pygame.Surface) -> None:
        draw_overlay_backdrop(screen, screen_size=(SCREEN_WIDTH, SCREEN_HEIGHT), color=PAUSE_OVERLAY_COLOR)

    def _close(self) -> None:
        self.stack.pop()


class SettingsOverlayScene(MenuOverlayScene):
    def __init__(self, stack) -> None:
        super().__init__(stack, title="Configuracoes", panel_object_id="#overlay_panel_settings")


class HelpOverlayScene(BaseMenuScene):
    transparent = True

    def __init__(self, stack) -> None:
        super().__init__(stack)

        self.panel = create_centered_panel(
            manager=self.ui_manager,
            screen_size=(SCREEN_WIDTH, SCREEN_HEIGHT),
            config=PanelConfig(size=(760, 430), object_id="#overlay_panel_help"),
        )
        self.title_label = create_title(
            manager=self.ui_manager,
            container=self.panel,
            config=TitleConfig(text="Ajuda", rect=pygame.Rect(16, 12, 728, 42)),
        )

        self.tabs: TabController = create_tab_controller(
            manager=self.ui_manager,
            container=self.panel,
            config=TabBarConfig(
                labels=("Controles", "Modos de jogo", "Inimigos"),
                object_ids=("#help_tab_controls", "#help_tab_modes", "#help_tab_enemies"),
                top_left=(16, 60),
                button_size=(236, 46),
                gap=10,
            ),
            tab_keys=("controls", "modes", "enemies"),
        )

        self.content_box = create_text_box(
            manager=self.ui_manager,
            container=self.panel,
            config=TextBoxConfig(html_text="", rect=pygame.Rect(16, 116, 728, 248), object_id="#help_content"),
        )

        self.close_button: UIControl = create_button(
            manager=self.ui_manager,
            container=self.panel,
            config=ButtonConfig(text="x", rect=pygame.Rect(16, 372, 728, 46), object_id="#overlay_close_button"),
        )

        self._tab_content: dict[str, str] = {
            "controls": (
                "<b>Controles</b><br>"
                "WASD: movimentacao<br>"
                "Espaco: dash<br>"
                "Esc: pausa/voltar<br>"
                "Enter ou Espaco (menu): confirmar<br>"
                "A/D ou Setas (menu): navegar<br>"
                "Mouse: selecionar e clicar"
            ),
            "modes": (
                "<b>Modos de jogo</b><br>"
                "Corrida: colete energia e avance por portais.<br>"
                "Resistencia: sobreviva ao aumento progressivo de pressao.<br>"
                "1v1: enfrente um inimigo por vez e avance no portal."
            ),
            "enemies": (
                "<b>Inimigos</b><br>"
                "Follower: persegue o jogador continuamente.<br>"
                "Shooter/Turrets: atacam a distancia com padroes proprios.<br>"
                "Charge/Explosive: alta pressao com investida e explosao.<br>"
                "Minibosses: variantes com escudo, sniper e espiral."
            ),
        }
        self.selected_tab = "controls"

        self.set_navigator(
            buttons=[*self.tabs.buttons, self.close_button],
            actions=[*self.tabs.build_actions(self._set_tab), self._close],
            on_cancel=self._close,
        )
        self._set_tab("controls")

    def render_menu_background(self, screen: pygame.Surface) -> None:
        draw_overlay_backdrop(screen, screen_size=(SCREEN_WIDTH, SCREEN_HEIGHT), color=PAUSE_OVERLAY_COLOR)

    def _set_tab(self, tab_name: str) -> None:
        self.selected_tab = tab_name
        self.content_box.set_text(self._tab_content[tab_name])
        self.tabs.set_active(tab_name)

    def _close(self) -> None:
        self.stack.pop()
