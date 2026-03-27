from __future__ import annotations

from dataclasses import dataclass, field

from pygame import Vector2

from game.components.data_components import CollisionComponent, StaggeredComponent, TransformComponent
from game.config import ENEMY_SPAWN_FREEZE_TIME
from game.core.events import EnemyShotFired, EventBus
from game.ecs.entity import Entity
from game.ecs.query import WorldQuery


@dataclass
class GameWorld:
    width: int
    height: int
    entities: list[Entity] = field(default_factory=list)
    pending_add: list[Entity] = field(default_factory=list)
    pending_remove: list[Entity] = field(default_factory=list)
    player: Entity | None = None
    event_bus: EventBus = field(default_factory=EventBus)
    level: int = 1
    runtime_state: dict[str, object] = field(default_factory=dict)

    def add_entity(self, entity: Entity) -> None:
        self._apply_enemy_spawn_freeze(entity)
        self.pending_add.append(entity)

    def _apply_enemy_spawn_freeze(self, entity: Entity) -> None:
        if not entity.has_tag("enemy"):
            return
        stagger = entity.get_component(StaggeredComponent)
        if stagger is None:
            entity.add_component(StaggeredComponent(time_left=ENEMY_SPAWN_FREEZE_TIME, pulse_time=0.0))
            return
        stagger.time_left = max(stagger.time_left, ENEMY_SPAWN_FREEZE_TIME)

    def remove_entity(self, entity: Entity) -> None:
        if entity not in self.pending_remove:
            self.pending_remove.append(entity)

    def apply_pending(self) -> None:
        if self.pending_remove:
            remove_ids = {entity.id for entity in self.pending_remove}
            self.entities = [entity for entity in self.entities if entity.id not in remove_ids]
            self.pending_remove.clear()

        if self.pending_add:
            self.entities.extend(self.pending_add)
            self.pending_add.clear()

    def query(self, world_query: WorldQuery) -> list[Entity]:
        return world_query.filter(self.entities)

    def count_by_tag(self, tag: str) -> int:
        return sum(1 for entity in self.entities if entity.active and entity.has_tag(tag))

    def spawn_enemy_bullet(
        self,
        origin: Vector2,
        direction: Vector2,
        speed: float,
        radius: float,
        color: tuple[int, int, int] | None = None,
        enemy_type: str = "enemy",
        source_entity_id: int | None = None,
        source_enemy_kind: str | None = None,
    ) -> None:
        from game.factories.bullet_factory import BulletFactory

        owner_entity_id = source_entity_id
        if owner_entity_id is None:
            context_owner = self.runtime_state.get("current_enemy_shooter_id")
            if isinstance(context_owner, int):
                owner_entity_id = context_owner

        owner_kind = source_enemy_kind
        if owner_kind is None:
            context_kind = self.runtime_state.get("current_enemy_shooter_kind")
            if isinstance(context_kind, str):
                owner_kind = context_kind

        bullet = BulletFactory.create_enemy_bullet(
            origin,
            direction,
            speed,
            radius,
            color=color,
            owner_entity_id=owner_entity_id,
            owner_kind=owner_kind,
        )
        self.add_entity(bullet)
        self.event_bus.publish(EnemyShotFired(enemy_type=enemy_type))

    def clamp_to_bounds(self, position: Vector2, radius: float) -> Vector2:
        clamped_x = min(max(radius, position.x), self.width - radius)
        clamped_y = min(max(radius, position.y), self.height - radius)
        return Vector2(clamped_x, clamped_y)

    def clear_non_player_entities(self) -> None:
        self.entities = [entity for entity in self.entities if entity is self.player]
        self.pending_add.clear()
        self.pending_remove.clear()

    def get_collision_radius(self, entity: Entity) -> float:
        collision = entity.get_component(CollisionComponent)
        return 0.0 if collision is None else collision.radius

    def get_position(self, entity: Entity) -> Vector2 | None:
        transform = entity.get_component(TransformComponent)
        return None if transform is None else transform.position
