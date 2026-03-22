import pygame

class SoundManager:
    """
    Manages all game sound effects (SFX) and background music (BGM).
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
            
            # UI sounds
            'menu_button': "menu_button.wav",
            'menu_accept': "menu_accept.wav",
            'menu_reject': "menu_reject.wav",

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

        self.current_bgm = None
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

    def play_bgm(self, track_path, volume=0.2):
        """
        Stops any current BGM, then loads and plays a new track looping infinitely.
        Fails silently if file is missing.
        """
        try:
            if self.current_bgm == track_path and pygame.mixer.music.get_busy():
                return
                
            self.stop_bgm()
            # The prompt mentions assets/trilha_menu.wav but they are in NeonSurge/assets/
            full_path = track_path
            pygame.mixer.music.load(full_path)
            pygame.mixer.music.set_volume(volume)
            pygame.mixer.music.play(-1)
            self.current_bgm = track_path
        except:
            # Silent failure as requested
            pass

    def stop_bgm(self):
        """Stops the current BGM."""
        try:
            pygame.mixer.music.stop()
            pygame.mixer.music.unload()
            self.current_bgm = None
        except:
            pass

    def set_bgm_volume(self, volume):
        """Sets the BGM volume."""
        try:
            pygame.mixer.music.set_volume(volume)
        except:
            pass
