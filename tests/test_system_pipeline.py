from __future__ import annotations

import unittest

from game.systems.system_pipeline import PipelinePhase, SystemPipeline, SystemSpec


class _RecorderSystem:
    def __init__(self, name: str, calls: list[str]) -> None:
        self.name = name
        self.calls = calls

    def update(self, dt: float) -> None:
        self.calls.append(self.name)


class SystemPipelineTest(unittest.TestCase):
    def test_pipeline_runs_in_phase_then_priority_order(self) -> None:
        calls: list[str] = []
        systems = [
            SystemSpec(_RecorderSystem("sim_high", calls), phase=PipelinePhase.SIMULATION, priority=10),
            SystemSpec(_RecorderSystem("post", calls), phase=PipelinePhase.POST_UPDATE, priority=0),
            SystemSpec(_RecorderSystem("pre", calls), phase=PipelinePhase.PRE_UPDATE, priority=0),
            SystemSpec(_RecorderSystem("sim_low", calls), phase=PipelinePhase.SIMULATION, priority=1),
        ]

        pipeline = SystemPipeline(systems)
        pipeline.update(1.0 / 60.0)

        self.assertEqual(calls, ["pre", "sim_low", "sim_high", "post"])

    def test_add_system_defaults_to_simulation_phase(self) -> None:
        calls: list[str] = []
        pipeline = SystemPipeline([])
        pipeline.add_system(_RecorderSystem("sim", calls))
        pipeline.update(0.016)

        self.assertEqual(calls, ["sim"])


if __name__ == "__main__":
    unittest.main()
