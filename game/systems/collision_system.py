from __future__ import annotations

from game.components.data_components import (
    CollectibleComponent,
    CollisionComponent,
    DashComponent,
    InvulnerabilityComponent,
    MovementComponent,
    MortarShellComponent,
    PortalComponent,
    PortalSpawnComponent,
    TransformComponent,
)
from game.core.events import (
    CollectibleCollected,
    ExplosionTriggered,
    PlayerDamaged,
    PlayerDied,
    PortalEntered,
    SpawnPortalDestroyed,
)
from game.core.world import GameWorld
from game.ecs.entity import Entity
from game.systems.world_queries import COLLIDABLE_QUERY, MORTAR_SHELL_QUERY


class CollisionSystem:
    def __init__(self, world: GameWorld) -> None:
        self.world = world

    def update(self, dt: float) -> None:
        player = self.world.player
        if player is None:
            return

        player_transform = player.get_component(TransformComponent)
        player_collision = player.get_component(CollisionComponent)
        if player_transform is None or player_collision is None:
            return

        player_invulnerability = player.get_component(InvulnerabilityComponent)
        is_player_invulnerable = (
            player_invulnerability is not None and player_invulnerability.time_left > 0
        )
        player_dash = player.get_component(DashComponent)
        is_player_dashing = player_dash is not None and player_dash.active_time_left > 0

        if self._update_mortar_shells(
            dt=dt,
            player_position=player_transform.position,
            player_radius=player_collision.radius,
            is_player_invulnerable=is_player_invulnerable,
        ):
            return

        for entity in self.world.query(COLLIDABLE_QUERY):
            if entity is player:
                continue
            collision = entity.get_component(CollisionComponent)
            transform = entity.get_component(TransformComponent)
            if collision is None or transform is None:
                continue

            if entity.get_component(MortarShellComponent) is not None:
                continue

            if not self._collides(
                player_transform.position,
                player_collision.radius,
                transform.position,
                collision.radius,
            ):
                continue

            if entity.has_tag("collectible"):
                collectible = entity.get_component(CollectibleComponent)
                value = 1 if collectible is None else collectible.value
                self.world.event_bus.publish(CollectibleCollected(value=value))
                self.world.remove_entity(entity)
                continue

            portal_spawn = entity.get_component(PortalSpawnComponent)
            if portal_spawn is not None and is_player_dashing:
                self.world.event_bus.publish(SpawnPortalDestroyed(enemy_kind=portal_spawn.enemy_kind))
                self.world.remove_entity(entity)
                continue

            portal = entity.get_component(PortalComponent)
            if portal is not None and portal.is_level_portal:
                self.world.event_bus.publish(PortalEntered())
                self.world.remove_entity(entity)
                continue

            if entity.has_tag("enemy") or entity.has_tag("bullet"):
                if not is_player_invulnerable:
                    self.world.event_bus.publish(PlayerDamaged())
                    self.world.event_bus.publish(PlayerDied())
                    return

    def _update_mortar_shells(
        self,
        dt: float,
        player_position,
        player_radius: float,
        is_player_invulnerable: bool,
    ) -> bool:
        for shell_entity in self.world.query(MORTAR_SHELL_QUERY):
            shell = shell_entity.get_component(MortarShellComponent)
            shell_transform = shell_entity.get_component(TransformComponent)
            shell_collision = shell_entity.get_component(CollisionComponent)
            if shell is None or shell_transform is None:
                continue

            threshold = shell.arrival_epsilon
            if shell_collision is not None:
                threshold = max(threshold, shell_collision.radius)

            to_target = shell.target_position - shell_transform.position
            reached_target = to_target.length() <= threshold
            if not reached_target:
                movement_component = shell_entity.get_component(MovementComponent)
                if movement_component is not None and movement_component.velocity.length_squared() > 0:
                    projected_distance = movement_component.velocity.length() * dt
                    reached_target = to_target.length() <= projected_distance + threshold

            if not reached_target:
                continue

            self.world.remove_entity(shell_entity)
            self.world.event_bus.publish(ExplosionTriggered(position=shell.target_position))
            if is_player_invulnerable:
                continue
            if self._collides(player_position, player_radius, shell.target_position, shell.explosion_radius):
                self.world.event_bus.publish(PlayerDamaged())
                self.world.event_bus.publish(PlayerDied())
                return True
        return False

    @staticmethod
    def _collides(a_pos, a_radius: float, b_pos, b_radius: float) -> bool:
        distance_sq = (a_pos - b_pos).length_squared()
        radius_sum = a_radius + b_radius
        return distance_sq <= radius_sum * radius_sum
