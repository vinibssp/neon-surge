from __future__ import annotations

import threading
from dataclasses import dataclass
from typing import Any

from game.services.ranking_service import RankingService


@dataclass(frozen=True)
class RankingSyncSnapshot:
    status: str
    local_entries: list[dict[str, Any]]
    global_entries: list[dict[str, Any]]
    synced_now: int


class RankingSyncHandle:
    def __init__(self, snapshot: RankingSyncSnapshot) -> None:
        self._lock = threading.Lock()
        self._snapshot = snapshot

    def set_snapshot(self, snapshot: RankingSyncSnapshot) -> None:
        with self._lock:
            self._snapshot = snapshot

    def get_snapshot(self) -> RankingSyncSnapshot:
        with self._lock:
            return RankingSyncSnapshot(
                status=self._snapshot.status,
                local_entries=list(self._snapshot.local_entries),
                global_entries=list(self._snapshot.global_entries),
                synced_now=self._snapshot.synced_now,
            )


class RankingOrchestrator:
    def __init__(self, service: RankingService | None = None) -> None:
        self._service = RankingService() if service is None else service

    def start(self, mode: str, score: float, limit: int = 10) -> RankingSyncHandle:
        player_name = self._service.get_player_name() or "Desconhecido"
        self._service.save_local_score(player_name=player_name, mode=mode, score=score, synced=False)
        initial_local = self._service.get_local_top_10(mode)
        handle = RankingSyncHandle(
            RankingSyncSnapshot(
                status="syncing_global",
                local_entries=initial_local,
                global_entries=[],
                synced_now=0,
            )
        )

        def _run() -> None:
            synced_now = self._service.sync_pending_scores()
            local_after_sync = self._service.get_local_top_10(mode)
            global_entries: list[dict[str, Any]] = []
            status = "degraded"
            if not self._service.get_pending_entries():
                global_entries = self._service.fetch_global_ranking_sync(limit=limit, mode=mode)
                status = "done" if global_entries else "degraded"
            handle.set_snapshot(
                RankingSyncSnapshot(
                    status=status,
                    local_entries=local_after_sync,
                    global_entries=global_entries,
                    synced_now=synced_now,
                )
            )

        threading.Thread(target=_run, daemon=True).start()
        return handle
