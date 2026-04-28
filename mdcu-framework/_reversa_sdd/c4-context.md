# C4 — Nível 1 (Contexto)

> Gerado pelo **Reversa Architect** em 2026-04-27
> Adaptação: o "sistema" no centro é o framework metodológico (não uma aplicação web). "Personas" e "sistemas externos" foram reinterpretados.

```mermaid
C4Context
  title mdcu-framework — Contexto

  Person(user, "Usuário (Engenheiro/Dev)", "Adota o framework como metodologia de trabalho. Coautor das decisões em F5; autoridade exclusiva no disjuntor 2/2 e em PRs de upgrade.")
  Person(stakeholder, "Stakeholder do projeto-cliente", "Mapeado em dados_base.md / ARCHITECTURE.md. Não interage diretamente.")
  Person(dpo, "DPO / Responsável", "Owner de tratamento de dados. Citado em rsop/seguranca.md.")

  System_Boundary(framework, "mdcu-framework") {
    System(mdcu, "mdcu-framework", "Coleção de 6 Agent Skills (mdcu, rsop, commit-soap, project-init, project-setup, mdcu-seg) + camada canônica framework/ (principles, architecture-diagram, glossary) — kit de prosa prescritiva carregado por engines de IA.")
  }

  System_Ext(engine, "Engine de IA hospedeiro", "Claude Code / Codex / Cursor / Gemini CLI. Carrega as skills e executa comandos /.")
  System_Ext(downstreamEngines, "Engines downstream desacopláveis (P-8)", "spec-kit, superpowers, bmad, libs maduras, Reversa. Executam Análise/Spec/Código/Teste delegados pelo MDCU em F6.a.")
  System_Ext(scaffolding, "Engines de scaffolding", "cookiecutter / yeoman / plop / copier / cargo-generate. Usados por project-setup em modo desacoplado.")
  System_Ext(git, "Git + GitHub", "Repositório do projeto-cliente. Recebe commits-SOAP de qualquer marco (P-9: sessão MDCU, project-setup, refresh, release).")
  System_Ext(secmgr, "Secret Manager (recomendado)", "Vault / AWS Secrets Manager / equivalente. Prescrito em mdcu-seg.")
  System_Ext(secscan, "Ferramentas de segurança recomendadas", "SAST/DAST, gitleaks, Dependabot/Renovate, audit por gerenciador.")
  System_Ext(pkgmgr, "Gerenciadores de pacote", "npm/yarn/pnpm/Poetry/uv/Cargo/Go/Bundler/Composer/Mix/NuGet — declarados em ARCHITECTURE.md, materializados por project-setup.")

  Rel(user, mdcu, "invoca via comandos /", "/mdcu, /rsop, /commit-soap, /project-init, /project-setup, /mdcu-seg")
  Rel(user, engine, "usa", "via terminal/IDE/web")
  Rel(engine, mdcu, "carrega Agent Skills", "frontmatter YAML → description triggers")
  Rel(mdcu, downstreamEngines, "DELEGA execução técnica", "P-8: Análise/Spec/Código/Teste fora do MDCU")
  Rel(mdcu, scaffolding, "DELEGA setup técnico via project-setup", "modo desacoplado")
  Rel(mdcu, git, "produz commits-SOAP de qualquer marco", "P-9: commit-soap universal")
  Rel(mdcu, pkgmgr, "prescreve uso determinístico", "manifesto + lock no mesmo commit; enforcement via project-setup")
  Rel(mdcu, secscan, "delega quando rastreio dispara", "via /mdcu-seg threat-model | incidente | auditoria")
  Rel(mdcu, secmgr, "prescreve para segredos", "regra absoluta: segredo nunca em código/log/repo")
  Rel(stakeholder, mdcu, "é mapeado em", "dados_base.md (Anamnese F-5) / ARCHITECTURE.md")
  Rel(dpo, mdcu, "é registrado em", "rsop/seguranca.md (LGPD/HIPAA)")

  UpdateLayoutConfig($c4ShapeInRow="3", $c4BoundaryInRow="1")
```

## Notas sobre o contexto

- **O sistema central NÃO é executável** — é prosa interpretada pelo engine. Reinterpretar "sistema" como "kit de prescrições" é necessário.
- **Personas:**
  - `Usuário` é o ator principal. Único humano com autoridade decisória.
  - `Stakeholder` e `DPO` são roles informacionais — não consomem o framework, mas o framework os referencia.
- **Sistemas externos:**
  - `Engine de IA` é o "runtime" — sem ele, as skills são apenas Markdown.
  - `Git + GitHub` é o destino dos artefatos permanentes (commits-SOAP).
  - `Secret Manager` e `Ferramentas de segurança` são **prescritos** pelo framework (recomendações), não executados por ele.
  - `Gerenciadores de pacote` são escolhidos via `/project-init` segundo a stack.

## Lacunas 🔴 do C4 Context

- **Múltiplos engenheiros em paralelo:** o framework não modela colaboração multi-humano (ver `permissions.md` LAC). Cada usuário aparenta operar isoladamente.
- **Outros agentes consumindo SOAPs:** SOAPs antigos podem ser lidos por agentes futuros, mas não há contrato sobre **quais agentes** podem ler **quais SOAPs** (privacidade/sensibilidade).

## Mudanças no contexto desde 2026-04-27 17:44 (refresh)

- **6 skills** (era 5) — `project-setup` adicionado por split estrutural de `project-init` (P-8)
- **Camada canônica `framework/`** declarada — separa fonte de verdade versionada de Reversa output gitignored
- **Engines downstream desacopláveis** explicitados como sistema externo (P-8) — antes eram implícitos
- **Engines de scaffolding** explicitados — antes parte do project-init monolítico
- **commit-soap desacoplado** — P-9: cobre marcos longitudinais arbitrários, não só sessão MDCU
