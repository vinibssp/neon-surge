# Neon Surge 2

Jogo 2D em Python + Pygame com arquitetura modular e desacoplada, seguindo ECS, Scene Stack, Factory/Strategy/Command Patterns, Event Bus de domínio e Query API para sistemas.

## Requisitos

- Python 3.11+
- `pygame-ce`
- `pygame_gui`
- Dependências em `requirements.txt`

## Instalação

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Execução

```bash
python -m game.main
```

## Controles

### Gameplay

- `WASD`: movimentação do player
- `Espaço`: dash
- `Esc`: abrir pausa

### Menus (UI Navigation unificado)

- `↑/↓` ou `W/S`: navegar entre botões
- `Enter` / `Espaço`: confirmar
- `Esc`: cancelar/voltar
- Mouse: hover + clique esquerdo
- Gamepad: D-Pad/analógico vertical para navegação, `A` confirmar, `B` cancelar

## Arquitetura e Design

### 1) Game Loop com Fixed Timestep

O loop principal usa atualização fixa desacoplada do render:

- `update()` em passo fixo (`FIXED_DT`)
- acumulador de tempo para estabilidade de simulação
- `render()` desacoplado da frequência de update

### 2) Scene Stack (State Stack)

As cenas são empilhadas via `SceneStack`:

- cena do topo recebe `handle_input()` e `update()`
- suporte a overlays transparentes (`PauseScene`)
- cenas principais: `MainMenuScene`, `GameScene`, `PauseScene`, `GameOverScene`

### 3) ECS + Query API

O núcleo ECS fica em `game/ecs` e a consulta foi centralizada via `WorldQuery`:

- `Entity` com componentes e tags
- componentes de dados (sem lógica pesada)
- lógica concentrada em systems
- `GameWorld.query(WorldQuery)` para filtros reutilizáveis
- catálogo de queries em `game/systems/world_queries.py` para evitar loops duplicados

### 4) Domain Event Bus + Dispatcher

Eventos de domínio substituem flags de estado:

- `EventBus` em `game/core/events.py`
- eventos principais: `PlayerDied`, `PortalEntered`, `EnemySpawned`
- eventos adicionais de telemetria/domínio: `CollectibleCollected`, `SpawnPortalDestroyed`, `DashStarted`, `BulletExpired`, `LifetimeExpired`
- systems publicam eventos em `EventBus`
- `GameScene` drena a fila e distribui via `DomainEventDispatcher.on(...)`
- handlers tipados removem `if isinstance(...)` espalhado na cena

### 5) Factory Pattern + Registry

Criação de entidades centralizada nas factories (`game/factories`):

- `EnemyFactory` com registries distintos para `enemy`, `miniboss` e `boss`
- factory cria por tipo/categoria e não define política de spawn global
- `create_by_kind()` elimina condicionais hardcoded por tipo
- factories montam componentes, tags, behavior e render strategy

### 6) Strategy Pattern (modos, progressão, spawn, render, IA)

#### Modos de jogo

`GameScene` recebe um `GameModeStrategy` e delega comportamento ao modo:

- `RaceMode`
- `SurvivalMode`

Cada modo define:

- pipeline de systems (`build_systems`)
- estratégia de spawn (`build_spawn_strategy`)
- estratégia de progressão (`build_level_progression_strategy`)
- HUD (`build_hud_lines`)
- retry (`create_retry_strategy`)

#### Presets por modo

Configuração por preset em `game/modes/mode_config.py`:

- `RaceConfig`
- `SurvivalConfig`

Isso remove blocos hardcoded e concentra tuning por modo.

#### Progressão e Spawn plugáveis

- `LevelProgressionStrategy` por modo (`RaceLevelProgressionStrategy` / `SurvivalLevelProgressionStrategy`)
- `SpawnDirector` desacoplado de cena em `game/systems/spawn_director.py`
- `SpawnStrategy` em `game/modes/spawn_strategy.py` opera por `GameWorld` + `elapsed_time`
- cada modo controla a política de spawn por categoria (`enemy`, `miniboss`, `boss`)
- escala de spawn por modo:
  - corrida: mais portais por ciclo conforme avanço
  - sobrevivência: mais portais por ciclo conforme tempo

#### Render desacoplado

- `RenderComponent` guarda `render_strategy`
- estratégias em `game/rendering/strategies.py`
- estilos distintos para player, follower, shooter, portais e coletáveis

### 7) Orquestração da `GameScene`

Para reduzir acoplamento e responsabilidades:

- `BackgroundRenderer`
- `HudRenderer`
- `SpawnDirector` (systems layer)
- `SystemPipeline` com fases e prioridade explícita

`SystemPipeline` executa por etapa:

- `pre_update`
- `simulation`
- `post_update`

Com `SystemSpec(system, phase, priority)` definido pelos modos, evitando acoplamento por ordem implícita de lista.

### 8) Command Pattern no Input

#### Gameplay

- `MoveCommand` e `DashCommand` desacoplam input do estado interno da entidade

#### UI desacoplada de player cursor

Menus não dependem mais do player para navegação:

- `UINavigator` é a fonte única de foco/seleção
- `UINavigationInputHandler` traduz dispositivo em comandos de UI
- mesma semântica de navegação para teclado, mouse e gamepad
- cenas de menu consomem comandos; não roteiam lógica de navegação manualmente

### 9) Arquitetura de UI, Menus e Cenas de Menu

#### Princípios de design

- UI orientada a composição (builders/configs/controllers), sem herança profunda
- contrato explícito entre input de UI, navegação e ações de cena
- responsabilidade da cena: orquestrar fluxo; responsabilidade da UI: estado visual e estrutura
- estilo visual centralizado em tema, sem decisões visuais espalhadas em regras de domínio

#### Contratos arquiteturais

- `BaseMenuScene` define o ciclo padrão de menu (input/update/render) e evita duplicação
- cenas de menu registram `buttons` + `actions` no navigator; ações disparam transições de stack
- overlays compartilham construção via factory de cena (`OverlaySceneFactory`) para consistência de contrato
- componentes reutilizáveis (ex.: tabs) encapsulam estado de UI e expõem API declarativa para cena

#### Regras para Menu Scenes

- menu scene não concentra detalhe de composição de widget em cascata
- menu scene não usa estado global/flags implícitas para navegação
- overlays usam `transparent=True` e mantêm comportamento previsível de cancelamento
- extensões de menu devem adicionar novas ações/componentes sem alterar contratos base

### 10) Query API completa

- Consulta de mundo centralizada em `WorldQuery`
- `PORTAL_SPAWN_QUERY` em `game/systems/world_queries.py` substitui loop ad-hoc remanescente
- `SpawnDirector` usa `world.query(PORTAL_SPAWN_QUERY)`


## Estrutura de Pastas

```text
game/
├── core/          # loop, scene stack, input gameplay, event bus, world
├── ecs/           # entity/component/system/query
├── components/    # data components
├── systems/       # systems + world_queries + pipeline + spawn_director
├── factories/     # criação de entidades
├── behaviors/     # IA dos inimigos
├── modes/         # strategies de modo, progressão e presets
├── rendering/     # render strategies e utilitários visuais
├── ui/            # contratos, tema, navegação e componentes reutilizáveis
└── scenes/        # orquestração de menu/gameplay e transições de stack
```

## Fluxo de Alto Nível

1. `main` inicia `Game` e `SceneStack`
2. `MainMenuScene` escolhe `RaceMode` ou `SurvivalMode`
3. `GameScene` monta `LevelProgressionStrategy`, `SystemPipeline` e `SpawnDirector` desacoplado (world + strategy)
4. systems atualizam estado via ECS, queries reutilizáveis e fases do pipeline
5. systems publicam eventos; `GameScene` despacha handlers por tipo e decide transições

## Observações

- Renderização do jogo usa apenas formas (`pygame.draw.circle`, `pygame.draw.rect`, `pygame.draw.line`).
- Textos de UI usam `pygame.font` para legibilidade.
