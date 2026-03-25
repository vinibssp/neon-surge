from __future__ import annotations

from pygame import Vector2

from game.behaviors.advanced_helpers import normalized
from game.behaviors.behavior import Behavior
from game.components.data_components import GhostComponent, MovementComponent, TransformComponent, TurretComponent
from game.ecs.entity import Entity


class PhantomOverlordMinibossBehavior(Behavior):
    def update(self, entity: Entity, world: "GameWorld", dt: float) -> None:
        player = world.player
        if player is None:
            return

        transform = entity.get_component(TransformComponent)
        movement = entity.get_component(MovementComponent)
        ghost = entity.get_component(GhostComponent)
        turret = entity.get_component(TurretComponent)
        player_transform = player.get_component(TransformComponent)
        if transform is None or movement is None or ghost is None or turret is None or player_transform is None:
            return

        ghost.timer += dt
        to_player = player_transform.position - transform.position

        if not ghost.is_visible:
            movement.input_direction = normalized(to_player)
            movement.max_speed = ghost.hidden_speed
            if ghost.timer >= ghost.hidden_duration:
                ghost.is_visible = True
                ghost.timer = 0.0
                turret.shot_timer = 0.0
            return

        movement.input_direction = Vector2()
        movement.velocity.update(0.0, 0.0)
        movement.max_speed = 0.0

        turret.shot_timer += dt
        if turret.shot_timer >= 0.22:
            turret.shot_timer = 0.0
            base = normalized(to_player)
            for spread in (-10.0, 0.0, 10.0):
                world.spawn_enemy_bullet(
                    transform.position,
                    base.rotate(spread),
                    speed=350.0,
                    radius=6.0,
                    color=(206, 220, 255),
                )

        if ghost.timer < ghost.visible_duration:
            return

        ghost.is_visible = False
        ghost.timer = 0.0


from game.core.world import GameWorld
