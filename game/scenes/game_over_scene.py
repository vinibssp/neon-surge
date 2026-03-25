from __future__ import annotations

from typing import Callable

import pygame

from game.config import SCREEN_HEIGHT, SCREEN_WIDTH
from game.core.events import AudioContextChanged
from game.core.session_stats import GameSessionStats
from game.modes.game_mode_strategy import GameModeStrategy
from game.scenes.base_menu_scene import BaseMenuScene
from game.scenes.overlay_scene_factory import OverlayActionBinding, OverlaySceneFactory
from game.ui.types import UIControl


class GameOverScene(BaseMenuScene):
    def __init__(
        self,
        stack,
        reached_level: int,
        title: str = "Game Over",
        subtitle: str | None = None,
        retry_strategy_factory: Callable[[], GameModeStrategy] | None = None,
        death_cause: str | None = None,
        session_stats: GameSessionStats | None = None,
        elapsed_time: float | None = None,
    ) -> None:
        super().__init__(stack)
        self.reached_level = reached_level
        self.retry_strategy_factory = retry_strategy_factory
        subtitle_text = subtitle if subtitle is not None else f"Level {self.reached_level}"
        body_text = self._build_body_text(
            subtitle=subtitle_text,
            death_cause=death_cause,
            stats=session_stats,
            elapsed_time=elapsed_time,
            reached_level=reached_level,
        )
        overlay = OverlaySceneFactory.build(
            screen_size=(SCREEN_WIDTH, SCREEN_HEIGHT),
            ui_manager=self.ui_manager,
            title=title,
            panel_object_id="#overlay_panel",
            panel_size=(560, 470),
            body_text=body_text,
            body_rect=pygame.Rect(14, 66, 532, 310),
            action_bindings=(
                OverlayActionBinding(
                    key="retry",
                    text="Retry",
                    rect=pygame.Rect(14, 390, 448, 64),
                    handler=self._retry,
                ),
                OverlayActionBinding(
                    key="menu",
                    text="X",
                    rect=pygame.Rect(502, 12, 44, 44),
                    object_id="#overlay_close_button",
                    handler=self._menu,
                ),
            ),
            on_cancel_key="menu",
        )
        self.panel = overlay.panel
        self.subtitle_box = overlay.body
        self.retry_button: UIControl = overlay.controls["retry"]
        self.menu_button: UIControl = overlay.controls["menu"]
        self.set_navigator(
            buttons=overlay.navigation_buttons,
            actions=overlay.navigation_actions,
            on_cancel=overlay.cancel_action,
        )

    def on_enter(self) -> None:
        self.stack.event_bus.publish(AudioContextChanged(context="game_over", reason="game_over_scene_entered"))

    @staticmethod
    def _build_body_text(
        subtitle: str,
        death_cause: str | None,
        stats: GameSessionStats | None,
        elapsed_time: float | None,
        reached_level: int,
    ) -> str:
        lines = [f"<font size='4'><b>{subtitle}</b></font>"]

        lines.append("<br><font color='#ffb4b4'><b>Causa da morte</b></font>")
        lines.append(f"<font color='#ffd7d7'>{GameOverScene._format_death_cause(death_cause)}</font>")

        lines.append("<br><font color='#9ddcff'><b>Resumo da partida</b></font>")
        lines.append(f"Nivel alcancado: {reached_level}")
        if elapsed_time is not None:
            lines.append(f"Tempo sobrevivido: {elapsed_time:.1f}s")

        if stats is not None:
            lines.append(f"Inimigos gerados: {stats.enemy_spawned_total}")
            lines.append(f"Coletaveis: {stats.collectible_collected_total}")
            lines.append(f"Dash usados: {stats.dash_started_total}")
            lines.append(f"Portais destruidos: {stats.spawn_portal_destroyed_total}")
            top_kind = GameOverScene._top_enemy_kind(stats.enemy_spawned_by_kind)
            if top_kind is not None:
                lines.append(f"Inimigo mais comum: {top_kind}")

        return "<br>".join(lines)

    @staticmethod
    def _top_enemy_kind(enemy_spawned_by_kind: dict[str, int]) -> str | None:
        if not enemy_spawned_by_kind:
            return None
        kind, _ = max(enemy_spawned_by_kind.items(), key=lambda item: item[1])
        return kind.replace("_", " ").title()

    @staticmethod
    def _format_death_cause(death_cause: str | None) -> str:
        if death_cause is None or not death_cause.strip():
            return "Falha critica nao identificada."

        normalized = death_cause.strip().lower()
        if "projetil" in normalized:
            return "Voce foi atingido por um projetil inimigo."
        if "colisao" in normalized or "impacto" in normalized:
            return "Voce colidiu com um inimigo."
        if "morteiro" in normalized:
            return "Voce foi pego na explosao de um morteiro."
        if "lava" in normalized:
            return "Voce permaneceu na zona de lava durante a fase ativa."
        if "buraco negro" in normalized:
            return "Voce foi consumido por um buraco negro."

        text = death_cause.strip()
        if text.endswith((".", "!", "?")):
            return text[0].upper() + text[1:]
        return (text[0].upper() + text[1:]) + "."

    def _retry(self) -> None:
        from game.scenes.game_scene import GameScene

        strategy_factory = self.retry_strategy_factory
        if strategy_factory is None:
            return
        self.stack.replace(GameScene(self.stack, mode=strategy_factory()))

    def _menu(self) -> None:
        from game.scenes.main_menu_scene import MainMenuScene

        self.stack.replace(MainMenuScene(self.stack))
