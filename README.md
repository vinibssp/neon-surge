# Neon Surge

Jogo arcade em `pygame` com modos de corrida e sobrevivência.

## Estrutura do projeto

```text
.
├── neon_surge.py               # Entrypoint
├── neon_surge/
│   ├── __init__.py
│   ├── config.py               # Configurações e constantes
│   ├── ui.py                   # Funções de renderização/UI
│   ├── entities.py             # Player, inimigos e partículas
│   ├── ranking.py              # Persistência e ordenação de ranking
│   ├── gameplay.py             # Regras e atualização da partida
│   ├── rendering.py            # Renderização de telas e HUD
│   ├── runtime.py              # Loop principal e eventos de input
│   └── game.py                 # Orquestrador principal (sem God Class)
├── ranking_completo.json       # Persistência do ranking
└── trilha.mp3                  # Música de fundo
```

## Requisitos

- Python 3.10+
- Dependências em `requirements.txt`

## Como executar

```bash
python -m pip install -r requirements.txt
python neon_surge.py
```
