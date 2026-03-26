from __future__ import annotations

from typing import Callable, Protocol, runtime_checkable

import pygame
import pygame_gui

from game.core.events import EventBus, UICancelled, UIConfirmed, UINavigated


@runtime_checkable
class FocusableControl(Protocol):
    def focus(self) -> None: ...

    def unfocus(self) -> None: ...


UIControl = FocusableControl


class PygameGUIEventAdapter:
    def __init__(self, navigator: "UINavigator") -> None:
        self.navigator = navigator
        self._slider_moved_event = getattr(pygame_gui, "UI_HORIZONTAL_SLIDER_MOVED", None)
        self._text_entry_changed_event = getattr(pygame_gui, "UI_TEXT_ENTRY_CHANGED", None)
        self._text_entry_finished_event = getattr(pygame_gui, "UI_TEXT_ENTRY_FINISHED", None)

    def process_event(self, event: pygame.event.Event) -> bool:
        if event.type == pygame.KEYDOWN:
            return self.navigator.on_keydown(event)

        if event.type == pygame_gui.UI_BUTTON_ON_HOVERED:
            ui_element = event.ui_element
            if self.navigator.knows_control(ui_element):
                self.navigator.on_control_hovered(ui_element)
            return False

        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            ui_element = event.ui_element
            if self.navigator.knows_control(ui_element):
                self.navigator.on_control_pressed(ui_element)
            return False

        if self._slider_moved_event is not None and event.type == self._slider_moved_event:
            ui_element = getattr(event, "ui_element", None)
            if self.navigator.knows_control(ui_element):
                self.navigator.on_control_hovered(ui_element)
            return False

        if self._text_entry_changed_event is not None and event.type == self._text_entry_changed_event:
            ui_element = getattr(event, "ui_element", None)
            if self.navigator.knows_control(ui_element):
                self.navigator.on_control_hovered(ui_element)
            return False

        if self._text_entry_finished_event is not None and event.type == self._text_entry_finished_event:
            ui_element = getattr(event, "ui_element", None)
            if self.navigator.knows_control(ui_element):
                self.navigator.on_control_pressed(ui_element)
            return False

        return False


class UINavigator:
    def __init__(
        self,
        controls: list[UIControl] | None = None,
        actions: dict[UIControl, Callable[[], None]] | None = None,
        on_cancel: Callable[[], None] | None = None,
        event_bus: EventBus | None = None,
        buttons: list[UIControl] | None = None,
    ) -> None:
        if controls is None:
            controls = buttons or []

        self.controls = tuple(controls)
        self.actions = actions or {}
        self.on_cancel = on_cancel
        self.event_bus = event_bus
        self._selected_element: UIControl | None = None
        first_active_control = self._first_active_control()
        if first_active_control is not None:
            self._set_selected_element(first_active_control, publish_navigation=False)

    @property
    def buttons(self) -> tuple[UIControl, ...]:
        return self.controls

    @property
    def selected_index(self) -> int:
        return self._index_for(self._selected_element)

    @property
    def selected_control(self) -> UIControl | None:
        return self._selected_element

    def knows_control(self, element: object) -> bool:
        return self._index_for(element) >= 0

    def on_control_hovered(self, element: UIControl) -> None:
        if self._index_for(element) < 0:
            return
        if not self._is_active(element):
            return
        if self._selected_element is element:
            return
        self._set_selected_element(element)

    def on_control_pressed(self, element: UIControl) -> None:
        if self._index_for(element) < 0:
            return
        if not self._is_active(element):
            return
        self._set_selected_element(element, publish_navigation=False)
        selected_index = self.selected_index
        if selected_index < 0:
            return
        if self.event_bus is not None:
            self.event_bus.publish(UIConfirmed(index=selected_index))
        self._activate_control(element)
        action = self.actions.get(element)
        if action is not None:
            action()

    def on_button_hovered(self, element: UIControl) -> None:
        self.on_control_hovered(element)

    def on_button_pressed(self, element: UIControl) -> None:
        self.on_control_pressed(element)

    def cancel(self) -> None:
        if self.event_bus is not None:
            self.event_bus.publish(UICancelled())
        if self.on_cancel is not None:
            self.on_cancel()

    def on_keydown(self, event: pygame.event.Event) -> bool:
        if not self._has_active_controls():
            return False

        key = event.key
        if key in (pygame.K_UP, pygame.K_LEFT, pygame.K_w, pygame.K_a):
            self.move_selection(-1)
            return True
        if key in (pygame.K_DOWN, pygame.K_RIGHT, pygame.K_s, pygame.K_d):
            self.move_selection(1)
            return True
        if key == pygame.K_TAB:
            direction = -1 if event.mod & pygame.KMOD_SHIFT else 1
            self.move_selection(direction)
            return True
        if key == pygame.K_HOME:
            self.select_first_active()
            return True
        if key == pygame.K_END:
            self.select_last_active()
            return True
        if key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
            self.confirm_selected()
            return True
        if key in (pygame.K_ESCAPE, pygame.K_BACKSPACE):
            self.cancel()
            return True
        return False

    def move_selection(self, delta: int) -> None:
        if not self._has_active_controls():
            return

        next_index = self._next_active_index(delta)
        if next_index is None:
            return
        self.select_index(next_index)

    def select_index(self, index: int) -> None:
        if not self.controls:
            return
        if index < 0 or index >= len(self.controls):
            return
        selected_control = self.controls[index]
        if not self._is_active(selected_control):
            return
        self._set_selected_element(selected_control)

    def select_first_active(self) -> None:
        first_active_control = self._first_active_control()
        if first_active_control is None:
            return
        self._set_selected_element(first_active_control)

    def select_last_active(self) -> None:
        last_active_control = self._last_active_control()
        if last_active_control is None:
            return
        self._set_selected_element(last_active_control)

    def confirm_selected(self) -> None:
        if self._selected_element is None:
            return
        if not self._is_active(self._selected_element):
            return
        self.on_control_pressed(self._selected_element)

    def _set_selected_element(self, element: UIControl, publish_navigation: bool = True) -> None:
        if not self._is_active(element):
            return
        if self._selected_element is element:
            return

        previous_element = self._selected_element
        if previous_element is not None:
            self._unselect(previous_element)
            self._unfocus(previous_element)

        self._selected_element = element
        self._focus(self._selected_element)
        self._select(self._selected_element)

        if publish_navigation:
            self._publish_navigated()

    def _publish_navigated(self) -> None:
        selected_index = self.selected_index
        if selected_index < 0:
            return
        if self.event_bus is None:
            return
        self.event_bus.publish(UINavigated(index=selected_index))

    def _index_for(self, element: object | None) -> int:
        if element is None:
            return -1
        for index, control in enumerate(self.controls):
            if control is element:
                return index
        return -1

    def _has_active_controls(self) -> bool:
        return self._first_active_control() is not None

    def _first_active_control(self) -> UIControl | None:
        for control in self.controls:
            if self._is_active(control):
                return control
        return None

    def _last_active_control(self) -> UIControl | None:
        for control in reversed(self.controls):
            if self._is_active(control):
                return control
        return None

    def _next_active_index(self, delta: int) -> int | None:
        if not self.controls:
            return None

        normalized_delta = 1 if delta >= 0 else -1
        start_index = self.selected_index

        if start_index < 0 or not self._is_active(self.controls[start_index]):
            if normalized_delta > 0:
                first_active_control = self._first_active_control()
                return self._index_for(first_active_control)
            last_active_control = self._last_active_control()
            return self._index_for(last_active_control)

        candidate_index = start_index
        for _ in range(len(self.controls)):
            candidate_index = (candidate_index + normalized_delta) % len(self.controls)
            if self._is_active(self.controls[candidate_index]):
                return candidate_index

        return None

    @staticmethod
    def _is_active(element: UIControl) -> bool:
        enabled = getattr(element, "is_enabled", True)
        if callable(enabled):
            try:
                return bool(enabled())
            except Exception:
                return False
        return bool(enabled)

    @staticmethod
    def _focus(element: UIControl) -> None:
        focus = getattr(element, "focus", None)
        if callable(focus):
            focus()

    @staticmethod
    def _unfocus(element: UIControl) -> None:
        unfocus = getattr(element, "unfocus", None)
        if callable(unfocus):
            unfocus()

    @staticmethod
    def _select(element: UIControl) -> None:
        select = getattr(element, "select", None)
        if callable(select):
            select()

    @staticmethod
    def _unselect(element: UIControl) -> None:
        unselect = getattr(element, "unselect", None)
        if callable(unselect):
            unselect()

    @staticmethod
    def _activate_control(element: UIControl) -> None:
        if isinstance(element, pygame_gui.elements.UICheckBox):
            toggle = getattr(element, "toggle", None)
            if callable(toggle):
                toggle()
                return

            is_checked = bool(getattr(element, "checked", False))
            if is_checked:
                uncheck = getattr(element, "uncheck", None)
                if callable(uncheck):
                    uncheck()
            else:
                check = getattr(element, "check", None)
                if callable(check):
                    check()
