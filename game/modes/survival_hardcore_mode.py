from __future__ import annotations

from typing import TYPE_CHECKING

from game.modes.game_mode_strategy import GameModeStrategy
from game.modes.mode_config import SurvivalHardcoreConfig
from game.modes.survival_mode import SurvivalMode

if TYPE_CHECKING:
    from game.scenes.game_scene import GameScene


class SurvivalHardcoreMode(SurvivalMode):
    def __init__(self, config: SurvivalHardcoreConfig | None = None) -> None:
        super().__init__(config=SurvivalHardcoreConfig() if config is None else config)

    def on_player_death(self, scene: "GameScene") -> None:
        death_cause = scene.world.runtime_state.get("last_death_cause")
        scene.open_game_over(
            title="Hardcore Over",
            subtitle=f"Resistiu: {scene.elapsed_time:.2f}s",
            retry_strategy_factory=self.create_retry_strategy,
            death_cause=death_cause if isinstance(death_cause, str) else None,
            include_session_summary=True,
        )

    def build_hud_lines(self, scene: "GameScene") -> list[str]:
        lines = super().build_hud_lines(scene)
        if lines:
            lines[0] = "Modo: Survival Hardcore"
        return lines

    def create_retry_strategy(self) -> GameModeStrategy:
        return SurvivalHardcoreMode(config=self.config)
