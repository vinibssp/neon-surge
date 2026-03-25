---
name: ecs-debugging
description: "Utilize esta skill sempre que o usuário relatar comportamentos estranhos na física, renderização ou ECS, lentidão, gargalos de performance, ou problemas onde sistemas parecem não atualizar entidades."
---

# Workflow: Debugging e Resolução de Problemas no ECS

Siga este checklist quando estiver diagnosticando problemas na engine (Entity-Component-System):

### 1. Entidade não está fazendo o que deveria?
- **Verifique a Query**: O `WorldQuery` do sistema está cobrindo todos os componentes necessários? O componente recém-adicionado está na tupla de `component_types` do filtro?
- **Inatividade**: A entidade está com `entity.active = False`? As queries, por padrão, ignoram entidades inativas.
- **Factory Completa**: Garanta que a factory (em `game/factories/`) incluiu a tag ou componente necessário para aquele comportamento.

### 2. Entidade não some da tela após a morte?
- **Remoção Pendente**: A entidade foi passada para `world.remove_entity()`? No final do frame, `apply_pending()` deve ser chamado.
- **Vazamento no Render**: O sistema de renderização não deve manter referências diretas às entidades.

### 3. Jogo lento ou travando (Performance Drops)?
- **Queries Repetitivas**: O sistema está usando laços aninhados massivos? O ECS puro pode ser gargalo se a consulta (`world.query(...)`) for feita em demasia. Tente fazer cache das entidades da query caso não sejam alteradas todo frame.
- **Criação de Objetos**: Instanciar muitos `Vector2` por frame dentro de loops profundos pode causar overhead do Garbage Collector do Python.
- **Componente vs Variável Global**: Lógica de verificação muito global ou cálculos custosos (ex: distâncias radiais para colisão de milhares de partículas) devem usar indexação espacial.

### 4. Erros e Concorrência de Sistemas
- Revise o `SystemPipeline`. A fase do sistema é crucial. Por exemplo:
  - `CollisionSystem` DEVE rodar preferencialmente na fase `SIMULATION` logo após o `MovementSystem`.
  - Destruição e spawns extras devem ficar no `POST_UPDATE` para não mudar arrays de entidades enquanto iteramos sobre elas.
