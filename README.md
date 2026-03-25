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
- `Esc`: alternar pausa (abrir/fechar)

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

### 4) Domain Event Bus

Eventos de domínio seguem um barramento único:

- `EventBus` global compartilhado pelo `SceneStack`
- eventos principais: `PlayerDied`, `PortalEntered`, `EnemySpawned`
- eventos adicionais de telemetria/domínio: `CollectibleCollected`, `SpawnPortalDestroyed`, `DashStarted`, `BulletExpired`, `LifetimeExpired`
- systems publicam eventos em `EventBus`
- consumidores transversais (ex.: áudio/UI) podem registrar handlers diretamente no `EventBus`
- `GameScene` registra/desregistra handlers de gameplay em `on_enter()`/`on_exit()`

### 5) Factory Pattern + Registry

Criação de entidades centralizada nas factories (`game/factories`):

- `EnemyFactory` com registries distintos para `enemy`, `miniboss` e `boss`
- factory cria por tipo/categoria e não define política de spawn global
- `create_by_kind()` elimina condicionais hardcoded por tipo
- factories montam componentes, tags, behavior e render strategy
- roster base de `enemy` inclui arquétipos de perseguição, strafe, shotgun, órbita radial, investida e bombardeio rúnico
- roster base também inclui arquétipos de projétil especial e suporte (`atirador_laser`, `kamehameha`, `lanca_chamas`, `fantasma`, `buffer`, `sapo`)
- roster base recebeu expansão com arquétipos inspirados em RotMG (ex.: `bandido_arcano`, `mago_hobbit`, `escorpiao_rainha`, `gazer_vazio`, `assassino_crepuscular`, `necrolorde_orbital`) mantendo registro por tipo no factory
- nova leva de arquétipos adiciona padrões dedicados (`olho_orbitante`, `vigia_supressor`, `xama_mineiro`, `algoz_faseado`, `guardiao_cosmico`, `necromante_torre`) com behaviors específicos (`OrbitShooterBehavior`, `SuppressorBehavior`, `MineLayerBehavior`, `BlinkStrikerBehavior`)
- roster de `miniboss` e `boss` pode evoluir por novos arquétipos registrados (ex.: matrix laser, oráculo de feixe, piro-hidra, fantasma senhor, alquimista; colosso laser, druida tóxico, soberano espectral)

### 6) Strategy Pattern (modos, progressão, spawn, render, IA)

#### Modos de jogo

`GameScene` recebe um `GameModeStrategy` e delega comportamento ao modo:

- `RaceMode`
- `RaceInfiniteMode`
- `SurvivalMode`
- `SurvivalHardcoreMode`
- `LabyrinthMode`

Cada modo define:

- pipeline de systems (`build_systems`)
- estratégia de spawn (`build_spawn_strategy`)
- estratégia de progressão (`build_level_progression_strategy`)
- HUD (`build_hud_lines`)
- retry (`create_retry_strategy`)

#### Modo Labirinto

`LabyrinthMode` implementa progressão infinita baseada em grade procedural:

- geração com `Recursive Backtracking` (labirinto perfeito e conexo)
- escala de dificuldade por nível (dimensão de grade, contagem e velocidade de vírus)
- chave posicionada pelo maior valor de distância Euclidiana até a saída
- saída posicionada em borda externa e bloqueada até coleta da chave
- arena de boss em cada nível múltiplo de 5

Sistemas dedicados do modo:

- `LabyrinthAISystem`: pathfinding em grade para vírus com perfis `chaser` e `interceptor`
- `LabyrinthCollisionSystem`: colisão com paredes por índice espacial local
- `LabyrinthObjectiveSystem`: chave/porta e conclusão de boss arena
- `ParrySystem` + `StaggerSystem`: parry ativo no labirinto; vírus afetados ficam parados com pulso visual preto e branco

Para evitar acoplamento com o `SpawnDirector` global, o modo usa `LabyrinthSpawnStrategy` com ciclos de portal desativados e controla spawns via configuração de nível.

#### Presets por modo

Configuração por preset em `game/modes/mode_config.py`:

- `RaceConfig`
- `RaceInfiniteConfig`
- `SurvivalConfig`
- `SurvivalHardcoreConfig`

Isso remove blocos hardcoded e concentra tuning por modo.

#### Progressão e Spawn plugáveis

- `LevelProgressionStrategy` por modo (`RaceLevelProgressionStrategy` / `SurvivalLevelProgressionStrategy`)
- `SpawnDirector` desacoplado de cena em `game/systems/spawn_director.py`
- `SpawnStrategy` em `game/modes/spawn_strategy.py` opera por `GameWorld` + `elapsed_time`
- cada modo controla a política de spawn por categoria (`enemy`, `miniboss`, `boss`)
- pools de roster são liberados por fase (nível/tempo) para evitar picos injustos no early game
- sobrevivência/hardcore incluem hazard periódico de lava com fases de aviso, ativo e pisca no encerramento
- sobrevivência/hardcore incluem eventos ambientais periódicos: região de neve (drift), região de água com navios canhoneiros, nuvem de balas e buraco negro móvel com sucção
- eventos ambientais são mutuamente exclusivos: lava, neve, água, nuvem de balas e buraco negro nunca acontecem juntos
- player possui parry em `J`; inimigos atingidos no raio do parry ficam desestabilizados temporariamente com pulso visual
- durante stagger de parry, o inimigo nao causa dano ao player (colisao e projetil)
- tela de morte estilo resumo de run: causa da morte + estatisticas da sessao (tempo, nivel, dashes, coletaveis, etc.)
- no sobrevivencia/hardcore ha coletaveis de campo; a cada 100 coletados, ganha 1 carga de bomba nuclear acionada em I para limpar os inimigos atuais
- explosoes de dominio (`ExplosionTriggered`) exibem animacao de impacto e aplicam screen shake no gameplay
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

### 11) Sistema de Áudio (Arquitetura)

O áudio segue contrato em camadas, orientado a EventBus único:

- `EventBus` -> `AudioDirector` -> (`AudioRouter` + `MixerBackend`)
- `AudioRouter` decide ações de áudio de forma pura (sem dependência de `pygame`)
- `AudioDirector` orquestra runtime, mantém estado e consome eventos de domínio
- `MixerBackend` é o único ponto de contato com `pygame.mixer`
- `AudioCatalog` e `AudioSettings` centralizam mapeamento declarativo e política de volumes/limites
- `AudioSettingsManager` aplica ajustes globais de volume (Música/SFX) e persistência local

Contratos principais:

- `AudioAction` é a fronteira entre decisão (`AudioRouter`) e execução (`AudioDirector`)
- `AudioState` é a fonte única de verdade para contexto, trilha atual e duck
- cenas publicam eventos; cenas não manipulam `pygame.mixer` diretamente
- `UINavigator` publica eventos de UI (`UINavigated`, `UIConfirmed`, `UICancelled`) como fonte única de navegação
- UI de configuração altera volume via `AudioSettingsManager` (não via backend direto)

Política de contexto musical:

- `menu`: trilha de menu
- `gameplay`: trilha de gameplay
- `pause`: duck de música (sem troca de trilha)
- `game_over`: unduck + trilha de game over em one-shot; ao terminar, transição automática para trilha de menu

Decisão arquitetural importante:

- `pygame.mixer.music` é single-track; transições são sequenciais (fade out -> fade in), sem crossfade real entre duas trilhas simultâneas.
- volumes de Música/SFX são persistidos em `game/assets/audio_settings.json`.

### 12) Pause Menu (Overlay)

- `PauseScene` é overlay transparente e pausa gameplay por contrato do `SceneStack` (somente topo atualiza)
- menu principal da pausa: `Voltar pro Jogo`, `Configuracoes`, `Abandonar Partida`
- submenu de áudio usa ajuste incremental para `Música` e `SFX` com suporte a mouse e navegação por teclado/gamepad
- fundo da pausa usa overlay semi-transparente com alpha suave para manter legibilidade


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
2. `MainMenuScene` escolhe `RaceMode`, `SurvivalMode` ou `LabyrinthMode`
3. `GameScene` monta `LevelProgressionStrategy`, `SystemPipeline` e `SpawnDirector` desacoplado (world + strategy)
4. systems atualizam estado via ECS, queries reutilizáveis e fases do pipeline
5. systems publicam eventos; `GameScene` despacha handlers por tipo e decide transições

No `LabyrinthMode`, a progressão é infinita e a transição de nível ocorre por objetivo de sistema (porta destravada após chave ou limpeza de boss arena), sem lógica de objetivo em render.

## Observações

- Renderização do jogo usa apenas formas (`pygame.draw.circle`, `pygame.draw.rect`, `pygame.draw.line`).
- Textos de UI usam `pygame.font` para legibilidade.
