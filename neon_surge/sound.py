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
        # Path relative to the project root where neon_surge.py is run
        base_path = "NeonSurge/assets/sounds/"
        
        sound_files = {
            # Player sounds
            'player_walk': "player_walk.wav",
            'player_dash': "player_dash.wav",
            'player_hurt': "player_hurt.wav",
            'player_death': "player_death.wav",

            # Enemy sounds
            'enemy_spawn': "enemy_spawn.wav",
            'enemy_shoot': "enemy_shoot.wav",
            'enemy_hurt': "enemy_hurt.wav",
            'enemy_death': "enemy_death.wav",

            # Object sounds
            'coin_collect': "coin_collect.wav",

            # Portal sounds
            'portal_activation': "portal_activation.wav",
            'portal_enter': "portal_enter.wav",
        }

        for name, filename in sound_files.items():
            path = base_path + filename
            try:
                self.sounds[name] = pygame.mixer.Sound(path)
            except (pygame.error, FileNotFoundError):
                # Silent failure as requested
                pass

        self._is_walking = False
        self.set_sfx_volume(0.5)  # Default volume

    def play(self, sound_name):
        """Plays a sound from the loaded SFX library."""
        if sound_name in self.sounds:
            self.sounds[sound_name].play()

    def start_walking(self):
        """Starts the looping walk sound if it's not already playing."""
        if not self._is_walking and 'player_walk' in self.sounds:
            self.sounds['player_walk'].play(loops=-1)
            self._is_walking = True

    def stop_walking(self):
        """Stops the looping walk sound if it is playing."""
        if self._is_walking and 'player_walk' in self.sounds:
            self.sounds['player_walk'].stop()
            self._is_walking = False

    def set_sfx_volume(self, volume):
        """
        Sets the volume for all sound effects.
        """
        for sound in self.sounds.values():
            sound.set_volume(volume)
