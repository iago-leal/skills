# AI Engineering vs. Vibe Coding

> Carregue quando estiver decidindo qualquer integração de LLM (Large Language Model) em produto.

## 1. Definições operacionais

**Vibe coding** — usar LLM em produto sem contrato, sem eval, sem telemetria, sem fallback. "Vai dando certo." Funciona em demo. Quebra em prod, silenciosamente, em casos que não estavam na cabeça do dev quando codou.

**AI engineering** — tratar LLM como componente de sistema. Tem contrato (prompt versionado, schemas), avaliação (offline + online), observabilidade (telemetria estruturada), degradação graciosa (fallback determinístico) e custo declarado (budget de tokens).

**O CTO recusa vibe coding em produto.** Em PoC (Proof of Concept) ou spike, vibe coding é OK como ferramenta de descoberta — mas vira spike timeboxed, não feature.

## 2. Os 5 itens não-negociáveis

Antes de merge de qualquer feature que use LLM em código de produção, todos os 5:

### 2.1 Contrato de prompt versionado

Arquivo `prompts/NNNN-task.md` com:
- `task` (descrição curta)
- `version` SemVer
- `model` (ID literal — ex: `claude-haiku-4-5-20251001`)
- `## Input Schema` (JSON Schema)
- `## Output Schema` (JSON Schema)

Bump de versão = mudança de prompt. Mudança não-aditiva = major. Eval offline reroda em todo bump.

Criar via: `python scripts/prompt_contract.py --task ...`

### 2.2 Eval offline

`evals/<task>/cases.jsonl` — uma linha por caso, formato:

```json
{"id": "case-001", "input": {...}, "expected": {...}, "criteria": "exact_match | contains | json_match | custom"}
```

GitHub Action roda eval em todo PR que mexe em `prompts/<task>.md` ou em código que consome o prompt. Falha se taxa de pass cair abaixo de threshold (default 0.85; configurável por task).

Sem eval offline, qualquer ajuste de prompt é poker.

### 2.3 Telemetria de produção

Campos estruturados emitidos em **todo request**:

| Campo | Tipo | Por quê |
|---|---|---|
| `request_id` | UUID | Correlação cross-service |
| `prompt_version` | SemVer string | Atribuir comportamento à versão certa do prompt |
| `model` | string | Detectar drift quando model é atualizado |
| `tokens_in` | int | Custo + bater com budget |
| `tokens_out` | int | Custo + detectar respostas anormalmente longas |
| `latency_ms` | int | SLA |
| `confidence` | float [0,1] ou null | Decisão de fallback |
| `fallback_used` | bool | Métrica de qualidade do prompt principal |

Sem telemetria, você não sabe se está em outage de qualidade — só vê reclamação.

### 2.4 Fallback determinístico

Quando confidence < threshold (ou erro do LLM), caminho alternativo determinístico:
- Regra simples (regex, lookup, template)
- Resposta padrão segura
- Encaminhamento para humano

Sem fallback, queda do provedor de LLM = queda da feature inteira.

### 2.5 Budget de tokens declarado

`budget_tokens` no frontmatter do prompt = teto **por chamada**. Alarme se p95 do uso real exceder por 7 dias seguidos. Métrica de saúde do contrato.

Custo previsível é pré-requisito para colocar feature LLM em produto com tráfego real.

## 3. Anti-padrões e como o CTO reage

| Anti-padrão | Sinal | Reação |
|---|---|---|
| "Vou prompt-engenhar até funcionar" | Sem `prompts/`, sem `evals/` | Recusa merge; pede ADR + scripts |
| "O modelo entende o contexto" | Sem schema de input/output | Recusa; exige JSON Schema |
| "É rápido, não precisa fallback" | Sem caminho alternativo | Recusa; pede fallback ou abre spike pra desenhar |
| "Tokens não são problema" | Sem `budget_tokens` | Recusa; pede budget + alarme |
| "Eu testei manualmente" | Sem `cases.jsonl` | Recusa; pede mínimo 20 casos com expected |
| "Vou só melhorar o prompt" | Sem bump de versão, sem rerun de eval | Recusa; pede SemVer e CI |
| "O Claude/GPT é bom, não precisa monitorar" | Sem telemetria | Recusa; pede 8 campos mínimos |

## 4. Quando o CTO aceita LLM em produto

Quando, antes de abrir issue `feat`:

1. ADR aceito documentando: por que LLM (vs. regra/heurística), qual modelo (vs. alternativos), qual provedor (vs. self-hosted), qual fallback
2. `prompts/NNNN-task.md` criado e versionado
3. `evals/<task>/cases.jsonl` com 20+ casos cobrindo happy path + edge cases
4. Action de eval configurada e passando
5. Telemetria com 8 campos mínimos prevista
6. Fallback determinístico desenhado
7. Budget de tokens definido + alarme

Issue de implementação só é aberta após esses 7 prontos. CTO trata isso como pre-flight check, não burocracia.

## 5. Cheat sheet de decisão

```
Tem regra/heurística que resolve 80%+ casos?
  └─ SIM → use a regra. LLM como fallback ou enriquecimento.
  └─ NÃO → LLM como caminho principal, com fallback determinístico.

Output precisa ser estruturado?
  └─ SIM → JSON mode + JSON Schema rigoroso. Eval = json_match.
  └─ NÃO → text gen com critério "contains" ou avaliação humana amostral.

Latência crítica (<500ms)?
  └─ SIM → modelo pequeno (Haiku) + cache + fallback rápido.
  └─ NÃO → modelo apropriado para qualidade.

Privacidade alta (PII, PHI)?
  └─ SIM → ADR de DPA (Data Processing Agreement); redaction antes do prompt; logs sem dados sensíveis.
  └─ NÃO → telemetria padrão.

Volume alto (>1k req/min)?
  └─ SIM → batch API se aplicável; cache agressivo; budget muito restrito.
  └─ NÃO → real-time padrão.
```

## 6. Modelos Claude (referência rápida)

| Família | Quando |
|---|---|
| Opus 4.7 | Reasoning complexo, agente orquestrador, decisões arquiteturais |
| Sonnet 4.6 | Trabalho geral de produção, balanceando custo/qualidade |
| Haiku 4.5 | Latência crítica, classificação, extração simples, alto volume |

Em ADR de escolha de modelo, sempre incluir: prompt benchmark contra próximo modelo na escala (Haiku → Sonnet, Sonnet → Opus) com 50+ casos antes de upgrade.
