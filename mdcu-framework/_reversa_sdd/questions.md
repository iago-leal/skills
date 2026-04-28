# Perguntas para Validação — mdcu-framework

> Gerado pelo Reversa Reviewer em 2026-04-27 — atualizado em 2026-04-27 com 5 respostas processadas e 5 perguntas reformuladas com exemplos.

---

## ✅ Pergunta 1 — Comportamento de `/rsop soap` sem `_mdcu.md` (REFORMULADA com exemplos)

**Contexto:** `rsop/SKILL.md:155, 161` declara que o SOAP é hidratado a partir do `_mdcu.md`. Mas a skill não especifica o que acontece se `_mdcu.md` não existir.

**Quando isso aconteceria na prática (cenários):**

- **Cenário A — Adoção parcial:** novo usuário do framework instala `rsop` mas ainda não usa `mdcu`. Quer registrar SOAP de uma sessão informal ("ontem mexemos em X, hoje quero documentar"). Não há `_mdcu.md` porque nunca rodou `/mdcu`.
- **Cenário B — Sessão sem ciclo MDCU:** alguém faz um hotfix de 2 minutos e quer registrar um SOAP curto, sem passar pelas 6 fases do MDCU.
- **Cenário C — `_mdcu.md` deletado por engano:** o agente apagou o arquivo cedo demais, mas o usuário ainda quer fechar com SOAP.

**Pergunta reformulada:** em qualquer desses cenários, `/rsop soap` deveria:

- (a) **ABORTAR com mensagem orientadora** — "não há `_mdcu.md` na sessão. Use `/mdcu` antes, ou se é registro informal, edite manualmente um SOAP em `rsop/soap/`." (mesmo padrão que `commit-soap` usa quando não há SOAP)
- (b) **CRIAR SOAP "manual"** com S/O/A/P/R em branco, para o usuário preencher do zero. Permite uso fora do ciclo MDCU.
- (c) **PERGUNTAR** ao usuário qual cenário (A/B/C) e adaptar o comportamento.

**Resposta (Iago):** `(c)` — PERGUNTAR ao usuário qual cenário (A/B/C) e adaptar.

**Aplicado em:**
- `_reversa_sdd/sdd/rsop.md` Fluxos Alternativos — reclassificado de 🔴 para 🟢
  - Cenário A → SOAP em branco para preenchimento manual
  - Cenário B → SOAP guiado curto
  - Cenário C → ABORTA com orientação de recuperação
- Adicionado cenário Gherkin em `sdd/rsop.md`

---

## ✅ Pergunta 2 — Comportamento de `/rsop init` em diretório existente (REFORMULADA com exemplos)

**Contexto:** `/rsop init` cria a estrutura `rsop/` com `dados_base.md`, `lista_problemas.md`, `passivos.md` (vazio), e `soap/`. Não diz o que fazer se `rsop/` já existe.

**Quando isso aconteceria na prática (cenários):**

- **Cenário A — Re-instalação acidental:** usuário esquece que já rodou `/rsop init` neste projeto e roda de novo. `rsop/lista_problemas.md` já tem 12 ativos com histórico de SOAPs.
- **Cenário B — Reset deliberado:** usuário quer limpar e recomeçar (ex: projeto pivotou totalmente, prontuário antigo é irrelevante).
- **Cenário C — Restauração parcial:** alguém deletou `passivos.md` por engano; quer recriar só esse arquivo sem mexer no resto.

**Pergunta reformulada:** o que `/rsop init` deveria fazer quando `rsop/` já existe?

- (a) **ABORTAR com aviso** — "rsop/ já existe (X ativos, Y SOAPs). Para reset use `/rsop reset` (não existe ainda); para restaurar arquivos faltantes use `/rsop repair` (não existe ainda)." Decisão: não sobrescreve nada, e força o usuário a usar comando diferente para cada caso.
- (b) **MERGE não-destrutivo** — só cria os arquivos que não existem (resolve cenário C automaticamente, mas mascara cenário A).
- (c) **SOBRESCREVER com confirmação dupla** — "isso vai apagar 12 ativos e 35 SOAPs. Tem certeza? digite SIM" — atende cenário B ao custo de risco em A.
- (d) **outra abordagem** (descreva).

**Resposta (Iago):** `(a)` — ABORTAR com aviso, sugerindo `/rsop reset` e `/rsop repair` como comandos futuros distintos.

**Aplicado em:**
- `_reversa_sdd/sdd/rsop.md` Fluxos Alternativos — reclassificado de 🔴 para 🟢
- Comandos `/rsop reset` e `/rsop repair` adicionados à tabela de Interface como **(roadmap, não implementado)** 🔵
- Adicionado cenário Gherkin em `sdd/rsop.md`

---

## ✅ Pergunta 3 — `/commit-soap` com SOAP que tem A vazio — RESPONDIDA

**Resposta:** **ABORTA com aviso. Não há como SOAP existir sem A.**

**Aplicado em:**

- `_reversa_sdd/sdd/commit-soap.md` Fluxos Alternativos — reclassificado de 🔴 para 🟢
- Adicionado cenário Gherkin: "Dado que existe SOAP mas a seção ## A está vazia / Quando o usuário digita /commit-soap / Então commit-soap ABORTA..."

---

## ✅ Pergunta 4 — `/commit-soap --amend` em commit que NÃO veio do commit-soap — RESPONDIDA

**Resposta:** **AVISAR.**

**Aplicado em:**

- `_reversa_sdd/sdd/commit-soap.md` Fluxos Alternativos — reclassificado de 🔴 para 🟢
- Adicionado cenário Gherkin: "Dado que o último commit é um WIP padrão (sem formato A:/P:/Refs:) / Quando o usuário digita /commit-soap --amend / Então commit-soap AVISA... E aguarda confirmação explícita..."

---

## ✅ Pergunta 5 — Naming convention de `<contexto>` em SOAPs — RESPONDIDA

**Resposta:** **Sem opinião** — convenção livre (kebab-case, snake_case ou prosa, sem espaços por constraint de filesystem).

**Aplicado em:**

- `_reversa_sdd/data-dictionary.md` — Lacuna 2 reclassificada para 🟢; nota: scripts de busca devem usar `ls rsop/soap/ | grep -i <termo>` agnóstico a convenção

---

## ✅ Pergunta 6 — Idioma canônico do framework — RESPONDIDA

**Resposta:** **pt-BR canônico, com robustez operacional em inglês.**

**Aplicado em:**

- `_reversa_sdd/architecture.md` — nova seção "6. Idioma" 🟢 detalhando: SKILL.md sempre em pt-BR; frontmatter `description` deve ter triggers bilingues; conteúdo de artefatos pode ser misto pt-BR/EN; jargão técnico (SOAP, Demanda, Queixa, F0) mantém grafia pt-BR mesmo em contexto EN; **i18n completa** (tradução das skills) NÃO é objetivo desta release-train

---

## ✅ Pergunta 7 — Colaboração multi-humano em sessão MDCU — RESPONDIDA

**Resposta:** **`_mdcu.md` é compartilhado.** Engenheiros humanos no mesmo ciclo coautoram juntos; LLMs NÃO entram como coautores.

**Aplicado em:**

- `_reversa_sdd/sdd/mdcu.md` — linha "Co-autoria multi-humano" promovida de Won't para Should 🟢
- `_reversa_sdd/permissions.md` — seção "Lacuna 🔴" reescrita como "Multi-humano 🟢" com prática detalhada (S: pode ter notas atribuídas; commit usa `Co-authored-by:` PADRÃO Git para humanos, NÃO o trailer Anthropic; conflito de edição concorrente fica com git)
- Linha da matriz de permissões esclarecida: distinção entre `Co-Authored-By: Claude` (proibido) vs. `Co-authored-by: <humano>` (permitido em multi-humano)

---

## ✅ Pergunta 8 — Hooks programáticos prescritos vivem fora do repo distribuído (REFORMULADA com exemplos)

**Contexto:** ADR-006 (commit `6ed9d39` de 2026-04-17) registra que o framework prescreve hooks do Claude Code para enforcement programático:

| Hook                   | O que faz                                                                  | Onde fica                                          |
| ---------------------- | -------------------------------------------------------------------------- | -------------------------------------------------- |
| `UserPromptSubmit`   | injeta o conteúdo de `_mdcu.md` no system prompt a cada turno do agente | `~/.claude/settings.json` (ou equivalente local) |
| `commit-msg`         | filtra `Co-Authored-By: Claude` antes do commit ser efetivado            | `~/.claude/hooks/commit-msg`                     |
| anti-deriva de persona | impede o agente de "esquecer" o `mdcu` mid-sessão                       | `~/.claude/hooks/...`                            |

**Problema:** quem clona `mdcu-framework/` do GitHub recebe as 5 SKILL.md, mas **NÃO recebe os hooks**. Os hooks ficam na config global do usuário Iago. Resultado: comportamento real do framework varia drasticamente entre máquina do Iago (com hooks) e máquina de outro engenheiro (sem hooks).

**Cenários concretos:**

- **Cenário A — Outro engenheiro adota:** clona o repo, copia as 5 SKILL.md para `~/.claude/skills/`. Espera o disjuntor 2/2 funcionar; mas como o `_mdcu.md` não é injetado a cada turno (sem `UserPromptSubmit`), o agente esquece o contador entre interações. Disjuntor não funciona na prática.
- **Cenário B — Sem hook commit-msg:** Iago acidentalmente esquece de configurar o filtro. O agente pode escrever `Co-Authored-By: Claude` em algum commit, ferindo a regra absoluta.

**Pergunta reformulada:** como o framework deve tratar essa assimetria?

- (a) **Documentar em arquivo novo** (`HOOKS.md` ou `INSTALL.md` na raiz do repo) com receitas copy-paste — incluindo o JSON de `~/.claude/settings.json` para `UserPromptSubmit` e o script bash do hook `commit-msg`. Outros engenheiros aplicam manualmente.
- (b) **Aceitar como design** — hooks são específicos do Claude Code e o framework é multi-engine (Codex, Cursor, Gemini). Documentar apenas a **expectativa de comportamento** (o que cada hook faz), e cada engine que adapte. Sem receitas executáveis.
- (c) **Criar skill nova `mdcu-hooks`** com comandos `/mdcu-hooks install` e `/mdcu-hooks check` que aplicam as receitas no diretório certo do engine ativo. Eleva os hooks a artefato versionado dentro do framework.
- (d) **Outra abordagem** (descreva — ex: deixar 100% out-of-scope, dependendo do agente).

**Resposta (Iago):** **híbrido (a)+(c)** — JSON de spec versionado no repo + skill nova `mdcu-hooks` que o orquestrador invoca para aplicar a spec no engine ativo. Importante para o MDCU; precisa ser versionado.

**Aplicado em:**
- `_reversa_sdd/architecture.md` — D-004 reclassificada para ✅ resolvido; nova skill `mdcu-hooks` (versão `0.1.0`) adicionada à seção de versionamento
- `_reversa_sdd/c4-containers.md` — diagrama de container futuro adicionado mostrando `mdcu-hooks` lendo `hooks-spec.json` e aplicando em `~/.claude/settings.json` + `~/.claude/hooks/*`
- `_reversa_sdd/sdd/mdcu.md` — regra do D-004 reescrita para apontar para a nova skill como solução roadmap
- Comandos previstos: `/mdcu-hooks install`, `/mdcu-hooks check`, `/mdcu-hooks uninstall`

---

## ✅ Pergunta 9 — Gate de integração foi removido em ADR-005 sem substituto formal (REFORMULADA com exemplos)

**Contexto:** Em 2026-04-16 (commit `2265776`, ADR-004) você adicionou ao MDCU um gate explícito antes de F6 (deploy):

> "Gate de Integração (Fase 6 pré-deploy) aciona nova skill `teste-integrado` exigindo teste isolado verde + suíte integrada verde + critério objetivo do plano."

Em 2026-04-17 (commit `e06fa1a`, ADR-005), você consolidou tudo em `mdcu-seg` e **`teste-integrado` foi removido**. Hoje o que protege contra "deploy com teste vermelho" é apenas o `ARCHITECTURE.md.Comandos principais` que define `test`/`build` — mas **não há regra explícita do MDCU exigindo que o agente rode esses comandos antes do fechamento.**

**Cenário concreto do risco:**

> Iago pede `/mdcu` para implementar feature X. Agente faz F1-F6 normalmente. Em F6 implementa o código e os testes; alguns testes FALHAM mas estão "perto de passar". Agente sumariza para o usuário ("falta ajustar 2 testes da suíte de orders") e propõe `/mdcu fechar`. Sem gate explícito, MDCU aceita: gera SOAP, gera commit-soap, deleta `_mdcu.md`. **Commit entra na branch principal com testes quebrados.**

Com o gate antigo, isso não passaria — o gate exigiria suíte integrada verde antes de avançar para fechamento.

**Pergunta reformulada:** como tratar essa lacuna de gate?

- (a) **Deliberado — o gate ficou no `ARCHITECTURE.md`** e o agente em F6 deve, por disciplina, rodar `test`/`build` antes de propor `/mdcu fechar`. Sem regra explícita, mas com `Comandos principais` documentados, espera-se que agente respeite. Aceita-se o risco do cenário acima.
- (b) **É gap a corrigir — adicionar regra ao MDCU F6:** nova regra (ex: "regra 14") em `mdcu/SKILL.md` que torna `test` (do `ARCHITECTURE.md.Comandos principais`) **vinculante** antes de `/mdcu fechar`. Falha de teste impede fechamento até correção ou reenquadramento explícito.
- (c) **Reviver `teste-integrado` como skill** — recriar skill removida em ADR-005 com escopo enxuto; MDCU F6 invoca como gate.
- (d) **Outra abordagem** (descreva).

**Resposta (Iago):** `(b)` — adicionar regra explícita ao MDCU F6 vinculando `test`/`build` do `ARCHITECTURE.md` antes de `/mdcu fechar`.

**Aplicado em:**
- `_reversa_sdd/sdd/mdcu.md` — nova regra de Negócio "Gate de Integração (F6 pré-fechamento)" 🟢
- `_reversa_sdd/sdd/mdcu.md` — 2 cenários Gherkin novos cobrindo `test` falho e cobertura conjunta `test`+`build`
- `_reversa_sdd/sdd/mdcu.md` — Prioridade — adicionado linha **Must** "Gate de Integração (F6 pré-fechamento)"
- `_reversa_sdd/adrs/005-...md` — atualizado para apontar a resolução em P9 (não revive `teste-integrado`; gate vive dentro do MDCU)

---

## ✅ Pergunta 10 — Convenção de versionamento para frontmatter (REFORMULADA com exemplos)

**Contexto:** Você já confirmou (D-001) que adicionar `version` ao frontmatter das 5 SKILL.md é gap a corrigir. Falta definir **qual convenção** usar.

**Exemplos concretos** das 3 convenções típicas, aplicadas a `mdcu/SKILL.md`:

### Opção (a) — semver puro

```yaml
---
name: mdcu
version: "2.4.0"
description: ...
---
```

- Ao mexer numa skill, incrementa MAJOR/MINOR/PATCH conforme a regra clássica de semver.
- Cada skill evolui independente — `mdcu` pode estar em `2.4.0`, `rsop` em `1.7.3`.
- ✅ Ferramentas existentes (npm, cargo, etc.) entendem semver — facilita futuro `npm`-like de skills.
- ❌ Perde a noção de "release-train coletivo" do `MANIFEST.md`. Requer changelog por skill.

### Opção (b) — date-based atrelado ao release-train

```yaml
---
name: mdcu
version: "v2026.04.0"
description: ...
---
```

- Major segue o release-train (`v2026.04`); patch incrementa a cada hotfix dentro do mesmo release.
- Todas as 5 skills carregam o **mesmo** `vAAAA.MM.X` no momento do release.
- ✅ Coerente com `MANIFEST.md` atual. Fácil saber "qual release tenho instalado" — basta ler frontmatter de qualquer skill.
- ❌ Não distingue mudanças entre skills no mesmo release; menos granular.

### Opção (c) — híbrido (release + semver dentro)

```yaml
---
name: mdcu
version: "v2026.04+2.4.0"
description: ...
---
```

- Antes do `+`: release-train. Depois: semver da skill dentro daquele release.
- ✅ Mantém ambos os conceitos. Busca por release-train ainda funciona (`grep "v2026.04"`).
- ❌ Mais complexo; tooling precisa parsear.

**Adicionalmente:** o próximo release será `v2026.05` (incorporando essas decisões e patches da Reversa)?

**Resposta (Iago):** `(a)` — semver puro por skill.

**Aplicado em:**
- `_reversa_sdd/architecture.md` — nova seção "7. Versionamento" 🟢 com regras MAJOR/MINOR/PATCH e versões iniciais sugeridas para `v2026.05`:
  - `mdcu` → **3.0.0** (MAJOR — Gate de Integração + multi-humano)
  - `rsop` → **1.2.0** (MINOR — comportamentos P1/P2)
  - `commit-soap` → **1.1.0** (MINOR — comportamentos P3/P4)
  - `project-init` → **1.0.0** (sem mudanças funcionais nesta rodada)
  - `mdcu-seg` → **1.0.0** (sem mudanças funcionais)
  - `mdcu-hooks` → **0.1.0** (NOVA, pré-1.0)
- `MANIFEST.md` permanece como bundle marker (`vAAAA.MM` lista quais versões compõem o release); frontmatter `version` é fonte de verdade da skill individual
- **Próximo release:** `v2026.05` incorporando rodada 0 + rodada 1 + nova skill `mdcu-hooks`

---

## Resumo do estado (rodada 2 — final)

- **Respondidas e processadas (10/10):** TODAS as perguntas respondidas e aplicadas.
  - Rodada 1: P3, P4, P5, P6, P7
  - Rodada 2: P1, P2, P8, P9, P10
- **Lacunas pendentes:** **0** 🟢
- **Confiança geral:** subindo para perto de **100%** após rodada 2 (ver `confidence-report.md` para números finais).
- **Próximo release sugerido:** `v2026.05` incorporando todas as decisões + nova skill `mdcu-hooks`.
