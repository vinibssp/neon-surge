from __future__ import annotations

import pygame
from pygame_gui.elements import UITextEntryLine

from game.config import SCREEN_HEIGHT, SCREEN_WIDTH
from game.scenes.menus._base_menu_scene import BaseMenuScene
from game.services.ranking_service import RankingService
from game.ui.components import ButtonConfig, LabelConfig, TextInputConfig, create_button, create_label, create_text_input


class PlayerNameScene(BaseMenuScene):
    def __init__(self, stack, is_first_time: bool = False) -> None:
        super().__init__(stack)
        self.is_first_time = is_first_time
        
        create_label(
            LabelConfig(
                text=self.t("player_name.welcome") if is_first_time else self.t("player_name.change"), 
                rect=pygame.Rect((SCREEN_WIDTH // 2 - 350, 100), (700, 75)), 
                variant="title"
            ),
            manager=self.ui_manager,
        )
        
        create_label(
            LabelConfig(
                text=self.t("player_name.prompt"), 
                rect=pygame.Rect((SCREEN_WIDTH // 2 - 200, 220), (400, 40)), 
                variant="subtitle"
            ),
            manager=self.ui_manager,
        )
        
        current_name = RankingService().get_player_name() or ""
        
        self.text_entry = create_text_input(
            TextInputConfig(
                initial_text=current_name, 
                rect=pygame.Rect((SCREEN_WIDTH // 2 - 150, 280), (300, 50))
            ),
            manager=self.ui_manager
        )
        self.text_entry.set_text_length_limit(12)
        
        confirm_btn = create_button(
            ButtonConfig(
                text=self.t("player_name.confirm"), 
                rect=pygame.Rect((SCREEN_WIDTH // 2 - 100, 370), (200, 50)), 
                variant="primary"
            ),
            manager=self.ui_manager
        )
        
        buttons = [self.text_entry, confirm_btn]
        actions = {
            self.text_entry: self._confirm,
            confirm_btn: self._confirm,
        }
        
        cancel_action = None
        if not is_first_time:
            cancel_btn = create_button(
                ButtonConfig(
                    text=self.t("player_name.cancel"), 
                    rect=pygame.Rect((SCREEN_WIDTH // 2 - 100, 440), (200, 50)), 
                    variant="danger"
                ),
                manager=self.ui_manager
            )
            buttons.append(cancel_btn)
            actions[cancel_btn] = self.stack.pop
            cancel_action = self.stack.pop
            
        self.set_navigator(buttons=buttons, actions=actions, on_cancel=cancel_action)
        
    def _confirm(self) -> None:
        name = self.text_entry.get_text().strip()
        if not name:
            return
            
        RankingService().set_player_name(name)
        
        if self.is_first_time:
            from game.scenes.main_menu_scene import MainMenuScene
            self.stack.replace(MainMenuScene(self.stack))
        else:
            self.stack.pop()
