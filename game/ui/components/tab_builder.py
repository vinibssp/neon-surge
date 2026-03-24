from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

import pygame
from pygame_gui import UIManager
from pygame_gui.core.interfaces import IContainerLikeInterface
from pygame_gui.elements import UIButton

from game.ui.components.base_widgets import create_button
from game.ui.types import ButtonConfig, TabBarConfig, UIControl


@dataclass(frozen=True)
class TabController:
    tab_order: tuple[str, ...]
    labels: dict[str, str]
    buttons_by_key: dict[str, UIControl]
    active_template: str = "[{label}]"
    inactive_template: str = "{label}"

    def __post_init__(self) -> None:
        if len(self.tab_order) == 0:
            raise ValueError("TabController inválido: ao menos uma tab é obrigatória.")

        missing_labels = [key for key in self.tab_order if key not in self.labels]
        missing_buttons = [key for key in self.tab_order if key not in self.buttons_by_key]
        if missing_labels or missing_buttons:
            raise ValueError(
                "TabController inválido: tabs sem labels/botões "
                f"(missing_labels={missing_labels}, missing_buttons={missing_buttons})."
            )

    @property
    def buttons(self) -> list[UIControl]:
        return [self.buttons_by_key[key] for key in self.tab_order]

    def set_active(self, tab_key: str) -> None:
        if tab_key not in self.buttons_by_key:
            raise ValueError(f"Tab inválida: '{tab_key}'.")

        for key in self.tab_order:
            label = self.labels[key]
            text = self.active_template.format(label=label) if key == tab_key else self.inactive_template.format(label=label)
            self.buttons_by_key[key].set_text(text)

    def build_actions(self, on_select: Callable[[str], None]) -> list[Callable[[], None]]:
        return [self._build_select_action(tab_key=tab_key, on_select=on_select) for tab_key in self.tab_order]

    @staticmethod
    def _build_select_action(tab_key: str, on_select: Callable[[str], None]) -> Callable[[], None]:
        def _action() -> None:
            on_select(tab_key)

        return _action


def create_tab_buttons(
    manager: UIManager,
    container: IContainerLikeInterface,
    config: TabBarConfig,
) -> list[UIButton]:
    if len(config.labels) != len(config.object_ids):
        raise ValueError(
            "TabBarConfig inválido: 'labels' e 'object_ids' devem ter o mesmo tamanho "
            f"(labels={len(config.labels)}, object_ids={len(config.object_ids)})."
        )

    buttons: list[UIButton] = []
    left, top = config.top_left
    width, height = config.button_size
    for index, label in enumerate(config.labels):
        object_id = config.object_ids[index]
        rect = pygame.Rect(left + index * (width + config.gap), top, width, height)
        buttons.append(
            create_button(
                manager=manager,
                container=container,
                config=ButtonConfig(text=label, rect=rect, object_id=object_id),
            )
        )
    return buttons


def create_tab_controller(
    manager: UIManager,
    container: IContainerLikeInterface,
    config: TabBarConfig,
    tab_keys: tuple[str, ...],
) -> TabController:
    if len(tab_keys) != len(config.labels):
        raise ValueError(
            "Configuração de tabs inválida: 'tab_keys' e 'labels' devem ter o mesmo tamanho "
            f"(tab_keys={len(tab_keys)}, labels={len(config.labels)})."
        )

    buttons = create_tab_buttons(manager=manager, container=container, config=config)
    labels = {tab_keys[index]: label for index, label in enumerate(config.labels)}
    buttons_by_key: dict[str, UIControl] = {tab_keys[index]: button for index, button in enumerate(buttons)}
    return TabController(tab_order=tab_keys, labels=labels, buttons_by_key=buttons_by_key)
