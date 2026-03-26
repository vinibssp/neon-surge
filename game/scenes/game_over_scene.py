from __future__ import annotations

from typing import Callable

import pygame

from game.config import SCREEN_HEIGHT, SCREEN_WIDTH
from game.core.events import AudioContextChanged
from game.core.session_stats import GameSessionStats
from game.modes.game_mode_strategy import GameModeStrategy
from game.scenes.menus._base_menu_scene import BaseMenuScene
from game.ui.components import ButtonConfig, LabelConfig, create_button, create_label


class GameOverScene(BaseMenuScene):
    def __init__(
        self,
        stack,
        reached_level: int,
        title: str,
        subtitle: str,
        retry_strategy_factory: Callable[[], GameModeStrategy],
        death_cause: str | None = None,
        session_stats: GameSessionStats | None = None,
        elapsed_time: float | None = None,
    ) -> None:
        super().__init__(stack)
        self.retry_strategy_factory = retry_strategy_factory

        _labels: list[object] = []

        _labels.append(
            create_label(
                LabelConfig(
                    text=title,
                    rect=pygame.Rect((SCREEN_WIDTH // 2 - 350, 110), (700, 70)),
                    variant="title",
                ),
                manager=self.ui_manager,
            )
        )
        _labels.append(
            create_label(
                LabelConfig(
                    text=subtitle,
                    rect=pygame.Rect((SCREEN_WIDTH // 2 - 350, 180), (700, 42)),
                    variant="subtitle",
                ),
                manager=self.ui_manager,
            )
        )
        _labels.append(
            create_label(
                LabelConfig(
                    text=f"Nivel alcancado: {reached_level}",
                    rect=pygame.Rect((SCREEN_WIDTH // 2 - 260, 230), (520, 40)),
                    variant="muted",
                ),
                manager=self.ui_manager,
            )
        )

        next_row = 270
        if death_cause is not None and death_cause.strip() != "":
            _labels.append(
                create_label(
                    LabelConfig(
                        text=f"Causa da morte: {death_cause}",
                        rect=pygame.Rect((SCREEN_WIDTH // 2 - 390, next_row), (780, 36)),
                        variant="muted",
                    ),
                    manager=self.ui_manager,
                )
            )
            next_row += 34

        if session_stats is not None:
            stats_lines = [
                f"Tempo: {elapsed_time:.1f}s" if elapsed_time is not None else None,
                f"Coletaveis: {session_stats.collectible_collected_total}",
                f"Dashes: {session_stats.dash_started_total}",
                f"Portais destruidos: {session_stats.spawn_portal_destroyed_total}",
                f"Inimigos gerados: {session_stats.enemy_spawned_total}",
            ]
            for line in stats_lines:
                if line is None:
                    continue
                _labels.append(
                    create_label(
                        LabelConfig(
                            text=line,
                            rect=pygame.Rect((SCREEN_WIDTH // 2 - 240, next_row), (480, 32)),
                            variant="muted",
                        ),
                        manager=self.ui_manager,
                    )
                )
                next_row += 30

        del _labels

        buttons_y = min(SCREEN_HEIGHT - 170, next_row + 24)

        retry_button = create_button(
            ButtonConfig(
                text="Tentar Novamente",
                rect=pygame.Rect((SCREEN_WIDTH // 2 - 140, buttons_y), (280, 56)),
                variant="primary",
            ),
            manager=self.ui_manager,
        )
        menu_button = create_button(
            ButtonConfig(
                text="Menu Principal",
                rect=pygame.Rect((SCREEN_WIDTH // 2 - 140, buttons_y + 72), (280, 56)),
                variant="danger",
            ),
            manager=self.ui_manager,
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

    def _retry(self) -> None:
        from game.scenes.game_scene import GameScene

        self.stack.replace(GameScene(self.stack, self.retry_strategy_factory()))

    def _go_main_menu(self) -> None:
        from game.scenes.main_menu_scene import MainMenuScene

        self.stack.replace(MainMenuScene(self.stack))
