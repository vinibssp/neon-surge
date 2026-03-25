---
name: criar-novo-modo
description: "Utilize esta skill sempre que o usuário solicitar a criação de um novo modo de jogo (Game Mode) ou estratégia de progressão. Contém o passo a passo exato da arquitetura de modos."
---

# Workflow: Criação de Novo Modo de Jogo

Para criar um novo modo de jogo no Neon Surge 2, siga estritamente os passos abaixo para garantir a coesão da arquitetura orientada a Strategy:

### Passo 1: Definir as Configurações (`game/config.py` ou `game/modes/mode_config.py`)
- Crie uma nova `dataclass` ou constantes para balancear o novo modo (taxa de spawn, limites de pontuação, etc).
- Evite *magic numbers* dentro da lógica do modo.

### Passo 2: Criar as Estratégias (`game/modes/`)
- Crie um arquivo para o novo modo (ex: `capture_mode.py`).
- Implemente uma classe que herde de `GameModeStrategy`.
- O modo deve retornar instâncias de suas estratégias auxiliares:
  - Uma implementação de `SpawnStrategy` (dita *onde* e *quais* inimigos nascem).
  - Uma implementação de `LevelProgressionStrategy` (dita como o nível avança).

### Passo 3: Registrar Eventos e Objetivos Específicos
- Se o modo precisa de regras únicas (ex: capturar uma bandeira, coletar 10 itens), crie um `System` dedicado em `game/systems/` (ex: `CaptureObjectiveSystem`).
- O sistema deve publicar eventos de domínio no `EventBus` e o `GameModeStrategy` deve assinar/consumir esses eventos se precisar determinar o `GameOver` ou `LevelUp`.

### Passo 4: Atualizar UI e Inicialização (`game/scenes/`)
- Adicione a opção do novo modo no `MainMenuScene`.
- Quando instanciar `GameScene`, passe a nova classe de estratégia concreta.
