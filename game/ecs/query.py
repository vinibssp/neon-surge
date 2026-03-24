from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Iterable

from game.ecs.component import Component
from game.ecs.entity import Entity

EntityPredicate = Callable[[Entity], bool]


@dataclass(frozen=True)
class WorldQuery:
    component_types: tuple[type[Component], ...] = ()
    tags: tuple[str, ...] = ()
    excluded_tags: tuple[str, ...] = ()
    include_inactive: bool = False
    predicate: EntityPredicate | None = None

    def matches(self, entity: Entity) -> bool:
        if not self.include_inactive and not entity.active:
            return False
        if any(not entity.has_component(component_type) for component_type in self.component_types):
            return False
        if any(not entity.has_tag(tag) for tag in self.tags):
            return False
        if any(entity.has_tag(tag) for tag in self.excluded_tags):
            return False
        if self.predicate is not None and not self.predicate(entity):
            return False
        return True

    def filter(self, entities: Iterable[Entity]) -> list[Entity]:
        return [entity for entity in entities if self.matches(entity)]
