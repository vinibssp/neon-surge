from __future__ import annotations

from pygame import Vector2

from game.components.data_components import PlayerShootComponent, TransformComponent
from game.core.world import GameWorld
from game.factories.bullet_factory import BulletFactory


class PlayerShootSystem:
    def __init__(self, world: GameWorld) -> None:
        self.world = world

    def update(self, dt: float) -> None:
        player = self.world.player
        if player is None:
            return

        shoot = player.get_component(PlayerShootComponent)
        transform = player.get_component(TransformComponent)
        if shoot is None or transform is None:
            return

        shoot.cooldown_left = max(0.0, shoot.cooldown_left - dt)
        if not shoot.requested:
            return

        shoot.requested = False
        if shoot.cooldown_left > 0.0:
            return

        direction = Vector2(shoot.aim_direction)
        if direction.length_squared() <= 0.0001:
            return

        bullet = BulletFactory.create_player_bullet(
            origin=transform.position,
            direction=direction,
            speed=shoot.bullet_speed,
            radius=shoot.bullet_radius,
            damage=shoot.bullet_damage,
            color=shoot.bullet_color,
        )
        self.world.add_entity(bullet)
        shoot.cooldown_left = shoot.cooldown
