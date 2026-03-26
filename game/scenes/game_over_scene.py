from __future__ import annotations

from typing import Callable

import pygame
from pygame_gui.elements import UITextBox

from game.config import SCREEN_HEIGHT, SCREEN_WIDTH
from game.core.events import AudioContextChanged
from game.core.session_stats import GameSessionStats
from game.modes.game_mode_strategy import GameModeStrategy
from game.scenes.menus._base_menu_scene import BaseMenuScene
from game.services.ranking_service import RankingService
from game.ui.components import ButtonConfig, LabelConfig, PanelConfig, create_button, create_label, create_panel


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
        final_score: float = 0.0,
    ) -> None:
        super().__init__(stack)
        self.retry_strategy_factory = retry_strategy_factory
        self.reached_level = reached_level
        self.session_stats = session_stats
        self.elapsed_time = elapsed_time
        self._last_score = float(final_score)
        self._ranking_service = RankingService()
        self._current_player = self._ranking_service.get_player_name() or "ANONIMO"
        self._pending_global_data: list[dict] | None = None
        
        # Obter nome do modo
        self._retry_mode_instance = self.retry_strategy_factory()
        self._mode_name = self._retry_mode_instance.__class__.__name__.replace("Mode", "")
        
        # Display name mapping
        self._modes_display = {
            "Race": "CORRIDA",
            "RaceInfinite": "INFINITA",
            "Survival": "SOBREVIVÊNCIA",
            "SurvivalHardcore": "HARDCORE",
            "Labyrinth": "LABIRINTO"
        }
        self._time_based_modes = {"Race", "Survival", "SurvivalHardcore", "OneVsOne", "Training"}
        title_variant = "title" if len(title) <= 18 else "subtitle"
        
        _labels: list[object] = []

        _labels.append(
            create_label(
                LabelConfig(
                    text=title,
                    rect=pygame.Rect((40, 40), (400, 70)),
                    variant=title_variant,
                ),
                manager=self.ui_manager,
            )
        )
        _labels.append(
            create_label(
                LabelConfig(
                    text=subtitle,
                    rect=pygame.Rect((40, 110), (400, 42)),
                    variant="subtitle",
                ),
                manager=self.ui_manager,
            )
        )
        _labels.append(
            create_label(
                LabelConfig(
                    text=f"Nivel alcancado: {reached_level}",
                    rect=pygame.Rect((40, 160), (400, 40)),
                    variant="muted",
                ),
                manager=self.ui_manager,
            )
        )

        next_row = 200
        if death_cause is not None and death_cause.strip() != "":
            _labels.append(
                create_label(
                    LabelConfig(
                        text=f"Causa da morte: {death_cause}",
                        rect=pygame.Rect((40, next_row), (400, 36)),
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
                            rect=pygame.Rect((40, next_row), (400, 32)),
                            variant="muted",
                        ),
                        manager=self.ui_manager,
                    )
                )
                next_row += 30

        del _labels

        # Botões reposicionados (esquerda)
        buttons_y = min(SCREEN_HEIGHT - 170, next_row + 24)

        retry_button = create_button(
            ButtonConfig(
                text="Tentar Novamente",
                rect=pygame.Rect((40, buttons_y), (280, 56)),
                variant="primary",
            ),
            manager=self.ui_manager,
        )
        menu_button = create_button(
            ButtonConfig(
                text="Menu Principal",
                rect=pygame.Rect((40, buttons_y + 72), (280, 56)),
                variant="danger",
            ),
            manager=self.ui_manager,
        )
        
        self.combat_panel = create_panel(
            PanelConfig(
                rect=pygame.Rect((500, 40), (700, SCREEN_HEIGHT - 80)),
                variant="card"
            ),
            manager=self.ui_manager
        )
        
        mode_display = self._modes_display.get(self._mode_name, self._mode_name)
        create_label(
            LabelConfig(text=f"TOP 10 LOCAL - {mode_display}", rect=pygame.Rect((20, 20), (320, 40)), variant="subtitle"),
            manager=self.ui_manager,
            container=self.combat_panel
        )
        create_label(
            LabelConfig(text=f"TOP 10 GLOBAL - {mode_display}", rect=pygame.Rect((360, 20), (320, 40)), variant="subtitle"),
            manager=self.ui_manager,
            container=self.combat_panel
        )

        self.local_ranking_box = UITextBox(
            html_text="",
            relative_rect=pygame.Rect((20, 70), (320, SCREEN_HEIGHT - 170)),
            manager=self.ui_manager,
            container=self.combat_panel,
        )
        self.global_ranking_box = UITextBox(
            html_text="<i>Sincronizando com a rede...</i>",
            relative_rect=pygame.Rect((360, 70), (320, SCREEN_HEIGHT - 170)),
            manager=self.ui_manager,
            container=self.combat_panel
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

        self._ranking_service.save_local_score(
            player_name=self._current_player,
            mode=self._mode_name,
            score=self._last_score,
        )
        local_list = self._ranking_service.get_local_top_10(self._mode_name)
        self.local_ranking_box.set_text(
            self._format_ranking_html(local_list, self._current_player, self._last_score)
        )
        self._ranking_service.enviar_e_buscar_global(
            player_name=self._current_player,
            mode=self._mode_name,
            score=self._last_score,
            callback=self._on_global_ranking_received,
        )

    def _on_global_ranking_received(self, lista_global: list[dict]) -> None:
        self._pending_global_data = lista_global

    def update(self, dt: float) -> None:
        super().update(dt)
        if self._pending_global_data is not None:
            global_data = self._pending_global_data
            self._pending_global_data = None
            self.global_ranking_box.set_text(
                self._format_ranking_html(global_data, self._current_player, self._last_score)
            )

    def _format_ranking_html(self, ranking_list: list[dict], current_player: str, current_score: float) -> str:
        if not ranking_list:
            return "<i>Nenhum registro.</i>"

        lines: list[str] = []
        top_10 = ranking_list[:10]
        for index in range(10):
            if index < len(top_10):
                item = top_10[index]
                item_name = str(item.get("player_name", "ANONIMO"))
                item_score = float(item.get("score", 0.0))
                line = f"{index + 1}. {item_name} - {self._format_metric_value(item_score)}"
                if item_name == current_player and item_score == current_score:
                    line = f"<font color='#44ff44'>{line}</font>"
            else:
                line = f"{index + 1}. ---"
            lines.append(line)

        return "<br>".join(lines)

    def _metric_label(self) -> str:
        if self._mode_name in self._time_based_modes:
            return "Tempo"
        return "Score"

    def _format_metric_value(self, value: float) -> str:
        if self._mode_name in self._time_based_modes:
            return f"{value:.2f}s"
        return str(int(value)) if float(value).is_integer() else f"{value:.2f}"

    def _retry(self) -> None:
        from game.scenes.game_scene import GameScene
        self.stack.replace(GameScene(self.stack, self._retry_mode_instance))

    def _go_main_menu(self) -> None:
        from game.scenes.main_menu_scene import MainMenuScene
        self.stack.replace(MainMenuScene(self.stack))
