from __future__ import annotations

from game.components.data_components import (
    CollectibleComponent,
    BulletComponent,
    CollisionComponent,
    DashOnlyDefeatComponent,
    DashComponent,
    GhostComponent,
    InvulnerabilityComponent,
    NuclearBombComponent,
    ParryComponent,
    MovementComponent,
    MortarShellComponent,
    PortalComponent,
    PortalSpawnComponent,
    StaggeredComponent,
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
from game.core.enemy_names import enemy_kind_from_entity, format_enemy_name
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
        player_parry = player.get_component(ParryComponent)
        is_player_parrying = player_parry is not None and player_parry.active_time_left > 0

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
                bomb = player.get_component(NuclearBombComponent)
                if bomb is not None:
                    bomb.collectibles_progress += value
                    while bomb.collectibles_progress >= bomb.charge_threshold:
                        bomb.collectibles_progress -= bomb.charge_threshold
                        bomb.charges += 1
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
                if entity.has_tag("enemy") and is_player_parrying:
                    stagger_duration = 0.9 if player_parry is None else player_parry.stagger_duration
                    self._apply_stagger(entity, stagger_duration)
                    continue

                if entity.has_tag("enemy") and self._is_enemy_staggered(entity):
                    continue

                if entity.has_tag("bullet") and is_player_parrying:
                    bullet = entity.get_component(BulletComponent)
                    if bullet is not None and bullet.owner_tag == "enemy":
                        stagger_duration = 0.9 if player_parry is None else player_parry.stagger_duration
                        self.world.remove_entity(entity)
                        owner = self._find_entity_by_id(bullet.owner_entity_id)
                        if owner is not None and owner.has_tag("enemy"):
                            self._apply_stagger(owner, stagger_duration)
                        else:
                            parry_radius = 70.0 if player_parry is None else player_parry.radius
                            self._apply_area_stagger(player_transform.position, parry_radius, stagger_duration)
                        continue

                if entity.has_tag("bullet"):
                    bullet = entity.get_component(BulletComponent)
                    if bullet is not None and bullet.owner_tag == "enemy":
                        owner = self._find_entity_by_id(bullet.owner_entity_id)
                        if owner is not None and self._is_enemy_staggered(owner):
                            self.world.remove_entity(entity)
                            continue

                dash_only = entity.get_component(DashOnlyDefeatComponent)
                if dash_only is not None and dash_only.enabled and is_player_dashing:
                    self.world.remove_entity(entity)
                    continue

                ghost = entity.get_component(GhostComponent)
                if ghost is not None and not ghost.is_visible:
                    continue
                if ghost is not None and ghost.is_visible and ghost.timer < ghost.materialize_grace:
                    continue

                if not is_player_invulnerable:
                    if entity.has_tag("bullet"):
                        bullet = entity.get_component(BulletComponent)
                        cause = f"Atingido por {self._resolve_bullet_killer_name(bullet)}"
                    else:
                        cause = f"Derrotado por {format_enemy_name(enemy_kind_from_entity(entity))}"
                    self._kill_player(cause)
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
            bullet = shell_entity.get_component(BulletComponent)
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
                self._kill_player(f"Explosao de {self._resolve_bullet_killer_name(bullet)}")
                return True
        return False

    @staticmethod
    def _collides(a_pos, a_radius: float, b_pos, b_radius: float) -> bool:
        distance_sq = (a_pos - b_pos).length_squared()
        radius_sum = a_radius + b_radius
        return distance_sq <= radius_sum * radius_sum

    def _apply_stagger(self, enemy: Entity, duration: float) -> None:
        stagger = enemy.get_component(StaggeredComponent)
        if stagger is None:
            enemy.add_component(StaggeredComponent(time_left=duration, pulse_time=0.0))
            return
        stagger.time_left = max(stagger.time_left, duration)

    def _apply_area_stagger(self, center, radius: float, duration: float) -> None:
        radius_sq = radius * radius
        for enemy in tuple(self.world.entities):
            if not enemy.has_tag("enemy"):
                continue
            transform = enemy.get_component(TransformComponent)
            if transform is None:
                continue
            if (transform.position - center).length_squared() > radius_sq:
                continue
            self._apply_stagger(enemy, duration)

    def _find_entity_by_id(self, entity_id: int | None) -> Entity | None:
        if entity_id is None:
            return None
        for entity in self.world.entities:
            if entity.id == entity_id:
                return entity
        for entity in self.world.pending_add:
            if entity.id == entity_id:
                return entity
        return None

    def _resolve_bullet_killer_name(self, bullet: BulletComponent | None) -> str:
        if bullet is None:
            return format_enemy_name(None)
        if bullet.owner_kind is not None:
            return format_enemy_name(bullet.owner_kind)
        owner = self._find_entity_by_id(bullet.owner_entity_id)
        if owner is None:
            return format_enemy_name(None)
        return format_enemy_name(enemy_kind_from_entity(owner))

    @staticmethod
    def _is_enemy_staggered(enemy: Entity) -> bool:
        stagger = enemy.get_component(StaggeredComponent)
        return stagger is not None and stagger.time_left > 0.0

    def _kill_player(self, cause: str) -> None:
        if self.world.runtime_state.get("death_transition"):
            return
        self.world.runtime_state["death_transition"] = True
        self.world.runtime_state["last_death_cause"] = cause
        self.world.event_bus.publish(PlayerDamaged())
        self.world.event_bus.publish(PlayerDied())
