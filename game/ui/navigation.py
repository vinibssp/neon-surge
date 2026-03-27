from __future__ import annotations

from typing import Callable, Protocol, runtime_checkable

import pygame
import pygame_gui
from pygame_gui.elements import UITextEntryLine

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
        
        # Navigation management for continuous input
        self._last_nav_time = 0.0
        self._initial_nav_delay = 0.4  # Delay before starting repeat
        self._repeat_nav_rate = 0.08   # Rate of repeat after initial delay
        self._is_repeating = False
        self._joy_deadzone = 0.5
        self._current_direction = (0, 0) # (dx, dy)

    def process_event(self, event: pygame.event.Event) -> bool:
        if event.type == pygame.KEYDOWN:
            return self.navigator.on_keydown(event)

        # Joystick Buttons
        if event.type == pygame.JOYBUTTONDOWN:
            if event.button == 0: # A / Cross
                self.navigator.confirm_selected()
                return True
            if event.button == 1: # B / Circle
                self.navigator.cancel()
                return True

        # Joystick Hat (D-pad) - immediate response
        if event.type == pygame.JOYHATMOTION:
            hx, hy = event.value
            if hx != 0 or hy != 0:
                self.navigator.move_selection_spatial(hx, -hy) # hy is inverted in hats
                self._last_nav_time = pygame.time.get_ticks() / 1000.0
                return True

        # Pygame GUI Events
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

        return False

    def update(self, dt: float) -> None:
        """Handle continuous navigation (input repeat) for analog sticks and keys."""
        if not self.navigator.enabled:
            return

        now = pygame.time.get_ticks() / 1000.0
        
        # Check analog sticks
        found_input = False
        if pygame.joystick.get_count() > 0:
            try:
                joy = pygame.joystick.Joystick(0)
                jx = joy.get_axis(0)
                jy = joy.get_axis(1)
                
                if abs(jx) > self._joy_deadzone or abs(jy) > self._joy_deadzone:
                    dx = 1 if jx > self._joy_deadzone else (-1 if jx < -self._joy_deadzone else 0)
                    dy = 1 if jy > self._joy_deadzone else (-1 if jy < -self._joy_deadzone else 0)
                    
                    if (dx, dy) != (0, 0):
                        found_input = True
                        if (dx, dy) != self._current_direction:
                            # New direction: immediate move
                            self.navigator.move_selection_spatial(dx, dy)
                            self._current_direction = (dx, dy)
                            self._last_nav_time = now
                            self._is_repeating = False
                        else:
                            # Same direction: check for repeat
                            delay = self._repeat_nav_rate if self._is_repeating else self._initial_nav_delay
                            if now - self._last_nav_time > delay:
                                self.navigator.move_selection_spatial(dx, dy)
                                self._last_nav_time = now
                                self._is_repeating = True
            except pygame.error:
                pass

        if not found_input:
            self._current_direction = (0, 0)
            self._is_repeating = False


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
        self.enabled = True
        
        # Audio events helper
        self._hover_sound = "menu_button"
        self._accept_sound = "menu_accept"
        self._cancel_sound = "menu_reject"
        
        first_active_control = self._first_active_control()
        if first_active_control is not None:
            self._set_selected_element(first_active_control, publish_navigation=False, play_sound=False)

    @property
    def selected_index(self) -> int:
        return self._index_for(self._selected_element)

    @property
    def selected_control(self) -> UIControl | None:
        return self._selected_element

    def knows_control(self, element: object) -> bool:
        return self._index_for(element) >= 0

    def on_control_hovered(self, element: UIControl) -> None:
        if not self.enabled: return
        if self._index_for(element) < 0 or not self._is_active(element): return
        if self._selected_element is element: return
        self._set_selected_element(element)

    def on_control_pressed(self, element: UIControl) -> None:
        if not self.enabled: return
        if self._index_for(element) < 0 or not self._is_active(element): return
        
        self._set_selected_element(element, publish_navigation=False, play_sound=False)
        self._play_sound(self._accept_sound)
        
        if self.event_bus:
            self.event_bus.publish(UIConfirmed(index=self.selected_index))
        
        self._activate_control(element)
        action = self.actions.get(element)
        if action: action()

    def cancel(self) -> None:
        if not self.enabled: return
        self._play_sound(self._cancel_sound)
        if self.event_bus:
            self.event_bus.publish(UICancelled())
        if self.on_cancel:
            self.on_cancel()

    def on_keydown(self, event: pygame.event.Event) -> bool:
        if not self.enabled or not self._has_active_controls():
            return False

        if self._has_focused_text_entry():
            if event.key == pygame.K_ESCAPE:
                self.cancel()
                return True
            return False

        key = event.key
        if key in (pygame.K_UP, pygame.K_w):
            self.move_selection_spatial(0, -1)
            return True
        if key in (pygame.K_DOWN, pygame.K_s):
            self.move_selection_spatial(0, 1)
            return True
        if key in (pygame.K_LEFT, pygame.K_a):
            self.move_selection_spatial(-1, 0)
            return True
        if key in (pygame.K_RIGHT, pygame.K_d):
            self.move_selection_spatial(1, 0)
            return True
        if key == pygame.K_TAB:
            self.move_selection(-1 if event.mod & pygame.KMOD_SHIFT else 1)
            return True
        if key == pygame.K_HOME:
            self.select_first_active(); return True
        if key == pygame.K_END:
            self.select_last_active(); return True
        if key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
            if key == pygame.K_SPACE and isinstance(self._selected_element, UITextEntryLine):
                return False
            self.confirm_selected()
            return True
        if key in (pygame.K_ESCAPE, pygame.K_BACKSPACE):
            if key == pygame.K_BACKSPACE and isinstance(self._selected_element, UITextEntryLine):
                return False
            self.cancel()
            return True
        return False

    def move_selection_spatial(self, dx: int, dy: int) -> None:
        if not self.controls or not self.enabled:
            return

        if self._selected_element is None:
            self.select_first_active()
            return

        current_rect = self._get_rect(self._selected_element)
        if current_rect is None:
            self.move_selection(dy if dy != 0 else dx)
            return

        current_center = pygame.Vector2(current_rect.center)
        best_candidate = None
        min_dist = float('inf')
        
        wrap_candidate = None
        max_wrap_dist = -float('inf')

        for control in self.controls:
            if control is self._selected_element or not self._is_active(control):
                continue
            
            rect = self._get_rect(control)
            if rect is None: continue
            
            candidate_center = pygame.Vector2(rect.center)
            diff = candidate_center - current_center
            
            # Direct movement
            is_in_direction = False
            if dx > 0 and diff.x > 0: is_in_direction = True
            elif dx < 0 and diff.x < 0: is_in_direction = True
            elif dy > 0 and diff.y > 0: is_in_direction = True
            elif dy < 0 and diff.y < 0: is_in_direction = True
            
            if is_in_direction:
                dist = diff.length_squared()
                # Penalize off-axis deviation
                if dx != 0: dist += (diff.y * diff.y) * 10.0
                if dy != 0: dist += (diff.x * diff.x) * 10.0
                if dist < min_dist:
                    min_dist = dist
                    best_candidate = control
            else:
                # Wrap-around
                wrap_dist = 0.0
                if dx > 0: wrap_dist = -diff.x
                elif dx < 0: wrap_dist = diff.x
                elif dy > 0: wrap_dist = -diff.y
                elif dy < 0: wrap_dist = diff.y
                
                cross_axis_error = abs(diff.y if dx != 0 else diff.x)
                wrap_score = wrap_dist - (cross_axis_error * 2.0)
                if wrap_score > max_wrap_dist:
                    max_wrap_dist = wrap_score
                    wrap_candidate = control
        
        target = best_candidate or wrap_candidate
        if target:
            self._set_selected_element(target)

    def select_control(self, element: UIControl) -> None:
        if self.knows_control(element) and self._is_active(element):
            self._set_selected_element(element)

    def select_index(self, index: int) -> None:
        if 0 <= index < len(self.controls):
            self.select_control(self.controls[index])

    def move_selection(self, delta: int) -> None:
        if not self.enabled or not self._has_active_controls(): return
        step = 1 if delta >= 0 else -1
        curr = self.selected_index
        for _ in range(len(self.controls)):
            curr = (curr + step) % len(self.controls)
            if self._is_active(self.controls[curr]):
                self.select_index(curr)
                return

    def select_first_active(self) -> None:
        c = self._first_active_control()
        if c: self._set_selected_element(c)

    def select_last_active(self) -> None:
        c = self._last_active_control()
        if c: self._set_selected_element(c)

    def confirm_selected(self) -> None:
        if self._selected_element and self._is_active(self._selected_element):
            self.on_control_pressed(self._selected_element)

    def _set_selected_element(self, element: UIControl, publish_navigation: bool = True, play_sound: bool = True) -> None:
        if not self._is_active(element) or self._selected_element is element:
            return

        if self._selected_element:
            self._unselect(self._selected_element)
            self._unfocus(self._selected_element)

        self._selected_element = element
        self._focus(self._selected_element)
        self._select(self._selected_element)

        if play_sound:
            self._play_sound(self._hover_sound)

        if publish_navigation:
            self._publish_navigated()

    def _play_sound(self, sound_name: str) -> None:
        pygame.event.post(pygame.event.Event(pygame.USEREVENT, {"sound": sound_name}))

    def _publish_navigated(self) -> None:
        if self.event_bus and self.selected_index >= 0:
            self.event_bus.publish(UINavigated(index=self.selected_index))

    def _index_for(self, element: object | None) -> int:
        if element is None: return -1
        for i, c in enumerate(self.controls):
            if c is element: return i
        return -1

    def _has_active_controls(self) -> bool:
        return self._first_active_control() is not None

    def _first_active_control(self) -> UIControl | None:
        for c in self.controls:
            if self._is_active(c): return c
        return None

    def _last_active_control(self) -> UIControl | None:
        for c in reversed(self.controls):
            if self._is_active(c): return c
        return None

    def _get_rect(self, element: UIControl) -> pygame.Rect | None:
        for attr in ["get_abs_rect", "rect", "relative_rect"]:
            val = getattr(element, attr, None)
            if callable(val): val = val()
            if isinstance(val, pygame.Rect): return val
        return None

    @staticmethod
    def _is_active(element: UIControl) -> bool:
        enabled = getattr(element, "is_enabled", True)
        if callable(enabled):
            try: return bool(enabled())
            except: return False
        return bool(enabled)

    @staticmethod
    def _focus(e: UIControl) -> None:
        f = getattr(e, "focus", None)
        if callable(f): f()

    @staticmethod
    def _unfocus(e: UIControl) -> None:
        u = getattr(e, "unfocus", None)
        if callable(u): u()

    @staticmethod
    def _select(e: UIControl) -> None:
        s = getattr(e, "select", None)
        if callable(s): s()

    @staticmethod
    def _unselect(e: UIControl) -> None:
        u = getattr(e, "unselect", None)
        if callable(u): u()

    @staticmethod
    def _activate_control(e: UIControl) -> None:
        if isinstance(e, pygame_gui.elements.UICheckBox):
            t = getattr(e, "toggle", None)
            if callable(t): t(); return
            if bool(getattr(e, "checked", False)):
                u = getattr(e, "uncheck", None)
                if callable(u): u()
            else:
                c = getattr(e, "check", None)
                if callable(c): c()

    def _has_focused_text_entry(self) -> bool:
        for c in self.controls:
            if isinstance(c, UITextEntryLine) and getattr(c, "is_focused", False):
                return True
        return False
