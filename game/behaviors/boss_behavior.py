from __future__ import annotations

import random

from pygame import Vector2

from game.behaviors.advanced_helpers import normalized
from game.behaviors.behavior import Behavior
from game.components.data_components import BossComponent, MovementComponent, TransformComponent
from game.config import (
    ENEMY_BOSS_ARTILLERY_BULLET_COLOR,
    ENEMY_BOSS_CHAOTIC_BULLET_COLOR,
    ENEMY_BOSS_LASER_BULLET_COLOR,
    ENEMY_BOSS_SPECTRAL_BULLET_COLOR,
    ENEMY_BOSS_STANDARD_BULLET_COLOR,
    ENEMY_BOSS_TOXIC_BULLET_COLOR,
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

        if boss.boss_kind == "boss_colosso_laser":
            self._update_laser_colossus(world, dt, boss, transform, movement, player_transform)
            return

        if boss.boss_kind == "boss_druida_toxico":
            self._update_toxic_druid(world, dt, boss, transform, movement, player_transform)
            return

        if boss.boss_kind == "boss_soberano_espectral":
            self._update_spectral_overlord(world, dt, boss, transform, movement, player_transform)
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
                speed = 310.0 + min(85.0, boss.variant * 20.0)
                world.spawn_enemy_bullet(
                    transform.position,
                    normalized(to_player),
                    speed,
                    8.0,
                    color=ENEMY_BOSS_STANDARD_BULLET_COLOR,
                )
                for spread in (-10.0, 10.0):
                    world.spawn_enemy_bullet(
                        transform.position,
                        normalized(to_player).rotate(spread),
                        speed=speed - 30.0,
                        radius=6.0,
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
            forward = normalized(to_player)
            for spread in (-14.0, 0.0, 14.0):
                world.spawn_enemy_bullet(
                    transform.position,
                    forward.rotate(spread),
                    speed=340.0,
                    radius=7.0,
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
            speed = 320.0 + min(90.0, boss.variant * 18.0)
            world.spawn_enemy_bullet(
                transform.position,
                normalized(to_player),
                speed=speed,
                radius=7.0,
                color=ENEMY_BOSS_CHAOTIC_BULLET_COLOR,
            )
            side = normalized(to_player).rotate(90.0)
            world.spawn_enemy_bullet(
                transform.position,
                side,
                speed=speed - 65.0,
                radius=6.0,
                color=ENEMY_BOSS_CHAOTIC_BULLET_COLOR,
            )
            world.spawn_enemy_bullet(
                transform.position,
                -side,
                speed=speed - 65.0,
                radius=6.0,
                color=ENEMY_BOSS_CHAOTIC_BULLET_COLOR,
            )

        if boss.ability_timer >= 3.2:
            boss.ability_timer = 0.0
            movement.velocity = normalized(to_player) * max(320.0, movement.max_speed * 4.6)
            movement.input_direction = normalized(movement.velocity)
            movement.max_speed = max(1.0, movement.velocity.length())

    def _update_laser_colossus(
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
        tangent = normalized(to_player).rotate(90.0)
        movement.velocity = movement.velocity.lerp(tangent * (movement.max_speed * 0.9), 0.08)
        movement.input_direction = normalized(movement.velocity)
        movement.max_speed = max(1.0, movement.velocity.length())

        if boss.shot_timer >= 0.2:
            boss.shot_timer = 0.0
            forward = normalized(to_player)
            side = Vector2(-forward.y, forward.x)
            for offset in (-26.0, -13.0, 0.0, 13.0, 26.0):
                origin = transform.position + side * offset
                world.spawn_enemy_bullet(origin, forward, speed=430.0, radius=6.0, color=ENEMY_BOSS_LASER_BULLET_COLOR)

        if boss.ability_timer < 4.8:
            return
        boss.ability_timer = 0.0
        world.add_entity(
            PortalFactory.create_enemy_spawn_portal(Vector2(transform.position), "miniboss_laser_matrix", delay=0.9)
        )

    def _update_toxic_druid(
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
        desired = normalized(to_player).rotate(45.0 if boss.variant % 2 else -45.0) * (movement.max_speed * 0.88)
        movement.velocity = movement.velocity.lerp(desired, 0.07)
        movement.input_direction = normalized(movement.velocity)
        movement.max_speed = max(1.0, movement.velocity.length())

        if boss.shot_timer >= 1.05:
            boss.shot_timer = 0.0
            for angle in range(0, 360, 30):
                world.spawn_enemy_bullet(
                    transform.position,
                    Vector2(1, 0).rotate(float(angle + boss.ability_timer * 30.0)),
                    speed=245.0,
                    radius=6.0,
                    color=ENEMY_BOSS_TOXIC_BULLET_COLOR,
                )

        if boss.ability_timer < 4.2:
            return
        boss.ability_timer = 0.0
        for kind in ("sapo", "miniboss_alquimista"):
            world.add_entity(PortalFactory.create_enemy_spawn_portal(Vector2(transform.position), kind, delay=0.85))

    def _update_spectral_overlord(
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
        desired = normalized(to_player) * (movement.max_speed * (1.18 if int(boss.ability_timer // 2.0) % 2 else 0.7))
        movement.velocity = movement.velocity.lerp(desired, 0.09)
        movement.input_direction = normalized(movement.velocity)
        movement.max_speed = max(1.0, movement.velocity.length())

        if boss.shot_timer >= 0.48:
            boss.shot_timer = 0.0
            base = normalized(to_player)
            for spread in (-18.0, -9.0, 0.0, 9.0, 18.0):
                world.spawn_enemy_bullet(
                    transform.position,
                    base.rotate(spread),
                    speed=320.0,
                    radius=7.0,
                    color=ENEMY_BOSS_SPECTRAL_BULLET_COLOR,
                )

        if boss.ability_timer < 5.0:
            return
        boss.ability_timer = 0.0
        world.add_entity(
            PortalFactory.create_enemy_spawn_portal(
                Vector2(transform.position),
                random.choice(("fantasma", "miniboss_fantasma_senhor")),
                delay=0.8,
            )
        )

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
