# Análise técnica consolidada — mdcu-framework

> Gerado pelo **Reversa Archaeologist** em 2026-04-27
> Reinterpretação obrigatória: este projeto é prosa prescritiva, não código executável. "Função" = comando `/`; "condicional" = gate; "algoritmo" = método; "estrutura de dados" = artefato em disco. Ver `decisions.md` apêndice.

---

## Módulo 1 — `mdcu` (mdcu/SKILL.md, 351 linhas)

### Propósito 🟢
Orquestrador metodológico inspirado no Método Clínico Centrado na Pessoa (MCCP). Conduz uma sessão de desenvolvimento em 6 fases (F1–F6) cujos artefatos são transitórios; única persistência é o SOAP final escrito pelo `rsop`.

### "API pública" — comandos `/` (mdcu/SKILL.md:347-351) 🟢

| Comando | Parâmetros | Efeito | Pré-condição |
|---|---|---|---|
| `/mdcu` | — | Cria `_mdcu.md` com template; inicia F1; dispara gatilho de conformidade | Nenhuma |
| `/mdcu fase [N]` | N ∈ {1..6} | Salta/retorna para fase N | Gatilho de conformidade aplica para N≥2 |
| `/mdcu status` | — | Mostra `_mdcu.md`, fase corrente, contador de Reenquadramento, presença de `ARCHITECTURE.md` | `_mdcu.md` existe |
| `/mdcu reenquadrar` | — | Aplica protocolo de reenquadramento; **incrementa contador se em F6** | `_mdcu.md` existe |
| `/mdcu fechar` | — | Dispara `/rsop soap` → `/commit-soap` → delete de `_mdcu.md` | F6 concluída |

### Fluxo de controle — fases F1→F6 🟢

```
F1 Preparação
  ├─[gate: ARCHITECTURE.md existe?]
  │    ├─ NÃO → INTERROMPE → invoca /project-init → retorna a F1 do início
  │    └─ SIM → lê stack/guardrails; lê rsop/{dados_base, lista_problemas}, último SOAP
  │            verifica vieses; verifica reenquadramento pendente
  │            rastreio: há # de segurança ativo no RSOP?
  ↓
F2 Escuta (2 minutos de ouro)
  ├─ pergunta aberta única
  ├─ separa Demanda × Queixa (SIFE quando opaco)
  └─ ESCREVE em _mdcu.md → seção F2 → S: (Demandas/Queixas/Notas)
  ↓
F3 Exploração
  ├─ "por que isso é problema?" / patobiografia / sistema ao redor
  ├─ rastreio de segurança (5 itens — ver bloco abaixo)
  └─ ESCREVE em _mdcu.md → seção F3 → O: (fatos, medidas, fontes)
  ↓
F4 Avaliação (hipótese)
  ├─ "o provável problema é X devido a Y"
  ├─ pró/contra; reversibilidade
  └─ atualiza rsop/lista_problemas.md (novo # ou evolui descrição existente)
  ↓
F5 Plano (decisão compartilhada)
  ├─ precedência de evidência: skills > MCPs > libs mantidas > padrões > original
  ├─ ≥2 alternativas com trade-offs
  ├─ rastreio de segurança em cada alternativa
  ├─ verifica conformidade com ARCHITECTURE.md (violar → /project-init --refresh)
  └─ ESCREVE em _mdcu.md → seção F5
  ↓
F6 Execução
  ├─ RELÊ _mdcu.md por inteiro (S: + O:)
  ├─ executa plano (skills > MCPs > tools)
  ├─ micro-commits permitidos (git commit padrão); SOAP só no fechamento
  ├─ dependências: manifesto + lock file no MESMO commit
  ├─ reenquadramento → incrementa contador em _mdcu.md
  │    ├─ contador atinge 2/2 → DISJUNTOR → exit protocol → aguarda usuário
  │    └─ contador < 2/2 → retorna a F2 ou F3
  └─ FECHAMENTO:
       ├─ relê _mdcu.md
       ├─ /rsop soap (destila S, O, A, P, R)
       ├─ /commit-soap (selo longitudinal a partir de A+P)
       └─ DELETA _mdcu.md
```

### Gates não-negociáveis 🟢

| Gate | Onde | Efeito se falha |
|---|---|---|
| **Conformidade `ARCHITECTURE.md`** | F1 antes de F2 | Interrompe MDCU; invoca `/project-init`; retoma F1 |
| **Disjuntor 2/2** | F6, contador de Reenquadramento | Aborta execução; exit protocol; exige decisão humana |
| **Lock file ao mexer dependência** | F6 | Proibido instalar/upgrade/remove sem regenerar lock; commit conjunto |
| **Conformidade de guardrail** | F5 alternativa que viola guardrail | Exige `/project-init --refresh` antes de F6 |

### Algoritmos não-triviais 🟢

1. **SIFE (Sentimentos / Ideias sobre causa / Funcionalidade afetada / Expectativas)** — instrumento de F2 para revelar demanda oculta quando D e Q sozinhos são insuficientes (mdcu/SKILL.md:139, 145).
2. **Padrões de demanda aparente** — taxonomia: cartão de visita / exploratória / shopping / cure-me. Heurística: motivo declarado ≠ motivo real (mdcu/SKILL.md:140).
3. **Disjuntor humano (Circuit Breaker)** — algoritmo determinístico de loop-breaker em F6 (mdcu/SKILL.md:304-339):
   ```
   contador := 0
   ao reenquadrar em F6:
     contador += 1
     se contador == 2:
       abortar execução
       acionar exit protocol (formato fixo de 5 campos)
       proibido prosseguir sozinho
       reset apenas com novo /mdcu (novo _mdcu.md)
   ```
4. **Precedência de evidência** (F5, mdcu/SKILL.md:186-191) — algoritmo de seleção de solução em 5 níveis: skills instaladas > MCPs validados > libs mantidas > padrões consolidados > original.
5. **Rastreio de segurança (5 itens binários)** — heurística aplicada em F1, F3, F5, F6 (mdcu/SKILL.md:228-251).

### Estruturas de dados produzidas/consumidas 🟢

| Artefato | Lifecycle | Quem escreve | Quem lê |
|---|---|---|---|
| `_mdcu.md` | transitório (sessão) | mdcu (todas as fases) | mdcu (F6 relê) + rsop (no SOAP) |
| `rsop/lista_problemas.md` | longitudinal | mdcu (F4) + rsop (`/rsop revisar`) | mdcu (F1) |
| `rsop/dados_base.md` | estrutural | rsop | mdcu (F1) |
| `rsop/soap/YYYY-MM-DD_*.md` | permanente | rsop (`/rsop soap`) | mdcu (F1 lê último), commit-soap |
| `ARCHITECTURE.md` | estrutural | project-init | mdcu (F1, F5, F6) |

### Template do `_mdcu.md` 🟢 (mdcu/SKILL.md:58-77)

Campos obrigatórios:
- Cabeçalho: `# Sessão [data] — [projeto/tema]`
- `Tentativas de Reenquadramento: 0/2` (counter)
- Seções: `## F1 Preparação`, `## F2 Escuta` (com `S:`), `## F3 Exploração` (com `O:`), `## F4 Avaliação`, `## F5 Plano`, `## F6 Execução`

### Constantes de domínio 🟢

- Severidade de problema: `[A]` alta, `[M]` média, `[B]` baixa.
- Limite do disjuntor: **2 reenquadramentos por sessão F6** (literal, não configurável).
- Janela de F2: **2 minutos** (apelido "2 minutos de ouro" — diretriz, não enforcement).

### Dependências 🟢
- **Bloqueante:** `project-init` (F1→F2)
- **Lifecycle:** `rsop`, `commit-soap`
- **Condicional:** `mdcu-seg`

### Complexidade
**Alta** — 13 regras de operação, 6 fases, 4 gates, disjuntor com estado, integração com 4 outras skills.

---

## Módulo 2 — `rsop` (rsop/SKILL.md, 238 linhas)

### Propósito 🟢
Prontuário longitudinal do software, inspirado no RMOP de Lawrence Weed (1968) e no RCOP do e-SUS PEC. Formato telegráfico, orientado por problema. Único registro permanente da sessão MDCU.

### "API pública" — comandos `/` (rsop/SKILL.md:231-238) 🟢

| Comando | Efeito | Lê | Escreve |
|---|---|---|---|
| `/rsop init` | Cria estrutura + artefatos vazios (incluindo `passivos.md` vazio) | — | `dados_base.md`, `lista_problemas.md`, `passivos.md`, `soap/` |
| `/rsop dados` | Exibe/atualiza dados base | `dados_base.md` | `dados_base.md` |
| `/rsop lista` | Exibe ativos. **Não inclui passivos por default** | `lista_problemas.md` | — |
| `/rsop passivos` | Exibe `passivos.md` sob demanda | `passivos.md` | — |
| `/rsop soap` | Cria SOAP. **Lê `_mdcu.md` para hidratar S e O** | `_mdcu.md`, `lista_problemas.md` | `soap/YYYY-MM-DD_contexto.md` |
| `/rsop revisar` | Reclassifica severidade; **move resolvidos `lista_problemas.md` → `passivos.md`** | `lista_problemas.md`, `passivos.md` | ambos |
| `/rsop regressao [#]` | Consulta passivos buscando regressão; reabre se encontrado | `passivos.md` | `lista_problemas.md`, `passivos.md` |
| `/rsop status` | Resumo: data dados base, #ativos, #passivos (número), último SOAP | todos | — |

### Componentes (= "classes/entities") 🟢

```
rsop/
├── dados_base.md         # Componente 1 — perfil mínimo do sistema (estrutural)
├── lista_problemas.md    # Componente 2 — ATIVOS (índice vivo, injetado em CLAUDE.md)
├── passivos.md           # Componente 3 — ARQUIVO MORTO (consultável sob demanda)
├── seguranca.md          # OPCIONAL — gerido por mdcu-seg
└── soap/
    └── YYYY-MM-DD_contexto.md  # Componente 4 — SOAP por sessão
```

### Algoritmos não-triviais 🟢

1. **Princípio de separação ativos/passivos** (rsop/SKILL.md:34) — algoritmo de gestão de atenção: `lista_problemas.md` é injetado no system prompt (consome tokens); passivos vivem em arquivo estático fora do contexto. Trade-off: agente perde memória de problema fechado, ganha foco em ativo.
2. **Escrita do SOAP** (rsop/SKILL.md:131-211):
   - S: três sub-slots — Demandas / Queixas / Notas (SIFE opcional)
   - O: tópicos telegráficos sem sub-slots
   - A: lista numerada, **máx 5 palavras por item**, cada item referencia um `#`
   - P: lista numerada, **1:1 com A**
   - R: **uma linha** ou omitir
3. **Regra de consulta de passivos** (rsop/SKILL.md:103-109) — DOIS gatilhos exclusivos: (a) suspeita de regressão; (b) requisição direta. Fora disso, invisível ao agente.
4. **Exceção de segurança** (rsop/SKILL.md:80) — bug de segurança SEMPRE entra na lista (mesmo se corrigido no mesmo dia); ao resolver migra para passivos com `reativável? sim — vigiar recorrência`.

### Estruturas de dados — schemas inline 🟢

#### `dados_base.md` (rsop/SKILL.md:42-62)
```
# Dados base
- Projeto: [nome]
- Atualizado: [data]
## Identificação: Propósito, Responsáveis, Stakeholders
## Stack: Linguagens/frameworks, Infra, Repositório
## Dívidas conhecidas: [lista]
```

#### `lista_problemas.md` (rsop/SKILL.md:84-92)
```
# Lista de problemas — Ativos
- Projeto: [nome] — Última revisão: [data]
| # | Problema | Desde | Últ. SOAP |
```
Severidade prefixada: `[A] N+1 queries listagem pedidos`. Sem coluna `Notas`. Sem seção `## Passivos`.

#### `passivos.md` (rsop/SKILL.md:111-120)
```
| # | Problema | Ativo em | Fechado por | Fechado em | Reativável? |
```
Reativação: linha em `passivos.md` recebe nota `reaberto em [data] — ver SOAP [ref]`; `#` reabre em `lista_problemas.md`.

#### `soap/YYYY-MM-DD_contexto.md` (rsop/SKILL.md:177-208)
```
# SOAP YYYY-MM-DD — [contexto]
- Problemas: #1, #2

## S
**Demandas**: [bullets]
**Queixas**: [bullets]
**Notas**: [SIFE / demanda oculta — opcional]

## O: [bullets telegráficos com fonte]
## A: [lista numerada, max 5 palavras, refs #]
## P: [lista numerada, 1:1 com A]
## R: [uma linha, ou omitida]
```

### Constantes 🟢
- Severidade: `[A]`, `[M]`, `[B]` (ver módulo `mdcu`).
- Limite de palavras em A: **5** por item.
- R: **uma linha**.
- Naming convention SOAP: `YYYY-MM-DD_contexto.md`.

### Dependências 🟢
- **Autônoma** (não importa nada de outras skills do framework).
- É alvo de: `mdcu`, `mdcu-seg`, `commit-soap`.

### Complexidade
**Média** — 4 componentes, 8 comandos, regras de migração ativos↔passivos com casos especiais (segurança).

---

## Módulo 3 — `commit-soap` (commit-soap/SKILL.md, 114 linhas)

### Propósito 🟢
Gerador de mensagem de commit derivada do A (Avaliação) e P (Plano) do SOAP da sessão atual — selo longitudinal do ciclo. Preserva contexto cognitivo no `git log`.

### "API pública" 🟢 (commit-soap/SKILL.md:97-101)

| Comando | Efeito |
|---|---|
| `/commit-soap` | Lê SOAP mais recente; extrai A+P; gera mensagem; exibe; comita após confirmação |
| `/commit-soap --dry-run` | Gera mensagem sem comitar |
| `/commit-soap --amend` | Reescreve mensagem do último commit a partir do SOAP atualizado |

### Fluxo de controle 🟢 (commit-soap/SKILL.md:104-114)

```
1. Localizar SOAP mais recente em rsop/soap/
   ├─ Não existe → mensagem fixa de orientação ("registre /rsop soap antes de commitar
   │              — ou se é WIP, use git commit padrão")
   │              ABORTA — não inventa mensagem
   └─ Existe ↓
2. Extrair seções A e P
3. Sintetizar segundo regras de formatação
4. Montar mensagem no formato canônico
5. Exibir ao usuário para revisão
6. Após confirmação → git commit
```

### Algoritmo de formatação 🟢 (commit-soap/SKILL.md:42-71)

**Formato canônico:**
```
A: [síntese da Avaliação — 1ª linha máx 72 chars]
P: [síntese do Plano]

Refs: rsop/soap/YYYY-MM-DD_contexto.md
```

**Regras:**
- Linha A: 1–3 frases. Hipótese principal, nível de resolução.
- Linha P: 1–3 frases. O que foi feito, pendente, próxima reavaliação.
- 1ª linha (A): **≤ 72 chars** (compatibilidade `git log --oneline`).
- Sem tipo técnico obrigatório (pode coexistir com Conventional Commits opcional).

**Múltiplos problemas** (commit-soap/SKILL.md:75-84):
```
A: #3 [síntese]
A: #7 [síntese]
P: #3 [síntese]
P: #7 [síntese]
Refs: rsop/soap/...
```

### Política de uso (gates) 🟢 (commit-soap/SKILL.md:21-32)

**EXCLUSIVO para:**
1. Fechamento de sessão MDCU (após `/rsop soap`).
2. Merge de feature final.

**PROIBIDO para:**
- WIPs / micro-commits / formatação / typos / merge sem SOAP atrelado → `git commit` padrão.

### Padrão de retrospectiva 🟢 (commit-soap/SKILL.md:88-95)

Comandos de auditoria habilitados pelo formato:
- `git log --grep="A:"` — todas as avaliações
- `git log --grep="P:"` — todos os planos
- `git log --grep="#3"` — história longitudinal do problema 3
- `git log --grep="Refs: rsop"` — todos os commits-SOAP
- `git log --invert-grep --grep="A:"` — apenas micro-commits (auditoria de ruído)

### Constantes 🟢
- Largura máxima da 1ª linha: **72 caracteres**.
- Trailer `Refs:` apontando para `rsop/soap/YYYY-MM-DD_contexto.md` (caminho relativo).

### Dependências 🟢
- **Lê:** `rsop/soap/` (SOAP mais recente).
- **Não escreve** em nenhum artefato — apenas no histórico git.

### Complexidade
**Baixa** — 1 algoritmo de formatação, 3 comandos, política de uso clara.

---

## Módulo 4 — `project-init` (project-init/SKILL.md, 278 linhas)

### Propósito 🟢
Inicializa o contrato técnico de um projeto — `ARCHITECTURE.md` + manifesto + lock file determinístico + commit inicial. Pré-requisito bloqueante para o MDCU (F1→F2).

### "API pública" 🟢 (project-init/SKILL.md:262-266)

| Comando | Efeito | Pré-condição |
|---|---|---|
| `/project-init` | 7 fases; aborta se `ARCHITECTURE.md` já existe | `ARCHITECTURE.md` ausente |
| `/project-init --refresh` | Re-executa fases 2–6 sobre `ARCHITECTURE.md` existente | `ARCHITECTURE.md` presente; mudança estrutural |
| `/project-init --check` | Valida conformidade: `ARCHITECTURE.md` existe? lock bate com manifesto? guardrails coerentes? | Nenhuma |
| `/project-init status` | Resumo: stack, gerenciador, lock presente, última atualização | Nenhuma |

### Fluxo de controle — 7 fases 🟢 (project-init/SKILL.md:39-133)

```
F1 Identificação
  ├─ nome / propósito / responsáveis / stakeholders / raiz
  └─ se MDCU já tem em rsop/dados_base.md, REUTILIZA (não pergunta 2x)

F2 Seleção de stack
  └─ linguagem / framework / runtime / infra alvo
     Critério: consolidado > experimental (justificar via ADR)

F3 Definição de gerenciador + lock file (VINCULANTE)
  ├─ lookup canônico (tabela project-init/SKILL.md:67-80)
  ├─ stack desconhecida → pesquisa+propõe lock canônico → confirma com usuário
  └─ se nenhum lock determinístico viável → ABORTA

F4 Estrutura + convenções
  └─ src/, tests/, rsop/, docs/ + lint/format/naming/branches

F5 Comandos principais
  └─ install/dev/test/build/lint/format/(migrate|seed)
     → viram contrato no ARCHITECTURE.md

F6 Guardrails e invariantes
  └─ decisões irreversíveis + limites de escopo + segurança estrutural
     → violação em MDCU F5/F6 exige --refresh ou reenquadramento

F7 Geração e commit inicial
  ├─ cria ARCHITECTURE.md
  ├─ inicializa gerenciador (npm init / poetry init / cargo init / go mod init / ...)
  ├─ instala deps iniciais → GERA LOCK FILE
  ├─ git init (se necessário) + .gitignore por stack
  └─ commit inicial com mensagem canônica:
       "chore: project-init — contrato técnico estabelecido
        A: Projeto sem contrato técnico formal — risco de decisões ad hoc...
        P: ARCHITECTURE.md + [manifesto] + [lock file] gerados e commitados
        Refs: ARCHITECTURE.md"
```

### Algoritmos não-triviais 🟢

1. **Mapeamento canônico stack → gerenciador → lock** (project-init/SKILL.md:67-80) — tabela determinística com 12 stacks. Stacks fora da tabela: pesquisa + proposta + confirmação humana. `requirements.txt` sem pinning estrito **não conta como lock**.
2. **Gestão Determinística de Dependências** (project-init/SKILL.md:137-184) — 8 regras vinculantes:
   - Lock obrigatório, sempre commitado, **nunca** em `.gitignore`.
   - Manifesto + lock no MESMO commit em F6.
   - Versões flutuantes no manifesto OK; lock congela versão exata.
   - Upgrades são deliberados (Dependabot/Renovate só sugere; merge é decisão humana).
   - CI usa `npm ci` / `poetry install --no-update` / `cargo build --locked` (nunca install solto).
   - Auditoria periódica obrigatória (parte do `mdcu-seg auditoria`).
3. **Algoritmo `--check`** — verificação 4-pontos: `ARCHITECTURE.md` existe? lock existe? lock bate com manifesto? guardrails coerentes com código atual?

### Tabela canônica stack → lock 🟢

| Stack | Gerenciador | Manifesto | Lock |
|---|---|---|---|
| JS/TS | npm/yarn/pnpm | `package.json` | `package-lock.json` / `yarn.lock` / `pnpm-lock.yaml` |
| Python | Poetry/uv/pip-tools | `pyproject.toml` / `requirements.in` | `poetry.lock` / `uv.lock` / `requirements.txt` (pinado) |
| Rust | Cargo | `Cargo.toml` | `Cargo.lock` |
| Go | Go modules | `go.mod` | `go.sum` |
| Ruby | Bundler | `Gemfile` | `Gemfile.lock` |
| PHP | Composer | `composer.json` | `composer.lock` |
| Elixir | Mix | `mix.exs` | `mix.lock` |
| .NET | NuGet | `*.csproj` | `packages.lock.json` (habilitar) |

### Estruturas de dados produzidas 🟢

#### `ARCHITECTURE.md` (project-init/SKILL.md:189-245)
Seções: Identificação / Stack / Dependências (gerenciador, manifesto, lock, política, auditoria, upgrades) / Estrutura de diretórios / Convenções (lint, format, naming, branches, commits) / Comandos principais / **Guardrails (invariantes)** / Escopo (Faz / NÃO faz) / ADRs relacionados.

### Constantes 🟢
- Lock file **nunca** em `.gitignore` (regra absoluta).
- 12 stacks com mapeamento determinístico.

### Dependências 🟢
- **Autônoma** (não depende de outras skills do framework).
- É invocada por: `mdcu` (gate F1→F2 bloqueante).

### Complexidade
**Alta** — 7 fases sequenciais com gates, 8 regras vinculantes de dependências, 12 stacks suportadas, integração explícita com 5 outras skills (tabela project-init/SKILL.md:272-279).

---

## Módulo 5 — `mdcu-seg` (mdcu-seg/SKILL.md, 238 linhas)

### Propósito 🟢
Módulo de segurança aprofundado, adjunto ao MDCU. Faz **exploração** (STRIDE), **contenção** (F0/IRP) e **vigilância longitudinal** (auditoria trimestral). Não duplica o rastreio de 5 itens do MDCU.

### "API pública" 🟢 (mdcu-seg/SKILL.md:233-238)

| Comando | Efeito |
|---|---|
| `/mdcu-seg` | Menu dos 3 domínios + status (última auditoria, `#` segurança ativos) |
| `/mdcu-seg threat-model [escopo]` | Roda STRIDE; gera tabela; atualiza RSOP |
| `/mdcu-seg incidente` | Inicia F0; **suspende MDCU ativo** (preserva `_mdcu.md`) |
| `/mdcu-seg auditoria` | Abre/atualiza `rsop/seguranca.md` |
| `/mdcu-seg status` | Resumo: `#` segurança ativos, última auditoria, incidentes abertos |

### Três domínios funcionais 🟢

```
mdcu-seg/
├── 1. threat-model   → STRIDE
├── 2. incidente (F0) → IRP 5 etapas
└── 3. auditoria      → rsop/seguranca.md (trimestral)
```

### Algoritmos não-triviais 🟢

#### A. STRIDE (mdcu-seg/SKILL.md:35-58)
Tabela 6 categorias × por componente/fluxo:

| Categoria | Pergunta-gatilho |
|---|---|
| **S**poofing | Quem diz ser X pode ser falsificado? |
| **T**ampering | Dados podem ser alterados sem detecção? |
| **R**epudiation | Há log auditável? |
| **I**nformation disclosure | Que informação vaza? |
| **D**enial of service | Qual recurso pode ser esgotado? |
| **E**levation of privilege | Comum vira admin? |

Output: tabela `| Categoria | Ameaça concreta | Vetor | Mitigação | → RSOP # |`. Toda ameaça com mitigação não-trivial vira `#` no RSOP. Categoria não aplicável: linha `— não aplicável (por quê)` (silêncio proibido).

#### B. F0 — Protocolo de contenção de incidente (mdcu-seg/SKILL.md:79-145)
```
Disparo → SUSPENDE MDCU ativo (_mdcu.md PRESERVADO, não deletado)
  ↓
1. Identificação
   ├─ sinal / quando / por quem
   ├─ escopo: sistema / dado / usuários
   └─ severidade: L1 (baixa, contida) / L2 (média, parcial)
                / L3 (alta, exposição confirmada) / L4 (crítica, ativa em prod)
  ↓
2. Contenção
   ├─ curto prazo (min–h): isolar / desabilitar / bloquear / cortar tráfego
   └─ médio prazo (h–dias): patch temporário, rotação de credenciais
  ↓
3. Erradicação
   └─ patch definitivo / rotação completa / remoção de IoC / revisão de código
  ↓
4. Recuperação
   └─ restaura serviço com monitoramento reforçado; valida que IoC não reaparecem
  ↓
5. Postmortem (BLAMELESS)
   ├─ linha do tempo factual
   ├─ causa raiz
   ├─ falhas de detecção (por que não pegamos antes?)
   └─ ações ESTRUTURAIS, nunca pessoais
  ↓
Artefato: rsop/soap/YYYY-MM-DD_incidente-[ref].md (formato SOAP estendido)
  ↓
MDCU retoma do _mdcu.md preservado, ciente de novos #
```

#### C. Auditoria trimestral (mdcu-seg/SKILL.md:151-202)
- Artefato: `rsop/seguranca.md`.
- **Revisão obrigatória a cada 90 dias.** Sem revisão → `/mdcu-seg auditoria` sinaliza atraso.
- Seções: Classificação de dados / Regime de auditoria (SAST/DAST/Dep scan/Secret scan/Pentest/Code review) / Gestão de segredos / Conformidade (LGPD/HIPAA/PCI-DSS/...) / Histórico de incidentes (12 meses) / Vulnerabilidades ativas (espelho).

### Gatilhos de delegação MDCU → mdcu-seg 🟢 (mdcu-seg/SKILL.md:206-216)

| Fase MDCU | Condição | Chamada |
|---|---|---|
| F1 | RSOP tem `#[A]` segurança ativo | `/mdcu-seg auditoria` |
| F3 | Item 1 (PII) ou 2 (auth) afirmativo | `/mdcu-seg threat-model` |
| F5 | Alternativa falha no rastreio | `/mdcu-seg threat-model` |
| F6 | Sinal de incidente | `/mdcu-seg incidente` IMEDIATAMENTE |
| Qualquer | Vazamento/breach/CVE crítico/LGPD | delegar conforme contexto |

### Estruturas de dados produzidas 🟢

#### `rsop/soap/YYYY-MM-DD_incidente-[ref].md` (mdcu-seg/SKILL.md:102-145)
SOAP estendido — adiciona:
- Cabeçalho: `Tipo: incidente (F0)`, `Severidade: L1..L4`
- Seção `## Etapas F0` numerada 1–6 (Identificação, Contenção curta, Contenção média, Erradicação, Recuperação, Postmortem) com timestamps

#### `rsop/seguranca.md` (mdcu-seg/SKILL.md:160-200)
Seções fixas — ver "Auditoria trimestral" acima.

### Constantes 🟢
- Severidade de incidente: **L1 / L2 / L3 / L4** (escala própria, NÃO confundir com `[A]/[M]/[B]` de problema RSOP).
- Período de revisão de auditoria: **90 dias**.
- Severidade mínima de vulnerabilidade na lista de problemas: `[M]`; `[A]` se explorável em produção.

### Dependências 🟢
- **Suspende:** `mdcu` (em F0).
- **Atualiza:** `rsop` (lista_problemas.md, seguranca.md, soap/).

### Complexidade
**Alta** — 3 domínios funcionais, 5 etapas IRP, tabela STRIDE 6×N, integração com 2 skills, escala dupla de severidade.

---

## Achados transversais 🟢

### Padrão recorrente: "F0 = contenção"
- Em **mdcu-seg**, F0 é o protocolo de incidente (numeração começa em 0 = anterior ao ciclo MDCU normal).
- Em outras skills do ecossistema (não no escopo deste projeto, mas referenciadas em commits — ver `meca-aval`), F0 também é "intervenção focal pré-ciclo". Padrão semântico consistente: F0 = ação que precede e pode suspender o ciclo principal.

### Padrão recorrente: "telegráfico por princípio"
Citado literal em `rsop/SKILL.md:10` ("formato é telegráfico por princípio, não por economia"). Aplicado a:
- SOAP (S/O/A/P/R com regras de palavras-por-item)
- `_mdcu.md` (bullets em S: e O:)
- Checklist de rastreio de segurança (5 itens binários)
- Lista de problemas (severidade prefixada, sem coluna Notas)
- Reflexão R do SOAP (1 linha ou omitida)

### Padrão recorrente: "artefatos efêmeros vs. permanentes"
Princípio arquitetural do framework: tudo que é raciocínio de ciclo é efêmero (`_mdcu.md`, deletado pós-SOAP); tudo que é destilado é permanente (SOAP, lista de problemas, ADRs). Alinhado a Weed: "the medical record is the doctor's tool to think with" — o framework adapta isso para "the SOAP is the engineer's tool to remember with."

### Padrão recorrente: "exceção de segurança"
Em pelo menos 3 lugares (rsop, mdcu, mdcu-seg), regras são afrouxadas para vulnerabilidades:
- `lista_problemas.md`: bug pontual não entra; **vulnerabilidade SEMPRE entra** (rsop/SKILL.md:80).
- Severidade mínima de vulnerabilidade: `[M]`; `[A]` se explorável.
- Passivo de segurança: `reativável? sim — vigiar recorrência` (não "não").

### Lacuna 🔴 técnica de implementação
Toda a "execução" deste framework depende do agente de IA hospedeiro **interpretar prosa em Markdown** e seguir as instruções. Não há enforcement por código. Por exemplo:
- O disjuntor 2/2 só funciona se o agente respeitar o contador escrito em `_mdcu.md`.
- A separação ativos/passivos só funciona se o agente respeitar a regra de "consultar passivos só por suspeita ou pedido".
- A regra de lock file só funciona se o agente verificar e commitar.

**Implicação:** o framework é tão forte quanto a fidelidade do agente às instruções. A escolha de Markdown puro (vs. hooks programáticos do Claude Code) é decisão arquitetural — provavelmente para portabilidade entre engines, mas vale registrar como ADR retroativo (Detective).

---

# APÊNDICE — REFRESH 2026-04-27 (commits ba76256 → be71eca)

> Adicionado pelo **Reversa Archaeologist** em refresh cirúrgico após 6 sessões MDCU consecutivas.
> A análise primária acima permanece historicamente correta para v2026.04. Esta seção documenta o **delta** introduzido em direção a v2026.05 planejada.

## Δ Módulo 1 — `mdcu` (462 linhas, era 351)

### Mudanças estruturais 🟢

| Mudança | Localização | Origem |
|---|---|---|
| **Seção "Escopo do MDCU" no topo** | logo após "Workflow integrado" | F-1 + P-8 (`framework/principles.md`) |
| **Persona reescrita com 3 camadas** | "Persona (núcleo)" | F-2 (`framework/principles.md`) |
| **Princípio central reforçado** com referência a F-3 (satisfação clínica + dever de alerta) | "Princípio central" | F-3 + RN-D-014 |
| **Workflow integrado redesenhado** — agora declara `project-init → project-setup → MDCU → engine downstream OU monolítico → RSOP SOAP → commit-soap` | "Workflow integrado" | P-8 + P-9 |
| **Gatilho de conformidade DUAL** — verifica `ARCHITECTURE.md` E setup materializado | F1 — Gatilho | split #9 (commit `1378d5e`) |
| **F6 reformulada em 3 sub-blocos** | F6 inteira | resolução `#8` (commit `599307d`) |
| **F5 nota refinada** sobre delegação de análise arquitetural a engines | F5 | P-8 |
| **Regra de operação 12 atualizada** — "F2 com ARCHITECTURE.md presente E setup materializado" | Regras | gatilho dual |

### F6 — anatomia em 3 sub-blocos (NOVO) 🟢

```
F6 — Acompanhamento, tradução de retorno e fechamento
├─ F6.a Delegação ao engine
│    ├─ MODO DESACOPLADO: invoca engine downstream apropriado
│    └─ MODO MONOLÍTICO (declarado, com critério de saída):
│       orquestrador-instância como engine ad-hoc
│       └─ disciplina herdada: micro-commits, lock file, divergências
├─ F6.b Acompanhamento (metaprotocolo de observação)
│    ├─ releitura periódica de _mdcu.md
│    ├─ reenquadramento (incrementa contador 0/2 → 1/2 → 2/2)
│    └─ Disjuntor 2/2 (P-3 preservado)
└─ F6.c Tradução de retorno e fechamento
     ├─ tradução: complexidade técnica → opção decidível pelo usuário
     ├─ dever de alerta (RN-D-014)
     ├─ validação ativa com o usuário (não "OK?" automático)
     ├─ releitura final de _mdcu.md
     ├─ /rsop soap → destila S/O/A/P/R em registro permanente
     ├─ /commit-soap → selo
     └─ delete _mdcu.md
```

**Conservação canônica:** Disjuntor 2/2 (P-3 em `_reversa_sdd/architecture.md`) preservado em F6.b. Reformulação não quebrou gates.

### Modo monolítico declarado (anti-padrão silencioso) 🟢

Quando nenhum engine downstream concreto está plugado, orquestrador-instância opera como engine ad-hoc. **Exceção declarada**, não regra silenciosa. Critérios de aceitação + critérios de saída listados explicitamente em F6.a.

**Justificativa F-3:** decisão informada para adopters — saber que está no atalho e qual é o caminho de saída.

## Δ Módulo 2 — `rsop` (297 linhas, era 238) — v1.4.0

### Mudanças estruturais 🟢

| Mudança | Localização | Origem |
|---|---|---|
| **Frontmatter `version: "1.4.0"` + `author: Iago Leal`** | topo | adicionado em sessões |
| **Schema lista_problemas.md enriquecido** com colunas `Tipo` + `Revisitar` | "Componente 2" | resolução `#3` + `#10` (commit `cd59735`) |
| **Seção "Dívida consciente × acidental"** | "Componente 2" | RN-D-016 nova |
| **Seção "Triagem precisa-resolver"** com prefixo `[aceito-arquivado]` | "Componente 2" | RN-D-015 |
| **Seção NOVA "Checklist de qualidade do SOAP"** com 10 itens binários | entre Componente 4 e Regras | resolução `#7` (commit `be71eca`) |
| **Cap F-4 declarado explicitamente** no checklist | nova seção | F-4 |

### Schema da lista_problemas.md (NOVO) 🟢

```
| # | Problema | Tipo | Revisitar | Desde | Últ. SOAP |
```

**Defaults implícitos:**
- `Tipo` omitido = `acidental`
- `Revisitar` omitido = sem prazo
- Apenas `Tipo: consciente` é declarado explicitamente, e exige `Revisitar` preenchido (RN-D-016)

**Status precisa-resolver:** prefixo `[aceito-arquivado]` na coluna `#`. Coluna `Status` separada **rejeitada** por redundância numa lista de ativos.

### Checklist de qualidade do SOAP (NOVO) 🟢

10 itens binários, auto-aplicado pelo orquestrador na F6.c, **não-bloqueante**. Cap F-4 declarado: checklist mede o necessário, não o suficiente.

| # | Item | Verificável |
|---|---|---|
| 1 | S separa Demandas de Queixas | sim |
| 2 | Padrão de demanda aparente classificado quando aplicável | sim |
| 3 | A é lista numerada com itens ≤5 palavras | sim |
| 4 | P é 1:1 com A | sim |
| 5 | Cada item de A referencia `#` válido | sim |
| 6 | R é uma linha OU omitido | sim |
| 7 | S e O lidos do `_mdcu.md`, não da memória | sim (via timestamp) |
| 8 | Dívida consciente tem Tipo + Revisitar preenchidos | sim |
| 9 | Aceito-arquivado usa prefixo na coluna `#` | sim |
| 10 | Anamnese atualizada se padrão novo emergiu | semi (subjetivo "padrão novo") |

**Anti-padrão a vigiar:** percorrer mecanicamente. Checklist é gatilho para releitura, não substituto dela.

## Δ Módulo 3 — `commit-soap` (185 linhas, era 114) — v2.0.0

### Mudanças estruturais 🟢

| Mudança | Localização | Origem |
|---|---|---|
| **Frontmatter `version: "2.0.0"`** | topo | bump MAJOR |
| **Description expandida** — agora "Selo longitudinal universal" | frontmatter | desacoplamento (commit `1378d5e`) |
| **Seção "Mudança em v2.0.0 (desacoplamento)"** | logo após Problema | explica MAJOR bump |
| **Seção "Fontes de A+P aceitas"** com 3 modos (default SOAP, --from, --inline) | nova | desacoplamento |
| **Seção "Quando usar"** expandida — 4 marcos cobertos: sessão MDCU, project-setup, refresh estrutural, marcos do adopter | "Quando usar" | P-9 |
| **Seção "Fluxo canônico (project-setup)"** | nova | integração com project-setup |
| **Seção "Fluxo canônico (refresh estrutural)"** | nova | suporte a `--refresh` |
| **Operação atualizada** — 6 passos com determinação de fonte (default/from/inline) | "Operação" | desacoplamento |

### "API pública" expandida 🟢

| Comando | Parâmetros | Efeito | Pré-condição |
|---|---|---|---|
| `/commit-soap` | — | Lê último SOAP em `rsop/soap/`; extrai A+P; gera commit | SOAP existe |
| `/commit-soap --from <path>` | path | Lê A+P de arquivo arbitrário | path válido |
| `/commit-soap --inline` | A+P estruturado | Recebe A+P direto (usado por outras skills) | A+P bem formado |
| `/commit-soap --dry-run` | — | Gera mensagem sem commitar | — |
| `/commit-soap --amend` | — | Reescreve mensagem do último commit | último commit é commit-soap |

### Compatibilidade com v1.x 🟢

Comportamento default (sem argumento) **idêntico à v1.x**. Quebra de versão é semântica — escopo da skill mudou de "fechamento MDCU" para "selo longitudinal universal".

## Δ Módulo 4 — `project-init` (293 linhas, era 278) — v2.0.0

### Mudanças estruturais 🟢

| Mudança | Localização | Origem |
|---|---|---|
| **Frontmatter `version: "2.0.0"` + `author`** | topo | bump MAJOR |
| **Description redefinida** — "extração de contrato técnico" (não inicialização completa) | frontmatter | split #9 (commit `1378d5e`) |
| **Workflow redesenhado** — `project-init → project-setup → MDCU` | "Posição no workflow" | split |
| **"Artefato produzido" reduzido** — apenas `ARCHITECTURE.md`; **NÃO produz** manifesto, lock, .gitignore, commit | nova seção | split |
| **Fase 7 reescrita** — gera `ARCHITECTURE.md` + handoff para `project-setup` (não executa setup) | "Fase 7" | split |
| **Mensagem de handoff** explicitada para o usuário | "Fase 7" | split |
| **Regras de operação atualizadas** — regra 3 declara: "Esta skill NÃO executa setup técnico" | "Regras" | split |
| **Integração com project-setup** | "Integração com outras skills" | split |

### Diferença essencial vs. v1.x

**v1.x:** project-init executava `npm init`, instalava deps, fazia `git init` + `git commit` inicial — ato monolítico de extração + materialização.

**v2.0.0:** project-init **só extrai contrato** e gera `ARCHITECTURE.md` em prosa. Materialização técnica é **delegada ao novo `project-setup`** (P-8 em `framework/principles.md`).

### Gestão Determinística de Dependências preservada 🟢

Seção integral preservada como **prescrição canônica vinculante** que vigora em ambos os modos (desacoplado e monolítico) do `project-setup`. Conceito: regras descrevem **como** o lock file deve funcionar, independente de **quem** executa.

## Δ Módulo 5 — `project-setup` (NOVO, 163 linhas, v0.1.0)

### Propósito 🟢

Materialização do contrato técnico extraído por `project-init`. Recebe `ARCHITECTURE.md` como input e executa setup técnico em disco. **Engine de fundação** sob a anatomia de 4 camadas.

### "API pública" — comandos `/` 🟢

| Comando | Parâmetros | Efeito | Pré-condição |
|---|---|---|---|
| `/project-setup` | — | Materializa setup baseado em `ARCHITECTURE.md` | `ARCHITECTURE.md` existe |
| `/project-setup --refresh` | — | Reaplica após mudança de stack/gerenciador | `ARCHITECTURE.md` modificado |
| `/project-setup --check` | — | Valida conformidade (lock file, .gitignore, schema) | — |
| `/project-setup --mode <desacoplado\|monolitico>` | mode | Força modo específico | engine disponível para `desacoplado` |

### Modos de operação (PARALELO COM F6.a do MDCU) 🟢

**Modo desacoplado:** delega a engine de scaffolding maduro (cookiecutter, yeoman, plop, copier, cargo-generate, etc.) conforme stack declarada. Verifica que engine produziu manifesto + lock + `.gitignore` corretos.

**Modo monolítico declarado (exceção com critério de saída):** orquestrador-instância como engine ad-hoc — executa `npm init`/`poetry init`/`cargo init`/`go mod init`/etc. Critérios de aceitação + critérios de saída explícitos.

### Selo via commit-soap desacoplado 🟢

`project-setup` invoca `commit-soap --inline` ao final, com A+P pré-formatado:

```
A: Projeto sem contrato técnico materializado — sem lock file, sem reprodutibilidade
P: ARCHITECTURE.md materializado: [manifesto] + [lock file] + .gitignore + estrutura inicial; modo: [desacoplado via <engine> | monolítico]

Refs: ARCHITECTURE.md
```

P-9 (acompanhamento longitudinal transversal): mesmo selo de qualquer marco longitudinal.

### Regras canônicas herdadas (vigoram em ambos os modos) 🟢

Regras de Gestão Determinística de Dependências de `project-init/SKILL.md` são **enforcement efetivo** aqui. project-setup é onde a regra "manifesto + lock no mesmo commit" passa de prescrição a fato.

## Δ Módulo 6 — `mdcu-seg` (sem mudanças)

Mantido em v1.0.0. Não tocado pelas 6 sessões.

## Δ Camada NOVA — `framework/` (artefatos canônicos versionados)

### Propósito 🟢

Fonte de verdade epistemológica e arquitetural do framework, versionada e distribuída. Distinta de `_reversa_sdd/` (output do Reversa, gitignored, regenerável).

### Conteúdo 🟢

| Arquivo | Linhas | Conteúdo |
|---|---|---|
| `principles.md` | 192 | F-1 a F-5 (princípios fundacionais) + P-8, P-9 (princípios arquiteturais canônicos) |
| `architecture-diagram.md` | 116 | Diagrama ASCII das 4 camadas + diretivas de seta + implicações para skills atuais |
| `glossary.md` | 135 | Termos canônicos do framework (Satisfação clínica, Decisão informada, Composição do orquestrador, Anamnese, Engine downstream desacoplável, Precisa-resolver, Dívida consciente × acidental) + RN-D-014/015/016 |
| `README.md` | 39 | Explica relação `framework/` (versionado canônico) × `_reversa_sdd/` (Reversa output gitignored) |

### Princípios fundacionais (F-1 a F-5) 🟢

- **F-1:** MDCU é operacionalização do MCCP em SE — herança direta, não inspiração análoga
- **F-2:** Composição do orquestrador-instância (3 camadas: arquiteto SE sênior + comunicador MCCP + tradutor-artista)
- **F-3:** Satisfação clínica do usuário (bem-estar de longo prazo > desejo imediato; dever de alerta)
- **F-4:** Incompressibilidade da arte da tradução (scorer/checklist mede o necessário, não o suficiente)
- **F-5:** Anatomia humana persistente (bloco "Anamnese do projeto/stakeholder" em `rsop/dados_base.md`)

### Princípios arquiteturais canônicos (P-8, P-9) 🟢

- **P-8:** Delegação a engines downstream desacopláveis (spec-kit, superpowers, bmad, libs maduras, Reversa). Framework é agnóstico ao engine.
- **P-9:** Acompanhamento longitudinal transversal — `rsop` + `commit-soap` abraçam todas as fases (Requisitos → Manutenção)

### Anatomia em 4 camadas (declarada no diagrama) 🟢

| Camada | Componentes | Papel |
|---|---|---|
| Interface humana | `mdcu` | Canal bidirecional Usuário ↔ pipeline |
| Delegação técnica | engines externos desacopláveis | Análise/Especificação/Código/Teste |
| Acompanhamento longitudinal | `rsop` + `commit-soap` | Transversal a todas as fases |
| Fundação | `project-init` + `project-setup` + `mdcu-seg` | Estabelece terreno + vigia |

### Regras de negócio canônicas novas (RN-D-014, 015, 016) 🟢

- **RN-D-014:** Orquestrador alerta contra desejo imediato prejudicial — não compactua com decisão que viola bem-estar de longo prazo declarado
- **RN-D-015:** Nem toda queixa vira `#` — triagem precisa-resolver entre F2 e F4; aceitos-arquivados via prefixo na coluna `#`
- **RN-D-016:** Dívida consciente exige `Tipo: consciente` + `Revisitar` preenchidos — sem prazo, vira acidental travestida

## Δ RSOP populado (artefatos do próprio framework)

Pela primeira vez, o RSOP do `mdcu-framework` está populado — exemplo concreto de dogfooding:

| Artefato | Estado |
|---|---|
| `rsop/dados_base.md` | Inaugurado com bloco "Anamnese do projeto/stakeholder" (F-5) |
| `rsop/lista_problemas.md` | 4 ativos: #2 (consciente), #5/#6/#7 ([B] design-heavy) |
| `rsop/passivos.md` | 7 entries — todos os # resolvidos hoje (commits ba76256, 599307d, 1378d5e, cd59735, be71eca) |
| `rsop/soap/` | 5 SOAPs registrados, um por sessão |

**Observação metodológica:** o último SOAP (`2026-04-27_checklist-qualidade-soap.md`) testa o próprio checklist de qualidade do SOAP introduzido na mesma sessão — auto-aplicação do princípio.

## Padrões transversais novos (refresh)

### 6. Padrão "split estrutural com sub-blocos declarados"

Aplicado em F6 do `mdcu` (3 sub-blocos: delegação + acompanhamento + tradução-fechamento) e parcialmente herdado por `project-setup` (modo desacoplado vs. monolítico declarado). Quando uma fase mistura múltiplos concerns (interface + execução + observação), o padrão é separar em sub-blocos com defaults explícitos e exceções declaradas.

### 7. Padrão "modo monolítico declarado com critério de saída"

Anti-padrão silencioso: framework promete delegação mas falha quando engine não está plugado, e o adopter não percebe. Padrão explícito: nomear o modo monolítico, declarar critérios de aceitação + saída para modo desacoplado. Aplicado em F6.a do MDCU e em `project-setup` 7.a.

### 8. Padrão "regras canônicas vigem em ambos os modos"

Quando há split entre interface/extração e execução/materialização, regras prescritivas (ex: Gestão Determinística de Dependências, Disjuntor 2/2) **não se dividem** — vigoram em ambos os modos, com enforcement diferente em cada (engine externo vs. orquestrador-instância). Aplicado em `project-init/SKILL.md` Gestão Determinística (rule preservada como prescrição canônica) e em `mdcu/SKILL.md` Disjuntor (preservado em F6.b independente do modo de execução).

### 9. Padrão "skill canônico desacoplado da sessão MDCU"

Aplicado em `commit-soap` v2.0.0: skill que era "exclusiva para fechamento de sessão MDCU" passou a "selo longitudinal universal" (qualquer marco). Permite reuso em `project-setup` (commit inicial), `/project-init --refresh` (refresh estrutural), release tags, etc. Reforça P-9.

## Implicações para Detective (deferred)

ADRs retroativos a serem criados em sessão futura:
- **ADR-009** Tese formalizada (F-1 a F-5) como princípios canônicos do framework — commit `ba76256`
- **ADR-010** F6 reformulada em 3 sub-blocos com modo monolítico declarado — commit `599307d`
- **ADR-011** Split project-init / project-setup; commit-soap desacoplado — commit `1378d5e`
- **ADR-012** Schema enriquecido lista_problemas com Tipo + Revisitar — commit `cd59735`
- **ADR-013** Checklist binário de qualidade do SOAP rejeitando scorer numérico — commit `be71eca`

