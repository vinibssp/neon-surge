from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Callable

import pygame
from pygame import Vector2

from game.ui.elements import Button


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
    def __init__(self, buttons: list[Button], on_cancel: Callable[[], None] | None = None) -> None:
        self.buttons = buttons
        self.on_cancel = on_cancel
        self.selected_index = 0 if buttons else -1
        self.sync_hover_state()

    def move(self, delta: int) -> None:
        if not self.buttons or delta == 0:
            return
        next_index = (self.selected_index + delta) % len(self.buttons)
        self.selected_index = next_index
        self.sync_hover_state()

    def select_by_position(self, position: Vector2) -> None:
        for index, button in enumerate(self.buttons):
            if button.rect().collidepoint(position.x, position.y):
                self.selected_index = index
                self.sync_hover_state()
                return

    def confirm(self) -> None:
        if self.selected_index < 0 or self.selected_index >= len(self.buttons):
            return
        button = self.buttons[self.selected_index]
        if button.callback is not None:
            button.callback()

    def cancel(self) -> None:
        if self.on_cancel is not None:
            self.on_cancel()

    def sync_hover_state(self) -> None:
        for index, button in enumerate(self.buttons):
            button.hovered = index == self.selected_index


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

            if event.type == pygame.MOUSEMOTION:
                commands.append(UIMouseHoverCommand(position=Vector2(event.pos[0], event.pos[1])))
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                commands.append(UIMouseClickCommand(position=Vector2(event.pos[0], event.pos[1])))

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
