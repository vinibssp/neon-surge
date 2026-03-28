from __future__ import annotations

import os
import unittest

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")

import pygame

from game.audio.mixer_backend import MUSIC_ENDED_EVENT
from game.core.events import AudioContextChanged
from game.core.scene_stack import Scene, SceneStack


class _TestScene(Scene):
    def __init__(self, stack: SceneStack, name: str, transparent: bool = False) -> None:
        super().__init__(stack)
        self.name = name
        self.transparent = transparent
        self.entered = 0
        self.exited = 0
        self.handled_events = 0
        self.updated = 0
        self.render_calls: list[str] = []

    def on_enter(self) -> None:
        self.entered += 1

    def on_exit(self) -> None:
        self.exited += 1

    def handle_input(self, events: list[pygame.event.Event]) -> None:
        self.handled_events += 1

    def update(self, dt: float) -> None:
        self.updated += 1

    def render(self, screen: pygame.Surface) -> None:
        self.render_calls.append(self.name)


class SceneStackTest(unittest.TestCase):
    def setUp(self) -> None:
        pygame.init()
        self.screen = pygame.display.set_mode((320, 180))

    def tearDown(self) -> None:
        pygame.quit()

    def test_push_pop_replace_call_lifecycle_hooks(self) -> None:
        stack = SceneStack()
        scene_a = _TestScene(stack, "a")
        scene_b = _TestScene(stack, "b")

        stack.push(scene_a)
        stack.replace(scene_b)

        self.assertEqual(scene_a.entered, 1)
        self.assertEqual(scene_a.exited, 1)
        self.assertEqual(scene_b.entered, 1)

        popped = stack.pop()
        self.assertIs(popped, scene_b)
        self.assertEqual(scene_b.exited, 1)

    def test_only_top_scene_handles_input_and_update(self) -> None:
        stack = SceneStack()
        bottom = _TestScene(stack, "bottom")
        top = _TestScene(stack, "top", transparent=True)
        stack.push(bottom)
        stack.push(top)

        events = [pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_a})]
        stack.handle_input(events)
        stack.update(1.0 / 60.0)

        self.assertEqual(bottom.handled_events, 0)
        self.assertEqual(bottom.updated, 0)
        self.assertEqual(top.handled_events, 1)
        self.assertEqual(top.updated, 1)

    def test_render_starts_from_last_opaque_scene(self) -> None:
        stack = SceneStack()
        background = _TestScene(stack, "background")
        overlay = _TestScene(stack, "overlay", transparent=True)
        stack.push(background)
        stack.push(overlay)

        stack.render(self.screen)

        self.assertEqual(background.render_calls, ["background"])
        self.assertEqual(overlay.render_calls, ["overlay"])

    def test_music_ended_event_publishes_audio_context_changed(self) -> None:
        stack = SceneStack()
        received: list[AudioContextChanged] = []
        stack.event_bus.on(AudioContextChanged, received.append)
        stack.push(_TestScene(stack, "only"))

        events = [pygame.event.Event(MUSIC_ENDED_EVENT)]
        stack.handle_input(events)

        self.assertEqual(len(received), 1)
        self.assertEqual(received[0].context, "menu")
        self.assertEqual(received[0].reason, "game_over_music_finished")


if __name__ == "__main__":
    unittest.main()
