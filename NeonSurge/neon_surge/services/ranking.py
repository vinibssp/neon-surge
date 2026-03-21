from __future__ import annotations

import json
import os
import time
from typing import Dict, List

from ..constants import MODE_RACE, MODE_RACE_HC, MODE_SURV, MODE_HC


class RankingManager:
    """Persists, sorts and queries the leaderboard JSON file."""

    _KEYS: List[str] = ["Corrida", "Corrida_Hardcore", "Sobrevivencia", "Hardcore"]

    _MODE_TO_KEY: Dict[str, str] = {
        MODE_RACE:    "Corrida",
        MODE_RACE_HC: "Corrida_Hardcore",
        MODE_SURV:    "Sobrevivencia",
        MODE_HC:      "Hardcore",
    }

    def __init__(self, filepath: str) -> None:
        self.filepath  = filepath
        self.data      = self._load()
        self.last_pos  = 0
        self.last_time = 0.0

    # ── persistence ───────────────────────────────────────────────────────────
    def _load(self) -> dict:
        if os.path.exists(self.filepath):
            with open(self.filepath) as f:
                d = json.load(f)
            for k in self._KEYS:
                d.setdefault(k, [])
            return d
        return {k: [] for k in self._KEYS}

    def save(self, mode: str, player_name: str, elapsed: float) -> None:
        key = self._MODE_TO_KEY.get(mode, "Corrida")
        rec = {"nome": player_name, "tempo": round(elapsed, 1), "id": time.time()}
        self.data[key].append(rec)

        asc = "Corrida" in key      # race → lower time wins; survival → higher wins
        self.data[key].sort(key=lambda x: x["tempo"], reverse=not asc)

        self.last_pos  = self.data[key].index(rec) + 1
        self.last_time = rec["tempo"]
        self.data[key] = self.data[key][:50]

        os.makedirs(os.path.dirname(self.filepath) or ".", exist_ok=True)
        with open(self.filepath, "w") as f:
            json.dump(self.data, f, indent=4)

    # ── queries ───────────────────────────────────────────────────────────────
    def top(self, mode: str, n: int = 5) -> list:
        key = self._MODE_TO_KEY.get(mode, "Corrida")
        return self.data.get(key, [])[:n]

    def last_record_id(self, mode: str) -> float:
        key    = self._MODE_TO_KEY.get(mode, "Corrida")
        bucket = self.data.get(key, [])
        if self.last_pos <= len(bucket):
            return bucket[self.last_pos - 1].get("id", -1)
        return -1
