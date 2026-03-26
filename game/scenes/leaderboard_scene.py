from __future__ import annotations

from typing import Any

import pygame

from game.config import SCREEN_HEIGHT, SCREEN_WIDTH
from game.scenes.menus._base_menu_scene import BaseMenuScene
from game.services.ranking_service import RankingService
from game.ui.components import (
    ButtonConfig,
    LabelConfig,
    PanelConfig,
    RankingTable,
    RankingTableConfig,
    create_button,
    create_label,
    create_panel,
)


class LeaderboardScene(BaseMenuScene):
    def __init__(self, stack, highlight_data: dict | None = None) -> None:
        super().__init__(stack)
        self._local_data: list[dict[str, Any]] = []
        self._global_data: list[dict[str, Any]] | None = None
        self._local_applied = False
        self._global_applied = False
        self._fetch_ticket = 0
        self._mode_key = "Race"
        self._highlight_data = highlight_data
        self._local_table: RankingTable | None = None
        self._global_table: RankingTable | None = None
        
        # Internal key -> Display name
        self._modes = {
            "Race": "CORRIDA",
            "RaceInfinite": "INFINITA",
            "Survival": "SOBREVIVÊNCIA",
            "SurvivalHardcore": "HARDCORE",
            "Labyrinth": "LABIRINTO"
        }
        self._time_based_modes = {"OneVsOne", "Training"}
        
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

        mode_y = 110
        mode_btn_w = 124
        keys = list(self._modes.keys())
        total_width = len(keys) * mode_btn_w + (len(keys) - 1) * 10
        start_x = (SCREEN_WIDTH - total_width) // 2
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

        container_width = 980
        panel_gap = 20
        panel_width = (container_width - panel_gap) // 2
        panel_height = 380
        container_x = (SCREEN_WIDTH - container_width) // 2
        panel_y = 180

        self.local_panel = create_panel(
            PanelConfig(
                rect=pygame.Rect((container_x, panel_y), (panel_width, panel_height)),
                variant="card"
            ),
            manager=self.ui_manager
        )
        self.global_panel = create_panel(
            PanelConfig(
                rect=pygame.Rect((container_x + panel_width + panel_gap, panel_y), (panel_width, panel_height)),
                variant="card"
            ),
            manager=self.ui_manager
        )

        self._local_table = RankingTable(
            manager=self.ui_manager,
            container=self.local_panel,
            config=RankingTableConfig(
                rect=pygame.Rect((12, 12), (panel_width - 24, panel_height - 24)),
                metric_label=self._metric_label(),
                max_rows=10,
            ),
        )
        self._global_table = RankingTable(
            manager=self.ui_manager,
            container=self.global_panel,
            config=RankingTableConfig(
                rect=pygame.Rect((12, 12), (panel_width - 24, panel_height - 24)),
                metric_label=self._metric_label(),
                max_rows=10,
            ),
        )
        self._local_table.show_loading("Carregando ranking local...")
        self._global_table.show_loading("Carregando ranking global...")

        self.voltar_btn = create_button(
            ButtonConfig(
                text="Voltar",
                rect=pygame.Rect((SCREEN_WIDTH // 2 - 140, SCREEN_HEIGHT - 90), (280, 56)),
                variant="danger",
            ),
            manager=self.ui_manager,
        )

        buttons = list(self.mode_buttons.values()) + [self.voltar_btn]
        actions = {
            self.voltar_btn: self.stack.pop
        }
        for m_key, btn in self.mode_buttons.items():
            actions[btn] = lambda k=m_key: self._change_mode(k)
            
        self.set_navigator(
            buttons=buttons,
            actions=actions,
            on_cancel=self.stack.pop,
        )

    def _change_mode(self, mode_key: str) -> None:
        if self._mode_key != mode_key:
            self._mode_key = mode_key
            self._setup_ui()
            self._fetch_data()

    def _fetch_data(self) -> None:
        self._fetch_ticket += 1
        current_ticket = self._fetch_ticket
        self._local_applied = False
        self._global_applied = False
        self._local_data = RankingService().get_local_ranking(mode=self._mode_key, limit=10)
        self._global_data = None

        RankingService().fetch_global_ranking(
            limit=10,
            mode=self._mode_key,
            callback=lambda data: self._on_global_ranking_fetched(current_ticket, data),
        )

    def _on_global_ranking_fetched(self, ticket: int, data: list[dict[str, Any]]) -> None:
        if ticket != self._fetch_ticket:
            return
        self._global_data = data

    def update(self, dt: float) -> None:
        super().update(dt)

        if not self._local_applied:
            self._apply_local_panel()

        if self._global_data is not None and not self._global_applied:
            self._apply_global_panel()

    def _apply_local_panel(self) -> None:
        self._local_applied = True
        if self._local_table is None:
            return

        if not self._local_data:
            self._local_table.show_empty("Nenhum registro local.")
            return

        self._local_table.set_entries(
            entries=self._local_data,
            format_metric=self._format_metric_value,
            is_highlight=self._is_highlight,
        )

    def _apply_global_panel(self) -> None:
        self._global_applied = True
        if self._global_table is None:
            return

        if not self._global_data:
            self._global_table.show_empty("Nenhum registro global.")
            return

        self._global_table.set_entries(
            entries=self._global_data,
            format_metric=self._format_metric_value,
            is_highlight=self._is_highlight,
        )

    def _is_highlight(self, entry: dict[str, Any], score: float) -> bool:
        if self._highlight_data is None:
            return False
        highlight_name = str(self._highlight_data.get("player_name", ""))
        highlight_score = float(self._highlight_data.get("score", 0.0))
        return entry.get("player_name") == highlight_name and abs(score - highlight_score) < 0.01

    def _metric_label(self) -> str:
        if self._mode_key in self._time_based_modes:
            return "Tempo"
        return "Score"

    def _format_metric_value(self, value: float) -> str:
        if self._mode_key in self._time_based_modes:
            return f"{value:.2f}s"
        return f"{value:.2f}"
