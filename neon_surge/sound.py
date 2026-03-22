import pygame

class SoundManager:
    """
    Manages all game sound effects (SFX).
    """
    def __init__(self):
        """
        Initializes the SoundManager, loading all SFX.
        Handles missing files or mixer errors gracefully.
        """
        self.sounds = {}
        # Path relative to the project root where neon_surge.py is run
        base_path = "NeonSurge/assets/sounds/"
        
        sound_files = {
            # Player sounds
            'player_dash': "player_dash.wav",
            'player_hurt': "player_hurt.wav",
            'player_death': "player_death.wav",

            # Action sounds
            'coin_collect': "coin_collect.wav",
            'black_hole': "black_hole.wav",
            'menu_button': "menu_button.wav",

            # Portal sounds
            'portal_activation': "portal_activation.wav",
            'portal_enter': "portal_enter.wav",
            'exit_portal': "exit_portal.wav",

            # Enemy sounds
            'enemy_shoot': "enemy_shoot.wav",
        }

        if not pygame.mixer.get_init():
            try:
                pygame.mixer.init()
            except:
                pass

        for name, filename in sound_files.items():
            path = base_path + filename
            try:
                self.sounds[name] = pygame.mixer.Sound(path)
            except:
                # Silent failure as requested
                pass

        self.set_sfx_volume(0.5)

    def play(self, sound_name):
        """Plays a sound if it exists. Fails silently if key or file is missing."""
        if not sound_name:
            return
        sound = self.sounds.get(sound_name)
        if sound:
            try:
                sound.play()
            except:
                # Silent failure as requested
                pass

    def set_sfx_volume(self, volume):
        """Sets the volume for all loaded sound effects."""
        for sound in self.sounds.values():
            try:
                sound.set_volume(volume)
            except:
                pass
