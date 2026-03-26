from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

import pygame
import pygame_gui

from game.ui.components.table_view import TableCell, TableColumn, TableRow, TableView, TableViewConfig


@dataclass
class RankingTableConfig:
    rect: pygame.Rect
    metric_label: str = "SCORE"
    max_rows: int = 10
    show_sync_column: bool = False


class RankingTable:
    def __init__(
        self,
        manager: pygame_gui.UIManager,
        container: pygame_gui.core.UIContainer,
        config: RankingTableConfig,
    ) -> None:
        self._manager = manager
        self._container = container
        self._config = config
        self._table_view = TableView(
            manager=manager,
            container=container,
            config=TableViewConfig(rect=config.rect),
        )

    def clear(self) -> None:
        self._table_view.clear()

    def show_loading(self, text: str) -> None:
        self._table_view.show_message(text, variant="subtitle")

    def show_empty(self, text: str) -> None:
        self._table_view.show_message(text, variant="muted")

    def set_entries(
        self,
        entries: list[dict[str, Any]],
        format_metric: Callable[[float], str],
        is_highlight: Callable[[dict[str, Any], float], bool] | None = None,
    ) -> None:
        rect = self._config.rect
        padding_x = 8
        col_gap = 8
        pos_w = 48
        metric_w = 100
        sync_w = 56 if self._config.show_sync_column else 0
        content_width = rect.width - (padding_x * 2)
        fixed_width = pos_w + metric_w + sync_w + (col_gap * (3 if self._config.show_sync_column else 2))
        name_w = max(100, content_width - fixed_width)

        columns: tuple[TableColumn, ...]
        if self._config.show_sync_column:
            columns = (
                TableColumn("POS", pos_w),
                TableColumn("NOME", name_w),
                TableColumn(self._config.metric_label.upper(), metric_w),
                TableColumn("SYNC", sync_w),
            )
        else:
            columns = (
                TableColumn("POS", pos_w),
                TableColumn("NOME", name_w),
                TableColumn(self._config.metric_label.upper(), metric_w),
            )

        rows: list[TableRow] = []
        for index, entry in enumerate(entries[: self._config.max_rows]):
            score = float(entry.get("score", 0.0))
            variant = "highlight" if is_highlight is not None and is_highlight(entry, score) else "value"
            row_cells = [
                TableCell(text=f"{index + 1:02d}", variant=variant),
                TableCell(text=str(entry.get("player_name", "Desconhecido"))[:18], variant=variant),
                TableCell(text=format_metric(score), variant=variant),
            ]
            if self._config.show_sync_column:
                synced_text = "OK" if bool(entry.get("synced", False)) else "X"
                row_cells.append(TableCell(text=synced_text, variant=variant))
            rows.append(TableRow(cells=tuple(row_cells)))

        self._table_view.set_table(columns=columns, rows=tuple(rows))
