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
from game.ui.components import ButtonConfig, LabelConfig, PanelConfig, create_button, create_label, create_panel


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

        # Botões reposicionados (centro da coluna esquerda)
        buttons_y = min(SCREEN_HEIGHT - 170, next_row + 24)
        btn_x = 40 + (400 - 280) // 2

        retry_button = create_button(
            ButtonConfig(
                text="Tentar Novamente",
                rect=pygame.Rect((btn_x, buttons_y), (280, 56)),
                variant="primary",
            ),
            manager=self.ui_manager,
        )
        menu_button = create_button(
            ButtonConfig(
                text="Menu Principal",
                rect=pygame.Rect((btn_x, buttons_y + 72), (280, 56)),
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
        
        mode_display = self._modes_display.get(self._mode_key, self._mode_key)
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
            relative_rect=pygame.Rect((20, 70), (320, SCREEN_HEIGHT - 195)),
            manager=self.ui_manager,
            container=self.combat_panel,
        )
        self.global_ranking_box = UITextBox(
            html_text="<i>Sincronizando com a rede...</i>",
            relative_rect=pygame.Rect((360, 70), (320, SCREEN_HEIGHT - 360)),
            manager=self.ui_manager,
            container=self.combat_panel
        )
        create_label(
            LabelConfig(text="DETALHE DA PONTUACAO", rect=pygame.Rect((360, SCREEN_HEIGHT - 280), (320, 30)), variant="subtitle"),
            manager=self.ui_manager,
            container=self.combat_panel,
        )
        self.breakdown_box = UITextBox(
            html_text=self._format_score_breakdown_html(self._score_breakdown_lines),
            relative_rect=pygame.Rect((360, SCREEN_HEIGHT - 245), (320, 120)),
            manager=self.ui_manager,
            container=self.combat_panel,
        )
        self.sync_status_label = create_label(
            LabelConfig(text="Status: sincronizando...", rect=pygame.Rect((20, SCREEN_HEIGHT - 120), (660, 30)), variant="muted"),
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
        if self._ranking_sync_handle is None:
            self.local_ranking_box.set_text("<i>Nenhum dado local.</i>")
            self.global_ranking_box.set_text("<i>Sem sincronizacao global.</i>")
            return

        snapshot = self._ranking_sync_handle.get_snapshot()
        if snapshot.status == self._last_snapshot_status:
            return
        self._last_snapshot_status = snapshot.status

        self.local_ranking_box.set_text(
            self._format_ranking_html(snapshot.local_entries, self._last_score, show_sync_status=True)
        )
        if snapshot.global_entries:
            self.global_ranking_box.set_text(
                self._format_ranking_html(snapshot.global_entries, self._last_score, show_sync_status=False)
            )
        elif snapshot.status == "degraded":
            self.global_ranking_box.set_text("<i>Falha na sincronizacao global.</i>")
        else:
            self.global_ranking_box.set_text("<i>Sincronizando com a rede...</i>")

        if snapshot.status == "done":
            self.sync_status_label.set_text(f"Status: sincronizado ({snapshot.synced_now} item(ns) enviados)")
        elif snapshot.status == "degraded":
            self.sync_status_label.set_text("Status: pendencias locais aguardando proxima sincronizacao")
        else:
            self.sync_status_label.set_text("Status: sincronizando ranking global...")

    def update(self, dt: float) -> None:
        super().update(dt)
        self._apply_snapshot()

    def _format_ranking_html(self, ranking_list: list[dict], current_score: float, show_sync_status: bool) -> str:
        if not ranking_list:
            return "<i>Nenhum registro.</i>"

        lines: list[str] = []
        top_10 = ranking_list[:10]
        for index in range(10):
            if index < len(top_10):
                item = top_10[index]
                item_name = str(item.get("player_name", "ANONIMO"))
                item_score = float(item.get("score", 0.0))
                sync_suffix = ""
                if show_sync_status:
                    sync_suffix = " ✓" if bool(item.get("synced", False)) else " ⏳"
                line = f"{index + 1}. {item_name} - {self._format_metric_value(item_score)}{sync_suffix}"
                if abs(item_score - current_score) < 0.01:
                    line = f"<font color='#44ff44'>{line}</font>"
            else:
                line = f"{index + 1}. ---"
            lines.append(line)

        return "<br>".join(lines)

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
