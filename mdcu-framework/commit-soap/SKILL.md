---
name: commit-soap
version: "2.0.0"
author: Iago Leal <github.com/iago-leal>
description: Selo longitudinal — gera mensagem de commit em formato A+P para qualquer marco do projeto. **Desacoplado da sessão MDCU**: aceita SOAP gerado pela skill `rsop`, A+P inline (passado por outra skill como `project-setup`), ou caminho explícito via `--from`. ATIVE SEMPRE que o usuário digitar /commit-soap, pedir para commitar com contexto cognitivo (A+P), encerrar sessão MDCU com SOAP pendente, ou quando outra skill (project-setup, rsop) precisar selar marco longitudinal. Também ative quando o usuário mencionar "commit com A+P", "selo longitudinal", "marco do projeto", "commit-soap inicial". NÃO ative para commits intermediários triviais (formatação, typo, WIP, checkpoints) — esses usam `git commit` padrão.
---

# commit-soap — Selo Longitudinal Universal

## Problema que resolve

Mensagens de commit convencionais capturam *o quê* foi alterado, mas não *por quê se chegou a essa conclusão* nem *o que se planejou a partir dela*. O contexto cognitivo do **marco** se perde — quem retoma o projeto depois de um intervalo precisa reconstruir o raciocínio lendo código, issues ou perguntando.

O `commit-soap` resolve isso para **qualquer marco longitudinal do projeto** — não só fechamento de sessão MDCU. A mensagem de commit funciona como o A+P de um SOAP: o mínimo suficiente para retomar contexto sem reler todo histórico.

**Marcos cobertos:**
- Fechamento de sessão MDCU (SOAP gerado pela skill `rsop`)
- Setup inicial do projeto (commit zero gerado pelo `project-setup`)
- Refresh estrutural após `/project-init --refresh`
- Release/tag de versão com A+P de release notes
- Merge de feature final
- Qualquer outro marco que o adopter declare como longitudinal

**Princípio P-9 do framework** (`framework/principles.md`): acompanhamento longitudinal abraça todas as fases do ciclo de desenvolvimento, não só o ciclo MDCU. `commit-soap` é o selo dessa camada — universal por design.

## Mudança em v2.0.0 (desacoplamento)

Versão 1.x era **exclusiva para fechamento de sessão MDCU** — lia `rsop/soap/` sempre. Versão 2.0.0 desacopla:

- **Default preservado:** `/commit-soap` sem argumento continua lendo o último SOAP em `rsop/soap/` (comportamento da v1.x).
- **Novo:** `/commit-soap --from <path>` lê A+P de qualquer arquivo estruturado.
- **Novo:** `/commit-soap --inline` aceita A+P direto na invocação (usado por `project-setup`, `project-init --refresh`, etc.).

Compatibilidade: comportamento default (sem argumento) idêntico à v1.x. Quebra de versão é semântica — escopo da skill mudou de "fechamento MDCU" para "selo longitudinal universal", o que justifica o MAJOR bump.

## Fontes de A+P aceitas

| Fonte | Como invocar | Quem usa |
|---|---|---|
| **SOAP em `rsop/soap/`** (último) | `/commit-soap` (default) | Fechamento de sessão MDCU |
| **Caminho explícito** | `/commit-soap --from <path>` | Refresh manual, marco customizado |
| **A+P inline** | `/commit-soap --inline` (recebe via stdin ou argumento estruturado) | `project-setup`, `project-init --refresh`, integrações de outras skills |

## Quando usar

O `commit-soap` é o **selo de marco longitudinal**. **Uso EXCLUSIVO para:**

1. **Fechamento de sessão MDCU:** após `/rsop soap` registrar o SOAP destilado da sessão.
2. **Setup inicial do projeto:** `project-setup` ao materializar `ARCHITECTURE.md` em disco.
3. **Refresh estrutural:** `/project-init --refresh` que muda stack/gerenciador.
4. **Marcos declarados pelo adopter:** release tag com A+P de release notes, merge de feature final, etc.

**NÃO usar para:**

- **WIPs (Work In Progress):** checkpoints intermediários durante F6 do MDCU em modo monolítico. Esses usam `git commit` padrão.
- **Micro-commits atômicos:** salvamentos intermediários para preservar estado, refactors de baixo risco, ajustes de formatação, typos. `git commit` padrão basta.
- **Commits de merge sem A+P:** merge de branch de trabalho intermediário, bumps de dependência rotineiros, etc.

**Regra prática:** se o evento é um **marco** (algo que adopter futuro vai querer encontrar via `git log --grep="A:"`), use `commit-soap`. Se é ruído operacional, use `git commit` padrão.

### Fluxo canônico (sessão MDCU)

1. Sessão MDCU acontece — durante F6, múltiplos micro-commits (`git commit`) podem ocorrer em modo monolítico.
2. Sessão termina → SOAP é registrado via `/rsop soap` (obrigatório para fechamento).
3. Selo via `/commit-soap` (sem argumento) — extrai A+P do SOAP mais recente em `rsop/soap/`.

### Fluxo canônico (project-setup)

1. `/project-init` extrai contrato → `ARCHITECTURE.md`.
2. `/project-setup` materializa setup (manifesto + lock file + `.gitignore` + estrutura).
3. `project-setup` invoca `commit-soap --inline` com A+P pré-formatado:
   ```
   A: Projeto sem contrato técnico materializado — sem lock file, sem reprodutibilidade
   P: ARCHITECTURE.md materializado: [manifesto] + [lock file] + .gitignore + estrutura inicial; modo: [desacoplado/monolítico]

   Refs: ARCHITECTURE.md
   ```

### Fluxo canônico (refresh estrutural)

1. Usuário roda `/project-init --refresh` (mudança de stack ou gerenciador).
2. `ARCHITECTURE.md` editado in-place; changelog interno atualizado.
3. `/project-setup --refresh` aplica mudanças no setup técnico.
4. `commit-soap --inline` sela com A+P:
   ```
   A: Stack do projeto mudou de [old] para [new] — contrato técnico precisava reformalizar
   P: ARCHITECTURE.md atualizado; manifesto + lock file regenerados; estrutura ajustada

   Refs: ARCHITECTURE.md (changelog interno)
   ```

Visão: o `git log` separa dois registros — micro-commits técnicos (ruído operacional) e commits-SOAP (marcos cognitivos). O valor do framework depende dessa distinção ser preservada — agora reforçada por commits-SOAP **de qualquer origem** (sessão MDCU, project-setup, refresh, release, etc.).

## Formato da mensagem

```
A: [avaliação síntese — o que se entendeu sobre este marco]
P: [plano síntese — o que foi feito ou planejado a partir do marco]

Refs: [caminho do artefato canônico relacionado: SOAP completo, ARCHITECTURE.md, etc.]
```

### Regras de formatação

- **Linha A:** síntese da Avaliação. O que foi entendido neste marco; hipótese principal; nível de resolução atingido. Uma a três frases. Ordem direta, sem redundância.
- **Linha P:** síntese do Plano. O que foi feito ou planejado a partir desta avaliação. Uma a três frases. Ordem direta, sem redundância.
- **Refs:** caminho relativo do artefato canônico relacionado (SOAP, ARCHITECTURE.md, release notes, etc.) para quem quiser profundidade.
- **Primeira linha (A) deve ter no máximo 72 caracteres** para compatibilidade com `git log --oneline`. Se a avaliação for complexa, usar a primeira linha como resumo e detalhar no corpo.
- **Sem tipo técnico obrigatório** (feat/fix/refactor). Pode coexistir se o projeto usar Conventional Commits, mas não é exigido. O valor está no A+P, não na categoria.
- **Mesma disciplina de escrita do SOAP:** conciso sem perder informação relevante, sem redundância, ordem direta, dispensa de secundário.

### Formato com Conventional Commits (opcional)

Se o projeto adota Conventional Commits, o formato pode ser combinado:

```
fix: [resumo técnico curto]

A: [avaliação síntese]
P: [plano síntese]

Refs: rsop/soap/2026-04-15_performance.md
```

## Múltiplos problemas (no caso de SOAP de sessão MDCU)

Se o SOAP da sessão abordou múltiplos problemas, a mensagem lista cada um:

```
A: #3 N+1 confirmado na listagem de pedidos — piorou desde último deploy
A: #7 Timeout do serviço externo — intermitente, sem padrão claro ainda
P: #3 Eager loading em OrderQuery + índice composto — reavaliação pós-deploy
P: #7 Circuit breaker adicionado — monitorar por 48h antes de reclassificar

Refs: rsop/soap/2026-04-15_performance-e-timeout.md
```

## Consulta via git log

O formato permite buscas contextuais diretas no terminal:

- `git log --grep="A:"` — todas as avaliações (marcos cognitivos do projeto, **incluindo setup inicial e refreshes**, não só sessões MDCU).
- `git log --grep="P:"` — todos os planos.
- `git log --grep="#3"` — toda a história longitudinal do problema 3 (sessões MDCU).
- `git log --grep="Refs: rsop"` — todos os commits-SOAP com SOAP de sessão MDCU vinculado.
- `git log --grep="Refs: ARCHITECTURE.md"` — marcos arquiteturais (setup inicial + refreshes).

Filtro inverso: `git log --invert-grep --grep="A:"` — exibe apenas os micro-commits técnicos, útil para auditar ruído operacional.

## Uso com `/commit-soap`

- `/commit-soap` — Lê o SOAP mais recente da sessão em `rsop/soap/`, extrai A+P, gera a mensagem formatada e exibe para revisão antes de commitar. (Default — comportamento da v1.x preservado.)
- `/commit-soap --from <path>` — Lê A+P de arquivo arbitrário (SOAP customizado, release notes estruturada, etc.).
- `/commit-soap --inline` — Recebe A+P diretamente via argumento estruturado (usado por `project-setup`, `project-init --refresh`, integrações).
- `/commit-soap --dry-run` — Gera a mensagem mas não executa o commit. Útil para revisar.
- `/commit-soap --amend` — Reescreve a mensagem do último commit a partir da fonte de A+P (caso o SOAP/marco tenha sido atualizado após o commit).

## Operação

1. **Determinar fonte de A+P:**
   - Sem argumento → `rsop/soap/` (último arquivo).
   - `--from <path>` → ler arquivo apontado.
   - `--inline` → A+P passado pelo invocador.
2. **Extrair seções A e P** (e Refs implícita ou explícita).
3. **Sintetizar** cada seção seguindo as regras de formatação.
4. **Montar a mensagem** no formato especificado.
5. **Exibir ao usuário** para revisão e confirmação.
6. **Executar `git commit`** com a mensagem aprovada.

Se a fonte de A+P está vazia ou não existe:
- Modo default (sem argumento): "Não há SOAP da sessão atual. Registre via `/rsop soap` antes de commitar — ou, se isto é apenas um WIP/checkpoint, use `git commit` padrão."
- Modo `--from`: "Arquivo `<path>` não encontrado ou não contém A+P. Verifique o caminho ou use `/commit-soap --inline`."
- Modo `--inline`: "A+P inline vazio ou malformado. Estrutura esperada: `A: ...\nP: ...\nRefs: ...`."
- **Não gerar commit com mensagem inventada.**

---

## Integração com outras skills

| Skill | Integração |
|-------|------------|
| `rsop` | Fonte default de A+P (último SOAP em `rsop/soap/`). Mantida do v1.x. |
| `project-setup` | Invoca `--inline` ao final do setup técnico para selar commit inicial. |
| `project-init` | Invoca `--inline` em `--refresh` que muda stack/gerenciador. |
| `mdcu` | F6.c (tradução de retorno + fechamento) invoca `commit-soap` (sem argumento) para selo de fechamento da sessão. |
