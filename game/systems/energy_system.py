from __future__ import annotations

from game.components.data_components import EnergyComponent
from game.core.world import GameWorld
from game.systems.world_queries import PLAYER_QUERY


class EnergySystem:
    def __init__(self, world: GameWorld) -> None:
        self.world = world

    def update(self, dt: float) -> None:
        for player in self.world.query(PLAYER_QUERY):
            energy = player.get_component(EnergyComponent)
            if energy is None:
                continue
            energy.current_energy = min(
                energy.max_energy,
                energy.current_energy + (energy.regen_rate * dt),
            )
