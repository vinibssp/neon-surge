from __future__ import annotations

from abc import ABC, abstractmethod

import pygame

from game.core.events import EventBus


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
