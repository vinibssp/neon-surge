from __future__ import annotations

from typing import TYPE_CHECKING

from game.modes.game_mode_strategy import GameModeStrategy
from game.modes.mode_config import RaceInfiniteConfig
from game.modes.race_mode import RaceMode

if TYPE_CHECKING:
    from game.scenes.game_scene import GameScene


class RaceInfiniteMode(RaceMode):
    def __init__(self, config: RaceInfiniteConfig | None = None) -> None:
        super().__init__(config=RaceInfiniteConfig() if config is None else config)

    def build_hud_lines(self, scene: "GameScene") -> list[str]:
        return [
            "Modo: Corrida Infinita",
            f"Tempo: {scene.elapsed_time:.2f}s",
            f"Nivel: {scene.world.level}",
        ]

    def on_player_death(self, scene: "GameScene") -> None:
        elapsed_time = float(scene.elapsed_time)
        reached_level = int(scene.world.level)
        score = self.calcular_ranking(elapsed_time, reached_level)
        death_cause = scene.world.runtime_state.get("last_death_cause")
        scene.open_game_over(
            title="Corrida Infinita - Derrota",
            subtitle=f"Nivel alcancado: {scene.world.level}",
            retry_strategy_factory=self.create_retry_strategy,
            death_cause=death_cause if isinstance(death_cause, str) else None,
            include_session_summary=True,
            final_score=score,
        )

    def calcular_ranking(self, elapsed_time: float, reached_level: int) -> float:
        del elapsed_time
        return float(reached_level)

    def create_retry_strategy(self) -> GameModeStrategy:
        return RaceInfiniteMode(config=self.config)
