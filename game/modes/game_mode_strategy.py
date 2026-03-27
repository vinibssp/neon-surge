from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from game.core.world import GameWorld
from game.modes.level_progression_strategy import LevelProgressionStrategy
from game.modes.spawn_strategy import SpawnStrategy
from game.systems.system_pipeline import SystemSpec

if TYPE_CHECKING:
    from game.core.session_stats import GameSessionStats
    from game.scenes.game_scene import GameScene


class GameModeStrategy(ABC):
    @abstractmethod
    def on_enter(self, scene: "GameScene") -> None:
        ...

    @abstractmethod
    def on_player_death(self, scene: "GameScene") -> None:
        ...

    def mode_key(self) -> str:
        mapping = {
            "RaceMode": "Race",
            "RaceInfiniteMode": "RaceInfinite",
            "SurvivalMode": "Survival",
            "SurvivalHardcoreMode": "SurvivalHardcore",
            "LabyrinthMode": "Labyrinth",
            "OneVsOneMode": "OneVsOne",
            "TrainingMode": "Training",
        }
        return mapping.get(type(self).__name__, type(self).__name__.replace("Mode", ""))

    def calcular_ranking(self, elapsed_time: float, reached_level: int, session_stats: "GameSessionStats") -> float:
        return round(sum(value for _, value in self.score_breakdown(elapsed_time, reached_level, session_stats)), 2)

    def score_breakdown(
        self,
        elapsed_time: float,
        reached_level: int,
        session_stats: "GameSessionStats",
    ) -> list[tuple[str, float]]:
        portal_count = session_stats.spawn_portal_destroyed_total
        collectible_count = session_stats.collectible_collected_total
        parry_count = session_stats.parry_landed_total
        return [
            (f"Nivel ({reached_level}x100)", reached_level * 100.0),
            (f"Coletaveis ({collectible_count}x5)", collectible_count * 5.0),
            (f"Portais ({portal_count}x10)", portal_count * 10.0),
            (f"Parry ({parry_count}x5)", parry_count * 5.0),
            (f"Tempo (-{elapsed_time:.1f}s)", -elapsed_time),
        ]

    @abstractmethod
    def configure_level(self, scene: "GameScene", level: int) -> None:
        ...

    @abstractmethod
    def build_level_progression_strategy(self) -> LevelProgressionStrategy:
        ...

    @abstractmethod
    def build_spawn_strategy(self) -> SpawnStrategy:
        ...

    @abstractmethod
    def build_hud_lines(self, scene: "GameScene") -> list[str]:
        ...

    @abstractmethod
    def create_retry_strategy(self) -> "GameModeStrategy":
        ...

    @abstractmethod
    def build_systems(self, world: GameWorld) -> list[SystemSpec]:
        ...

    def render_background(self, scene: "GameScene", screen, width: int, height: int) -> bool:
        del scene
        del screen
        del width
        del height
        return False
