from __future__ import annotations

import pygame
from pygame import Vector2

from game.core.command import Command, DashCommand, MoveCommand, NuclearBombCommand, ParryCommand
from game.core.input_settings import InputSettings


class InputHandler:
    def __init__(self, settings: InputSettings | None = None) -> None:
        self.settings = settings or InputSettings()
        self.joysticks = []
        self._refresh_joysticks()

    def _refresh_joysticks(self) -> None:
        self.joysticks = [pygame.joystick.Joystick(i) for i in range(pygame.joystick.get_count())]
        for joy in self.joysticks:
            if not joy.get_init():
                joy.init()

    def build_commands(self, events: list[pygame.event.Event], pressed: pygame.key.ScancodeWrapper) -> list[Command]:
        commands: list[Command] = []
        
        # Keyboard movement
        up_pressed = any(pressed[k] for k in self.settings.up if k < len(pressed))
        down_pressed = any(pressed[k] for k in self.settings.down if k < len(pressed))
        left_pressed = any(pressed[k] for k in self.settings.left if k < len(pressed))
        right_pressed = any(pressed[k] for k in self.settings.right if k < len(pressed))

        move_dir = Vector2(
            float(right_pressed) - float(left_pressed),
            float(down_pressed) - float(up_pressed),
        )

        # Joystick movement (Axes 0 and 1 are usually Left Stick)
        if pygame.joystick.get_count() > 0:
            for joy in self.joysticks:
                try:
                    jx = joy.get_axis(0)
                    jy = joy.get_axis(1)
                    
                    if abs(jx) > self.settings.joy_deadzone or abs(jy) > self.settings.joy_deadzone:
                        # Override or combine with keyboard
                        move_dir.x = jx
                        move_dir.y = jy
                except pygame.error:
                    continue

        # Always append MoveCommand to ensure the player stops when there is no input
        commands.append(MoveCommand(move_dir))

        # Action commands (Events)
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key in self.settings.dash:
                    commands.append(DashCommand())
                if event.key in self.settings.parry:
                    commands.append(ParryCommand())
                if event.key in self.settings.bomb:
                    commands.append(NuclearBombCommand())
            
            if event.type == pygame.JOYBUTTONDOWN:
                if event.button in self.settings.joy_dash:
                    commands.append(DashCommand())
                if event.type == pygame.JOYBUTTONDOWN and event.button in self.settings.joy_parry:
                    commands.append(ParryCommand())
                if event.type == pygame.JOYBUTTONDOWN and event.button in self.settings.joy_bomb:
                    commands.append(NuclearBombCommand())
            
            # Handle joystick connection/disconnection
            if event.type in (pygame.JOYDEVICEADDED, pygame.JOYDEVICEREMOVED):
                self._refresh_joysticks()

        return commands
