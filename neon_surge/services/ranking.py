import json
import os
import time
import threading
from urllib import request, error

from ..constants import ARQUIVO_RANKING

# Configurações Supabase
SUPABASE_URL = "https://irwyyqgxahlmoncfpacg.supabase.co/rest/v1/rankings"
API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imlyd3l5cWd4YWhsbW9uY2ZwYWNnIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzQyNzUwMDMsImV4cCI6MjA4OTg1MTAwM30.Lum4HXhLBMn4GmtAjbKAh-7pnjI6YYNoI41g0fZkxUg"
SERVICE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imlyd3l5cWd4YWhsbW9uY2ZwYWNnIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzQyNzUwMDMsImV4cCI6MjA4OTg1MTAwM30.Lum4HXhLBMn4GmtAjbKAh-7pnjI6YYNoI41g0fZkxUg"
GAME_VERSION = "1.0.0"

def _enviar_supabase(player_name, mode, score):
    """Thread function to send score to Supabase."""
    data = json.dumps({
        "player_name": player_name,
        "mode": mode,
        "score": float(score),
        "version": GAME_VERSION
    }).encode('utf-8')
    
    req = request.Request(SUPABASE_URL, data=data, method='POST')
    # Cabeçalhos padrão Supabase para REST
    req.add_header("apikey", API_KEY)
    req.add_header("Authorization", f"Bearer {SERVICE_KEY}")
    req.add_header("Content-Type", "application/json")
    req.add_header("Prefer", "return=minimal")
    
    try:
        with request.urlopen(req, timeout=5) as response:
            pass
    except error.HTTPError as e:
        corpo = e.read().decode('utf-8')
        print(f"Erro HTTP ao enviar ranking ({e.code}): {corpo}")
    except Exception as e:
        print(f"Erro ao enviar ranking global: {e}")

def buscar_ranking_global(modo, limit=10):
    """Fetch Top 10 from Supabase for a specific mode."""
    order = "score.asc" if modo == "CORRIDA" else "score.desc"
    url = f"{SUPABASE_URL}?mode=eq.{modo}&order={order}&limit={limit}"
    
    req = request.Request(url, method='GET')
    req.add_header("apikey", API_KEY)
    req.add_header("Authorization", f"Bearer {SERVICE_KEY}")
    
    try:
        with request.urlopen(req, timeout=5) as response:
            return json.loads(response.read().decode('utf-8'))
    except error.HTTPError as e:
        corpo = e.read().decode('utf-8')
        print(f"Erro HTTP ao buscar ranking ({e.code}): {corpo}")
        return []
    except Exception as e:
        print(f"Erro ao buscar ranking global: {e}")
        return []

def carregar_ranking(self):
    if os.path.exists(ARQUIVO_RANKING):
        with open(ARQUIVO_RANKING, "r") as f:
            dados = json.load(f)
            if "Corrida_Hardcore" in dados:
                dados.pop("Corrida_Hardcore", None)
            if "Hardcore" not in dados:
                dados["Hardcore"] = []
            if "Corrida_Infinita" not in dados:
                dados["Corrida_Infinita"] = []
            if "Labirinto_Infinito" not in dados:
                dados["Labirinto_Infinito"] = []
            return dados
    return {"Corrida": [], "Sobrevivencia": [], "Hardcore": [], "Corrida_Infinita": [], "Labirinto_Infinito": []}


def salvar_ranking(self, modo, valor):
    if modo == "CORRIDA":
        chave_modo = "Corrida"
    elif modo == "SOBREVIVENCIA":
        chave_modo = "Sobrevivencia"
    elif modo == "CORRIDA_INFINITA":
        chave_modo = "Corrida_Infinita"
    elif modo == "LABIRINTO":
        chave_modo = "Labirinto_Infinito"
    else:
        chave_modo = "Hardcore"

    if chave_modo in ["Corrida_Infinita", "Labirinto_Infinito"]:
        novo_registro = {"nome": self.nome_jogador, "fase": int(valor), "id": time.time()}
        self.ranking[chave_modo].append(novo_registro)
        self.ranking[chave_modo] = sorted(self.ranking[chave_modo], key=lambda x: x["fase"], reverse=True)
        self.ultima_posicao = self.ranking[chave_modo].index(novo_registro) + 1
        self.ultimo_tempo = float(valor)
    else:
        tempo_str = f"{valor:.1f}"
        novo_registro = {"nome": self.nome_jogador, "tempo": float(tempo_str), "id": time.time()}
        self.ranking[chave_modo].append(novo_registro)
        if chave_modo == "Corrida":
            self.ranking[chave_modo] = sorted(self.ranking[chave_modo], key=lambda x: x["tempo"])
        else:
            self.ranking[chave_modo] = sorted(self.ranking[chave_modo], key=lambda x: x["tempo"], reverse=True)
        self.ultima_posicao = self.ranking[chave_modo].index(novo_registro) + 1
        self.ultimo_tempo = float(tempo_str)

    self.ranking[chave_modo] = self.ranking[chave_modo][:50]
    with open(ARQUIVO_RANKING, "w") as f:
        json.dump(self.ranking, f, indent=4)

    # Identificador único para destacar o score atual
    self.id_sessao_atual = novo_registro["id"]

    # Enviar para o Supabase em background
    threading.Thread(target=_enviar_supabase, args=(self.nome_jogador, modo, valor), daemon=True).start()
