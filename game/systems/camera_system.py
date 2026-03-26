from __future__ import annotations

from pygame import Vector2

from game.components.data_components import TransformComponent
from game.core.world import GameWorld


class CameraSystem:
    def __init__(self, world: GameWorld, screen_width: int, screen_height: int) -> None:
        self.world = world
        self.screen_center = Vector2(screen_width * 0.5, screen_height * 0.5)

    def update(self, dt: float) -> None:
        del dt
        if self.world.runtime_state.get("camera_mode") != "center_player":
            self.world.runtime_state["camera_offset"] = Vector2()
            return

        player = self.world.player
        if player is None:
            self.world.runtime_state["camera_offset"] = Vector2()
            return

        transform = player.get_component(TransformComponent)
        if transform is None:
            self.world.runtime_state["camera_offset"] = Vector2()
            return

        self.world.runtime_state["camera_offset"] = self.screen_center - Vector2(transform.position)
