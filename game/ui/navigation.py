from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Callable

import pygame
import pygame_gui
from pygame import Vector2

from game.core.events import EventBus, UICancelled, UIConfirmed, UINavigated
from game.ui.types import UIControl


class UICommand(ABC):
    @abstractmethod
    def execute(self, navigator: "UINavigator") -> None:
        ...


@dataclass(frozen=True)
class UINavigateCommand(UICommand):
    delta: int

    def execute(self, navigator: "UINavigator") -> None:
        navigator.move(self.delta)


@dataclass(frozen=True)
class UIConfirmCommand(UICommand):
    def execute(self, navigator: "UINavigator") -> None:
        navigator.confirm()


@dataclass(frozen=True)
class UISelectElementCommand(UICommand):
    element: UIControl

    def execute(self, navigator: "UINavigator") -> None:
        navigator.select_by_element(self.element)


@dataclass(frozen=True)
class UIPressElementCommand(UICommand):
    element: UIControl

    def execute(self, navigator: "UINavigator") -> None:
        navigator.press_element(self.element)


@dataclass(frozen=True)
class UIMouseHoverCommand(UICommand):
    position: Vector2

    def execute(self, navigator: "UINavigator") -> None:
        navigator.select_by_position(self.position)


@dataclass(frozen=True)
class UIMouseClickCommand(UICommand):
    position: Vector2

    def execute(self, navigator: "UINavigator") -> None:
        navigator.select_by_position(self.position)
        navigator.confirm()


@dataclass(frozen=True)
class UICancelCommand(UICommand):
    def execute(self, navigator: "UINavigator") -> None:
        navigator.cancel()


class UINavigator:
    def __init__(
        self,
        buttons: list[UIControl],
        actions: list[Callable[[], None]] | None = None,
        on_cancel: Callable[[], None] | None = None,
        event_bus: EventBus | None = None,
    ) -> None:
        self.buttons = buttons
        self.actions = actions or []
        self.on_cancel = on_cancel
        self.event_bus = event_bus
        self.selected_index = 0 if buttons else -1
        self.sync_hover_state()

    def move(self, delta: int) -> None:
        if not self.buttons or delta == 0:
            return
        previous_index = self.selected_index
        next_index = (self.selected_index + delta) % len(self.buttons)
        self.selected_index = next_index
        self.sync_hover_state()
        if self.selected_index != previous_index:
            self._publish_navigated()

    def select_by_position(self, position: Vector2) -> None:
        previous_index = self.selected_index
        for index, button in enumerate(self.buttons):
            if self._button_rect(button).collidepoint(position.x, position.y):
                self.selected_index = index
                self.sync_hover_state()
                if self.selected_index != previous_index:
                    self._publish_navigated()
                return

    def select_by_element(self, element: UIControl) -> bool:
        previous_index = self.selected_index
        for index, button in enumerate(self.buttons):
            if button is element:
                self.selected_index = index
                self.sync_hover_state()
                if self.selected_index != previous_index:
                    self._publish_navigated()
                return True
        return False

    def press_element(self, element: UIControl) -> None:
        if self.select_by_element(element):
            self.confirm()

    def confirm(self) -> None:
        if self.selected_index < 0 or self.selected_index >= len(self.buttons):
            return
        if self.event_bus is not None:
            self.event_bus.publish(UIConfirmed(index=self.selected_index))
        if self.selected_index < len(self.actions):
            self.actions[self.selected_index]()

    def cancel(self) -> None:
        if self.event_bus is not None:
            self.event_bus.publish(UICancelled())
        if self.on_cancel is not None:
            self.on_cancel()

    def _publish_navigated(self) -> None:
        if self.event_bus is None:
            return
        if self.selected_index < 0:
            return
        self.event_bus.publish(UINavigated(index=self.selected_index))

    def sync_hover_state(self) -> None:
        for index, button in enumerate(self.buttons):
            is_selected = index == self.selected_index
            self._apply_selection_state(button, is_selected)

    @staticmethod
    def _button_rect(button: UIControl) -> pygame.Rect:
        return button.rect

    @staticmethod
    def _apply_selection_state(button: UIControl, is_selected: bool) -> None:
        if is_selected:
            button.select()
            return
        button.unselect()


class UINavigationInputHandler:
    AXIS_DEADZONE = 0.6

    def build_commands(self, events: list[pygame.event.Event]) -> list[UICommand]:
        commands: list[UICommand] = []
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_UP, pygame.K_w, pygame.K_LEFT, pygame.K_a):
                    commands.append(UINavigateCommand(delta=-1))
                elif event.key in (pygame.K_DOWN, pygame.K_s, pygame.K_RIGHT, pygame.K_d):
                    commands.append(UINavigateCommand(delta=1))
                elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
                    commands.append(UIConfirmCommand())
                elif event.key == pygame.K_ESCAPE:
                    commands.append(UICancelCommand())

            if event.type == pygame_gui.UI_BUTTON_ON_HOVERED:
                ui_element = event.ui_element
                if isinstance(ui_element, pygame_gui.elements.UIButton):
                    commands.append(UISelectElementCommand(element=ui_element))
            elif event.type == pygame_gui.UI_BUTTON_PRESSED:
                ui_element = event.ui_element
                if isinstance(ui_element, pygame_gui.elements.UIButton):
                    commands.append(UIPressElementCommand(element=ui_element))

            if event.type == pygame.JOYHATMOTION:
                if event.value[1] > 0:
                    commands.append(UINavigateCommand(delta=-1))
                elif event.value[1] < 0:
                    commands.append(UINavigateCommand(delta=1))
            elif event.type == pygame.JOYAXISMOTION and event.axis == 1:
                if event.value <= -self.AXIS_DEADZONE:
                    commands.append(UINavigateCommand(delta=-1))
                elif event.value >= self.AXIS_DEADZONE:
                    commands.append(UINavigateCommand(delta=1))
            elif event.type == pygame.JOYBUTTONDOWN and event.button == 0:
                commands.append(UIConfirmCommand())
            elif event.type == pygame.JOYBUTTONDOWN and event.button == 1:
                commands.append(UICancelCommand())

        return commands
