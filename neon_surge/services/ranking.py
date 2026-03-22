import json
import os
import time

from ..constants import ARQUIVO_RANKING


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
