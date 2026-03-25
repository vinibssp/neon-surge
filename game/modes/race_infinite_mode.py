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

    def create_retry_strategy(self) -> GameModeStrategy:
        return RaceInfiniteMode(config=self.config)
