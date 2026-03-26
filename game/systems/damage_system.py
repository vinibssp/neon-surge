from __future__ import annotations

from game.components.data_components import (
    BulletComponent,
    CollisionComponent,
    DamageComponent,
    DormantComponent,
    HealthComponent,
    TransformComponent,
)
from game.core.world import GameWorld
from game.ecs.query import WorldQuery


PLAYER_BULLET_QUERY = WorldQuery(
    component_types=(BulletComponent, TransformComponent, CollisionComponent, DamageComponent),
    tags=("bullet",),
)
ENEMY_HEALTH_QUERY = WorldQuery(
    component_types=(TransformComponent, CollisionComponent, HealthComponent),
    tags=("enemy",),
)


class DamageSystem:
    def __init__(self, world: GameWorld) -> None:
        self.world = world

    def update(self, dt: float) -> None:
        del dt
        bullets = self.world.query(PLAYER_BULLET_QUERY)
        enemies = self.world.query(ENEMY_HEALTH_QUERY)
        if not bullets or not enemies:
            return

        for bullet_entity in bullets:
            bullet = bullet_entity.get_component(BulletComponent)
            bullet_transform = bullet_entity.get_component(TransformComponent)
            bullet_collision = bullet_entity.get_component(CollisionComponent)
            damage = bullet_entity.get_component(DamageComponent)
            if bullet is None or bullet_transform is None or bullet_collision is None or damage is None:
                continue
            if bullet.owner_tag != "player":
                continue

            bullet_radius = bullet_collision.radius
            bullet_position = bullet_transform.position

            hit_enemy = None
            for enemy in enemies:
                if enemy is bullet_entity:
                    continue
                dormant = enemy.get_component(DormantComponent)
                if dormant is not None and not dormant.active:
                    continue

                enemy_transform = enemy.get_component(TransformComponent)
                enemy_collision = enemy.get_component(CollisionComponent)
                enemy_health = enemy.get_component(HealthComponent)
                if enemy_transform is None or enemy_collision is None or enemy_health is None:
                    continue

                if not self._collides(
                    bullet_position,
                    bullet_radius,
                    enemy_transform.position,
                    enemy_collision.radius,
                ):
                    continue

                enemy_health.current = max(0.0, enemy_health.current - damage.amount)
                hit_enemy = enemy
                if enemy_health.current <= 0.0:
                    self.world.remove_entity(enemy)
                break

            if hit_enemy is not None:
                self.world.remove_entity(bullet_entity)

    @staticmethod
    def _collides(a_pos, a_radius: float, b_pos, b_radius: float) -> bool:
        distance_sq = (a_pos - b_pos).length_squared()
        radius_sum = a_radius + b_radius
        return distance_sq <= radius_sum * radius_sum
