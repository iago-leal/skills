# Protocolo de spawn de archetype efêmero

> Carregue quando o CTO decidir delegar tarefa técnica a um agent especializado.

## 1. Princípio

Archetype é **efêmero**. Não vive em `.claude/agents/`. Existe apenas durante a execução de uma tarefa atômica delimitada. Memória persistente do projeto vive em:

- GitHub (issue, milestone, comments) — estado de execução
- Repo (`docs/adr/`, `prompts/`, código) — decisões e implementação

Sem state em filesystem do agent, sem drift, sem agents abandonados.

## 2. Quando spawnar

Spawne archetype quando a tarefa:
- Tem escopo fechado (1 issue ou sub-tarefa concreta)
- Pertence a especialidade clara (frontend? backend? security? AI? devops? QA? docs?)
- Tem contrato de entrega definido (DoD da issue + critério de aceite)

NÃO spawne para:
- "Pensar em geral" sobre algo (use o orquestrador direto)
- Tarefa que cruza várias especialidades (decomponha primeiro)
- Decisão arquitetural (CTO toma; depois delega implementação)
- Code review (não é função de archetype)

## 3. Fluxo literal de spawn

Passo a passo o orquestrador deve seguir, em ordem:

### 3.1 Identificar o archetype

Tabela de decisão:

| Sinal na issue / contexto | Archetype |
|---|---|
| Componente de UI, formulário, página, estado de cliente | `frontend-dev` |
| API, modelo de dados, integração de serviço | `backend-dev` |
| Prompt, eval, classificação ML, RAG, chamada a Claude/GPT | `ai-engineer` |
| Auth, autz, criptografia, segredo, threat model | `security-engineer` |
| CI/CD, deploy, observabilidade, runbook, infra | `devops` |
| Plano de teste, automação E2E, harness de fuzzing | `qa-engineer` |
| README, docs/, ADR-as-prosa, changelog | `tech-writer` |

Em casos limítrofes (ex: "API que chama LLM"), preferir o archetype dominante (`ai-engineer` se a complexidade está na chamada; `backend-dev` se está no design da API). Se realmente ambíguo, decompor em duas issues.

### 3.2 Carregar a definição do archetype

### 3.2 Carregar a definição do archetype

Ler o arquivo `references/archetypes/<archetype>.md`.

A definição contém: identidade, quando é chamado, contrato, o que NÃO faz, heurísticas.

### 3.3 Coletar contexto do projeto

Em paralelo:

### 3.3 Coletar contexto do projeto

Em paralelo:

1. Executar: `python scripts/briefing.py --json`
2. Executar: `gh issue view <N> --json title,body,comments,labels,milestone,assignees`
3. Ler: `docs/adr/<adrs-relevantes>.md` (cada ADR mencionado na issue ou no milestone)

Se houver `ARCHITECTURE.md`, ler o arquivo.
Se houver `RSOP/lista_problemas.md`, ler e filtrar problemas relevantes ao escopo.

### 3.4 Compor o prompt

Template literal:

```
{conteúdo de references/archetypes/<archetype>.md}

---

## Briefing do projeto
{output JSON de briefing.py}

---

## Arquitetura
{ARCHITECTURE.md ou "N/A se ainda não existe"}

---

## ADRs relevantes
{conteúdo dos ADRs lidos, separados por ---}

---

## Issue alvo
**Número**: #{N}
**Título**: {title}
**Labels**: {labels}
**Milestone**: {milestone}

### Corpo
{body}

### Comentários relevantes (achados anteriores)
{comments}

---

## Tarefa específica para você

{descrição precisa do que esse archetype precisa entregar nesta invocação —
escrita pelo CTO, não copiada da issue. Pode ser um sub-passo da issue.}

## Contrato de entrega
- Você entrega: {artefatos esperados — branch+PR? rascunho de ADR? script de migração? tests?}
- Você NÃO entrega: {coisas fora de escopo}
- Critério de aceite: {checklist binário}

## Restrições do projeto
- Stack: {do ARCHITECTURE.md}
- Convenções: {do ARCHITECTURE.md}
- Guardrails: {do ARCHITECTURE.md + ADRs}

## Output
Retorne ao CTO:
1. Resumo do que foi feito (1 parágrafo)
2. Link para PR/branch/arquivo gerado
3. Itens fora de escopo que você identificou (NÃO os faça — reporte)
4. Riscos/dúvidas que ficaram em aberto
```

### 3.5 Delegar ou Executar Diretamente (v1.3.0)

Dependendo das ferramentas disponíveis no seu ambiente:

**Modo Subagent:**
Se você possuir uma ferramenta de delegação (ex: tool `Agent`), invoque-a passando a definição do archetype como prompt de sistema e o prompt composto acima como a tarefa. O subagent será instanciado efemeramente.

**Modo Auto-Persona:**
Se você NÃO possuir uma ferramenta de subagent (ex: operando no Antigravity), você mesmo assumirá a persona temporariamente:
1. Declare ao usuário: "Assumindo persona de `<archetype>` para esta tarefa."
2. Execute a tarefa descrita no prompt usando as suas ferramentas nativas, respeitando estritamente o contrato e as heurísticas lidas em `archetypes/<archetype>.md`.
3. Ao terminar, retorne à persona do CTO e siga para o passo de consolidação.

### 3.6 Consolidar resultado

Quando o subagent retornar:

1. Analisar o resumo + entregáveis gerados
2. Postar comentário na issue:
   ```bash
   python scripts/issue.py update --number <N> --finding "<resumo + link para PR/branch + dúvidas em aberto>"
   ```
3. Se subagent reportou risco/dúvida, decidir:
   - Resolver pessoalmente (CTO + usuário)
   - Abrir issue `spike` para investigar
   - Bloquear issue atual com label `blocked` + finding explicando

## 4. Encadeamento de archetypes

Comum: tarefa que precisa de mais de um archetype em sequência.

Exemplo: "Adicionar autenticação OIDC".

```
backend-dev → implementa middleware OIDC + testes unitários
  ↓
security-engineer → revisa configuração de OIDC, valida que não vaza segredo
  ↓
qa-engineer → escreve teste E2E que valida fluxo de login
  ↓
tech-writer → atualiza README + docs/architecture/auth.md
  ↓
devops → adiciona env vars no deploy + alarme em /auth/* error rate
```

Cada um é um spawn independente, com contexto fresco. CTO orquestra entre eles, não delega para um archetype "fazer tudo".

## 5. Anti-padrões de spawn

- **Spawn sem critério de aceite** — archetype não sabe quando parar; volta com algo "completo" mas que não bate com a issue
- **Spawn sem ADRs no contexto** — archetype propõe solução que viola decisão já tomada
- **Spawn sem briefing** — archetype não sabe estado do projeto, prazos, bloqueios; entrega solução isolada
- **Spawn de archetype errado** — `backend-dev` recebendo tarefa de threat model entrega checklist genérico, não threat model rigoroso
- **Spawn em paralelo de archetypes interdependentes** — entregam soluções que não combinam; CTO precisa reconciliar manualmente
- **Persistir archetype** — escrever `.claude/agents/backend-dev.md` no projeto. Vira state mutável que diverge do `references/archetypes/backend-dev.md` original. Não fazer.

## 6. Custo de spawn

Cada spawn = 1 sub-conversa com janela de contexto independente. Pesos para considerar:

- **Tempo**: archetype precisa ler todo o contexto que você passou. Quanto maior, mais lento começa.
- **Tokens**: contexto maior = custo maior. Não inclua ADR/RSOP irrelevantes "só por garantia".
- **Consolidação**: archetype retorna texto que o CTO precisa processar. Texto demais = CTO gasta turno consolidando.

Heurística: se o spawn vai economizar > 5 turnos do CTO direto, vale. Se < 3, faça você mesmo.
