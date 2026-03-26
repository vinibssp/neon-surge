from __future__ import annotations

from typing import Callable

import pygame

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
    ) -> None:
        super().__init__(stack)
        self.retry_strategy_factory = retry_strategy_factory
        self.reached_level = reached_level
        self.session_stats = session_stats
        self.elapsed_time = elapsed_time
        
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
        
        self._global_data: list[dict] | None = None
        self._global_applied = False
        self._global_labels: list[object] = []

        _labels: list[object] = []

        _labels.append(
            create_label(
                LabelConfig(
                    text=title,
                    rect=pygame.Rect((40, 40), (400, 70)),
                    variant="title",
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
        
        # Painel Direito: RELATÓRIO DE COMBATE
        self.combat_panel = create_panel(
            PanelConfig(
                rect=pygame.Rect((500, 40), (700, SCREEN_HEIGHT - 80)),
                variant="card"
            ),
            manager=self.ui_manager
        )
        
        mode_display = self._modes_display.get(self._mode_name, self._mode_name)
        create_label(
            LabelConfig(text=f"TOP 5 LOCAL - {mode_display}", rect=pygame.Rect((20, 20), (320, 40)), variant="subtitle"),
            manager=self.ui_manager,
            container=self.combat_panel
        )
        create_label(
            LabelConfig(text=f"TOP 5 GLOBAL - {mode_display}", rect=pygame.Rect((360, 20), (320, 40)), variant="subtitle"),
            manager=self.ui_manager,
            container=self.combat_panel
        )
        
        self.loading_global_lbl = create_label(
            LabelConfig(text="Buscando...", rect=pygame.Rect((360, 80), (320, 30)), variant="muted"),
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
        
        self._last_score = self.reached_level * 1000
        if self.session_stats is not None:
            self._last_score += self.session_stats.enemy_spawned_total * 50
            self._last_score += self.session_stats.collectible_collected_total * 200

        RankingService().save_score(
            score=self._last_score,
            mode=self._mode_name
        )
        
        self._show_local_ranking()
        RankingService().fetch_global_ranking(limit=5, mode=self._mode_name, callback=self._on_global_fetched)

    def _show_local_ranking(self) -> None:
        local_data = RankingService().get_local_ranking(mode=self._mode_name, limit=5)
        player_name = RankingService().get_player_name() or "Desconhecido"
        start_y = 80
        if not local_data:
            create_label(
                LabelConfig(text="Nenhum registro.", rect=pygame.Rect((20, start_y), (320, 30)), variant="muted"),
                manager=self.ui_manager, container=self.combat_panel
            )
            return
            
        for i, entry in enumerate(local_data):
            is_current = (
                entry.get("player_name") == player_name and 
                abs(entry.get("score", 0) - self._last_score) < 0.01
            )
            create_label(
                LabelConfig(
                    text=f"{i+1}. {entry.get('player_name', '')} | {entry.get('score', 0)}",
                    rect=pygame.Rect((20, start_y + (i * 35)), (320, 30)),
                    variant="highlight" if is_current else "value"
                ),
                manager=self.ui_manager, container=self.combat_panel
            )

    def _on_global_fetched(self, data: list[dict]) -> None:
        self._global_data = data

    def update(self, dt: float) -> None:
        super().update(dt)
        if self._global_data is not None and not self._global_applied:
            self._global_applied = True
            self.loading_global_lbl.kill()
            
            start_y = 80
            if not self._global_data:
                self._global_labels.append(
                    create_label(
                        LabelConfig(text="Sem registros ou erro.", rect=pygame.Rect((360, start_y), (320, 30)), variant="muted"),
                        manager=self.ui_manager, container=self.combat_panel
                    )
                )
                return
            
            player_name = RankingService().get_player_name() or "Desconhecido"
            for i, entry in enumerate(self._global_data):
                is_current = (
                    entry.get("player_name") == player_name and 
                    abs(entry.get("score", 0) - self._last_score) < 0.01
                )
                self._global_labels.append(
                    create_label(
                        LabelConfig(
                            text=f"{i+1}. {entry.get('player_name', '')} | {entry.get('score', 0)}",
                            rect=pygame.Rect((360, start_y + (i * 35)), (320, 30)),
                            variant="highlight" if is_current else "value"
                        ),
                        manager=self.ui_manager, container=self.combat_panel
                    )
                )

    def _retry(self) -> None:
        from game.scenes.game_scene import GameScene
        self.stack.replace(GameScene(self.stack, self._retry_mode_instance))

    def _go_main_menu(self) -> None:
        from game.scenes.main_menu_scene import MainMenuScene
        self.stack.replace(MainMenuScene(self.stack))
