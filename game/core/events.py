from __future__ import annotations

from dataclasses import dataclass
import logging
from typing import Callable, Literal, TypeVar, cast

from pygame import Vector2


class DomainEvent:
    pass


EventType = TypeVar("EventType", bound="DomainEvent")
EventHandler = Callable[[DomainEvent], None]

_logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class PlayerDied(DomainEvent):
    pass


@dataclass(frozen=True)
class PortalEntered(DomainEvent):
    pass


@dataclass(frozen=True)
class EnemySpawned(DomainEvent):
    enemy_kind: str


@dataclass(frozen=True)
class CollectibleCollected(DomainEvent):
    value: int


@dataclass(frozen=True)
class SpawnPortalDestroyed(DomainEvent):
    enemy_kind: str


@dataclass(frozen=True)
class DashStarted(DomainEvent):
    entity_id: int


@dataclass(frozen=True)
class ParryLanded(DomainEvent):
    entity_id: int


@dataclass(frozen=True)
class BulletExpired(DomainEvent):
    owner_tag: str


@dataclass(frozen=True)
class LifetimeExpired(DomainEvent):
    entity_id: int
    tags: tuple[str, ...]


@dataclass(frozen=True)
class UINavigated(DomainEvent):
    index: int


@dataclass(frozen=True)
class UIConfirmed(DomainEvent):
    index: int


@dataclass(frozen=True)
class UICancelled(DomainEvent):
    pass


@dataclass(frozen=True)
class EnemyShotFired(DomainEvent):
    enemy_type: str


@dataclass(frozen=True)
class PlayerDamaged(DomainEvent):
    pass


@dataclass(frozen=True)
class PortalActivated(DomainEvent):
    portal_kind: Literal["enemy_spawn", "level"]


@dataclass(frozen=True)
class ExplosionTriggered(DomainEvent):
    position: Vector2


@dataclass(frozen=True)
class AudioContextChanged(DomainEvent):
    context: Literal["menu", "gameplay", "pause", "game_over"]
    reason: str


@dataclass(frozen=True)
class AudioDuckRequested(DomainEvent):
    reason: str


@dataclass(frozen=True)
class AudioUnduckRequested(DomainEvent):
    reason: str


@dataclass(frozen=True)
class LabyrinthKeyCollected(DomainEvent):
    level: int


@dataclass(frozen=True)
class LabyrinthExitUnlocked(DomainEvent):
    level: int


@dataclass(frozen=True)
class LabyrinthBossCleared(DomainEvent):
    level: int


@dataclass(frozen=True)
class SubscriptionToken:
    event_type: type[DomainEvent]
    handler_id: int


class EventBus:
    def __init__(self) -> None:
        self._handlers: dict[type[DomainEvent], list[tuple[int, EventHandler]]] = {}
        self._next_handler_id = 1

    def on(self, event_type: type[EventType], handler: Callable[[EventType], None]) -> SubscriptionToken:
        handler_id = self._next_handler_id
        self._next_handler_id += 1
        handlers = self._handlers.setdefault(event_type, [])
        handlers.append((handler_id, cast(EventHandler, handler)))
        return SubscriptionToken(event_type=event_type, handler_id=handler_id)

    def off(self, token: SubscriptionToken) -> bool:
        handlers = self._handlers.get(token.event_type)
        if handlers is None:
            return False

        remaining_handlers = [(handler_id, handler) for handler_id, handler in handlers if handler_id != token.handler_id]
        if len(remaining_handlers) == len(handlers):
            return False

        if remaining_handlers:
            self._handlers[token.event_type] = remaining_handlers
            return True

        del self._handlers[token.event_type]
        return True

    def publish(self, event: DomainEvent) -> None:
        self._dispatch_to_subscribers(event)

    def drain(self) -> list[DomainEvent]:
        return []

    def _dispatch_to_subscribers(self, event: DomainEvent) -> None:
        for event_type in self._matching_types(type(event)):
            handlers = self._handlers.get(event_type)
            if handlers is None:
                continue
            for _, handler in list(handlers):
                try:
                    handler(event)
                except Exception:
                    _logger.exception(
                        "Event handler failed for event_type=%s event=%s",
                        event_type.__name__,
                        type(event).__name__,
                    )

    @staticmethod
    def _matching_types(event_type: type[DomainEvent]) -> list[type[DomainEvent]]:
        matching_types: list[type[DomainEvent]] = []
        for current_type in event_type.__mro__:
            if not issubclass(current_type, DomainEvent):
                continue
            matching_types.append(cast(type[DomainEvent], current_type))
        return matching_types
