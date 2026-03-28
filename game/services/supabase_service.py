import json
import urllib.parse
import urllib.request
from typing import Any

from game.services.ranking_service import SUPABASE_URL, SUPABASE_KEY

class SupabaseService:
    def __init__(self):
        self.headers = {
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}",
            "Content-Type": "application/json",
            "Prefer": "return=minimal",
        }

    def submit_score(self, player_name: str, score: float, mode: str, signature: str, timeout: float = 3.0) -> bool:
        del signature
        try:
            payload = json.dumps(
                {
                    "player_name": player_name,
                    "score": float(score),
                    "mode": mode
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
            print(f"[SupabaseService] Erro no envio global de score: {e}")
            return False

    def fetch_top_scores(self, mode: str, limit: int = 10, timeout: float = 3.0) -> list[dict[str, Any]]:
        mode_encoded = urllib.parse.quote(mode)
        url = f"{SUPABASE_URL}?select=*&mode=eq.{mode_encoded}&order=score.desc&limit={int(limit)}"
        req = urllib.request.Request(url, headers=self.headers, method="GET")
        with urllib.request.urlopen(req, timeout=timeout) as response:
            data = json.loads(response.read().decode("utf-8"))
        if not isinstance(data, list):
            return []
        normalized: list[dict[str, Any]] = []
        for entry in data:
            if not isinstance(entry, dict):
                continue
            normalized.append(entry)
        return normalized
