from __future__ import annotations

import pygame

from game.config import BACKGROUND_COLOR, FIXED_DT, MAX_FRAME_DT, TARGET_FPS
from game.core.scene_stack import SceneStack


class Game:
    def __init__(self, screen: pygame.Surface, scene_stack: SceneStack) -> None:
        self.screen = screen
        self.scene_stack = scene_stack
        self.clock = pygame.time.Clock()
        self.running = True

    def run(self, max_updates: int | None = None) -> None:
        accumulator = 0.0
        update_count = 0

        while self.running and not self.scene_stack.is_empty():
            frame_dt = min(self.clock.tick(TARGET_FPS) / 1000.0, MAX_FRAME_DT)
            accumulator += frame_dt

            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    self.running = False

            self.scene_stack.handle_input(events)

            while accumulator >= FIXED_DT and self.running:
                self.scene_stack.update(FIXED_DT)
                accumulator -= FIXED_DT
                update_count += 1
                if max_updates is not None and update_count >= max_updates:
                    self.running = False
                    break

            interpolation = accumulator / FIXED_DT
            del interpolation
            self.screen.fill(BACKGROUND_COLOR)
            self.scene_stack.render(self.screen)
            pygame.display.flip()
