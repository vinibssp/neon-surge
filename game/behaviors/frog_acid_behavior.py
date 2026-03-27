from __future__ import annotations

from pygame import Vector2

from game.behaviors.advanced_helpers import normalized, predict_intercept_position
from game.behaviors.behavior import Behavior
from game.components.data_components import MovementComponent, TransformComponent, TurretComponent
from game.core.enemy_names import enemy_kind_from_entity
from game.ecs.entity import Entity
from game.factories.bullet_factory import BulletFactory


class FrogAcidBehavior(Behavior):
    ACID_WARNING_DURATION = 0.45
    ACID_POOL_RADIUS = 22.0
    ACID_POOL_LIFETIME = 4.6
    ACID_POOL_COLOR = (96, 224, 102)
    ACID_WARNING_COLOR = (166, 255, 168)

    def __init__(self) -> None:
        self._hop_timer: dict[int, float] = {}
        self._spit_cycle: dict[int, int] = {}
        self._pending_spits: dict[int, list[tuple[Vector2, float]]] = {}

    def update(self, entity: Entity, world: "GameWorld", dt: float) -> None:
        entity_id = entity.id
        owner_kind = enemy_kind_from_entity(entity)
        self._update_pending_spits(entity_id=entity_id, owner_kind=owner_kind, world=world, dt=dt)

        player = world.player
        if player is None:
            return

        transform = entity.get_component(TransformComponent)
        movement = entity.get_component(MovementComponent)
        turret = entity.get_component(TurretComponent)
        player_transform = player.get_component(TransformComponent)
        player_movement = player.get_component(MovementComponent)
        if transform is None or movement is None or turret is None or player_transform is None:
            return

        hop_timer = self._hop_timer.get(entity_id, 0.0) - dt
        if hop_timer <= 0.0:
            jump_dir = normalized(player_transform.position - transform.position)
            lateral_sign = 1.0 if entity_id % 2 == 0 else -1.0
            jump_dir = normalized(jump_dir + Vector2(-jump_dir.y, jump_dir.x) * 0.28 * lateral_sign, jump_dir)
            movement.velocity = jump_dir * 240.0
            movement.input_direction = jump_dir
            movement.max_speed = 240.0
            hop_timer = 0.82
        else:
            movement.velocity *= 0.86
            movement.input_direction = normalized(movement.velocity, movement.input_direction)
            movement.max_speed = max(65.0, movement.velocity.length())
        self._hop_timer[entity_id] = hop_timer

        turret.shot_timer += dt
        if turret.shot_timer < 2.25:
            return
        turret.shot_timer = 0.0

        target_velocity = Vector2() if player_movement is None else Vector2(player_movement.velocity)
        puddle_position = predict_intercept_position(
            origin=transform.position,
            target_position=player_transform.position,
            target_velocity=target_velocity,
            projectile_speed=190.0,
            max_lead_time=0.45,
        )
        spit_cycle = self._spit_cycle.get(entity_id, 0)
        self._spit_cycle[entity_id] = (spit_cycle + 1) % 3
        offsets = (Vector2(),) if spit_cycle != 2 else (Vector2(), Vector2(28.0, 0.0), Vector2(-28.0, 0.0))
        pending_spits = self._pending_spits.setdefault(entity_id, [])
        for offset in offsets:
            target_position = puddle_position + offset
            world.add_entity(
                BulletFactory.create_mortar_target_marker(
                    position=target_position,
                    duration=self.ACID_WARNING_DURATION,
                    color=self.ACID_WARNING_COLOR,
                    radius=self.ACID_POOL_RADIUS,
                )
            )
            pending_spits.append((target_position, self.ACID_WARNING_DURATION))

    def _update_pending_spits(
        self,
        entity_id: int,
        owner_kind: str | None,
        world: "GameWorld",
        dt: float,
    ) -> None:
        pending_spits = self._pending_spits.get(entity_id)
        if not pending_spits:
            return

        next_pending: list[tuple[Vector2, float]] = []
        for position, timer in pending_spits:
            timer_left = timer - dt
            if timer_left > 0.0:
                next_pending.append((position, timer_left))
                continue
            world.add_entity(
                BulletFactory.create_acid_pool(
                    position=position,
                    radius=self.ACID_POOL_RADIUS,
                    lifetime=self.ACID_POOL_LIFETIME,
                    color=self.ACID_POOL_COLOR,
                    owner_kind=owner_kind,
                )
            )

        if next_pending:
            self._pending_spits[entity_id] = next_pending
            return
        self._pending_spits.pop(entity_id, None)


from game.core.world import GameWorld
