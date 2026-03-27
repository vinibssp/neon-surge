from __future__ import annotations

from pygame import Rect
from pygame import Vector2

from game.components.data_components import (
    CollisionComponent,
    EnemyKindComponent,
    LabyrinthExitComponent,
    LabyrinthKeyComponent,
    LabyrinthVirusComponent,
    MovementComponent,
    RenderComponent,
    TransformComponent,
)
from game.ecs.entity import Entity
from game.rendering.labyrinth_visuals import (
    BossArenaFloorTileRenderStrategy,
    PALETTE,
    LabyrinthExitRenderStrategy,
    LabyrinthFloorTileRenderStrategy,
    LabyrinthKeyRenderStrategy,
    LabyrinthVirusRenderStrategy,
    LabyrinthWallRenderStrategy,
)


class LabyrinthFactory:
    @staticmethod
    def create_floor_tile(position: Vector2, size: float, checker_variant: bool, boss_arena: bool = False) -> Entity:
        tile = Entity()
        tile.add_tag("maze-floor")
        tile.add_component(TransformComponent(position=Vector2(position)))
        if boss_arena:
            base_color = PALETTE.boss_floor_a if checker_variant else PALETTE.boss_floor_b
            tile.add_tag("maze-floor-boss")
            tile.add_component(
                RenderComponent(
                    render_strategy=BossArenaFloorTileRenderStrategy(
                        width=size,
                        height=size,
                        base_color=base_color,
                        grid_color=PALETTE.boss_floor_grid,
                        rune_color=PALETTE.boss_floor_rune,
                        checker_variant=checker_variant,
                    )
                )
            )
            return tile

        base_color = PALETTE.floor_a if checker_variant else PALETTE.floor_b
        tile.add_component(
            RenderComponent(
                render_strategy=LabyrinthFloorTileRenderStrategy(
                    width=size,
                    height=size,
                    base_color=base_color,
                    edge_color=PALETTE.floor_edge,
                )
            )
        )
        return tile

    @staticmethod
    def create_wall_visual(
        wall_rect: Rect,
        color: tuple[int, int, int] | None = None,
        is_outer_border: bool = False,
    ) -> Entity:
        wall = Entity()
        wall.add_tag("maze-wall")
        if is_outer_border:
            wall.add_tag("maze-wall-border")
        center = Vector2(wall_rect.left + (wall_rect.width * 0.5), wall_rect.top + (wall_rect.height * 0.5))
        default_fill = PALETTE.wall_outer_fill if is_outer_border else PALETTE.wall_fill
        wall_fill = default_fill if color is None else color
        outline_color = PALETTE.wall_outer_outline if is_outer_border else PALETTE.wall_outline
        edge_color = PALETTE.wall_outer_edge if is_outer_border else PALETTE.wall_edge
        edge_thickness = 3 if is_outer_border else 2
        wall.add_component(TransformComponent(position=center))
        wall.add_component(
            RenderComponent(
                render_strategy=LabyrinthWallRenderStrategy(
                    width=float(wall_rect.width),
                    height=float(wall_rect.height),
                    outline_color=outline_color,
                    fill_color=wall_fill,
                    edge_color=edge_color,
                    edge_thickness=edge_thickness,
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
        key.add_component(RenderComponent(render_strategy=LabyrinthKeyRenderStrategy(color=(255, 205, 92), radius=10.0)))
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
                    locked_color=(230, 110, 130),
                    unlocked_color=(92, 232, 194),
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
        virus.add_component(EnemyKindComponent(kind=f"virus_{behavior_kind}"))
        color = (96, 222, 210) if behavior_kind == "chaser" else (234, 126, 184)
        core = (226, 235, 250)
        virus.add_component(RenderComponent(render_strategy=LabyrinthVirusRenderStrategy(color, core, radius=radius)))
        return virus
