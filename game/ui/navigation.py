from __future__ import annotations

from typing import Callable

import pygame
import pygame_gui

from game.core.events import EventBus, UICancelled, UIConfirmed, UINavigated

UIControl = pygame_gui.elements.UIButton


class PygameGUIEventAdapter:
    def __init__(self, navigator: "UINavigator") -> None:
        self.navigator = navigator

    def process_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame_gui.UI_BUTTON_ON_HOVERED:
            ui_element = event.ui_element
            if isinstance(ui_element, pygame_gui.elements.UIButton):
                self.navigator.on_button_hovered(ui_element)
            return

        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            ui_element = event.ui_element
            if isinstance(ui_element, pygame_gui.elements.UIButton):
                self.navigator.on_button_pressed(ui_element)


class UINavigator:
    def __init__(
        self,
        buttons: list[UIControl],
        actions: dict[UIControl, Callable[[], None]] | None = None,
        on_cancel: Callable[[], None] | None = None,
        event_bus: EventBus | None = None,
    ) -> None:
        self.buttons = tuple(buttons)
        self.actions = actions or {}
        self.on_cancel = on_cancel
        self.event_bus = event_bus
        self._selected_element: UIControl | None = buttons[0] if buttons else None

    @property
    def selected_index(self) -> int:
        return self._index_for(self._selected_element)

    def on_button_hovered(self, element: UIControl) -> None:
        if self._index_for(element) < 0:
            return
        if self._selected_element is element:
            return
        self._selected_element = element
        self._publish_navigated()

    def on_button_pressed(self, element: UIControl) -> None:
        if self._index_for(element) < 0:
            return
        self._selected_element = element
        selected_index = self.selected_index
        if selected_index < 0:
            return
        if self.event_bus is not None:
            self.event_bus.publish(UIConfirmed(index=selected_index))
        action = self.actions.get(element)
        if action is not None:
            action()

    def cancel(self) -> None:
        if self.event_bus is not None:
            self.event_bus.publish(UICancelled())
        if self.on_cancel is not None:
            self.on_cancel()

    def _publish_navigated(self) -> None:
        selected_index = self.selected_index
        if selected_index < 0:
            return
        if self.event_bus is None:
            return
        self.event_bus.publish(UINavigated(index=selected_index))

    def _index_for(self, element: UIControl | None) -> int:
        if element is None:
            return -1
        for index, button in enumerate(self.buttons):
            if button is element:
                return index
        return -1
