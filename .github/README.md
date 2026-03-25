# 🤖 Guia de Customização da IA (GitHub Copilot)

Este diretório contém as regras, fluxos de trabalho (skills) e diretrizes de arquitetura para o projeto **Neon Surge 2**. O objetivo desta estrutura é alinhar o comportamento do GitHub Copilot com as melhores práticas, padrões de código e a arquitetura específica do jogo.

Aqui está um passo a passo simples de como utilizar e expandir esta estrutura, tanto para desenvolvedores humanos quanto para a própria IA.

---

## 👨‍💻 Para os Desenvolvedores: Como Ensinar a IA

Sempre que o projeto ganhar um novo padrão, você pode "ensinar" a IA criando ou editando os arquivos abaixo. O VS Code e o GitHub Copilot lerão esses arquivos automaticamente.

### 1. Regras Globais (Para todo o projeto)
Se você quer que a IA sempre siga uma regra (ex: "Sempre use ECS puro", "Sempre digite as variáveis"), edite o arquivo:
📄 `.github/copilot-instructions.md`

### 2. Regras Específicas de Contexto (Por pasta/arquivo)
Se você tem regras que só servem para uma parte do código (ex: "Sempre use `pygame_gui` na pasta de UI"), crie um arquivo dentro de `.github/instructions/`.

**Passo a passo:**
1. Crie um arquivo terminando em `.instructions.md` (ex: `audio.instructions.md`).
2. No topo do arquivo, coloque o cabeçalho `applyTo` informando onde a regra se aplica:
   ```yaml
   ---
   applyTo: 'game/audio/**'
   ---
   ```
3. Escreva as regras logo abaixo.

### 3. Criando novos Fluxos de Trabalho (Skills)
Se você quer que a IA aprenda a executar uma tarefa complexa passo a passo (ex: "Como criar um novo inimigo" ou "Como fazer o build do jogo"), crie uma **Skill**.

**Passo a passo:**
1. Crie uma pasta em `.github/skills/` com o nome da tarefa (ex: `criar-inimigo`).
2. Dentro dela, crie um arquivo chamado `SKILL.md`.
3. Adicione o bloco de metadados no topo usando YAML Frontmatter:
   ```yaml
   ---
   name: criar-inimigo
   description: "Use esta skill quando o usuário pedir para criar um novo tipo de inimigo."
   ---
   ```
4. Escreva o passo a passo (Workflow) detalhado de como a tarefa deve ser feita na arquitetura atual.

**Como invocar?** No chat do Copilot, basta pedir a tarefa (ex: *"Crie um inimigo atirador"*), e a IA automaticamente buscará e usará a skill correspondente.

---

## 🧠 Para a Inteligência Artificial (Copilot)

Ao interagir com este repositório, você (IA) **deve obrigatoriamente** seguir estas diretrizes operacionais:

1. **Prioridade Absoluta:** O conteúdo de `.github/copilot-instructions.md` e dos arquivos `.instructions.md` tem precedência sobre o seu conhecimento base genérico de Python ou Pygame.
2. **Match de Contexto:** Antes de sugerir edições ou criar arquivos, verifique silenciosamente se a rota do arquivo corresponde a alguma regra em `instructions/` (via `applyTo`).
3. **Leitura de Skills:** Quando o usuário solicitar a criação de uma mecânica, entidade, modo de jogo, ou relatar um bug estrutural, faça um *scan* mental nas skills disponíveis em `.github/skills/`. Se uma skill (`SKILL.md`) for aplicável (ex: `ecs-debugging` ou `criar-novo-modo`), carregue o conteúdo usando a ferramenta `readFile` **ANTES** de gerar código ou responder.
4. **Sem Textos de Preenchimento:** Siga o contrato de respostas diretas, orientadas à intenção e sem explicações exaustivas, conforme definido em `gameDeveloper.instructions.md`.

---
*Mantenha este repositório vivo! À medida que o código evolui, estas regras devem evoluir junto.*