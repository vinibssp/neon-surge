from __future__ import annotations

from pygame import Rect
from pygame import Vector2

from game.components.data_components import RenderComponent, TransformComponent
from game.ecs.entity import Entity
from game.modes.mode_config import DungeonTheme
from game.rendering.strategies import LabyrinthWallRenderStrategy


class DungeonFactory:
    @staticmethod
    def create_wall_visual(wall_rect: Rect, theme: DungeonTheme) -> Entity:
        wall = Entity()
        wall.add_tag("dungeon-wall")
        center = Vector2(wall_rect.centerx, wall_rect.centery)
        wall.add_component(TransformComponent(position=center))
        wall.add_component(
            RenderComponent(
                render_strategy=LabyrinthWallRenderStrategy(
                    fill_color=theme.wall_fill,
                    edge_color=theme.wall_edge,
                    width=float(wall_rect.width),
                    height=float(wall_rect.height),
                    line_thickness=theme.wall_line_thickness,
                )
            )
        )
        return wall
