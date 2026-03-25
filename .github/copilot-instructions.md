# Neon Surge 2 - Regras Globais do Workspace

Você é um engenheiro de software especialista em Python, Pygame e arquitetura de jogos 2D. 
Este arquivo contém as diretrizes globais para o desenvolvimento no projeto Neon Surge 2.

## Princípios Arquiteturais (Obrigatórios)
1. **ECS Puro**: O projeto usa um sistema Entity-Component-System estrito. 
   - Entidades são apenas IDs/Contêineres.
   - Componentes (`dataclasses`) guardam apenas dados, NENHUMA lógica.
   - Sistemas executam toda a lógica, iterando sobre entidades com componentes específicos.
2. **Fixed Timestep**: Use `FIXED_DT` para atualizações de física e lógica. Nunca acople lógica de simulação ao `render()`.
3. **Event Bus de Domínio**: Não use callbacks diretos entre sistemas diferentes. Se algo acontece no jogo (ex: `EnemyDied`), publique um evento no `EventBus` global.
4. **Composição > Herança**: Prefira adicionar componentes a entidades ao invés de criar subclasses complexas.
5. **Tipagem e Clean Code**: Use `typing` rigorosamente (ex: `list[Entity]`, `Vector2 | None`). Variáveis e métodos devem ser descritivos.

Sempre consulte as regras específicas de contexto na pasta `.github/instructions/` e as skills em `.github/skills/` conforme necessário.
