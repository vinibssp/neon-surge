from __future__ import annotations

from typing import cast
from typing import TypeVar

from game.ecs.component import Component

ComponentType = TypeVar("ComponentType", bound=Component)


class Entity:
    _next_id = 1

    def __init__(self) -> None:
        self.id = Entity._next_id
        Entity._next_id += 1
        self.components: dict[type[Component], Component] = {}
        self.tags: set[str] = set()
        self.active = True

    def add_component(self, component: Component) -> None:
        self.components[type(component)] = component

    def get_component(self, component_type: type[ComponentType]) -> ComponentType | None:
        component = self.components.get(component_type)
        return cast(ComponentType | None, component)

    def has_component(self, component_type: type[Component]) -> bool:
        return component_type in self.components

    def add_tag(self, tag: str) -> None:
        self.tags.add(tag)

    def has_tag(self, tag: str) -> bool:
        return tag in self.tags
