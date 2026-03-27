from __future__ import annotations

import pygame
from pygame import Vector2

from game.core.command import Command, DashCommand, MoveCommand, NuclearBombCommand, ParryCommand
from game.core.input_settings import InputSettings


class InputHandler:
    def __init__(self, settings: InputSettings | None = None) -> None:
        self.settings = settings or InputSettings()

    def build_commands(self, events: list[pygame.event.Event], pressed: pygame.key.ScancodeWrapper) -> list[Command]:
        commands: list[Command] = []
        
        up_pressed = any(pressed[k] for k in self.settings.up if k < len(pressed))
        down_pressed = any(pressed[k] for k in self.settings.down if k < len(pressed))
        left_pressed = any(pressed[k] for k in self.settings.left if k < len(pressed))
        right_pressed = any(pressed[k] for k in self.settings.right if k < len(pressed))

        direction = Vector2(
            float(right_pressed) - float(left_pressed),
            float(down_pressed) - float(up_pressed),
        )
        commands.append(MoveCommand(direction))

        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key in self.settings.dash:
                    commands.append(DashCommand())
                if event.key in self.settings.parry:
                    commands.append(ParryCommand())
                if event.key in self.settings.bomb:
                    commands.append(NuclearBombCommand())

        return commands
