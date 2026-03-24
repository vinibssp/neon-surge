from __future__ import annotations

from typing import Protocol


class UpdatableSystem(Protocol):
    def update(self, dt: float) -> None:
        ...
