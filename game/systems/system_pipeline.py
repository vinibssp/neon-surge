from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Protocol


class UpdatableSystem(Protocol):
    def update(self, dt: float) -> None:
        ...


class PipelinePhase(str, Enum):
    PRE_UPDATE = "pre_update"
    SIMULATION = "simulation"
    POST_UPDATE = "post_update"


@dataclass(frozen=True)
class SystemSpec:
    system: UpdatableSystem
    phase: PipelinePhase = PipelinePhase.SIMULATION
    priority: int = 0


class SystemPipeline:
    def __init__(self, systems: list[UpdatableSystem | SystemSpec]) -> None:
        self._specs: list[SystemSpec] = []
        self._phase_buckets: dict[PipelinePhase, list[SystemSpec]] = {
            PipelinePhase.PRE_UPDATE: [],
            PipelinePhase.SIMULATION: [],
            PipelinePhase.POST_UPDATE: [],
        }
        for item in systems:
            if isinstance(item, SystemSpec):
                self.add_system(item.system, phase=item.phase, priority=item.priority)
                continue
            self.add_system(item)

    def add_system(
        self,
        system: UpdatableSystem,
        phase: PipelinePhase = PipelinePhase.SIMULATION,
        priority: int = 0,
    ) -> None:
        spec = SystemSpec(system=system, phase=phase, priority=priority)
        self._specs.append(spec)
        bucket = self._phase_buckets[phase]
        bucket.append(spec)
        bucket.sort(key=lambda item: item.priority)

    def update(self, dt: float) -> None:
        for phase in (PipelinePhase.PRE_UPDATE, PipelinePhase.SIMULATION, PipelinePhase.POST_UPDATE):
            for spec in self._phase_buckets[phase]:
                spec.system.update(dt)
