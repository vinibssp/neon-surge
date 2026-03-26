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
- Sempre busque SKILL adequada para sua atividade atual.

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
- Transições pesadas de cena iniciadas por eventos de domínio (ex.: `PlayerDied`) devem ser enfileiradas e efetivadas no fim do `update()` da cena atual

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
- Mudanças de cena disparadas durante handlers/eventos devem ser aplicadas fora do loop crítico de systems para evitar hitch na simulação

### Event Bus de Domínio

- Um único `EventBus` global para eventos de domínio (sem barramentos paralelos)
- Systems publicam no `EventBus`; consumidores transversais (áudio/UI) registram handlers diretamente nele
- `GameScene` registra/desregistra handlers de gameplay no ciclo `on_enter()`/`on_exit()`
- Não usar flags globais para transições de estado
- Evitar roteamento espalhado baseado em `isinstance`
- Eventos de explosão de domínio (`ExplosionTriggered`) devem acionar feedback visual (animação + tremor de tela) na orquestração de cena/render, sem acoplamento da regra de dano

### Factories

- Toda criação de entidade passa por factory
- Factory monta componentes, tags e strategies
- `EnemyFactory` mantém registries distintos para `enemy`, `miniboss` e `boss`
- Factory expõe criação por tipo/categoria; não decide política de spawn por modo
- Evolução de roster de inimigos base deve ocorrer por novos tipos registrados (arquétipos), sem ramificações condicionais em systems de spawn
- Evolução de roster de `miniboss` e `boss` deve seguir o mesmo princípio (registro por tipo no factory), preservando contratos públicos de seleção por categoria
- Evoluções temáticas de roster (ex.: inspiração em jogos bullet-hell) devem manter o mesmo contrato de registro por arquétipo e desbloqueio progressivo por estratégia de spawn

### Strategy Pattern

- Variabilidade por strategy em IA, modos de jogo e renderização
- Modos concretos suportados: `RaceMode`, `RaceInfiniteMode`, `SurvivalMode`, `SurvivalHardcoreMode`, `LabyrinthMode`, `TrainingMode`
- Cada modo define systems, spawn, progressão e HUD
- Estratégias de spawn do modo devem controlar categoria/tipo spawnado (enemy/miniboss/boss)
- `TrainingMode` deve receber plano declarativo de spawn (tipo -> quantidade) vindo da UI de treino com abas por categoria
- Estratégias de spawn devem aplicar progressão de roster por fase (nível/tempo), liberando arquétipos de maior pressão de forma gradual
- Evitar comportamento condicional por tipo dentro de systems centrais
- Arquétipos de inimigo com estados especiais (ex.: suporte/buff, invulnerabilidade por fase, hazards persistentes) devem expor estado por componente e lógica em behavior/system dedicado
- Novos padrões de combate devem priorizar behaviors dedicados e reutilizáveis (composição), evitando ramificações por tipo em systems globais


### Command Pattern

- Input de gameplay -> Command -> alvo (entidade/system)
- Para UI, usar eventos de alto nível do framework pygame_gui + adapter fino
- Gameplay deve suportar ação de parry por comando dedicado, desacoplada do input físico
- Inimigos sob efeito de stagger do parry nao devem causar dano ao player (contato ou projeteis)

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
- contexto `game_over` deve tocar uma vez e transicionar automaticamente para contexto `menu`
- transições de música devem ser centralizadas no `AudioDirector`

Resiliência operacional:

- falhas de áudio não podem quebrar loop de jogo
- métodos do backend devem isolar exceções e degradar para modo silencioso quando necessário
- ajustes de volume em runtime devem passar por gerenciador global (`AudioSettingsManager`)
- persistência de `music_volume` e `sfx_volume` deve ficar fora da camada de UI
- controles de `music_volume` e `sfx_volume` na UI devem refletir e aplicar valor imediatamente (slider + ajuste incremental)

---

## UI, Menus e Cenas de Menu (Design e Arquitetura)

### UI System

- UI orientada a composição (`builders`, `configs`, `controllers`)
- Estado de foco/seleção com fonte única de verdade
- Componentes declarativos e reutilizáveis
- Componentes devem ser criados por factories declarativas (`ButtonConfig`, `LabelConfig`, `PanelConfig`, `SliderConfig`, `CheckboxConfig`, `TextInputConfig`, `StatusBarConfig`)
- Decisões de tema/estilo centralizadas e desacopladas da regra de fluxo
- Componentes visuais não devem conter regra de domínio

### Navegação de UI

- Contrato único: evento `pygame_gui` -> `PygameGUIEventAdapter` -> `UINavigator` -> ação
- `UINavigator` deve operar sobre `FocusableControl` (não apenas botão), suportando no mesmo fluxo: `button`, `slider`, `checkbox`, `text_entry`
- `PygameGUIEventAdapter` é a fronteira única para mouse/teclado/eventos do framework; cenas não podem criar rota paralela de navegação
- A lista ordenada de `controls` é a fonte oficial da ordem de foco
- `UINavigated`, `UIConfirmed` e `UICancelled` devem continuar sendo o contrato de evento de domínio para feedback transversal (áudio/UI)
- Sem navegação baseada em “player cursor”
- Sem tradução manual de input bruto para navegação de menu
- Evitar caminhos paralelos/ambíguos para confirmar, cancelar e navegar

### Menu Scenes

- `BaseMenuScene` é o contrato base para ciclo de menu (`input/update/render`)
- Cenas de menu devem orquestrar transições, não implementar motor de navegação
- Cenas devem registrar navegação via `set_navigator(controls=..., actions=...)`; `buttons=` é compatibilidade legada e não deve ser usado em novas telas
- Ordem de foco deve refletir ordem de ações registradas
- Cancelamento (`Esc`/`B`) explícito e consistente por cena
- Overlays com contrato compartilhado via composição/factory (ex.: `OverlaySceneFactory`)
- `PauseScene` deve ser overlay transparente e congelar gameplay por regra do `SceneStack` (apenas topo atualiza)
- `Esc` em gameplay abre pausa; `Esc` na pausa/submenu fecha o overlay atual
- Menu de pausa padrão: retomar, configurações, abandonar partida
- Configurações de pausa devem aceitar mouse + teclado/gamepad no mesmo contrato de navegação
- `SettingsScene` deve ser reutilizável entre menu principal e pausa, sem duplicar lógica de áudio por cena
- `GameOverScene` deve exibir causa da morte e estatisticas da sessao encerrada, sem acoplar coleta de dados ao render

### Evolução de Menus

- Novas telas devem estender por composição, não duplicar estrutura
- Separar layout/configuração da decisão de fluxo
- Evitar números mágicos de layout; preferir specs/configs declarativos
- Interações de confirmação devem permanecer no `UINavigator` (inclusive toggle de `checkbox`), sem lógica duplicada na cena
- Preservar contratos públicos estáveis para evolução incremental

---

## Configuração por Modo

- Evitar números mágicos em blocos de regra
- `config.py` contém base global
- Presets (`RaceConfig`, `RaceInfiniteConfig`, `SurvivalConfig`, `SurvivalHardcoreConfig`, etc.) concentram tuning por modo
- Presets de modo devem concentrar tuning de política de spawn por categoria
- Tuning global de dificuldade deve priorizar curva progressiva: frequência de spawn, chance por categoria e desbloqueio de roster
- Presets de sobrevivência devem concentrar hazards periódicos (ex.: lava): intervalo, aviso, duração ativa e janela de pisca de encerramento
- Lava deve poder surgir em regiões variadas da arena (não fixa na borda), mantendo o mesmo contrato de aviso, janela ativa e pisca final
- Presets de sobrevivência devem concentrar eventos ambientais periódicos (neve/água/nuvem de balas/buraco negro): intervalo global, duração e intensidade por evento
- Lava integra o sistema de eventos ambientais e deve respeitar exclusividade: apenas um evento ativo por vez
- Presets de sobrevivência devem concentrar progressão de coletáveis especiais e habilidades de pico (ex.: bomba nuclear por limiar de coleta)

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