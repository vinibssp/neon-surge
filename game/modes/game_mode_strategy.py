from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from game.core.world import GameWorld
from game.modes.level_progression_strategy import LevelProgressionStrategy
from game.modes.spawn_strategy import SpawnStrategy
from game.systems.system_pipeline import SystemSpec

if TYPE_CHECKING:
    from game.scenes.game_scene import GameScene


class GameModeStrategy(ABC):
    @abstractmethod
    def on_enter(self, scene: "GameScene") -> None:
        ...

    @abstractmethod
    def on_player_death(self, scene: "GameScene") -> None:
        ...

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
