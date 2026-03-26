from __future__ import annotations

import random
from typing import TYPE_CHECKING

from pygame import Vector2

from game.components.data_components import DormantComponent, HealthComponent, PlayerShootComponent, TransformComponent
from game.config import SCREEN_HEIGHT, SCREEN_WIDTH
from game.core.world import GameWorld
from game.factories.enemy_factory import EnemyFactory
from game.factories.dungeon_factory import DungeonFactory
from game.modes.dungeons_layout import DungeonLayout, DungeonRuntimeState, DungeonSpatialIndex
from game.modes.game_mode_strategy import GameModeStrategy
from game.modes.level_progression_strategy import DungeonsLevelProgressionStrategy, LevelProgressionStrategy
from game.modes.mode_config import DungeonTheme, DungeonsConfig
from game.modes.spawn_strategy import DungeonsSpawnStrategy, SpawnStrategy, EARLY_ENEMY_KINDS, MID_ENEMY_KINDS, LATE_ENEMY_KINDS, EARLY_BOSS_KINDS, MID_BOSS_KINDS, LATE_BOSS_KINDS
from game.systems.camera_system import CameraSystem
from game.systems.collision_system import CollisionSystem
from game.systems.dash_system import DashSystem
from game.systems.damage_system import DamageSystem
from game.systems.dungeon_collision_system import DungeonCollisionSystem
from game.systems.dungeon_objective_system import DungeonObjectiveSystem
from game.systems.dungeon_visibility_system import DungeonVisibilitySystem
from game.systems.follow_system import FollowSystem
from game.systems.invulnerability_system import InvulnerabilitySystem
from game.systems.lifetime_system import LifetimeSystem
from game.systems.movement_system import MovementSystem
from game.systems.parry_system import ParrySystem
from game.systems.player_shoot_system import PlayerShootSystem
from game.systems.shoot_system import ShootSystem
from game.systems.stagger_system import StaggerSystem
from game.systems.system_pipeline import PipelinePhase, SystemSpec

if TYPE_CHECKING:
    from game.core.session_stats import GameSessionStats
    from game.scenes.game_scene import GameScene


class DungeonsMode(GameModeStrategy):
    def __init__(self, config: DungeonsConfig | None = None, theme: DungeonTheme | None = None, seed: int | None = None) -> None:
        self.config = DungeonsConfig() if config is None else config
        self.theme = theme or self.default_themes()[0]
        self._rng = random.Random(seed)
        self._runtime_state: DungeonRuntimeState | None = None

    def on_enter(self, scene: "GameScene") -> None:
        scene.setup_level(1)

    def on_player_death(self, scene: "GameScene") -> None:
        elapsed_time = float(scene.elapsed_time)
        reached_level = int(scene.world.level)
        score = self.calcular_ranking(elapsed_time, reached_level, scene.session_stats)
        death_cause = scene.world.runtime_state.get("last_death_cause")
        scene.open_game_over(
            title="Dungeons - Queda",
            subtitle=f"Nivel alcancado: {scene.world.level}",
            retry_strategy_factory=self.create_retry_strategy,
            death_cause=death_cause if isinstance(death_cause, str) else None,
            include_session_summary=True,
            final_score=score,
        )

    def mode_key(self) -> str:
        return "Dungeons"

    def calcular_ranking(self, elapsed_time: float, reached_level: int, session_stats: "GameSessionStats") -> float:
        return round(sum(points for _, points in self.score_breakdown(elapsed_time, reached_level, session_stats)), 2)

    def score_breakdown(
        self,
        elapsed_time: float,
        reached_level: int,
        session_stats: "GameSessionStats",
    ) -> list[tuple[str, float]]:
        portal_count = session_stats.spawn_portal_destroyed_total
        return [
            (f"Nivel ({reached_level}x120)", reached_level * 120.0),
            (f"Tempo (-{elapsed_time:.1f}s)", -elapsed_time),
            (f"Portais ({portal_count}x6)", portal_count * 6.0),
        ]

    def configure_level(self, scene: "GameScene", level: int) -> None:
        del level
        layout = DungeonLayout.generate(
            width=self.config.grid_width,
            height=self.config.grid_height,
            cell_size=self.config.cell_size,
            rng=self._rng,
            room_attempts=self.config.room_attempts,
            room_min_size=self.config.room_min_size,
            room_max_size=self.config.room_max_size,
            corridor_width=self.config.corridor_width,
        )
        spatial_index = DungeonSpatialIndex.build(layout)
        self._runtime_state = DungeonRuntimeState(
            layout=layout,
            spatial_index=spatial_index,
            revealed_cells=set(),
            visible_cells=set(),
        )

        scene.world.width = int(layout.width * layout.geometry.cell_size)
        scene.world.height = int(layout.height * layout.geometry.cell_size)
        scene.world.runtime_state["camera_mode"] = "center_player"
        scene.world.runtime_state["camera_offset"] = Vector2()
        scene.world.runtime_state["background_mode"] = "dungeon"
        scene.world.runtime_state["dungeon_runtime"] = self._runtime_state

        self._position_player(scene, layout)
        self._ensure_player_shooting(scene)

        for wall_rect in layout.wall_rects:
            scene.world.add_entity(DungeonFactory.create_wall_visual(wall_rect, self.theme))

        self._spawn_room_enemies(scene, layout)
        self._spawn_boss(scene, layout)

    def build_level_progression_strategy(self) -> LevelProgressionStrategy:
        return DungeonsLevelProgressionStrategy()

    def build_spawn_strategy(self) -> SpawnStrategy:
        return DungeonsSpawnStrategy()

    def build_hud_lines(self, scene: "GameScene") -> list[str]:
        runtime = self._runtime_state
        theme_name = self.theme.name
        if runtime is None:
            return [
                f"Modo: Dungeons - {theme_name}",
                f"Tempo: {scene.elapsed_time:.2f}s",
                f"Nivel: {scene.world.level}",
            ]

        boss_status = "derrotado" if runtime.boss_defeated else "ativo"
        return [
            f"Modo: Dungeons - {theme_name}",
            f"Tempo: {scene.elapsed_time:.2f}s",
            f"Nivel: {scene.world.level}",
            f"Boss: {boss_status}",
        ]

    def create_retry_strategy(self) -> GameModeStrategy:
        return DungeonsMode(config=self.config, theme=self.theme)

    def build_systems(self, world: GameWorld) -> list[SystemSpec]:
        runtime_provider = self._get_runtime_state
        return [
            SystemSpec(system=DashSystem(world), phase=PipelinePhase.PRE_UPDATE, priority=10),
            SystemSpec(system=ParrySystem(world), phase=PipelinePhase.PRE_UPDATE, priority=15),
            SystemSpec(system=InvulnerabilitySystem(world), phase=PipelinePhase.PRE_UPDATE, priority=20),
            SystemSpec(system=PlayerShootSystem(world), phase=PipelinePhase.PRE_UPDATE, priority=25),
            SystemSpec(
                system=DungeonVisibilitySystem(world, runtime_provider, vision_radius=self.config.vision_radius),
                phase=PipelinePhase.PRE_UPDATE,
                priority=30,
            ),
            SystemSpec(system=FollowSystem(world), phase=PipelinePhase.PRE_UPDATE, priority=35),
            SystemSpec(system=ShootSystem(world), phase=PipelinePhase.PRE_UPDATE, priority=40),
            SystemSpec(system=LifetimeSystem(world), phase=PipelinePhase.PRE_UPDATE, priority=50),
            SystemSpec(system=StaggerSystem(world), phase=PipelinePhase.PRE_UPDATE, priority=55),
            SystemSpec(system=MovementSystem(world), phase=PipelinePhase.SIMULATION, priority=10),
            SystemSpec(
                system=DungeonCollisionSystem(world, runtime_provider),
                phase=PipelinePhase.POST_UPDATE,
                priority=5,
            ),
            SystemSpec(system=DamageSystem(world), phase=PipelinePhase.POST_UPDATE, priority=7),
            SystemSpec(system=CollisionSystem(world), phase=PipelinePhase.POST_UPDATE, priority=10),
            SystemSpec(
                system=DungeonObjectiveSystem(world, runtime_provider),
                phase=PipelinePhase.POST_UPDATE,
                priority=20,
            ),
            SystemSpec(
                system=CameraSystem(world, screen_width=SCREEN_WIDTH, screen_height=SCREEN_HEIGHT),
                phase=PipelinePhase.POST_UPDATE,
                priority=90,
            ),
        ]

    def _get_runtime_state(self) -> DungeonRuntimeState | None:
        return self._runtime_state

    def _position_player(self, scene: "GameScene", layout: DungeonLayout) -> None:
        player = scene.world.player
        if player is None:
            return
        transform = player.get_component(TransformComponent)
        if transform is None:
            return
        spawn_center = layout.room_center(layout.spawn_room_index)
        transform.position = Vector2(spawn_center)

    def _ensure_player_shooting(self, scene: "GameScene") -> None:
        player = scene.world.player
        if player is None:
            return
        shoot = player.get_component(PlayerShootComponent)
        if shoot is not None:
            return
        player.add_component(
            PlayerShootComponent(
                cooldown=self.config.player_shoot_cooldown,
                bullet_speed=self.config.player_bullet_speed,
                bullet_radius=self.config.player_bullet_radius,
                bullet_color=self.config.player_bullet_color,
                bullet_damage=self.config.player_bullet_damage,
            )
        )

    def _spawn_room_enemies(self, scene: "GameScene", layout: DungeonLayout) -> None:
        blocked_rooms = {layout.spawn_room_index, layout.boss_room_index}
        enemy_pool = self._enemy_pool_for_level(scene.world.level)
        for index, room in enumerate(layout.rooms):
            if index in blocked_rooms:
                continue
            enemy_count = self._rng.randint(self.config.enemy_per_room_min, self.config.enemy_per_room_max)
            blocked_cells: set[tuple[int, int]] = set()
            for _ in range(enemy_count):
                spawn_cell = self._random_cell_in_room(room, blocked_cells)
                blocked_cells.add(spawn_cell)
                position = layout.cell_center(spawn_cell)
                enemy_kind = EnemyFactory.choose_random_enemy_kind_from(list(enemy_pool))
                enemy = EnemyFactory.create_by_kind(enemy_kind, position)
                self._adapt_enemy(enemy)
                scene.world.add_entity(enemy)

    def _spawn_boss(self, scene: "GameScene", layout: DungeonLayout) -> None:
        boss_position = layout.room_center(layout.boss_room_index)
        boss_pool = self._boss_pool_for_level(scene.world.level)
        boss_kind = EnemyFactory.choose_random_boss_kind_from(list(boss_pool))
        boss = EnemyFactory.create_by_kind(boss_kind, boss_position)
        boss.add_tag("dungeon_boss")
        self._adapt_enemy(boss, is_boss=True)
        scene.world.add_entity(boss)

    def _random_cell_in_room(self, room, blocked: set[tuple[int, int]]) -> tuple[int, int]:
        min_x = room.x + 1
        max_x = max(room.x + 1, room.x + room.width - 2)
        min_y = room.y + 1
        max_y = max(room.y + 1, room.y + room.height - 2)
        for _ in range(8):
            x = self._rng.randint(min_x, max_x)
            y = self._rng.randint(min_y, max_y)
            cell = (x, y)
            if cell not in blocked:
                return cell
        return (min_x, min_y)

    def _adapt_enemy(self, enemy, is_boss: bool = False) -> None:
        if not enemy.has_tag("dungeon_enemy"):
            enemy.add_tag("dungeon_enemy")

        dormant = enemy.get_component(DormantComponent)
        if dormant is None:
            enemy.add_component(DormantComponent(active=False))
        else:
            dormant.active = False

        health = enemy.get_component(HealthComponent)
        if health is None:
            max_health = self.config.boss_health if is_boss else float(self._rng.randint(self.config.enemy_health_min, self.config.enemy_health_max))
            enemy.add_component(HealthComponent(current=max_health, maximum=max_health))

    @staticmethod
    def _enemy_pool_for_level(level: int) -> tuple[str, ...]:
        if level <= 3:
            return EARLY_ENEMY_KINDS
        if level <= 7:
            return MID_ENEMY_KINDS
        return LATE_ENEMY_KINDS

    @staticmethod
    def _boss_pool_for_level(level: int) -> tuple[str, ...]:
        if level <= 6:
            return EARLY_BOSS_KINDS
        if level <= 10:
            return MID_BOSS_KINDS
        return LATE_BOSS_KINDS

    @staticmethod
    def default_themes() -> list[DungeonTheme]:
        return [
            DungeonTheme(
                name="Crypt",
                description="Criptas antigas com energia instavel.",
                wall_fill=(74, 68, 92),
                wall_edge=(186, 160, 232),
                enemy_primary=(160, 130, 210),
                enemy_secondary=(110, 190, 210),
                enemy_tertiary=(210, 110, 150),
                enemy_bullet=(180, 220, 255),
                boss_color=(255, 170, 220),
                wall_line_thickness=9,
            ),
            DungeonTheme(
                name="Frost",
                description="Galerias congeladas e ecos glaciares.",
                wall_fill=(64, 92, 120),
                wall_edge=(190, 240, 255),
                enemy_primary=(90, 210, 255),
                enemy_secondary=(120, 160, 255),
                enemy_tertiary=(180, 230, 255),
                enemy_bullet=(170, 245, 255),
                boss_color=(120, 230, 255),
                wall_line_thickness=9,
            ),
            DungeonTheme(
                name="Inferno",
                description="Galerias ardentes e pressao constante.",
                wall_fill=(96, 46, 30),
                wall_edge=(255, 170, 110),
                enemy_primary=(255, 120, 90),
                enemy_secondary=(255, 170, 90),
                enemy_tertiary=(255, 90, 110),
                enemy_bullet=(255, 200, 120),
                boss_color=(255, 110, 70),
                wall_line_thickness=9,
            ),
        ]
