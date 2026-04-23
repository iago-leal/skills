# Rubrica de Determinismo — 5 Dimensões

Rubrica oficial aplicada por `scripts/spec_scorer.py` para avaliar uma `SPEC.md`. Score total 0–100.

**Princípio-guia:** uma SPEC é determinística quando dois agentes diferentes, executando-a em máquinas diferentes, produzem skills funcionalmente idênticas. Cada dimensão mede uma faceta disso.

---

## Pesos

| Dimensão | Peso | Razão |
|----------|------|-------|
| **Determinismo** | 30 | Núcleo do valor da SPEC — ambiguidade aqui invalida tudo |
| **Reprodutibilidade** | 25 | Mesma entrada em qualquer agente → mesma saída |
| **Completude** | 20 | Seção faltando = ponto de improvisação = divergência |
| **Testabilidade** | 15 | Sem critério verificável, não dá para saber se foi cumprida |
| **Delimitação** | 10 | Sem "NÃO faz" explícito, a skill cresce por acidente |
| **Total** | **100** | |

---

## 1. Determinismo (30 pts)

**Mede:** ausência de ambiguidade semântica na especificação.

| Sinal | Pontos |
|-------|--------|
| Todas as dependências Python têm versão pinada (`==X.Y.Z`) ou justificativa explícita para `latest` | 6 |
| Valores de configuração são literais (não "algo próximo de 1000") | 6 |
| Caminhos de arquivos/diretórios são absolutos ou relativos explícitos (não "na pasta da skill") | 4 |
| Outputs JSON têm schema completo com tipo de cada campo | 5 |
| CLI de cada script está especificada com flags, tipos, defaults | 5 |
| Nenhum uso de "geralmente", "normalmente", "geralmente", "se necessário" em prescrições técnicas | 4 |

**Red flags (−5 cada, até −15):**
- "Use o modelo adequado" sem listar os aceitos
- "Trate erros apropriadamente" sem tabela de exit codes
- Referência a "padrão X" sem apontar o arquivo/skill/código exato
- Versões só no CHANGELOG mas não na seção de deps

---

## 2. Reprodutibilidade (25 pts)

**Mede:** se outro agente, em outra máquina, produziria a mesma skill.

| Sinal | Pontos |
|-------|--------|
| Estrutura de arquivos obrigatória é desenhada em árvore ASCII literal | 5 |
| Frontmatter do SKILL.md é literal (copia-e-cola, não descrição narrativa) | 5 |
| Corpo do SKILL.md tem seções listadas em ordem com conteúdo mínimo de cada | 4 |
| Dependências de sistema incluem comando de instalação por plataforma | 4 |
| Dados persistidos têm schema literal (não "um json com as configurações") | 4 |
| Fluxo interativo, se houver, tem mock completo com prompts literais | 3 |

**Red flags (−5 cada, até −10):**
- "Igual à skill X" sem citar a versão/commit de X
- Diagrama ASCII diferente entre seções (ex: seção 2 diz `scripts/` mas seção 4 fala de `cli/`)
- Contradição entre texto narrativo e tabela estruturada

---

## 3. Completude (20 pts)

**Mede:** presença das 11 seções obrigatórias do template, sem campos vazios.

| Seção | Pontos |
|-------|--------|
| 1. Identidade (tabela) | 2 |
| 2. Estrutura de Arquivos | 2 |
| 3. SKILL.md (frontmatter + corpo) | 3 |
| 4. Scripts (ou `N/A` justificado) | 2 |
| 5. Dependências (ou `N/A`) | 2 |
| 6. Armazenamento (ou `N/A`) | 1 |
| 7. Padrões de Implementação | 2 |
| 8. Fluxo Interativo (ou `N/A`) | 1 |
| 9. Critérios de Aceite | 2 |
| 10. O que NÃO faz | 2 |
| 11. Propósito (cabeçalho) | 1 |

**Penalidade:** cada seção marcada `N/A` sem justificativa de 1 frase → −1 ponto.

**Red flags:**
- Campo em branco (sem `N/A` explícito) → −3 pts
- Seção presente mas com placeholder tipo `TODO` ou `<preencher>` → −2 pts
- Seção de critérios de aceite com menos de 3 itens → −3 pts

---

## 4. Testabilidade (15 pts)

**Mede:** se o critério de "pronta" pode ser verificado por um script ou checklist binário.

| Sinal | Pontos |
|-------|--------|
| Cada script tem ao menos 1 critério de aceite com CLI executável | 4 |
| Critérios de aceite retornam resultado binário (passa/falha), não subjetivo | 4 |
| Output JSON tem exemplo concreto (não só schema) | 3 |
| Comportamento de erro é especificado (exit code + mensagem) | 2 |
| Primeiros 60 segundos de uso estão mockados (happy path executável) | 2 |

**Red flags (−4 cada, até −8):**
- Critérios como "funciona bem", "é rápido", "é útil"
- "Teste manualmente que..." sem comando concreto
- Ausência de exemplos de input/output

---

## 5. Delimitação (10 pts)

**Mede:** clareza sobre o que a skill deliberadamente NÃO faz.

| Sinal | Pontos |
|-------|--------|
| Seção "NÃO faz" tem ≥ 3 itens | 3 |
| Cada item é específico e acionável (não genérico) | 3 |
| Pelo menos 1 item delega para outra skill nomeada | 2 |
| Frontmatter do SKILL.md repete o "NÃO ative para..." | 2 |

**Red flags (−3 cada):**
- Itens genéricos ("não faz nada mágico", "não substitui julgamento humano")
- Contradição entre "NÃO faz" da SPEC e descrição do SKILL.md
- Lista de "NÃO faz" vazia ou com 1 item

---

## Interpretação do score

| Faixa | Veredicto | Ação |
|-------|-----------|------|
| **≥ 90** | Exemplar | Entregue. Considere usar como referência em outras SPECs. |
| **80–89** | Pronta | Entregue. Opcional: revisar os 1–2 gaps antes. |
| **70–79** | Quase lá | Corrija os gaps do scorer. Sem nova entrevista. |
| **60–69** | Incompleta | Volte ao `interview_protocol.md` nas perguntas em aberto. |
| **< 60** | Inviável | Recomece a entrevista. A SPEC atual dará origem a uma skill inconsistente. |

---

## Uso pelo scorer

O scorer em `scripts/spec_scorer.py` aplica esta rubrica via heurísticas sobre o texto da SPEC:

- **Detecção de seções** — por headers `## N.` (11 obrigatórios)
- **Detecção de `N/A`** — case-insensitive, procura justificativa na mesma linha ou próxima
- **Detecção de pinagem** — regex sobre blocos de tabela de deps (`==\d+\.`)
- **Detecção de placeholders** — busca por `TODO`, `<preencher>`, `<...>`, `XXX`
- **Detecção de linguagem vaga** — heurística sobre advérbios ("geralmente", "normalmente", "aproximadamente") em seções prescritivas

Heurísticas são conservadoras: falsos negativos (pontuar baixo algo bom) são preferidos a falsos positivos (aprovar algo ambíguo).
