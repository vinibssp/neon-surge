from __future__ import annotations

from typing import Callable

import pygame
from pygame_gui.elements import UITextBox

from game.config import SCREEN_HEIGHT, SCREEN_WIDTH
from game.core.events import AudioContextChanged
from game.core.session_stats import GameSessionStats
from game.modes.game_mode_strategy import GameModeStrategy
from game.scenes.menus._base_menu_scene import BaseMenuScene
from game.services.ranking_orchestrator import RankingSyncHandle
from game.ui.components import (
    ButtonConfig,
    LabelConfig,
    PanelConfig,
    RankingTable,
    RankingTableConfig,
    TableCell,
    TableColumn,
    TableRow,
    TableView,
    TableViewConfig,
    create_button,
    create_label,
    create_panel,
)


class GameOverScene(BaseMenuScene):
    def __init__(
        self,
        stack,
        reached_level: int,
        title: str,
        subtitle: str,
        retry_strategy_factory: Callable[[], GameModeStrategy],
        mode_key: str,
        death_cause: str | None = None,
        session_stats: GameSessionStats | None = None,
        elapsed_time: float | None = None,
        final_score: float = 0.0,
        ranking_sync_handle: RankingSyncHandle | None = None,
    ) -> None:
        super().__init__(stack)
        self.retry_strategy_factory = retry_strategy_factory
        self.reached_level = reached_level
        self.session_stats = session_stats
        self.elapsed_time = elapsed_time
        self._last_score = float(final_score)
        self._mode_key = mode_key
        self._ranking_sync_handle = ranking_sync_handle
        self._last_snapshot_status = ""
        self._local_table: RankingTable | None = None
        self._global_table: RankingTable | None = None
        self._status_table: TableView | None = None
        
        self._retry_mode_instance = self.retry_strategy_factory()
        stats_for_breakdown = session_stats if session_stats is not None else GameSessionStats()
        elapsed_for_breakdown = float(elapsed_time) if elapsed_time is not None else 0.0
        score_breakdown = self._retry_mode_instance.score_breakdown(
            elapsed_time=elapsed_for_breakdown,
            reached_level=reached_level,
            session_stats=stats_for_breakdown,
        )
        self._score_breakdown_lines = self._format_score_breakdown_lines(score_breakdown)
        
        # Display name mapping
        self._modes_display = {
            "Race": "CORRIDA",
            "RaceInfinite": "INFINITA",
            "Survival": "SOBREVIVÊNCIA",
            "SurvivalHardcore": "HARDCORE",
            "Labyrinth": "LABIRINTO"
        }
        title_variant = "title" if len(title) <= 18 else "subtitle"
        mode_display = self._modes_display.get(self._mode_key, self._mode_key)
        subtitle_text = subtitle.strip()
        subtitle_is_redundant = subtitle_text.lower().startswith("tempo:") or subtitle_text.lower().startswith("nivel alcancado:")

        summary_rect = pygame.Rect((30, 40), (440, SCREEN_HEIGHT - 80))
        combat_rect = pygame.Rect((490, 40), (SCREEN_WIDTH - 520, SCREEN_HEIGHT - 80))

        self.summary_panel = create_panel(
            PanelConfig(
                rect=summary_rect,
                variant="card",
            ),
            manager=self.ui_manager,
        )
        self.combat_panel = create_panel(
            PanelConfig(
                rect=combat_rect,
                variant="card"
            ),
            manager=self.ui_manager
        )
        
        _labels: list[object] = []

        _labels.append(
            create_label(
                LabelConfig(
                    text=title,
                    rect=pygame.Rect((20, 20), (400, 56)),
                    variant=title_variant,
                ),
                manager=self.ui_manager,
                container=self.summary_panel,
            )
        )
        next_row = 72
        if subtitle_text != "" and not subtitle_is_redundant:
            _labels.append(
                create_label(
                    LabelConfig(
                        text=subtitle,
                        rect=pygame.Rect((20, 72), (400, 36)),
                        variant="subtitle",
                    ),
                    manager=self.ui_manager,
                    container=self.summary_panel,
                )
            )
            next_row = 108

        if death_cause is not None and death_cause.strip() != "":
            _labels.append(
                create_label(
                    LabelConfig(
                        text=f"Causa da morte: {death_cause}",
                        rect=pygame.Rect((20, next_row), (400, 30)),
                        variant="value",
                    ),
                    manager=self.ui_manager,
                    container=self.summary_panel,
                )
            )
            next_row += 34


        status_rows: list[tuple[str, str]] = [("Nivel", str(reached_level))]
        if elapsed_time is not None:
            status_rows.append(("Tempo", f"{elapsed_time:.1f}s"))
        if session_stats is not None:
            status_rows.extend(
                [
                    ("Coletaveis", str(session_stats.collectible_collected_total)),
                    ("Dashes", str(session_stats.dash_started_total)),
                    ("Portais", str(session_stats.spawn_portal_destroyed_total)),
                    ("Inimigos", str(session_stats.enemy_spawned_total)),
                ]
            )

        status_table_height = 24 + (len(status_rows) * 28) + 10
        self._status_table = TableView(
            manager=self.ui_manager,
            container=self.summary_panel,
            config=TableViewConfig(rect=pygame.Rect((20, next_row), (400, status_table_height))),
        )
        status_columns = (
            TableColumn(title="ITEM", width=220),
            TableColumn(title="VALOR", width=160),
        )
        status_table_rows = tuple(
            TableRow(
                cells=(
                    TableCell(text=item_name, variant="subtitle"),
                    TableCell(text=item_value, variant="value"),
                )
            )
            for item_name, item_value in status_rows
        )
        self._status_table.set_table(columns=status_columns, rows=status_table_rows)
        next_row += status_table_height + 12

        create_label(
            LabelConfig(text="DETALHE DA PONTUACAO", rect=pygame.Rect((20, next_row), (400, 28)), variant="subtitle"),
            manager=self.ui_manager,
            container=self.summary_panel,
        )
        next_row += 28
        self.breakdown_box = UITextBox(
            html_text=self._format_score_breakdown_html(self._score_breakdown_lines),
            relative_rect=pygame.Rect((20, next_row), (400, 110)),
            manager=self.ui_manager,
            container=self.summary_panel,
        )

        del _labels

        buttons_y = summary_rect.height - 142
        btn_x = (summary_rect.width - 280) // 2

        retry_button = create_button(
            ButtonConfig(
                text="Tentar Novamente",
                rect=pygame.Rect((btn_x, buttons_y), (280, 56)),
                variant="primary",
            ),
            manager=self.ui_manager,
            container=self.summary_panel,
        )
        menu_button = create_button(
            ButtonConfig(
                text="Menu Principal",
                rect=pygame.Rect((btn_x, buttons_y + 72), (280, 56)),
                variant="danger",
            ),
            manager=self.ui_manager,
            container=self.summary_panel,
        )

        create_label(
            LabelConfig(text="LOCAL", rect=pygame.Rect((20, 20), (320, 40)), variant="subtitle"),
            manager=self.ui_manager,
            container=self.combat_panel
        )
        create_label(
            LabelConfig(text="GLOBAL", rect=pygame.Rect((combat_rect.width // 2 + 10, 20), (320, 40)), variant="subtitle"),
            manager=self.ui_manager,
            container=self.combat_panel
        )

        panel_padding = 20
        column_gap = 20
        column_width = (combat_rect.width - (panel_padding * 2) - column_gap) // 2
        table_top = 70
        table_height = combat_rect.height - 270
        local_x = panel_padding
        global_x = panel_padding + column_width + column_gap

        create_panel(
            PanelConfig(
                rect=pygame.Rect((global_x - (column_gap // 2), table_top - 8), (2, table_height + 16)),
                variant="hud",
            ),
            manager=self.ui_manager,
            container=self.combat_panel,
        )

        self._local_table = RankingTable(
            manager=self.ui_manager,
            container=self.combat_panel,
            config=RankingTableConfig(
                rect=pygame.Rect((local_x, table_top), (column_width, table_height)),
                metric_label=self._metric_label(),
                max_rows=10,
                show_sync_column=True,
            ),
        )
        self._global_table = RankingTable(
            manager=self.ui_manager,
            container=self.combat_panel,
            config=RankingTableConfig(
                rect=pygame.Rect((global_x, table_top), (column_width, table_height)),
                metric_label=self._metric_label(),
                max_rows=10,
                show_sync_column=False,
            ),
        )
        self._local_table.show_loading("Carregando ranking local...")
        self._global_table.show_loading("Sincronizando com a rede...")

        self.sync_status_label = create_label(
            LabelConfig(text="Status: sincronizando...", rect=pygame.Rect((20, combat_rect.height - 36), (combat_rect.width - 40, 24)), variant="muted"),
            manager=self.ui_manager,
            container=self.combat_panel,
        )

        self.set_navigator(
            buttons=[retry_button, menu_button],
            actions={
                retry_button: self._retry,
                menu_button: self._go_main_menu,
            },
            on_cancel=self._go_main_menu,
        )

    def on_enter(self) -> None:
        self.stack.event_bus.publish(AudioContextChanged(context="game_over", reason="game_over_entered"))
        self._apply_snapshot()

    def _apply_snapshot(self) -> None:
        if self._local_table is None or self._global_table is None:
            return
        if self._ranking_sync_handle is None:
            self._local_table.show_empty("Nenhum dado local.")
            self._global_table.show_empty("Sem sincronizacao global.")
            return

        snapshot = self._ranking_sync_handle.get_snapshot()
        if snapshot.status == self._last_snapshot_status:
            return
        self._last_snapshot_status = snapshot.status

        if snapshot.local_entries:
            self._local_table.set_entries(
                entries=snapshot.local_entries,
                format_metric=self._format_metric_value,
                is_highlight=self._is_current_entry,
            )
        else:
            self._local_table.show_empty("Nenhum registro local.")

        if snapshot.global_entries:
            self._global_table.set_entries(
                entries=snapshot.global_entries,
                format_metric=self._format_metric_value,
                is_highlight=self._is_current_entry,
            )
        elif snapshot.status == "degraded":
            self._global_table.show_empty("Falha na sincronizacao global.")
        else:
            self._global_table.show_loading("Sincronizando com a rede...")

        if snapshot.status == "done":
            self.sync_status_label.set_text(f"Status: sincronizado ({snapshot.synced_now} item(ns) enviados)")
        elif snapshot.status == "degraded":
            self.sync_status_label.set_text("Status: pendencias locais aguardando proxima sincronizacao")
        else:
            self.sync_status_label.set_text("Status: sincronizando ranking global...")

    def update(self, dt: float) -> None:
        super().update(dt)
        self._apply_snapshot()

    def _is_current_entry(self, entry: dict, score: float) -> bool:
        del score
        entry_score = float(entry.get("score", 0.0))
        return abs(entry_score - self._last_score) < 0.01

    def _metric_label(self) -> str:
        return "Score"

    def _format_metric_value(self, value: float) -> str:
        return str(int(value)) if float(value).is_integer() else f"{value:.2f}"

    def _format_score_breakdown_lines(self, breakdown: list[tuple[str, float]]) -> list[str]:
        if not breakdown:
            return [f"Total: {self._format_metric_value(self._last_score)}"]
        lines: list[str] = []
        for label, points in breakdown:
            points_prefix = "+" if points >= 0 else ""
            lines.append(f"- {label}: {points_prefix}{self._format_metric_value(points)}")
        lines.append(f"- Total: {self._format_metric_value(self._last_score)}")
        return lines

    @staticmethod
    def _format_score_breakdown_html(lines: list[str]) -> str:
        if not lines:
            return "<i>Sem detalhamento.</i>"
        return "<br>".join(lines)

    def _retry(self) -> None:
        from game.scenes.game_scene import GameScene
        self.stack.replace(GameScene(self.stack, self._retry_mode_instance))

    def _go_main_menu(self) -> None:
        from game.scenes.main_menu_scene import MainMenuScene
        self.stack.replace(MainMenuScene(self.stack))
