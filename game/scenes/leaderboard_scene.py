from __future__ import annotations

from typing import Any

import pygame

from game.config import SCREEN_HEIGHT, SCREEN_WIDTH
from game.scenes.menus._base_menu_scene import BaseMenuScene
from game.services.ranking_service import RankingService
from game.ui.components import ButtonConfig, LabelConfig, PanelConfig, create_button, create_label, create_panel


class LeaderboardScene(BaseMenuScene):
    def __init__(self, stack, highlight_data: dict | None = None) -> None:
        super().__init__(stack)
        self._ranking_data: list[dict[str, Any]] | None = None
        self._data_applied = False
        self._scope = "GLOBAL"
        self._mode_key = "Race"
        self._highlight_data = highlight_data
        
        # Internal key -> Display name
        self._modes = {
            "Race": "CORRIDA",
            "RaceInfinite": "INFINITA",
            "Survival": "SOBREVIVÊNCIA",
            "SurvivalHardcore": "HARDCORE",
            "Labyrinth": "LABIRINTO"
        }
        self._time_based_modes = {"Race", "Survival", "SurvivalHardcore", "OneVsOne", "Training"}
        
        self._setup_ui()
        self._fetch_data()

    def _setup_ui(self) -> None:
        self.ui_manager.clear_and_reset()
        
        self._title = create_label(
            LabelConfig(
                text="CLASSIFICAÇÃO",
                rect=pygame.Rect((SCREEN_WIDTH // 2 - 350, 20), (700, 70)),
                variant="title",
            ),
            manager=self.ui_manager,
        )

        scope_y = 100
        btn_width = 150
        self.btn_local = create_button(
            ButtonConfig(
                text="LOCAL",
                rect=pygame.Rect((SCREEN_WIDTH // 2 - btn_width - 10, scope_y), (btn_width, 40)),
                variant="primary" if self._scope == "LOCAL" else "ghost"
            ),
            manager=self.ui_manager
        )
        self.btn_global = create_button(
            ButtonConfig(
                text="GLOBAL",
                rect=pygame.Rect((SCREEN_WIDTH // 2 + 10, scope_y), (btn_width, 40)),
                variant="primary" if self._scope == "GLOBAL" else "ghost"
            ),
            manager=self.ui_manager
        )
        
        mode_y = 150
        mode_btn_w = 120
        keys = list(self._modes.keys())
        start_x = SCREEN_WIDTH // 2 - (len(keys) * (mode_btn_w + 10)) // 2
        self.mode_buttons = {}
        for i, m_key in enumerate(keys):
            rect = pygame.Rect((start_x + i * (mode_btn_w + 10), mode_y), (mode_btn_w, 40))
            btn = create_button(
                ButtonConfig(
                    text=self._modes[m_key],
                    rect=rect,
                    variant="primary" if self._mode_key == m_key else "ghost"
                ),
                manager=self.ui_manager
            )
            self.mode_buttons[m_key] = btn

        self.data_panel = create_panel(
            PanelConfig(
                rect=pygame.Rect((SCREEN_WIDTH // 2 - 350, 210), (700, 380)),
                variant="card"
            ),
            manager=self.ui_manager
        )

        self._loading_label = create_label(
            LabelConfig(
                text="Carregando dados...",
                rect=pygame.Rect((150, 150), (400, 40)),
                variant="subtitle",
            ),
            manager=self.ui_manager,
            container=self.data_panel
        )

        self.voltar_btn = create_button(
            ButtonConfig(
                text="Voltar",
                rect=pygame.Rect((SCREEN_WIDTH // 2 - 140, SCREEN_HEIGHT - 90), (280, 56)),
                variant="danger",
            ),
            manager=self.ui_manager,
        )

        buttons = [self.btn_local, self.btn_global] + list(self.mode_buttons.values()) + [self.voltar_btn]
        actions = {
            self.btn_local: lambda: self._change_scope("LOCAL"),
            self.btn_global: lambda: self._change_scope("GLOBAL"),
            self.voltar_btn: self.stack.pop
        }
        for m_key, btn in self.mode_buttons.items():
            actions[btn] = lambda k=m_key: self._change_mode(k)
            
        self.set_navigator(
            buttons=buttons,
            actions=actions,
            on_cancel=self.stack.pop,
        )

        self._labels: list[object] = []

    def _change_scope(self, scope: str) -> None:
        if self._scope != scope:
            self._scope = scope
            self._setup_ui()
            self._fetch_data()

    def _change_mode(self, mode_key: str) -> None:
        if self._mode_key != mode_key:
            self._mode_key = mode_key
            self._setup_ui()
            self._fetch_data()

    def _fetch_data(self) -> None:
        self._data_applied = False
        self._ranking_data = None
        if self._scope == "LOCAL":
            data = RankingService().get_local_ranking(mode=self._mode_key, limit=10)
            self._on_ranking_fetched(data)
        else:
            RankingService().fetch_global_ranking(limit=10, mode=self._mode_key, callback=self._on_ranking_fetched)

    def _on_ranking_fetched(self, data: list[dict[str, Any]]) -> None:
        self._ranking_data = data

    def update(self, dt: float) -> None:
        super().update(dt)
        
        if self._ranking_data is not None and not self._data_applied:
            self._data_applied = True
            self._loading_label.kill()

            if not self._ranking_data:
                self._labels.append(
                    create_label(
                        LabelConfig(
                            text="Nenhum registro encontrado.",
                            rect=pygame.Rect((100, 150), (500, 40)),
                            variant="muted",
                        ),
                        manager=self.ui_manager,
                        container=self.data_panel
                    )
                )
                return

            start_y = 20
            for i, entry in enumerate(self._ranking_data):
                name = entry.get("player_name", "Desconhecido")
                score = float(entry.get("score", 0.0))
                
                is_highlight = False
                if self._highlight_data:
                    is_highlight = (
                        entry.get("player_name") == self._highlight_data.get("player_name") and 
                        abs(score - float(self._highlight_data.get("score", 0.0))) < 0.01
                    )
                
                self._labels.append(
                    create_label(
                        LabelConfig(
                            text=f"{i+1}. {name} | {self._metric_label()}: {self._format_metric_value(score)}",
                            rect=pygame.Rect((50, start_y + (i * 30)), (600, 30)),
                            variant="highlight" if is_highlight else "value",
                        ),
                        manager=self.ui_manager,
                        container=self.data_panel
                    )
                )

    def _metric_label(self) -> str:
        if self._mode_key in self._time_based_modes:
            return "Tempo"
        return "Score"

    def _format_metric_value(self, value: float) -> str:
        if self._mode_key in self._time_based_modes:
            return f"{value:.2f}s"
        return f"{value:.2f}"
