from __future__ import annotations

import pygame
import pygame_gui

from game.config import SCREEN_HEIGHT, SCREEN_WIDTH
from game.scenes.menus._base_menu_scene import BaseMenuScene
from game.scenes.services import CyberpunkMenuBackgroundRenderer
from game.ui.components import (
    ButtonConfig,
    LabelConfig,
    PanelConfig,
    create_button,
    create_label,
    create_panel,
)


class ControlsScene(BaseMenuScene):
    def __init__(self, stack) -> None:
        super().__init__(stack)
        self._elapsed_time = 0.0
        self._background_renderer = CyberpunkMenuBackgroundRenderer()
        self._input_settings_manager = self.stack.input_settings_manager
        
        self._waiting_for_key: str | None = None
        self._binding_buttons: dict[str, pygame_gui.elements.UIButton] = {}
        self._binding_labels: dict[str, pygame_gui.elements.UILabel] = {}

        self._init_ui()

    def _init_ui(self) -> None:
        # Header
        create_label(
            LabelConfig(
                text="CONFIGURAÇÕES DE CONTROLES",
                rect=pygame.Rect((SCREEN_WIDTH // 2 - 400, 40), (800, 80)),
                variant="title",
            ),
            manager=self.ui_manager,
        )

        # Controls Panel
        self._controls_panel = create_panel(
            PanelConfig(
                rect=pygame.Rect((SCREEN_WIDTH // 2 - 450, 140), (900, 440)),
                variant="card",
            ),
            manager=self.ui_manager,
        )

        actions = [
            ("up", "MOVER PARA CIMA"),
            ("down", "MOVER PARA BAIXO"),
            ("left", "MOVER PARA ESQUERDA"),
            ("right", "MOVER PARA DIREITA"),
            ("dash", "DASH / IMPULSO"),
            ("parry", "PARRY / DEFESA"),
            ("bomb", "BOMBA NUCLEAR"),
        ]

        y_offset = 20
        for action_id, action_name in actions:
            create_label(
                LabelConfig(
                    text=action_name,
                    rect=pygame.Rect((40, y_offset), (300, 40)),
                    variant="settings_label",
                ),
                manager=self.ui_manager,
                container=self._controls_panel,
            )

            current_keys = getattr(self._input_settings_manager.settings, action_id)
            keys_text = ", ".join([pygame.key.name(k).upper() for k in current_keys])
            
            label = create_label(
                LabelConfig(
                    text=keys_text,
                    rect=pygame.Rect((350, y_offset), (300, 40)),
                    variant="value",
                ),
                manager=self.ui_manager,
                container=self._controls_panel,
            )
            self._binding_labels[action_id] = label

            btn = create_button(
                ButtonConfig(
                    text="REMAREAR",
                    rect=pygame.Rect((670, y_offset), (180, 40)),
                    variant="primary",
                ),
                manager=self.ui_manager,
                container=self._controls_panel,
            )
            self._binding_buttons[action_id] = btn
            
            y_offset += 55

        # Reset Button
        self._reset_button = create_button(
            ButtonConfig(
                text="RESTAURAR PADRÕES",
                rect=pygame.Rect((SCREEN_WIDTH // 2 - 320, 600), (300, 60)),
                variant="ghost",
            ),
            manager=self.ui_manager,
        )

        # Back Button
        self._back_button = create_button(
            ButtonConfig(
                text="VOLTAR",
                rect=pygame.Rect((SCREEN_WIDTH // 2 + 20, 600), (300, 60)),
                variant="danger",
            ),
            manager=self.ui_manager,
        )

        self._setup_navigation()

    def _setup_navigation(self) -> None:
        controls = []
        actions_map = {}

        for action_id, btn in self._binding_buttons.items():
            controls.append(btn)
            # Use a default argument in lambda to capture the current action_id
            actions_map[btn] = lambda aid=action_id: self._start_binding(aid)

        controls.append(self._reset_button)
        actions_map[self._reset_button] = self._reset_defaults
        
        controls.append(self._back_button)
        actions_map[self._back_button] = self._close

        self.set_navigator(
            controls=controls,
            actions=actions_map,
            on_cancel=self._close,
        )

    def _start_binding(self, action_id: str) -> None:
        self._waiting_for_key = action_id
        self._binding_labels[action_id].set_text("PRESSIONE UMA TECLA...")
        # Disable navigation while waiting for key
        self.navigator.enabled = False

    def _reset_defaults(self) -> None:
        from game.core.input_settings import InputSettings
        self._input_settings_manager.settings = InputSettings()
        self._input_settings_manager.save()
        self._update_all_labels()

    def _update_all_labels(self) -> None:
        for action_id, label in self._binding_labels.items():
            current_keys = getattr(self._input_settings_manager.settings, action_id)
            keys_text = ", ".join([pygame.key.name(k).upper() for k in current_keys])
            label.set_text(keys_text)

    def handle_input(self, events: list[pygame.event.Event]) -> None:
        if self._waiting_for_key:
            for event in events:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        # If already binding, ESC cancels it
                        self._waiting_for_key = None
                        self._update_all_labels()
                        self.navigator.enabled = True
                        return

                    # Rebind: for now, we replace the first key or just set it as the only key
                    # To keep it simple, let's just set this as the ONLY key for that action
                    # We could also append it to a list if we wanted multiple keys
                    setattr(self._input_settings_manager.settings, self._waiting_for_key, [event.key])
                    self._input_settings_manager.save()
                    
                    self._waiting_for_key = None
                    self._update_all_labels()
                    self.navigator.enabled = True
                    return
            return

        super().handle_input(events)

    def on_menu_update(self, dt: float) -> None:
        self._elapsed_time += dt

    def render_menu_background(self, screen: pygame.Surface) -> None:
        self._background_renderer.render(screen, self._elapsed_time, SCREEN_WIDTH, SCREEN_HEIGHT)

    def _close(self) -> None:
        self.stack.pop()
