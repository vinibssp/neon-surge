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
        
        self._current_tab = "KEYBOARD"
        self._waiting_for_key: str | None = None
        
        self._binding_labels: dict[str, pygame_gui.elements.UILabel] = {}
        self._binding_buttons: dict[str, pygame_gui.elements.UIButton] = {}
        
        self._init_ui()

    def _init_ui(self) -> None:
        # Header
        create_label(
            LabelConfig(
                text="CONFIGURAÇÕES DE CONTROLES",
                rect=pygame.Rect((SCREEN_WIDTH // 2 - 400, 20), (800, 60)),
                variant="title",
            ),
            manager=self.ui_manager,
        )

        # Tab Bar
        tab_width = 300
        tab_height = 50
        self._tab_keyboard_btn = create_button(
            ButtonConfig(
                text="TECLADO",
                rect=pygame.Rect((SCREEN_WIDTH // 2 - tab_width - 5, 90), (tab_width, tab_height)),
                variant="primary" if self._current_tab == "KEYBOARD" else "ghost",
            ),
            manager=self.ui_manager,
        )
        self._tab_joystick_btn = create_button(
            ButtonConfig(
                text="JOYSTICK",
                rect=pygame.Rect((SCREEN_WIDTH // 2 + 5, 90), (tab_width, tab_height)),
                variant="primary" if self._current_tab == "JOYSTICK" else "ghost",
            ),
            manager=self.ui_manager,
        )

        # Content Area Panel
        self._content_panel = create_panel(
            PanelConfig(
                rect=pygame.Rect((SCREEN_WIDTH // 2 - 450, 150), (900, 480)),
                variant="card",
            ),
            manager=self.ui_manager,
        )

        if self._current_tab == "KEYBOARD":
            self._build_keyboard_tab()
        else:
            self._build_joystick_tab()

        # Back Button
        self._back_button = create_button(
            ButtonConfig(
                text="VOLTAR",
                rect=pygame.Rect((SCREEN_WIDTH // 2 - 150, 650), (300, 50)),
                variant="danger",
            ),
            manager=self.ui_manager,
        )

        self._setup_navigation()

    def _build_keyboard_tab(self) -> None:
        create_label(
            LabelConfig(text="CONTROLES DO TECLADO", rect=pygame.Rect((20, 10), (860, 40)), variant="settings_header"),
            manager=self.ui_manager, container=self._content_panel
        )

        self._binding_labels.clear()
        self._binding_buttons.clear()

        actions = [
            ("up", "MOVER PARA CIMA"),
            ("down", "MOVER PARA BAIXO"),
            ("left", "MOVER PARA ESQUERDA"),
            ("right", "MOVER PARA DIREITA"),
            ("dash", "DASH / IMPULSO"),
            ("parry", "PARRY / DEFESA"),
            ("bomb", "BOMBA NUCLEAR"),
        ]

        y_offset = 60
        for action_id, action_name in actions:
            create_label(
                LabelConfig(text=action_name, rect=pygame.Rect((40, y_offset), (300, 30)), variant="settings_label"),
                manager=self.ui_manager, container=self._content_panel
            )

            current_val = getattr(self._input_settings_manager.settings, action_id)
            keys_text = ", ".join([pygame.key.name(k).upper() for k in current_val])
            
            label = create_label(
                LabelConfig(text=keys_text, rect=pygame.Rect((350, y_offset), (300, 30)), variant="value"),
                manager=self.ui_manager, container=self._content_panel
            )
            self._binding_labels[action_id] = label

            btn = create_button(
                ButtonConfig(text="REMAPEAR", rect=pygame.Rect((670, y_offset), (180, 30)), variant="primary"),
                manager=self.ui_manager, container=self._content_panel
            )
            self._binding_buttons[action_id] = btn
            y_offset += 45

        self._reset_btn = create_button(
            ButtonConfig(text="RESTAURAR PADRÕES", rect=pygame.Rect((300, 420), (300, 40)), variant="ghost"),
            manager=self.ui_manager, container=self._content_panel
        )

    def _build_joystick_tab(self) -> None:
        create_label(
            LabelConfig(text="CONTROLES DO JOYSTICK", rect=pygame.Rect((20, 10), (860, 40)), variant="settings_header"),
            manager=self.ui_manager, container=self._content_panel
        )

        self._binding_labels.clear()
        self._binding_buttons.clear()

        actions = [
            ("joy_dash", "DASH / IMPULSO"),
            ("joy_parry", "PARRY / DEFESA"),
            ("joy_bomb", "BOMBA NUCLEAR"),
            ("joy_pause", "PAUSAR JOGO"),
        ]

        y_offset = 60
        for action_id, action_name in actions:
            create_label(
                LabelConfig(text=action_name, rect=pygame.Rect((40, y_offset), (300, 30)), variant="settings_label"),
                manager=self.ui_manager, container=self._content_panel
            )

            current_val = getattr(self._input_settings_manager.settings, action_id)
            keys_text = ", ".join([f"BOTÃO {b}" for b in current_val])
            
            label = create_label(
                LabelConfig(text=keys_text, rect=pygame.Rect((350, y_offset), (300, 30)), variant="value"),
                manager=self.ui_manager, container=self._content_panel
            )
            self._binding_labels[action_id] = label

            btn = create_button(
                ButtonConfig(text="REMAPEAR", rect=pygame.Rect((670, y_offset), (180, 30)), variant="primary"),
                manager=self.ui_manager, container=self._content_panel
            )
            self._binding_buttons[action_id] = btn
            y_offset += 50

        self._reset_btn = create_button(
            ButtonConfig(text="RESTAURAR PADRÕES", rect=pygame.Rect((300, 420), (300, 40)), variant="ghost"),
            manager=self.ui_manager, container=self._content_panel
        )

    def _setup_navigation(self) -> None:
        controls = [self._tab_keyboard_btn, self._tab_joystick_btn]
        actions_map = {
            self._tab_keyboard_btn: lambda: self._switch_tab("KEYBOARD"),
            self._tab_joystick_btn: lambda: self._switch_tab("JOYSTICK"),
        }

        # Order matters for spatial navigation
        action_order = []
        if self._current_tab == "KEYBOARD":
            action_order = ["up", "down", "left", "right", "dash", "parry", "bomb"]
        else:
            action_order = ["joy_dash", "joy_parry", "joy_bomb", "joy_pause"]

        for aid in action_order:
            if aid in self._binding_buttons:
                btn = self._binding_buttons[aid]
                controls.append(btn)
                actions_map[btn] = (lambda a=aid: self._start_binding(a))

        controls.append(self._reset_btn)
        actions_map[self._reset_btn] = self._reset_controls

        controls.append(self._back_button)
        actions_map[self._back_button] = self._close

        self.set_navigator(controls=controls, actions=actions_map, on_cancel=self._close)

    def _switch_tab(self, tab: str) -> None:
        if self._current_tab == tab:
            return
        self._current_tab = tab
        self._waiting_for_key = None
        self.ui_manager.clear_and_reset()
        self._init_ui()

    def _start_binding(self, action_id: str) -> None:
        self._waiting_for_key = action_id
        if action_id in self._binding_labels:
            self._binding_labels[action_id].set_text("PRESSIONE INPUT...")
        self.navigator.enabled = False

    def _reset_controls(self) -> None:
        from game.core.input_settings import InputSettings
        self._input_settings_manager.settings = InputSettings()
        self._input_settings_manager.save()
        self._update_binding_labels()

    def _update_binding_labels(self) -> None:
        for aid, label in self._binding_labels.items():
            current_val = getattr(self._input_settings_manager.settings, aid)
            is_joy = aid.startswith("joy_")
            keys_text = ", ".join([f"BOTÃO {b}" if is_joy else pygame.key.name(k).upper() for k in current_val])
            label.set_text(keys_text)

    def handle_input(self, events: list[pygame.event.Event]) -> None:
        if self._waiting_for_key:
            for event in events:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self._waiting_for_key = None
                        self._update_binding_labels()
                        self.navigator.enabled = True
                        return
                    if not self._waiting_for_key.startswith("joy_"):
                        setattr(self._input_settings_manager.settings, self._waiting_for_key, [event.key])
                        self._input_settings_manager.save()
                        self._waiting_for_key = None
                        self._update_binding_labels()
                        self.navigator.enabled = True
                        return
                elif event.type == pygame.JOYBUTTONDOWN:
                    if self._waiting_for_key.startswith("joy_"):
                        setattr(self._input_settings_manager.settings, self._waiting_for_key, [event.button])
                        self._input_settings_manager.save()
                        self._waiting_for_key = None
                        self._update_binding_labels()
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
