# Neon Surge 2 - Wiki Completa

## 1. Visao Geral

Neon Surge 2 e um jogo 2D em Python + Pygame com arquitetura modular orientada a ECS, Scene Stack, Event Bus de dominio e uso de patterns (Factory, Strategy, Command).

Pilares do projeto:
- ECS puro (entidades com componentes de dados, logica em systems)
- Update com fixed timestep
- Render desacoplado da simulacao
- Event Bus unico para eventos de dominio
- Modos de jogo plugaveis via Strategy
- Criacao de entidades por Factory + registries por categoria

## 2. Requisitos e Execucao

Requisitos:
- Python 3.11+
- pygame-ce
- pygame_gui

Execucao:
- python -m game.main

Fontes:
- README.md
- game/main.py

## 3. Estrutura do Projeto

Raiz principal:
- game/assets: recursos (audio, fontes, configs de audio)
- game/audio: arquitetura de audio em camadas
- game/behaviors: IA e logica de comportamento de inimigos
- game/components: componentes ECS (dados)
- game/core: loop, comandos, eventos, mundo, stack de cenas
- game/ecs: primitives ECS (Entity, Component, Query)
- game/factories: factories de entidades
- game/modes: estrategias de modo/progressao/spawn/config
- game/rendering: estrategias de render e utilitarios visuais
- game/scenes: cenas de menu/gameplay/overlays
- game/services: servicos transversais (ranking)
- game/systems: systems de simulacao e pipeline
- game/ui: navegacao, tema e componentes de interface

## 4. Game Loop e Fluxo de Cena

Fluxo principal:
1. Inicializa pygame, audio e SceneStack
2. Abre PlayerNameScene (primeiro uso) ou MainMenuScene
3. Game roda loop com fixed timestep
4. SceneStack delega input/update para cena do topo
5. Render considera transparencias para overlays

Arquivos:
- game/core/game.py
- game/core/scene_stack.py
- game/main.py

## 5. ECS

### 5.1 Entidade e Query

- Entity possui id, componentes, tags e estado active
- WorldQuery filtra por componentes, tags, exclusoes, inatividade e predicate

Arquivos:
- game/ecs/entity.py
- game/ecs/query.py

### 5.2 Mundo de Jogo

GameWorld contem:
- entidades e filas pending_add/pending_remove
- player
- event_bus
- runtime_state
- helpers de spawn de bala, clamp, query e contagem por tag

Contrato relevante:
- inimigo recem-spawnado recebe freeze curto via StaggeredComponent

Arquivo:
- game/core/world.py

### 5.3 Componentes

Componentes de dados principais:
- TransformComponent, MovementComponent, CollisionComponent, RenderComponent
- ShootComponent, TurretComponent, ChargeComponent
- ParryComponent, DashComponent, InvulnerabilityComponent
- BulletComponent, LifetimeComponent, StaggeredComponent
- BossComponent, GhostComponent, KamehamehaComponent etc.

Arquivo:
- game/components/data_components.py

## 6. Event Bus de Dominio

Eventos principais:
- PlayerDied, PlayerDamaged
- PortalEntered, PortalActivated
- EnemySpawned
- CollectibleCollected, SpawnPortalDestroyed
- DashStarted, ParryLanded
- BulletExpired, LifetimeExpired
- ExplosionTriggered
- AudioContextChanged, AudioDuckRequested, AudioUnduckRequested
- UINavigated, UIConfirmed, UICancelled

Arquivo:
- game/core/events.py

## 7. Systems e Pipeline

Pipeline:
- fases: pre_update, simulation, post_update
- ordenacao por prioridade via SystemSpec

Arquivo:
- game/systems/system_pipeline.py

Systems presentes:
- movement_system, collision_system, shoot_system, follow_system
- dash_system, parry_system, stagger_system, invulnerability_system
- lifetime_system, render_system
- environment_event_system
- survival_collectible_system, nuclear_bomb_system
- labyrinth_ai_system, labyrinth_collision_system, labyrinth_objective_system
- spawn_director
- world_queries

Queries centralizadas:
- game/systems/world_queries.py

Spawn por estrategia:
- game/systems/spawn_director.py

## 8. Input e Comandos

InputHandler traduz input fisico em comandos:
- MoveCommand
- DashCommand
- ParryCommand
- NuclearBombCommand

Mapeamento atual:
- WASD: movimento
- Space/LShift/RShift: dash
- J: parry
- I: bomba nuclear
- Esc: pausa no gameplay

Arquivos:
- game/core/input_handler.py
- game/core/command.py

## 9. Modos de Jogo

Estrategias de modo implementadas:
- RaceMode
- RaceInfiniteMode
- SurvivalMode
- SurvivalHardcoreMode
- LabyrinthMode
- TrainingMode
- OneVsOneMode (presente no codigo)

Cada modo define:
- systems (build_systems)
- spawn strategy (build_spawn_strategy)
- progression strategy (build_level_progression_strategy)
- HUD (build_hud_lines)
- retry strategy

Arquivos:
- game/modes/game_mode_strategy.py
- game/modes/

Configs por preset:
- RaceConfig, RaceInfiniteConfig
- SurvivalConfig, SurvivalHardcoreConfig
- TrainingConfig
- LabyrinthConfig
- OneVsOneConfig

Arquivo:
- game/modes/mode_config.py

## 10. Cenas

Cenas principais:
- MainMenuScene
- GameScene
- PauseScene
- GameOverScene
- SettingsScene
- GuideScene
- LeaderboardScene
- PlayerNameScene
- TrainingSetupScene

Arquivos:
- game/scenes/
- game/scenes/game_scene.py
- game/scenes/main_menu_scene.py

## 11. UI

Estrutura de UI:
- navegacao centralizada em UINavigator
- adaptacao de eventos pygame_gui
- componentes reutilizaveis (button, slider, checkbox, text_input, panel, label etc)
- tema via gui_theme e pasta theme

Arquivos:
- game/ui/navigation.py
- game/ui/components/
- game/ui/gui_theme.py

## 12. Audio

Arquitetura:
- EventBus -> AudioDirector -> (AudioRouter + MixerBackend)
- AudioSettingsManager para persistencia e volume runtime
- Catalogo e settings declarativos

Arquivos:
- game/audio/audio_director.py
- game/audio/audio_router.py
- game/audio/mixer_backend.py
- game/audio/audio_settings_manager.py
- game/audio/audio_catalog.py
- game/audio/audio_settings.py

## 13. Factories

Factories principais:
- EnemyFactory
- BulletFactory
- PlayerFactory
- PortalFactory
- CollectibleFactory
- LabyrinthFactory

Arquivo:
- game/factories/

EnemyFactory:
- registries separados: enemy, miniboss, boss
- selecao aleatoria por peso
- criacao por kind via create_by_kind

Arquivo:
- game/factories/enemy_factory.py

## 14. Conteudo de Inimigos (Estado Atual)

Contagem:
- Enemies: 25
- Minibosses: 9
- Bosses: 6
- Total: 40

Lista completa:
- ENEMY_WIKI.md

Nomes amigaveis:
- game/core/enemy_names.py

## 15. Progressao, Score e Ranking

Telemetria de sessao:
- inimigos spawnados por tipo
- coletaveis
- portais destruidos
- dash/parry
- expiracoes

Arquivo:
- game/core/session_stats.py

Score por modo:
- calculo via GameModeStrategy.score_breakdown

Arquivo:
- game/modes/game_mode_strategy.py

Ranking:
- orchestrator e service dedicados

Arquivos:
- game/services/ranking_orchestrator.py
- game/services/ranking_service.py

## 16. Eventos Ambientais e Efeitos de Combate

Eventos ambientais:
- lava
- snow_drift
- water_region
- bullet_cloud
- black_hole

Sistema:
- game/systems/environment_event_system.py

Feedback de combate:
- ExplosionTriggered gera FX e screen shake em GameScene
- cards de boss no HUD por EnemySpawned

Arquivo:
- game/scenes/game_scene.py

## 17. Dados e Arquivos Importantes

- profile do player: player_profile.json
- configuracao de audio: game/assets/audio_settings.json
- instrucoes do workspace: README.md e .github/instructions/gameDeveloper.instructions.md

## 18. Guia Rapido de Extensao

Adicionar novo inimigo:
1. criar behavior em game/behaviors
2. criar factory method em EnemyFactory
3. registrar kind em _ensure_registry com peso
4. mapear nome em enemy_names
5. opcional: descricao em TrainingSetupScene

Adicionar novo modo:
1. implementar GameModeStrategy
2. criar config e spawn/progression strategies
3. registrar no menu principal
4. ajustar HUD, retry e pipeline de systems

Adicionar novo evento de dominio:
1. criar dataclass em events.py
2. publicar em system/cena responsavel
3. assinar handler em consumidor (audio/UI/game scene)
