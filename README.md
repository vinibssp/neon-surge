## 🏗️ Nova Estrutura de Pastas e Arquivos

**`main.py`** — Ponto de entrada do projeto

**`neon_surge/`** — Pacote principal do jogo
> **`game.py`** — Orquestrador principal
> **`runtime.py`** — Gerenciamento do loop principal e eventos
> **`rendering.py`** — Funções de desenho de telas
> **`constants.py`** — Centralização de todas as constantes e configurações
> **`utils.py`** — Funções utilitárias (ex: brilho neon)
>
> **`ai/`** — Lógicas de IA extraídas para o padrão Strategy
> `bosses.py` · `shooter.py` · `chaser.py` · `charge.py` · `bounce.py` · `explosive.py`
>
> **`components/`** — Lógica reutilizável via composição
> `transform.py` · `physics.py` · `collider.py` · `dash.py` · `emitter.py`
>
> **`entities/`** — Objetos do mundo de jogo
> `player.py` · `enemy.py` · `particle.py` · `collectible.py` · `hazards.py`
>
> **`hud/`** — Interface de usuário
> **`services/`** — Serviços externos e I/O (`audio.py` · `ranking.py`)
> **`systems/`** — Processamento de lógica de jogo (`gameplay.py`)

---

## 🛠️ Principais Melhorias Realizadas

**1. Composição em vez de Herança**
O `Player` agora é composto por componentes específicos (`PhysicsComponent`, `TransformComponent`, `DashAbility`), mantendo os valores originais (`accel=1.8`, `friction=0.82`, `max_speed=10`).
O `Enemy` adota o padrão **Strategy** para IA — em vez de um bloco gigante de `if/else`, um componente `self.ai` dita o comportamento por tipo, facilitando a adição de novos inimigos.

**2. Organização de Imports**
Todos os arquivos usam caminhos relativos e absolutos consistentes com a nova hierarquia.

**3. Limpeza de Redundâncias**
- Pasta duplicada `NeonSurge/` removida
- Arquivos temporários e caches deletados (`__pycache__`, `.venv`, `.pyc`)
- `ranking_completo.json` consolidado dentro de `data/`

**4. Desacoplamento**
Lógicas de áudio, ranking e UI isoladas em serviços e módulos próprios, removendo dependências de arquivos monolíticos.

---

O projeto está limpo, modular e pronto para escalabilidade, mantendo **100% da experiência de jogo original**.
```python
python main.py
```