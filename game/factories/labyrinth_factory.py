from __future__ import annotations

from pygame import Rect
from pygame import Vector2

from game.components.data_components import (
    CollisionComponent,
    LabyrinthExitComponent,
    LabyrinthKeyComponent,
    LabyrinthVirusComponent,
    MovementComponent,
    RenderComponent,
    TransformComponent,
)
from game.ecs.entity import Entity
from game.rendering.strategies import (
    LabyrinthExitRenderStrategy,
    LabyrinthKeyRenderStrategy,
    RectRenderStrategy,
    VirusGlitchRenderStrategy,
)


class LabyrinthFactory:
    @staticmethod
    def create_wall_visual(wall_rect: Rect, color: tuple[int, int, int] = (24, 180, 155)) -> Entity:
        wall = Entity()
        wall.add_tag("maze-wall")
        center = Vector2(wall_rect.centerx, wall_rect.centery)
        wall.add_component(TransformComponent(position=center))
        wall.add_component(
            RenderComponent(
                render_strategy=RectRenderStrategy(
                    color=color,
                    width=float(wall_rect.width),
                    height=float(wall_rect.height),
                )
            )
        )
        return wall

    @staticmethod
    def create_key(position: Vector2) -> Entity:
        key = Entity()
        key.add_tag("maze-key")
        key.add_component(TransformComponent(position=Vector2(position)))
        key.add_component(LabyrinthKeyComponent(collected=False))
        key.add_component(CollisionComponent(radius=11.0, layer="maze-objective"))
        key.add_component(RenderComponent(render_strategy=LabyrinthKeyRenderStrategy(color=(255, 232, 80), radius=10.0)))
        return key

    @staticmethod
    def create_exit(position: Vector2, unlocked: bool = False) -> Entity:
        exit_entity = Entity()
        exit_entity.add_tag("maze-exit")
        exit_entity.add_component(TransformComponent(position=Vector2(position)))
        exit_entity.add_component(LabyrinthExitComponent(unlocked=unlocked))
        exit_entity.add_component(CollisionComponent(radius=16.0, layer="maze-objective"))
        exit_entity.add_component(
            RenderComponent(
                render_strategy=LabyrinthExitRenderStrategy(
                    locked_color=(240, 70, 85),
                    unlocked_color=(70, 245, 145),
                    size=34.0,
                )
            )
        )
        return exit_entity

    @staticmethod
    def create_virus(position: Vector2, behavior_kind: str, speed: float, radius: float = 13.0) -> Entity:
        virus = Entity()
        virus.add_tag("enemy")
        virus.add_tag("maze-virus")
        virus.add_component(TransformComponent(position=Vector2(position)))
        virus.add_component(MovementComponent(max_speed=speed))
        virus.add_component(CollisionComponent(radius=radius, layer="enemy"))
        virus.add_component(
            LabyrinthVirusComponent(
                behavior_kind=behavior_kind,
                base_speed=speed,
                retarget_interval=0.18 if behavior_kind == "chaser" else 0.22,
                interception_seconds=0.7 if behavior_kind == "interceptor" else 0.45,
            )
        )
        color = (115, 255, 180) if behavior_kind == "chaser" else (255, 110, 145)
        core = (235, 245, 255)
        virus.add_component(RenderComponent(render_strategy=VirusGlitchRenderStrategy(color, core, radius=radius)))
        return virus
