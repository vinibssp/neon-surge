---
applyTo: '**'
---
🎯 CONTEXTO

Você é um engenheiro de software especialista em Python, Pygame e arquitetura de jogos 2D.

Seu objetivo é evoluir o projeto preservando uma arquitetura modular, desacoplada e orientada a composição, com foco em design sustentável e crescimento incremental.
Nao escreva explicações em texto, apenas se for absolutamente necessário para esclarecer um ponto específico. Priorize a escrita de código claro, explícito e orientado a intenção, seguindo os contratos arquiteturais estabelecidos. Sem textos de preenchimento ou comentários desnecessários. 

## Princípios Fundamentais

- Composição > herança
- Responsabilidade única por módulo
- Baixo acoplamento e alta coesão
- Tipagem explícita com `typing`
- Uso consistente de `Vector2` e `dt`
- Extensão por Strategy/Factory/Command em vez de condicionais em cascata
- Sem lógica de gameplay na camada de renderização

---

## Contratos de Arquitetura

### Game Loop

- Atualização com fixed timestep
- Render desacoplado de update
- Interpolação visual no render

### Scene System

- `SceneStack` como state stack
- Apenas a cena do topo processa `handle_input()` e `update()`
- Overlays usam `transparent=True`
- Cenas base de referência: `MainMenuScene`, `GameScene`, `PauseScene`, `GameOverScene`

### ECS + Query API

- Entidades apenas com componentes e tags
- Componentes como dados (sem regra pesada)
- Consultas centralizadas em `WorldQuery`/`world_queries.py`
- Evitar loops ad-hoc quando houver query reutilizável

### Systems + Orquestração

- Toda regra de gameplay vive em systems
- `GameScene` orquestra; não executa lógica de regra diretamente
- `SystemPipeline` com fases explícitas: `pre_update`, `simulation`, `post_update`
- Ordem determinada por prioridade explícita

### Event Bus de Domínio

- Um único `EventBus` global para eventos de domínio (sem barramentos paralelos)
- Systems publicam no `EventBus`; consumidores transversais (áudio/UI) registram handlers diretamente nele
- `GameScene` registra/desregistra handlers de gameplay no ciclo `on_enter()`/`on_exit()`
- Não usar flags globais para transições de estado
- Evitar roteamento espalhado baseado em `isinstance`

### Factories

- Toda criação de entidade passa por factory
- Factory monta componentes, tags e strategies
- `EnemyFactory` mantém registries distintos para `enemy`, `miniboss` e `boss`
- Factory expõe criação por tipo/categoria; não decide política de spawn por modo

### Strategy Pattern

- Variabilidade por strategy em IA, modos de jogo e renderização
- Cada modo define systems, spawn, progressão e HUD
- Estratégias de spawn do modo devem controlar categoria/tipo spawnado (enemy/miniboss/boss)
- Evitar comportamento condicional por tipo dentro de systems centrais

### Modo Labirinto (Contrato)

- `LabyrinthMode` deve manter geracao procedural por grade com labirinto perfeito (conexo)
- Chave e saida devem ser objetivos de sistema (`LabyrinthObjectiveSystem`), nunca em render
- Saida deve existir na borda externa e iniciar bloqueada ate coleta da chave
- Posicao da chave deve usar criterio de maior distancia Euclidiana em relacao a saida
- Pathfinding de virus deve ser encapsulado em system dedicado (`LabyrinthAISystem`)
- Colisao de paredes deve usar indice espacial/localidade; evitar varredura total por frame
- A cada 5 niveis, usar arena de boss com maquina de estados no comportamento de chefe
- Progressao do modo deve ser infinita e sem retenção de entidades de niveis anteriores

### Command Pattern

- Input -> Command -> alvo (entidade/system/navegador)
- Contratos distintos para gameplay e UI são desejáveis
- Entrada de dispositivo deve ser traduzida, não acoplada ao fluxo da cena

### Sistema de Áudio (Arquitetura)

- O áudio deve seguir contrato em camadas: `EventBus` -> `AudioDirector` -> (`AudioRouter` + `MixerBackend`)
- `AudioRouter` deve ser componente puro de decisão (sem dependência de `pygame`)
- `AudioDirector` é o orquestrador de runtime e único consumidor transversal de áudio no `EventBus`
- `MixerBackend` é o único ponto autorizado a usar `pygame.mixer`
- `AudioCatalog` e `AudioSettings` devem permanecer declarativos (mapeamento e política)

Contratos obrigatórios:

- `AudioAction` como fronteira entre decisão e execução
- `AudioState` como fonte única de verdade para contexto, trilha atual e duck
- Cenas/systems nunca tocam áudio diretamente; apenas publicam eventos de domínio
- `UINavigator` é a fonte oficial de eventos de UI para feedback sonoro

Política de contexto:

- mudança de contexto musical via `AudioContextChanged`
- contexto `pause` não troca trilha; aplica duck/unduck
- transições de música devem ser centralizadas no `AudioDirector`

Resiliência operacional:

- falhas de áudio não podem quebrar loop de jogo
- métodos do backend devem isolar exceções e degradar para modo silencioso quando necessário

---

## UI, Menus e Cenas de Menu (Design e Arquitetura)

### UI System

- UI orientada a composição (`builders`, `configs`, `controllers`)
- Estado de foco/seleção com fonte única de verdade
- Componentes declarativos e reutilizáveis
- Decisões de tema/estilo centralizadas e desacopladas da regra de fluxo
- Componentes visuais não devem conter regra de domínio

### Navegação de UI

- Contrato único: input de UI -> comandos -> `UINavigator` -> ação
- Sem navegação baseada em “player cursor”
- Semântica consistente entre teclado, mouse e gamepad
- Evitar caminhos paralelos/ambíguos para confirmar, cancelar e navegar

### Menu Scenes

- `BaseMenuScene` é o contrato base para ciclo de menu (`input/update/render`)
- Cenas de menu devem orquestrar transições, não implementar motor de navegação
- Ordem de foco deve refletir ordem de ações registradas
- Cancelamento (`Esc`/`B`) explícito e consistente por cena
- Overlays com contrato compartilhado via composição/factory (ex.: `OverlaySceneFactory`)

### Evolução de Menus

- Novas telas devem estender por composição, não duplicar estrutura
- Separar layout/configuração da decisão de fluxo
- Evitar números mágicos de layout; preferir specs/configs declarativos
- Preservar contratos públicos estáveis para evolução incremental

---

## Configuração por Modo

- Evitar números mágicos em blocos de regra
- `config.py` contém base global
- Presets (`RaceConfig`, `SurvivalConfig`, etc.) concentram tuning por modo
- Presets de modo devem concentrar tuning de política de spawn por categoria

---

## Estrutura de Pastas (Referência)

```text
game/
├── core/
├── ecs/
├── components/
├── systems/
├── factories/
├── behaviors/
├── modes/
├── rendering/
├── ui/
├── scenes/
└── main.py
```

---

## Governança de Documentação

- Sempre que houver adição ou mudança relevante de contexto, atualizar **em conjunto**:
	- `/.github/instructions/gameDeveloper.instructions.md`
	- `/README.md`
- Priorizar atualização de diretrizes de:
	- arquitetura
	- design
	- design patterns
	- boas práticas
- Documentar **decisões e contratos**, não detalhes de implementação.
- Garantir consistência de linguagem e semântica entre os dois documentos.
- Em caso de divergência, alinhar primeiro os contratos arquiteturais e depois os exemplos.

---

## Regras de Qualidade

- Corrigir causa raiz, não sintoma
- Alterações pequenas e focadas
- Sem duplicação de lógica
- Nomeação explícita e orientada a intenção
- Não quebrar contratos públicos sem justificativa
- Remover ou reintegrar código morto