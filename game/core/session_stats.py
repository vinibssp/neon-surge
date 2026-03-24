from __future__ import annotations

from dataclasses import dataclass, field

from game.core.events import (
    BulletExpired,
    CollectibleCollected,
    DashStarted,
    EnemySpawned,
    LifetimeExpired,
    SpawnPortalDestroyed,
)


@dataclass
class GameSessionStats:
    enemy_spawned_total: int = 0
    enemy_spawned_by_kind: dict[str, int] = field(default_factory=dict)
    collectible_collected_total: int = 0
    spawn_portal_destroyed_total: int = 0
    dash_started_total: int = 0
    bullet_expired_total: int = 0
    lifetime_expired_total: int = 0

    def reset(self) -> None:
        self.enemy_spawned_total = 0
        self.enemy_spawned_by_kind.clear()
        self.collectible_collected_total = 0
        self.spawn_portal_destroyed_total = 0
        self.dash_started_total = 0
        self.bullet_expired_total = 0
        self.lifetime_expired_total = 0


class StatsCollector:
    def __init__(self, stats: GameSessionStats | None = None) -> None:
        self.stats = GameSessionStats() if stats is None else stats

    def on_enemy_spawned(self, event: EnemySpawned) -> None:
        self.stats.enemy_spawned_total += 1
        current_count = self.stats.enemy_spawned_by_kind.get(event.enemy_kind, 0)
        self.stats.enemy_spawned_by_kind[event.enemy_kind] = current_count + 1

    def on_collectible_collected(self, event: CollectibleCollected) -> None:
        self.stats.collectible_collected_total += event.value

    def on_spawn_portal_destroyed(self, event: SpawnPortalDestroyed) -> None:
        del event
        self.stats.spawn_portal_destroyed_total += 1

    def on_dash_started(self, event: DashStarted) -> None:
        del event
        self.stats.dash_started_total += 1

    def on_bullet_expired(self, event: BulletExpired) -> None:
        del event
        self.stats.bullet_expired_total += 1

    def on_lifetime_expired(self, event: LifetimeExpired) -> None:
        del event
        self.stats.lifetime_expired_total += 1
