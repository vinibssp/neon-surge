# Neon Surge — Hardcore Edition

Cyberpunk top-down survival / speedrun game built with **pygame**.

---

## Estrutura do projeto

```
neon-surge/
├── main.py                   ← entry point  (python main.py)
├── requirements.txt
├── assets/
│   └── trilha.mp3            ← trilha sonora
├── data/
│   └── ranking_completo.json ← ranking persistido (criado automaticamente)
└── neon_surge/               ← pacote principal
    ├── __init__.py
    ├── __main__.py           ← permite: python -m neon_surge
    ├── constants.py          ← todas as constantes e config
    ├── utils.py              ← funções puras de desenho
    ├── level.py              ← gerenciador de fase (entidades + sistemas)
    ├── game.py               ← controlador principal (display + state machine)
    │
    ├── components/           ← bags de dados/comportamento (composição)
    │   ├── transform.py      TransformComponent  pos, vel
    │   ├── physics.py        PhysicsComponent    aceleração + atrito + clamping
    │   ├── collider.py       ColliderComponent   hitbox circular
    │   ├── emitter.py        ParticleEmitter     burst de partículas
    │   └── dash.py           DashAbility         dash com janela de invencibilidade
    │
    ├── ai/                   ← comportamentos de IA (Strategy pattern)
    │   ├── base.py           AIBehaviour         ABC base
    │   ├── bounce.py         BounceAI            Sentinela — rebate nas paredes
    │   ├── chaser.py         ChaserAI            Caçador — persegue o jogador
    │   └── charge.py         ChargeAI            Kamikaze — espera → mira → dispara
    │
    ├── entities/             ← objetos do mundo de jogo
    │   ├── particle.py       Particle
    │   ├── player.py         Player
    │   ├── enemy.py          Enemy               recebe AIBehaviour via composição
    │   ├── collectible.py    Collectible
    │   └── portal.py         Portal
    │
    ├── systems/              ← processadores stateless/levemente stateful
    │   ├── particles.py      ParticleSystem      pool de partículas
    │   ├── spawner.py        SpawnSystem         spawn temporizado (modo sobrevivência)
    │   └── collision.py      CollisionSystem     queries de colisão puras
    │
    ├── services/             ← I/O e integrações externas
    │   ├── audio.py          AudioManager        volume, mute, música
    │   └── ranking.py        RankingManager      persistência JSON, sort, top-N
    │
    ├── hud/                  ← UI de jogo
    │   ├── hud.py            HUD                 barra top (modo, timer, dash)
    │   └── volume_widget.py  VolumeWidget        controle +/− / mute nos menus
    │
    └── screens/              ← nós da máquina de estados (uma classe por tela)
        ├── base.py           Screen              ABC com helpers compartilhados
        ├── input_name.py     InputNameScreen
        ├── ask_mode.py       AskModeScreen
        ├── mode_menu.py      ModeMenuScreen
        ├── info_modes.py     InfoModesScreen
        ├── hotkeys.py        HotkeysScreen
        ├── enemy_info.py     EnemyInfoScreen
        ├── game_screen.py    GameScreen
        ├── pause.py          PauseScreen
        └── ranking.py        RankingScreen
```

---

## Como rodar

```bash
# instalar dependências
pip install -r requirements.txt

# copiar os assets para a pasta correta
cp trilha.mp3 assets/

# rodar
python main.py
# ou
python -m neon_surge
```

---

## Modos de jogo

| Modo                    | Objetivo                           | Morte                          |
|-------------------------|------------------------------------|--------------------------------|
| Corrida                 | 10 fases no menor tempo            | Repete só a fase atual         |
| Corrida Hardcore        | 10 fases no menor tempo            | Volta à fase 1, timer zera     |
| Sobrevivência           | Aguentar o máximo                  | Game over, salva o tempo       |
| Sobrevivência Hardcore  | Igual, mais rápido e mais brutal   | Game over, salva o tempo       |

---

## Controles

| Tecla             | Ação                          |
|-------------------|-------------------------------|
| W A S D / Setas   | Mover a nave                  |
| Espaço            | Dash (invencibilidade rápida) |
| ESC               | Pausar / voltar nos menus     |
| F11               | Alternar tela cheia           |
| + / −             | Volume                        |

---

## Arquitetura — padrões utilizados

- **Composição sobre herança** — `Player` não herda nada; recebe
  `TransformComponent`, `PhysicsComponent`, `ColliderComponent`,
  `DashAbility` e `ParticleEmitter` como campos.

- **Strategy (AI)** — `Enemy` recebe qualquer `AIBehaviour` no construtor.
  Para criar um novo inimigo: escreva uma subclasse de `AIBehaviour` e
  registre em `Enemy._REGISTRY`. Zero mudanças na classe `Enemy`.

- **State Machine (telas)** — cada `Screen` retorna a string da próxima tela
  em `handle_event` / `update`. `Game` só chama a tela atual e faz a
  transição. Para adicionar uma tela: crie a classe e registre em
  `game.screens`.

- **Systems** — `ParticleSystem`, `SpawnSystem` e `CollisionSystem` são
  processadores sem estado de entidade. `Level` os orquestra.

---

## Extensões sugeridas

| Extensão         | Onde encaixar                                      |
|------------------|----------------------------------------------------|
| `EventBus`       | `game.py` — triggers de som, conquistas, etc.      |
| `AssetManager`   | `game.py` — cache de fontes, sons e sprites        |
| `Config`         | `services/` — persiste volume e keybindings em JSON|
| `AchievementSystem` | hooks em `Level.outcome` e `level.elapsed`      |
| `PowerUpSystem`  | componente adicional droppado por inimigos ao morrer|
| `WaveDefinition` | JSON → `SpawnSystem` para waves data-driven        |
