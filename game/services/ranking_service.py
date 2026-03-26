from __future__ import annotations

import json
import os
import time
import threading
import urllib.parse
import urllib.request
from typing import Any, Callable

SUPABASE_URL = "https://irwyyqgxahlmoncfpacg.supabase.co/rest/v1/rankings"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imlyd3l5cWd4YWhsbW9uY2ZwYWNnIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzQyNzUwMDMsImV4cCI6MjA4OTg1MTAwM30.Lum4HXhLBMn4GmtAjbKAh-7pnjI6YYNoI41g0fZkxUg"


class RankingService:
    def __init__(self) -> None:
        self.headers = {
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}",
            "Content-Type": "application/json",
            "Prefer": "return=minimal",
        }
        self.profile_path = "player_profile.json"
        self._lock = threading.Lock()
        self.local_data = self._load_local_data()

    def _load_local_data(self) -> dict:
        if os.path.exists(self.profile_path):
            try:
                with open(self.profile_path, "r", encoding="utf-8") as f:
                    loaded = json.load(f)
                    if not isinstance(loaded, dict):
                        return self._empty_data()
                    player_name = loaded.get("player_name")
                    if player_name is not None and not isinstance(player_name, str):
                        return self._empty_data()
                    scores = loaded.get("scores")
                    if not isinstance(scores, dict):
                        return self._empty_data()
                    normalized_scores: dict[str, list[dict[str, Any]]] = {}
                    for mode, entries in scores.items():
                        if not isinstance(mode, str) or not isinstance(entries, list):
                            continue
                        normalized_entries: list[dict[str, Any]] = []
                        for entry in entries:
                            if not isinstance(entry, dict):
                                continue
                            entry_player = str(entry.get("player_name", "Desconhecido"))
                            entry_score = float(entry.get("score", 0.0))
                            entry_id = str(entry.get("id", f"{mode}-{time.time_ns()}"))
                            normalized_entries.append(
                                {
                                    "id": entry_id,
                                    "player_name": entry_player,
                                    "score": entry_score,
                                    "synced": bool(entry.get("synced", False)),
                                    "sync_attempts": max(0, int(entry.get("sync_attempts", 0))),
                                    "created_at": float(entry.get("created_at", time.time())),
                                }
                            )
                        normalized_entries.sort(key=lambda item: item.get("score", 0.0), reverse=True)
                        normalized_scores[mode] = normalized_entries[:30]
                    return {"player_name": player_name, "scores": normalized_scores}
            except Exception:
                pass
        return self._empty_data()

    @staticmethod
    def _empty_data() -> dict[str, Any]:
        return {"player_name": None, "scores": {}}

    def _save_local_data(self) -> None:
        try:
            with open(self.profile_path, "w", encoding="utf-8") as f:
                json.dump(self.local_data, f, indent=4)
        except Exception as e:
            print(f"[RankingService] Erro ao salvar dados locais: {e}")

    def get_player_name(self) -> str | None:
        return self.local_data.get("player_name")

    def set_player_name(self, name: str) -> None:
        with self._lock:
            self.local_data["player_name"] = name
            self._save_local_data()

    def save_local_score(self, player_name: str, mode: str, score: float, synced: bool = False) -> str:
        with self._lock:
            scores_dict = self.local_data.setdefault("scores", {})
            mode_scores = scores_dict.setdefault(mode, [])
            entry_id = f"{mode}-{time.time_ns()}"
            mode_scores.append(
                {
                    "id": entry_id,
                    "player_name": player_name,
                    "score": float(score),
                    "synced": synced,
                    "sync_attempts": 0,
                    "created_at": time.time(),
                }
            )
            mode_scores.sort(key=lambda x: x.get("score", 0.0), reverse=True)
            scores_dict[mode] = mode_scores[:30]
            self._save_local_data()
            return entry_id

    def get_local_top_10(self, mode: str) -> list[dict[str, Any]]:
        with self._lock:
            scores = self.local_data.get("scores", {}).get(mode, [])
            return list(scores[:10])

    def get_pending_entries(self) -> list[dict[str, Any]]:
        with self._lock:
            pending: list[dict[str, Any]] = []
            scores = self.local_data.get("scores", {})
            if not isinstance(scores, dict):
                return pending
            for mode, entries in scores.items():
                if not isinstance(mode, str) or not isinstance(entries, list):
                    continue
                for entry in entries:
                    if not isinstance(entry, dict):
                        continue
                    if bool(entry.get("synced", False)):
                        continue
                    pending.append(
                        {
                            "id": str(entry.get("id", "")),
                            "mode": mode,
                            "player_name": str(entry.get("player_name", "Desconhecido")),
                            "score": float(entry.get("score", 0.0)),
                            "sync_attempts": int(entry.get("sync_attempts", 0)),
                        }
                    )
            return pending

    def _mark_synced(self, mode: str, entry_id: str) -> None:
        with self._lock:
            entries = self.local_data.get("scores", {}).get(mode, [])
            if not isinstance(entries, list):
                return
            for entry in entries:
                if not isinstance(entry, dict):
                    continue
                if str(entry.get("id", "")) != entry_id:
                    continue
                entry["synced"] = True
                self._save_local_data()
                return

    def _increment_attempt(self, mode: str, entry_id: str) -> None:
        with self._lock:
            entries = self.local_data.get("scores", {}).get(mode, [])
            if not isinstance(entries, list):
                return
            for entry in entries:
                if not isinstance(entry, dict):
                    continue
                if str(entry.get("id", "")) != entry_id:
                    continue
                entry["sync_attempts"] = max(0, int(entry.get("sync_attempts", 0))) + 1
                self._save_local_data()
                return

    def submit_global_score(self, player_name: str, mode: str, score: float, timeout: float = 3.0) -> bool:
        try:
            payload = json.dumps(
                {
                    "player_name": player_name,
                    "score": float(score),
                    "mode": mode,
                }
            ).encode("utf-8")
            post_request = urllib.request.Request(
                SUPABASE_URL,
                data=payload,
                headers=self.headers,
                method="POST",
            )
            with urllib.request.urlopen(post_request, timeout=timeout):
                return True
        except Exception as e:
            print(f"[RankingService] Erro no envio global: {e}")
            return False

    def sync_pending_scores(
        self,
        max_attempts: int = 3,
        backoff_seconds: tuple[float, ...] = (0.5, 1.0, 2.0),
        timeout: float = 3.0,
    ) -> int:
        pending_entries = self.get_pending_entries()
        synced_count = 0
        for entry in pending_entries:
            mode = str(entry.get("mode", ""))
            entry_id = str(entry.get("id", ""))
            player_name = str(entry.get("player_name", "Desconhecido"))
            score = float(entry.get("score", 0.0))
            success = False
            for attempt_index in range(max_attempts):
                if self.submit_global_score(player_name=player_name, mode=mode, score=score, timeout=timeout):
                    success = True
                    break
                self._increment_attempt(mode=mode, entry_id=entry_id)
                if attempt_index < len(backoff_seconds):
                    time.sleep(backoff_seconds[attempt_index])
            if success:
                self._mark_synced(mode=mode, entry_id=entry_id)
                synced_count += 1
        return synced_count

    def save_score(self, score: float, mode: str) -> None:
        player_name = self.get_player_name() or "Desconhecido"
        self.save_local_score(player_name=player_name, mode=mode, score=score, synced=False)
        self.sync_pending_scores()

    def fetch_global_ranking_sync(self, limit: int, mode: str, timeout: float = 3.0) -> list[dict[str, Any]]:
        try:
            mode_encoded = urllib.parse.quote(mode)
            url = f"{SUPABASE_URL}?select=*&mode=eq.{mode_encoded}&order=score.desc&limit={limit}"
            req = urllib.request.Request(url, headers=self.headers, method="GET")
            with urllib.request.urlopen(req, timeout=timeout) as response:
                data = json.loads(response.read().decode("utf-8"))
                if isinstance(data, list):
                    return data
                return []
        except Exception as e:
            print(f"[RankingService] Erro ao buscar ranking: {e}")
            return []

    def fetch_global_ranking(self, limit: int, mode: str, callback: Callable[[list[dict[str, Any]]], None]) -> None:
        def _run() -> None:
            callback(self.fetch_global_ranking_sync(limit=limit, mode=mode))

        threading.Thread(target=_run, daemon=True).start()

    def get_local_ranking(self, mode: str, limit: int = 10) -> list[dict[str, Any]]:
        return self.get_local_top_10(mode)[:limit]
