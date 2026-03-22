"""
This module provides a centralized SoundManager for handling all game sound effects.
It uses pygame.mixer to load, play, and manage SFX, keeping them separate
from the background music channel.
"""
import pygame

class SoundManager:
    """
    Manages all game sound effects (SFX).
    """
    def __init__(self):
        """
        Initializes the SoundManager, loading all SFX.
        Sounds are loaded once to avoid disk I/O during gameplay.
        Handles missing files gracefully.
        """
        self.sounds = {}
        sound_files = {
            # Player sounds
            'player_walk': "assets/sounds/player_walk.mp3",
            'player_dash': "assets/sounds/player_dash.mp3",
            'player_hurt': "assets/sounds/player_hurt.mp3",
            'player_death': "assets/sounds/player_death.mp3",

            # Enemy sounds
            'enemy_spawn': "assets/sounds/enemy_spawn.mp3",
            'enemy_shoot': "assets/sounds/enemy_shoot.mp3",
            'enemy_hurt': "assets/sounds/enemy_hurt.mp3",
            'enemy_death': "assets/sounds/enemy_death.mp3",

            # Object sounds
            'coin_collect': "assets/sounds/coin_collect.wav",

            # Portal sounds
            'portal_activation': "assets/sounds/portal_activation.wav",
            'portal_enter': "assets/sounds/portal_enter.mp3",
        }

        for name, path in sound_files.items():
            try:
                self.sounds[name] = pygame.mixer.Sound(path)
            except pygame.error:
                print(f"Warning: Sound file not found: {path}")

        self._is_walking = False
        self.set_sfx_volume(0.5)  # Default volume

    def play(self, sound_name):
        """Plays a sound from the loaded SFX library."""
        if sound_name in self.sounds:
            self.sounds[sound_name].play()
        else:
            # This case now primarily handles sounds that failed to load.
            pass

    def start_walking(self):
        """Starts the looping walk sound if it's not already playing."""
        if not self._is_walking:
            self.sounds['player_walk'].play(loops=-1)
            self._is_walking = True

    def stop_walking(self):
        """Stops the looping walk sound if it is playing."""
        if self._is_walking:
            self.sounds['player_walk'].stop()
            self._is_walking = False

    def set_sfx_volume(self, volume):
        """
        Sets the volume for all sound effects.
        Volume should be a float between 0.0 (silent) and 1.0 (full).
        """
        for sound in self.sounds.values():
            sound.set_volume(volume)

    def get_sfx_volume(self):
        """
        Gets the volume of the first sound effect as a representative value.
        """
        return self.sounds['player_walk'].get_volume()
