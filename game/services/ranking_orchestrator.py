from __future__ import annotations

import threading
from dataclasses import dataclass
from typing import Any

from game.services.ranking_service import RankingService
from game.services.supabase_service import SupabaseService
from game.core.session_stats import GameSessionStats


@dataclass(frozen=True)
class RankingSyncSnapshot:
    status: str
    local_entries: list[dict[str, Any]]
    global_entries: list[dict[str, Any]]
    synced_now: int
    local_position: int | None
    global_position: int | None


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
                local_position=self._snapshot.local_position,
                global_position=self._snapshot.global_position,
            )


class RankingOrchestrator:
    def __init__(self, service: RankingService | None = None) -> None:
        self._service = RankingService() if service is None else service

    def _validate_run(self, score: float, stats: GameSessionStats | None, duration: float) -> bool:
        if score > 0 and duration < 1.0:
            return False
            
        if score > 0 and stats is not None:
            if stats.enemy_spawned_total == 0:
                return False
            
            # Anti-Cheat: Max score per enemy (heuristic)
            if score > stats.enemy_spawned_total * 5000:
                return False
                
        return True

    def start(self, mode: str, score: float, limit: int = 10, stats: GameSessionStats | None = None, duration: float = 0.0) -> RankingSyncHandle:
        if not self._validate_run(score, stats, duration):
            print(f"[Anti-Cheat] Submissão rejeitada ou tentativa de cheat detectada: score={score}, duration={duration}, enemies={stats.enemy_spawned_total if stats else 0}")
            return RankingSyncHandle(
                RankingSyncSnapshot(
                    status="rejected",
                    local_entries=[],
                    global_entries=[],
                    synced_now=0,
                    local_position=None,
                    global_position=None,
                )
            )

        player_name = self._service.get_player_name() or "Desconhecido"
        
        # Gerar o hash local
        signature = self._service.generate_signature(player_name, score, mode)
        
        entry_id = self._service.save_local_score(player_name=player_name, mode=mode, score=score, synced=False)
        initial_local = self._service.get_local_top_10(mode)
        initial_local_position = self._service.get_local_position(mode=mode, entry_id=entry_id)
        handle = RankingSyncHandle(
            RankingSyncSnapshot(
                status="syncing_global",
                local_entries=initial_local,
                global_entries=[],
                synced_now=0,
                local_position=initial_local_position,
                global_position=None,
            )
        )

        def _run() -> None:
            # Tenta enviar o score atual
            success = SupabaseService().submit_score(
                player_name=player_name,
                score=score,
                mode=mode,
                signature=signature
            )
            
            synced_now = 0
            if success:
                self._service._mark_synced(mode, entry_id)
                synced_now = 1
            else:
                self._service._increment_attempt(mode, entry_id)
                
            # Sincroniza outros que estejam pendentes
            synced_now += self._service.sync_pending_scores()

            local_after_sync = self._service.get_local_top_10(mode)
            local_position = self._service.get_local_position(mode=mode, entry_id=entry_id)
            global_entries: list[dict[str, Any]] = []
            global_position: int | None = None
            status = "degraded"
            
            if not self._service.get_pending_entries():
                global_position = self._service.get_global_position_sync(mode=mode, score=score)
                global_entries = self._service.fetch_global_ranking_sync(limit=limit, mode=mode)
                status = "done" if global_entries else "degraded"
                
            handle.set_snapshot(
                RankingSyncSnapshot(
                    status=status,
                    local_entries=local_after_sync,
                    global_entries=global_entries,
                    synced_now=synced_now,
                    local_position=local_position,
                    global_position=global_position,
                )
            )

        threading.Thread(target=_run, daemon=True).start()
        return handle
