from __future__ import annotations

import pygame
import pygame_gui

from game.config import SCREEN_HEIGHT, SCREEN_WIDTH
from game.core.events import AudioContextChanged
from game.modes.labyrinth_mode import LabyrinthMode
from game.modes.race_infinite_mode import RaceInfiniteMode
from game.modes.race_mode import RaceMode
from game.modes.survival_hardcore_mode import SurvivalHardcoreMode
from game.modes.survival_mode import SurvivalMode
from game.scenes.game_scene import GameScene
from game.scenes.guide_scene import GuideScene
from game.scenes.menus._base_menu_scene import BaseMenuScene
from game.scenes.settings_scene import SettingsScene
from game.scenes.training_setup_scene import TrainingSetupScene
from game.scenes.services import CyberpunkMenuBackgroundRenderer
from game.ui.components import ButtonConfig, LabelConfig, PanelConfig, create_button, create_label, create_panel

MODE_INFO = {
    "race": ("MÓDULO DE CORRIDA", "Navegação em alta velocidade. Colete núcleos de energia e alcance os portais de salto antes do tempo esgotar."),
    "race_infinite": ("INFINITO", "Teste de resistência sistêmica. O ambiente se torna progressivamente mais instável e hostil a cada salto."),
    "survival": ("SOBREVIVÊNCIA", "Protocolo de combate intenso. Sobreviva a ondas de inimigos enquanto lida com anomalias ambientais severas."),
    "hardcore": ("ERRO FATAL", "Simulação sem salvaguardas. Um único dano crítico resulta no encerramento imediato do processo de piloto."),
    "labyrinth": ("LABIRINTO", "Infiltração tática. Localize e neutralize as torres de controle em corredores protegidos por sistemas de segurança."),
    "training": ("TREINAMENTO", "Ambiente de simulação controlada. Configure livremente os parâmetros de combate para refinar suas habilidades."),
}

class MainMenuScene(BaseMenuScene):
    def __init__(self, stack) -> None:
        super().__init__(stack)
        self._elapsed_time = 0.0
        self._background_renderer = CyberpunkMenuBackgroundRenderer()
        self._init_ui()

    def _init_ui(self) -> None:
        # 1. Header
        create_label(
            LabelConfig(
                text="NEON SURGE",
                rect=pygame.Rect((SCREEN_WIDTH // 2 - 400, 40), (800, 100)),
                variant="title",
            ),
            manager=self.ui_manager,
        )
        create_label(
            LabelConfig(
                text="SYNTH COMBAT ARENA",
                rect=pygame.Rect((SCREEN_WIDTH // 2 - 260, 124), (520, 36)),
                variant="subtitle",
            ),
            manager=self.ui_manager,
        )

        # 2. Corner Buttons
        # Top Right: Exit
        self._exit_btn = create_button(
            ButtonConfig(text="X", rect=pygame.Rect((SCREEN_WIDTH - 70, 20), (50, 50)), variant="danger"),
            manager=self.ui_manager
        )
        
        # Bottom Right: Help and Settings
        self._settings_btn = create_button(
            ButtonConfig(text="*", rect=pygame.Rect((SCREEN_WIDTH - 70, SCREEN_HEIGHT - 70), (50, 50)), variant="ghost"),
            manager=self.ui_manager
        )
        self._guide_btn = create_button(
            ButtonConfig(text="?", rect=pygame.Rect((SCREEN_WIDTH - 130, SCREEN_HEIGHT - 70), (50, 50)), variant="primary"),
            manager=self.ui_manager
        )

        # 3. Mode Grid (Original Aesthetics - Centralized)
        btn_w, btn_h = 190, 60
        gap = 15
        cols = 6
        total_w = cols * btn_w + (cols - 1) * gap
        start_x = (SCREEN_WIDTH - total_w) // 2
        start_y = 320

        modes_list = [
            ("CORRIDA", "race", RaceMode(), "race"),
            ("INFINITA", "race_infinite", RaceInfiniteMode(), "race_infinite"),
            ("SOBREVIVÊNCIA", "survival", SurvivalMode(), "survival"),
            ("HARDCORE", "hardcore", SurvivalHardcoreMode(), "hardcore"),
            ("LABIRINTO", "labyrinth", LabyrinthMode(), "labyrinth"),
            ("TREINO", "training", None, "training"),
        ]

        self._mode_btns = []
        for i, (name, tag, mode_obj, variant) in enumerate(modes_list):
            rect = pygame.Rect((start_x + i * (btn_w + gap), start_y), (btn_w, btn_h))
            btn = create_button(
                ButtonConfig(text=name, rect=rect, variant=variant),
                manager=self.ui_manager
            )
            self._mode_btns.append((btn, mode_obj, tag))

        # 4. Info Card (Below Grid)
        self._info_panel = create_panel(
            PanelConfig(rect=pygame.Rect((SCREEN_WIDTH // 2 - 450, 420), (900, 140)), variant="hud"),
            manager=self.ui_manager
        )
        self._info_title = create_label(
            LabelConfig(text="SELECIONE UMA OPERAÇÃO", rect=pygame.Rect((20, 15), (860, 30)), variant="header"),
            manager=self.ui_manager, container=self._info_panel
        )
        self._info_desc = create_label(
            LabelConfig(
                text="Navegue pelos módulos acima para ver os detalhes técnicos da simulação.",
                rect=pygame.Rect((20, 50), (860, 70)),
                variant="guide_body"
            ),
            manager=self.ui_manager, container=self._info_panel
        )

        # 5. Global Ranking (Center Bottom)
        self._ranking_btn = create_button(
            ButtonConfig(
                text="RANKING GLOBAL DE PILOTOS",
                rect=pygame.Rect((SCREEN_WIDTH // 2 - 200, 580), (400, 50)),
                variant="primary"
            ),
            manager=self.ui_manager
        )

        # 6. Navigation
        from game.scenes.leaderboard_scene import LeaderboardScene
        controls = [b[0] for b in self._mode_btns] + [self._ranking_btn, self._guide_btn, self._settings_btn, self._exit_btn]
        
        actions = {
            self._ranking_btn: lambda: self.stack.push(LeaderboardScene(self.stack)),
            self._guide_btn: lambda: self.stack.push(GuideScene(self.stack)),
            self._settings_btn: lambda: self.stack.push(SettingsScene(self.stack)),
            self._exit_btn: self._quit,
        }
        for btn, mode_obj, tag in self._mode_btns:
            if tag == "training":
                actions[btn] = lambda: self.stack.push(TrainingSetupScene(self.stack))
            else:
                actions[btn] = lambda m=mode_obj: self.stack.replace(GameScene(self.stack, m))

        self.set_navigator(controls=controls, actions=actions, on_cancel=self._quit)

    def _update_info_card(self, tag: str | None) -> None:
        if tag in MODE_INFO:
            title, desc = MODE_INFO[tag]
            self._info_title.set_text(title)
            self._info_desc.set_text(desc)
        else:
            self._info_title.set_text("SISTEMA DE INTERFACE")
            self._info_desc.set_text("Pronto para iniciar. Selecione um módulo de simulação para prosseguir.")

    def handle_input(self, events: list[pygame.event.Event]) -> None:
        for event in events:
            # Update on Hover
            if event.type == pygame.USEREVENT and event.user_type == pygame_gui.UI_BUTTON_ON_HOVERED:
                for btn, _, tag in self._mode_btns:
                    if event.ui_element is btn:
                        self._update_info_card(tag)
                        break
            
            # Update on Keyboard Focus
            if self.navigator and self.navigator.selected_control:
                for btn, _, tag in self._mode_btns:
                    if self.navigator.selected_control is btn:
                        self._update_info_card(tag)
                        break

        super().handle_input(events)

    def on_enter(self) -> None:
        self.stack.event_bus.publish(AudioContextChanged(context="menu", reason="main_menu_entered"))

    def on_menu_update(self, dt: float) -> None:
        self._elapsed_time += dt

    def render_menu_background(self, screen: pygame.Surface) -> None:
        self._background_renderer.render(
            screen=screen,
            elapsed_time=self._elapsed_time,
            width=SCREEN_WIDTH,
            height=SCREEN_HEIGHT,
            sun_rise_progress=min(1.0, self._elapsed_time / 3.8),
        )

    def _quit(self) -> None:
        self.stack.pop()
