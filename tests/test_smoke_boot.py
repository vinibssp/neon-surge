from __future__ import annotations

import os
import unittest

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")

import pygame

from game.core.game import Game


class _StubSceneStack:
    def __init__(self) -> None:
        self._empty = False
        self.input_calls = 0
        self.update_calls = 0
        self.render_calls = 0

    def is_empty(self) -> bool:
        return self._empty

    def handle_input(self, events: list[pygame.event.Event]) -> None:
        self.input_calls += 1

    def update(self, dt: float) -> None:
        self.update_calls += 1

    def render(self, screen: pygame.Surface) -> None:
        self.render_calls += 1


class SmokeBootTest(unittest.TestCase):
    def setUp(self) -> None:
        pygame.init()
        self.screen = pygame.display.set_mode((320, 180))

    def tearDown(self) -> None:
        pygame.quit()

    def test_game_loop_runs_fixed_updates(self) -> None:
        stack = _StubSceneStack()
        game = Game(screen=self.screen, scene_stack=stack)  # type: ignore[arg-type]
        game.run(max_updates=2)

        self.assertGreaterEqual(stack.input_calls, 1)
        self.assertEqual(stack.update_calls, 2)
        self.assertGreaterEqual(stack.render_calls, 1)

    def test_main_module_imports(self) -> None:
        from game import main

        self.assertTrue(callable(main.main))


if __name__ == "__main__":
    unittest.main()
