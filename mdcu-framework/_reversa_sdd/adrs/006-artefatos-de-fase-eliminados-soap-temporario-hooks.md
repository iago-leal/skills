# ADR-006 — Artefatos de fase eliminados, `_mdcu.md` injetado por hook, SOAP temporário

- **Status:** Aceito
- **Data:** 2026-04-17
- **Commit-fonte:** `6ed9d39` 🟢
- **Confiança:** 🟢 CONFIRMADO (commit longo descreve a decisão)

## Contexto

Versões anteriores do MDCU mantinham **artefatos por fase** (`_sessao.md`, e estruturas separadas por fase). Em uso real, isso fragmentava o raciocínio e exigia que o agente lesse múltiplos arquivos. Pior: a janela de contexto do agente degradava entre fases (Lost in the Middle), e a memória de chat não bastava para fechamento.

Adicionalmente, alguns commits estavam ganhando trailer `Co-Authored-By: Claude` automaticamente, ferindo a regra absoluta de autoria do usuário.

## Decisão

Cinco mudanças simultâneas:

1. **Artefatos de fase eliminados.** Tudo passa a viver em **um único `_mdcu.md`** transitório.
2. **`_sessao.md` e diretório `rsop/` extintos** como caminhos primários (substituídos pela arquitetura atual).
3. **`_mdcu.md` injetado no contexto via `UserPromptSubmit`** — hook do Claude Code que insere o arquivo no system prompt a cada turno. Ataca Lost in the Middle no nível do harness.
4. **Lista de problemas (`lista_problemas.md`) injetada no `CLAUDE.md`** do projeto. Ativos passam a "morar" no system prompt; passivos saem (origem da regra "ativos vs. passivos").
5. **SOAP temporário (`_soap.md`?)** durante o fechamento — destilação intermediária antes do SOAP definitivo.
6. **Hook `commit-msg` filtra `Co-Authored-By` globalmente** — enforcement programático da regra de autoria.
7. **Hook anti-deriva de persona** — não detalhado neste commit, mas mencionado.

## Consequências
- ✅ Raciocínio do ciclo concentrado em UM arquivo (`_mdcu.md`).
- ✅ Defesa **arquitetural** contra Lost in the Middle (injeção a cada turno).
- ✅ Lista de problemas sempre visível (= sempre acionável) ao agente.
- ✅ Co-Authored-By bloqueado por hook, não por convenção.
- ⚠️ **Assimetria de distribuição (LACUNA D-004):** os hooks vivem em `~/.claude/` do usuário, NÃO em `mdcu-framework/`. Quem clona o repo NÃO recebe os hooks. O framework prescreve disciplina mas o enforcement real está fora do repo.
- ⚠️ Desde então, o subdiretório `rsop/` voltou a ser o "lar" canônico dos artefatos longitudinais (rsop/SKILL.md:25-32). Existe ambiguidade sobre o que "extinto" significou exatamente — possivelmente apenas o RSOP do próprio framework foi reorganizado, mantendo `rsop/` como convenção para projetos-clientes.
