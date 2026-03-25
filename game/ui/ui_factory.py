"""ui_factory.py — ponto único de bootstrap e criação de UI.

Responsabilidades:
- Inicializar UIManager com o tema retrowave
- Expor factories tipadas para todos os componentes
- Nenhuma lógica de gameplay ou layout
"""
from __future__ import annotations

from pathlib import Path
from typing import Optional, Tuple
import pygame
import pygame_gui

from game.ui.components import (
    ButtonConfig, create_button,
    LabelConfig, create_label,
    PanelConfig, create_panel,
    TextInputConfig, create_text_input,
    ProgressBarConfig, create_progress_bar,
    CheckboxConfig, create_checkbox,
    SliderConfig, create_slider,
    StatusBarConfig, create_status_bar,
)

_THEME_PATH = Path(__file__).parent / "theme" / "retrowave.json"


def build_manager(window_size: Tuple[int, int]) -> pygame_gui.UIManager:
    """Cria e retorna um UIManager configurado com o tema retrowave."""
    return pygame_gui.UIManager(window_size, theme_path=str(_THEME_PATH))


class UIFactory:
    """Wrapper estático com acesso tipado a todas as factories de componentes.

    Uso:
        manager = build_manager((1280, 720))
        btn = UIFactory.button(ButtonConfig("Start", pygame.Rect(100,100,200,50)), manager)
    """

    @staticmethod
    def button(
        config: ButtonConfig,
        manager: pygame_gui.UIManager,
        container: Optional[pygame_gui.core.UIContainer] = None,
    ) -> pygame_gui.elements.UIButton:
        return create_button(config, manager, container)

    @staticmethod
    def label(
        config: LabelConfig,
        manager: pygame_gui.UIManager,
        container: Optional[pygame_gui.core.UIContainer] = None,
    ) -> pygame_gui.elements.UILabel:
        return create_label(config, manager, container)

    @staticmethod
    def panel(
        config: PanelConfig,
        manager: pygame_gui.UIManager,
        container: Optional[pygame_gui.core.UIContainer] = None,
    ) -> pygame_gui.elements.UIPanel:
        return create_panel(config, manager, container)

    @staticmethod
    def text_input(
        config: TextInputConfig,
        manager: pygame_gui.UIManager,
        container: Optional[pygame_gui.core.UIContainer] = None,
    ) -> pygame_gui.elements.UITextEntryLine:
        return create_text_input(config, manager, container)

    @staticmethod
    def progress_bar(
        config: ProgressBarConfig,
        manager: pygame_gui.UIManager,
        container: Optional[pygame_gui.core.UIContainer] = None,
    ) -> pygame_gui.elements.UIProgressBar:
        return create_progress_bar(config, manager, container)

    @staticmethod
    def checkbox(
        config: CheckboxConfig,
        manager: pygame_gui.UIManager,
        container: Optional[pygame_gui.core.UIContainer] = None,
    ) -> pygame_gui.elements.UICheckBox:
        return create_checkbox(config, manager, container)

    @staticmethod
    def slider(
        config: SliderConfig,
        manager: pygame_gui.UIManager,
        container: Optional[pygame_gui.core.UIContainer] = None,
    ) -> pygame_gui.elements.UIHorizontalSlider:
        return create_slider(config, manager, container)

    @staticmethod
    def status_bar(
        config: StatusBarConfig,
        manager: pygame_gui.UIManager,
        container: Optional[pygame_gui.core.UIContainer] = None,
    ) -> pygame_gui.elements.UIStatusBar:
        return create_status_bar(config, manager, container)
