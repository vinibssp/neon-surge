from __future__ import annotations

import random

from pygame import Vector2

from game.behaviors.advanced_helpers import normalized
from game.behaviors.behavior import Behavior
from game.components.data_components import BossComponent, MovementComponent, TransformComponent
from game.config import (
    ENEMY_BOSS_ARTILLERY_BULLET_COLOR,
    ENEMY_BOSS_CHAOTIC_BULLET_COLOR,
    ENEMY_BOSS_STANDARD_BULLET_COLOR,
)
from game.ecs.entity import Entity
from game.factories.portal_factory import PortalFactory


class BossBehavior(Behavior):
    def update(self, entity: Entity, world: "GameWorld", dt: float) -> None:
        player = world.player
        if player is None:
            return

        boss = entity.get_component(BossComponent)
        transform = entity.get_component(TransformComponent)
        movement = entity.get_component(MovementComponent)
        player_transform = player.get_component(TransformComponent)
        if boss is None or transform is None or movement is None or player_transform is None:
            return

        if boss.boss_kind == "boss":
            self._update_standard_boss(entity, world, dt, boss, transform, movement, player_transform)
            return

        if boss.boss_kind == "boss_artilharia":
            self._update_artillery_boss(world, dt, boss, transform, movement, player_transform)
            return

        self._update_chaotic_boss(world, dt, boss, transform, movement, player_transform)

    def _update_standard_boss(
        self,
        entity: Entity,
        world: "GameWorld",
        dt: float,
        boss: BossComponent,
        transform: TransformComponent,
        movement: MovementComponent,
        player_transform: TransformComponent,
    ) -> None:
        del entity
        boss.ability_timer += dt
        boss.shot_timer += dt

        to_player = player_transform.position - transform.position
        if boss.state == "pursuing":
            desired = normalized(to_player) * movement.max_speed
            movement.velocity = movement.velocity.lerp(desired, max(0.0, min(1.0, 0.03 * 60.0 * dt)))
            movement.input_direction = normalized(movement.velocity)
            movement.max_speed = max(1.0, movement.velocity.length())

            interval = max(0.42, 0.85 - (boss.variant * 0.06))
            if boss.shot_timer >= interval:
                boss.shot_timer = 0.0
                spread = 8.0 + min(14.0, boss.variant * 2.0)
                shot_count = 3 if boss.variant < 3 else 5
                offsets = (
                    (-spread, 0.0, spread)
                    if shot_count == 3
                    else (-spread * 1.6, -spread * 0.7, 0.0, spread * 0.7, spread * 1.6)
                )
                speed = 310.0 + min(85.0, boss.variant * 20.0)
                for offset in offsets:
                    world.spawn_enemy_bullet(
                        transform.position,
                        normalized(to_player).rotate(offset),
                        speed,
                        8.0,
                        color=ENEMY_BOSS_STANDARD_BULLET_COLOR,
                    )

            if boss.ability_timer > 3.0:
                boss.state = "invoking"
                boss.ability_timer = 0.0
            return

        if boss.state == "invoking":
            movement.velocity *= 0.9
            movement.input_direction = normalized(movement.velocity)
            if boss.ability_timer <= 1.0:
                return

            self._spawn_boss_portals(world, transform.position, boss.variant)
            boss.state = "dash"
            boss.ability_timer = 0.0
            return

        if boss.ability_timer < 0.6:
            movement.velocity *= 0.8
            movement.input_direction = normalized(movement.velocity)
            return

        if boss.ability_timer < 1.2:
            if boss.ability_timer - dt < 0.6:
                movement.velocity = normalized(to_player) * max(350.0, movement.max_speed * 5.0)
            movement.input_direction = normalized(movement.velocity)
            movement.max_speed = max(1.0, movement.velocity.length())
            return

        boss.state = "pursuing"
        boss.ability_timer = 0.0

    def _update_artillery_boss(
        self,
        world: "GameWorld",
        dt: float,
        boss: BossComponent,
        transform: TransformComponent,
        movement: MovementComponent,
        player_transform: TransformComponent,
    ) -> None:
        boss.ability_timer += dt
        boss.shot_timer += dt

        to_player = player_transform.position - transform.position
        strafe = normalized(to_player).rotate(90.0) * (movement.max_speed * 0.8)
        movement.velocity = movement.velocity.lerp(strafe, max(0.0, min(1.0, 0.04 * 60.0 * dt)))
        movement.input_direction = normalized(movement.velocity)
        movement.max_speed = max(1.0, movement.velocity.length())

        interval = max(0.9, 1.35 - (boss.variant * 0.06))
        if boss.shot_timer >= interval:
            boss.shot_timer = 0.0
            steps = 10 + min(6, boss.variant)
            speed = 300.0 + min(80.0, boss.variant * 18.0)
            step_degrees = max(18, 360 // steps)
            for angle in range(0, 360, step_degrees):
                direction = Vector2(1, 0).rotate(angle + boss.ability_timer * 40.0)
                world.spawn_enemy_bullet(
                    transform.position,
                    direction,
                    speed=speed,
                    radius=8.0,
                    color=ENEMY_BOSS_ARTILLERY_BULLET_COLOR,
                )

        if boss.ability_timer >= 4.3:
            boss.ability_timer = 0.0
            kind = random.choice(("miniboss_cacador", "miniboss_sniper"))
            world.add_entity(PortalFactory.create_enemy_spawn_portal(Vector2(transform.position), kind, delay=0.85))

    def _update_chaotic_boss(
        self,
        world: "GameWorld",
        dt: float,
        boss: BossComponent,
        transform: TransformComponent,
        movement: MovementComponent,
        player_transform: TransformComponent,
    ) -> None:
        boss.ability_timer += dt
        boss.shot_timer += dt

        to_player = player_transform.position - transform.position
        desired = normalized(to_player) * (movement.max_speed * 1.1)
        movement.velocity = movement.velocity.lerp(desired, max(0.0, min(1.0, 0.06 * 60.0 * dt)))
        movement.input_direction = normalized(movement.velocity)
        movement.max_speed = max(1.0, movement.velocity.length())

        interval = max(0.34, 0.62 - (boss.variant * 0.03))
        if boss.shot_timer >= interval:
            boss.shot_timer = 0.0
            base = normalized(to_player)
            speed = 320.0 + min(90.0, boss.variant * 18.0)
            for offset in (-24.0, -10.0, 0.0, 10.0, 24.0):
                world.spawn_enemy_bullet(
                    transform.position,
                    base.rotate(offset),
                    speed=speed,
                    radius=7.0,
                    color=ENEMY_BOSS_CHAOTIC_BULLET_COLOR,
                )

        if boss.ability_timer >= 3.2:
            boss.ability_timer = 0.0
            movement.velocity = normalized(to_player) * max(320.0, movement.max_speed * 4.6)
            movement.input_direction = normalized(movement.velocity)
            movement.max_speed = max(1.0, movement.velocity.length())

    def _spawn_boss_portals(self, world: "GameWorld", position: Vector2, variant: int) -> None:
        if variant % 3 == 1:
            kinds = ("explosivo", "follower")
        elif variant % 3 == 2:
            kinds = ("investida", "metralhadora")
        else:
            kinds = ("quique", "quique")

        for kind in kinds:
            world.add_entity(PortalFactory.create_enemy_spawn_portal(Vector2(position), kind, delay=0.8))

        if variant % 3 == 0 and variant >= 2:
            world.add_entity(
                PortalFactory.create_enemy_spawn_portal(Vector2(position), "miniboss_espiral", delay=1.0)
            )


from game.core.world import GameWorld
