from __future__ import annotations

import unittest

from game.core.events import DomainEvent, EventBus, PlayerDied


class _CustomEvent(DomainEvent):
    def __init__(self, value: int) -> None:
        self.value = value


class EventBusTest(unittest.TestCase):
    def test_publish_dispatches_to_concrete_and_base_handlers(self) -> None:
        bus = EventBus()
        called: list[str] = []

        bus.on(PlayerDied, lambda event: called.append(type(event).__name__))
        bus.on(DomainEvent, lambda event: called.append("DomainEvent"))

        bus.publish(PlayerDied())

        self.assertEqual(called, ["PlayerDied", "DomainEvent"])

    def test_off_unsubscribes_handler(self) -> None:
        bus = EventBus()
        calls = {"count": 0}

        token = bus.on(PlayerDied, lambda event: calls.__setitem__("count", calls["count"] + 1))
        self.assertTrue(bus.off(token))

        bus.publish(PlayerDied())

        self.assertEqual(calls["count"], 0)
        self.assertFalse(bus.off(token))

    def test_publish_is_resilient_when_handler_raises(self) -> None:
        bus = EventBus()
        called = {"ok": 0}

        def bad_handler(event: _CustomEvent) -> None:
            raise RuntimeError("boom")

        def ok_handler(event: _CustomEvent) -> None:
            called["ok"] += 1

        bus.on(_CustomEvent, bad_handler)
        bus.on(_CustomEvent, ok_handler)

        bus.publish(_CustomEvent(10))

        self.assertEqual(called["ok"], 1)


if __name__ == "__main__":
    unittest.main()
