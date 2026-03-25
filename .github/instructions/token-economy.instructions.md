---
applyTo: '**'
---
## Economia de Tokens

### Respostas

- Sem saudações, confirmações ou fechamentos ("Claro!", "Ótimo!", "Espero ter ajudado")
- Sem repetir o que o usuário disse antes de responder
- Sem explicar o que você vai fazer — apenas faça
- Sem resumos do que acabou de ser feito ao final da resposta
- Se houver erro, forneça a correção exata; sem discurso sobre a causa, a menos que seja um problema arquitetural que exija clarificação

### Código

- Omitir código inalterado — usar `# ... (sem alteração)` para blocos não modificados
- Nunca reescrever um arquivo inteiro quando só uma função muda
- Sem comentários que apenas repetem o nome do método ou o que o código obviamente faz
- Quando a edição afetar múltiplos locais, usar ferramentas nativas do editor (`replace_string_in_file`, edições via API) em vez de imprimir blocos para copiar e colar

### Comentários permitidos

- Decisões não óbvias (`# Floyd-Warshall: grafo denso, O(n³) aceitável aqui`)
- Contratos de interface e invariantes de sistema
- TODOs com contexto suficiente para retomar sem perda

### Formato

- Preferir código a prosa sempre que possível
- Listas curtas em linha: `a`, `b`, `c` — não bullet points para 2–3 itens
- Tabelas apenas quando comparando ≥3 atributos de ≥2 entidades
- Sem explicações sobre como a arquitetura funciona ou detalhes de imports, a menos que o usuário pergunte explicitamente

### Nunca truncar

- Lógica de negócio ou regra de domínio incompleta
- Assinaturas de função ou tipos omitidos por brevidade
- Contratos arquiteturais relevantes ao contexto

---

### Técnicas Avançadas de Redução (2025)

**Outputs custam 2–5× mais que inputs** — limitar o tamanho da resposta tem impacto desproporcional no custo total.

**Budget hint:** Quando a resposta exigir raciocínio longo (debugging complexo, refatoração), sinalizar escopo antes de gerar:
- Responder dentro do escopo mínimo necessário
- Omitir passos intermediários óbvios no raciocínio

**Saída estruturada > prosa:** Quando dados precisam ser consumidos por código (configs, listas de entidades, mapeamentos), preferir estrutura direta ao invés de linguagem natural descritiva.

**Evitar few-shot desnecessário:** Exemplos inline no contexto são caros; usar apenas quando o padrão não puder ser inferido pelo tipo e nome.

**Sem reafirmação de contexto:** Nunca reintroduzir informação que já está no histórico da conversa ou nos arquivos do projeto — o contexto já está carregado.