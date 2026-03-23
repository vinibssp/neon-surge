# Backlog de Atualizações - Novas Features


## Interface, Experiência do Usuário (UX) e Mecânicas
*Novas habilidades e funcionalidades de interface/experiência do usuário (UX).*

- [ ] **Mecânica de Parry:** Adicionar sistema para refletir/aparar ataques no tempo exato.
- [ ] **Aba de Ranking:** Criar leaderboard no menu principal para mostrar pontuações.
- [ ] **Causa da Morte:** Exibir na tela de Game Over qual foi o mob, boss ou hazard que matou o jogador.
- [ ] **Atualizar Guia do Player:** Inserir as novas mecânicas, explicações dos novos modos e arquivo de ameaças.
- [ ] **Atualizar Arquivo de Ameaças:** Cadastrar todos os novos inimigos e obstáculos no bestiário/arquivo do jogo.


## Novos Inimigos (Mobs)
*Novas ameaças para o jogador lidar nas fases.*

- [ ] **Atirador de Laser:** Inimigo focado em atirar lasers normais contra o jogador.
- [ ] **Kamehameha:** Inimigo que carrega energia e atira um laser contínuo.
- [ ] **Lança-chamas:** Atira fogo em um raio de cone na direção para onde está apontando.
- [ ] **Fantasma:** Segue o jogador invulnerável/transparente sem dar dano; ao ficar visível, ele para e pode causar dano (estilo Boo do Mario).
- [ ] **Buffer:** Mago que buffa a velocidade de movimento e ataque dos outros mobs. Só toma dano/morre se o jogador der um dash por cima dele.
- [ ] **Sapo:** Vomita uma poça de ácido que fica no mapa causando dano por um tempo.


## Eventos de Ambiente (Hazards)
*Modificadores de mapa que alteram a física ou zona de perigo.*

- [ ] **Região de Neve (Drift):** Cria uma área escorregadia no mapa (com *drag*), deixando curvas mais lentas e liberando a mecânica de drift.
- [ ] **Região de Água:** Transforma uma parte do mapa em água e spawna navios piratas com canhões.
- [ ] **Nuvem de Balas:** Uma área onde chove bala constantemente, mas o jogador consegue atravessar ileso usando o dash.


## Novos Modos de Jogo
*Novas formas de jogar, sozinhas ou multiplayer.*

- [ ] **Modo Pontuação (Arcade):** Fases contínuas onde a dificuldade aumenta com o tempo. Pontuação é medida por segundo vivo e quantidade de mobs na tela (abate de mobs através de drops pontua mais).
- [ ] **Modo Rogue-like:** Corrida com coleta de buffs pelo tempo. Buffs leves na fase 5 (miniboss) e buffs fortes em boss normal.
- [ ] **Modo Fuga:** Auto-scroller para a direita enquanto a parede esquerda fecha e mobs spawnam na frente (Foco em Multiplayer).
- [ ] **Modo Party (Construtor):** Estilo *Ultimate Chicken Horse*. Jogadores adicionam paredes e mobs para montar a fase com o objetivo de conseguir moedas.


## Drops e Power-Ups
*Itens temporários no meio da partida.*

- [ ] **Drop Nuke:** Item momentâneo que elimina todos os inimigos da tela (Pode spawnar após um inimigo despawnar ou condição similar de balanceamento).

---


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