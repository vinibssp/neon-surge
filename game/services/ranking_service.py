from __future__ import annotations

import json
import os
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
        self.local_data = self._load_local_data()

    def _load_local_data(self) -> dict:
        if os.path.exists(self.profile_path):
            try:
                with open(self.profile_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
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
        self.local_data["player_name"] = name
        self._save_local_data()

    def save_local_score(self, player_name: str, mode: str, score: float) -> None:
        scores_dict = self.local_data.setdefault("scores", {})
        mode_scores = scores_dict.setdefault(mode, [])
        mode_scores.append({"player_name": player_name, "score": float(score)})
        mode_scores.sort(key=lambda x: x.get("score", 0), reverse=True)
        scores_dict[mode] = mode_scores[:10]
        self._save_local_data()

    def get_local_top_10(self, mode: str) -> list[dict[str, Any]]:
        scores = self.local_data.get("scores", {}).get(mode, [])
        return list(scores[:10])

    def enviar_e_buscar_global(
        self,
        player_name: str,
        mode: str,
        score: float,
        callback: Callable[[list[dict[str, Any]]], None],
    ) -> None:
        def _run() -> None:
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
                with urllib.request.urlopen(post_request):
                    pass

                mode_encoded = urllib.parse.quote(mode)
                get_url = f"{SUPABASE_URL}?select=*&mode=eq.{mode_encoded}&order=score.desc&limit=10"
                get_request = urllib.request.Request(get_url, headers=self.headers, method="GET")
                with urllib.request.urlopen(get_request) as response:
                    data = json.loads(response.read().decode("utf-8"))
                    callback(data)
            except Exception as e:
                print(f"[RankingService] Erro no envio/busca global: {e}")
                callback([])

        threading.Thread(target=_run, daemon=True).start()

    def save_score(self, score: float, mode: str) -> None:
        player_name = self.get_player_name() or "Desconhecido"
        self.save_local_score(player_name=player_name, mode=mode, score=score)
        self.enviar_e_buscar_global(
            player_name=player_name,
            mode=mode,
            score=score,
            callback=lambda _data: None,
        )

    def fetch_global_ranking(self, limit: int, mode: str, callback: Callable[[list[dict[str, Any]]], None]) -> None:
        def _run() -> None:
            try:
                mode_encoded = urllib.parse.quote(mode)
                url = f"{SUPABASE_URL}?select=*&mode=eq.{mode_encoded}&order=score.desc&limit={limit}"
                req = urllib.request.Request(url, headers=self.headers, method="GET")
                with urllib.request.urlopen(req) as response:
                    data = json.loads(response.read().decode("utf-8"))
                    callback(data)
            except Exception as e:
                print(f"[RankingService] Erro ao buscar ranking: {e}")
                callback([])

        threading.Thread(target=_run, daemon=True).start()

    def get_local_ranking(self, mode: str, limit: int = 10) -> list[dict[str, Any]]:
        return self.get_local_top_10(mode)[:limit]
