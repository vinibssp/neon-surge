from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, TypeVar, cast


class DomainEvent:
    pass


EventType = TypeVar("EventType", bound="DomainEvent")
EventHandler = Callable[[DomainEvent], None]


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
class BulletExpired(DomainEvent):
    owner_tag: str


@dataclass(frozen=True)
class LifetimeExpired(DomainEvent):
    entity_id: int
    tags: tuple[str, ...]


class EventBus:
    def __init__(self) -> None:
        self._queue: list[DomainEvent] = []

    def publish(self, event: DomainEvent) -> None:
        self._queue.append(event)

    def drain(self) -> list[DomainEvent]:
        events = self._queue.copy()
        self._queue.clear()
        return events


class DomainEventDispatcher:
    def __init__(self) -> None:
        self._handlers: dict[type[DomainEvent], list[EventHandler]] = {}

    def on(self, event_type: type[EventType], handler: Callable[[EventType], None]) -> None:
        handlers = self._handlers.setdefault(event_type, [])
        handlers.append(cast(EventHandler, handler))

    def dispatch(self, event: DomainEvent) -> None:
        for event_type in self._matching_types(type(event)):
            handlers = self._handlers.get(event_type)
            if handlers is None:
                continue
            for handler in handlers:
                handler(event)

    def dispatch_all(self, events: list[DomainEvent]) -> None:
        for event in events:
            self.dispatch(event)

    def _matching_types(self, event_type: type[DomainEvent]) -> list[type[DomainEvent]]:
        matching_types: list[type[DomainEvent]] = []
        for current_type in event_type.__mro__:
            if not issubclass(current_type, DomainEvent):
                continue
            matching_types.append(cast(type[DomainEvent], current_type))
        return matching_types
