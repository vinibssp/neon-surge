from __future__ import annotations

from typing import TYPE_CHECKING

from game.modes.game_mode_strategy import GameModeStrategy
from game.modes.mode_config import RaceInfiniteConfig
from game.modes.race_mode import RaceMode

if TYPE_CHECKING:
    from game.core.session_stats import GameSessionStats
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
        score = self.calcular_ranking(elapsed_time, reached_level, scene.session_stats)
        death_cause = scene.world.runtime_state.get("last_death_cause")
        scene.open_game_over(
            title="GAME OVER",
            subtitle=f"Nivel alcancado: {scene.world.level}",
            retry_strategy_factory=self.create_retry_strategy,
            death_cause=death_cause if isinstance(death_cause, str) else None,
            include_session_summary=True,
            final_score=score,
        )

    def mode_key(self) -> str:
        return "RaceInfinite"

    def calcular_ranking(self, elapsed_time: float, reached_level: int, session_stats: "GameSessionStats") -> float:
        return round(sum(points for _, points in self.score_breakdown(elapsed_time, reached_level, session_stats)), 2)

    def score_breakdown(
        self,
        elapsed_time: float,
        reached_level: int,
        session_stats: "GameSessionStats",
    ) -> list[tuple[str, float]]:
        del reached_level
        collectible_count = session_stats.collectible_collected_total
        portal_count = session_stats.spawn_portal_destroyed_total
        return [
            (f"Tempo ({elapsed_time:.1f}s)", elapsed_time),
            (f"Coletaveis ({collectible_count}x5)", collectible_count * 5.0),
            (f"Portais ({portal_count}x5)", portal_count * 5.0),
        ]

    def create_retry_strategy(self) -> GameModeStrategy:
        return RaceInfiniteMode(config=self.config)
