from __future__ import annotations

from dataclasses import dataclass

import pygame
import pygame_gui

from game.ui.components.label import LabelConfig, create_label


@dataclass(frozen=True)
class TableColumn:
    title: str
    width: int


@dataclass(frozen=True)
class TableCell:
    text: str
    variant: str = "value"


@dataclass(frozen=True)
class TableRow:
    cells: tuple[TableCell, ...]


@dataclass
class TableViewConfig:
    rect: pygame.Rect
    padding_x: int = 8
    column_gap: int = 8
    header_height: int = 22
    row_height: int = 24


class TableView:
    def __init__(
        self,
        manager: pygame_gui.UIManager,
        container: pygame_gui.core.UIContainer,
        config: TableViewConfig,
    ) -> None:
        self._manager = manager
        self._container = container
        self._config = config
        self._labels: list[pygame_gui.elements.UILabel] = []

    def clear(self) -> None:
        for label in self._labels:
            label.kill()
        self._labels.clear()

    def show_message(self, text: str, variant: str = "muted") -> None:
        self.clear()
        rect = self._config.rect
        self._labels.append(
            create_label(
                LabelConfig(
                    text=text,
                    rect=pygame.Rect((rect.x + self._config.padding_x, rect.y + 6), (rect.width - self._config.padding_x * 2, 24)),
                    variant=variant,
                ),
                manager=self._manager,
                container=self._container,
            )
        )

    def set_table(self, columns: tuple[TableColumn, ...], rows: tuple[TableRow, ...]) -> None:
        self.clear()

        rect = self._config.rect
        x = rect.x + self._config.padding_x
        y_header = rect.y + 2

        col_x_positions: list[int] = []
        for column in columns:
            col_x_positions.append(x)
            self._labels.append(
                create_label(
                    LabelConfig(
                        text=column.title,
                        rect=pygame.Rect((x, y_header), (column.width, self._config.header_height)),
                        variant="muted",
                    ),
                    manager=self._manager,
                    container=self._container,
                )
            )
            x += column.width + self._config.column_gap

        row_start_y = y_header + self._config.header_height + 6
        for row_index, row in enumerate(rows):
            y = row_start_y + row_index * (self._config.row_height + 4)
            for col_index, cell in enumerate(row.cells):
                if col_index >= len(columns):
                    break
                col_x = col_x_positions[col_index]
                col_w = columns[col_index].width
                self._labels.append(
                    create_label(
                        LabelConfig(
                            text=cell.text,
                            rect=pygame.Rect((col_x, y), (col_w, self._config.row_height)),
                            variant=cell.variant,
                        ),
                        manager=self._manager,
                        container=self._container,
                    )
                )
