from __future__ import annotations

import pygame
from pygame import Vector2

from game.core.command import Command, DashCommand, MoveCommand, NuclearBombCommand, ParryCommand


class InputHandler:
    def build_commands(self, events: list[pygame.event.Event], pressed: pygame.key.ScancodeWrapper) -> list[Command]:
        commands: list[Command] = []
        direction = Vector2(
            float(pressed[pygame.K_d]) - float(pressed[pygame.K_a]),
            float(pressed[pygame.K_s]) - float(pressed[pygame.K_w]),
        )
        commands.append(MoveCommand(direction))

        for event in events:
            if event.type == pygame.KEYDOWN and event.key in (pygame.K_SPACE, pygame.K_LSHIFT, pygame.K_RSHIFT):
                commands.append(DashCommand())
            if event.type == pygame.KEYDOWN and event.key == pygame.K_j:
                commands.append(ParryCommand())
            if event.type == pygame.KEYDOWN and event.key == pygame.K_i:
                commands.append(NuclearBombCommand())

        return commands
