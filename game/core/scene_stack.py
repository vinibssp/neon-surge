from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

import pygame

from game.audio.mixer_backend import MUSIC_ENDED_EVENT
from game.core.events import AudioContextChanged, EventBus

if TYPE_CHECKING:
    from game.audio.audio_settings_manager import AudioSettingsManager
    from game.core.display_settings import DisplaySettingsManager
    from game.core.input_settings import InputSettingsManager
    from game.core.localization import LocalizationManager


class Scene(ABC):
    transparent: bool = False

    def __init__(self, stack: "SceneStack") -> None:
        self.stack = stack

    @abstractmethod
    def handle_input(self, events: list[pygame.event.Event]) -> None:
        ...

    @abstractmethod
    def update(self, dt: float) -> None:
        ...

    @abstractmethod
    def render(self, screen: pygame.Surface) -> None:
        ...

    def on_enter(self) -> None:
        pass

    def on_exit(self) -> None:
        pass


class SceneStack:
    def __init__(self) -> None:
        self._stack: list[Scene] = []
        self.event_bus = EventBus()
        self.audio_settings_manager: AudioSettingsManager | None = None
        self.display_settings_manager: DisplaySettingsManager | None = None
        self.input_settings_manager: InputSettingsManager | None = None
        self.localization_manager: LocalizationManager | None = None
        self.joysticks: list[pygame.joystick.Joystick] = []
        self._refresh_joysticks()

    def _refresh_joysticks(self) -> None:
        """Initialize and maintain joystick objects to ensure events are pumped."""
        self.joysticks = []
        for i in range(pygame.joystick.get_count()):
            try:
                joy = pygame.joystick.Joystick(i)
                # In Pygame 2.x, creating the Joystick object is usually 
                # enough to start receiving events for it.
                self.joysticks.append(joy)
            except pygame.error:
                continue

    def push(self, scene: Scene) -> None:
        self._stack.append(scene)
        scene.on_enter()

    def pop(self) -> Scene | None:
        if not self._stack:
            return None
        scene = self._stack.pop()
        scene.on_exit()
        return scene

    def replace(self, scene: Scene) -> None:
        self.pop()
        self.push(scene)

    def top(self) -> Scene | None:
        return None if not self._stack else self._stack[-1]

    def is_empty(self) -> bool:
        return len(self._stack) == 0

    def handle_input(self, events: list[pygame.event.Event]) -> None:
        for event in events:
            if event.type == MUSIC_ENDED_EVENT:
                self.event_bus.publish(AudioContextChanged(context="menu", reason="game_over_music_finished"))
            
            # Hot-plug support
            if event.type in (pygame.JOYDEVICEADDED, pygame.JOYDEVICEREMOVED):
                self._refresh_joysticks()

        scene = self.top()
        if scene is not None:
            scene.handle_input(events)

    def update(self, dt: float) -> None:
        scene = self.top()
        if scene is not None:
            scene.update(dt)

    def render(self, screen: pygame.Surface) -> None:
        if not self._stack:
            return

        start_index = len(self._stack) - 1
        for index in range(len(self._stack) - 1, -1, -1):
            if not self._stack[index].transparent:
                start_index = index
                break

        for scene in self._stack[start_index:]:
            scene.render(screen)
