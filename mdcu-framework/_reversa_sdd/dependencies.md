# Dependências — mdcu-framework

> Gerado pelo **Reversa Scout** em 2026-04-27

---

## Resumo executivo

**O `mdcu-framework` não declara dependências de software.** Não há `package.json`, `pyproject.toml`, `Cargo.toml`, `go.mod`, `Gemfile`, `composer.json`, `mix.exs`, `*.csproj`, nem qualquer manifesto equivalente.

Isto é coerente com a natureza do projeto (coleção de Agent Skills em Markdown). Toda a "execução" do framework é delegada ao **agente de IA hospedeiro** que carrega as skills.

---

## Dependências de runtime (de quem CARREGA as skills)

🟢 **CONFIRMADO** — declarado em frontmatter e/ou SKILL.md de Reversa:

| Engine | Suporte declarado | Origem |
|---|---|---|
| Claude Code | sim — formato canônico de SKILL.md (Anthropic Agent Skills) | mdcu/SKILL.md frontmatter |
| Codex | sim — `AGENTS.md` na raiz | AGENTS.md (raiz) |
| Cursor | sim (pelo formato Agent Skills) | inferido do padrão |
| Gemini CLI | sim (idem) | inferido do padrão |

**🟡 INFERIDO** — não declarado, mas exigido implicitamente:

| Tool | Uso | Onde aparece |
|---|---|---|
| `git` | comando padrão para micro-commits e `commit-soap` | mdcu/SKILL.md:217, commit-soap/SKILL.md:34-40 |
| filesystem POSIX | leitura/escrita de `_mdcu.md`, `rsop/*`, `ARCHITECTURE.md` | toda skill |

**Não exigido:** banco de dados, runtime de aplicação, container, secret manager (apenas mencionado como recomendação prescritiva em mdcu-seg).

---

## Dependências entre skills (CONFIRMADO 🟢)

Esta é a "árvore de dependências" real do projeto. Cada item indica skill **dependente → dependência**.

```
mdcu  ─┬─→ project-init     (bloqueante: F1→F2 exige ARCHITECTURE.md)
       ├─→ rsop             (consultada início ciclo; atualizada via SOAP no fim)
       ├─→ commit-soap      (gera commit de fechamento a partir do SOAP)
       └─→ mdcu-seg         (condicional: gatilhos em F1, F3, F5, F6)

rsop  ─── (autônoma — sem dependências; é alvo de mdcu, mdcu-seg, commit-soap)

commit-soap ─→ rsop          (lê SOAP mais recente em rsop/soap/)

project-init ─── (autônoma — exige apenas existência do projeto)
              ↳ produz: ARCHITECTURE.md + manifesto + lock file (depende da stack do projeto-cliente, NÃO do framework)

mdcu-seg ─┬─→ rsop           (atualiza lista_problemas.md e rsop/seguranca.md)
          └─→ mdcu           (suspende ciclo MDCU em F0/incidente)
```

**Fontes (rastreabilidade):**
- `mdcu` → `project-init`: mdcu/SKILL.md:10, 91-113, 285
- `mdcu` → `rsop`: mdcu/SKILL.md:11, 17-30
- `mdcu` → `commit-soap`: mdcu/SKILL.md:12, 220-222
- `mdcu` → `mdcu-seg`: mdcu/SKILL.md:13, 252-262
- `commit-soap` → `rsop`: commit-soap/SKILL.md:17
- `mdcu-seg` → `rsop`: mdcu-seg/SKILL.md:151-200
- `mdcu-seg` → `mdcu`: mdcu-seg/SKILL.md:77, 206-216

---

## Dependências externas mencionadas (apenas prescritivas)

`project-init` e `mdcu-seg` **citam ferramentas terceiras como recomendação para o projeto-cliente**, não como dependência do framework em si:

| Ferramenta | Citada em | Papel prescrito |
|---|---|---|
| npm / yarn / pnpm | project-init/SKILL.md:67-71 | gerenciador JS/TS |
| Poetry / uv / pip-tools | project-init/SKILL.md:72-74 | gerenciador Python |
| Cargo / Go modules / Bundler / Composer / Mix / NuGet | project-init/SKILL.md:75-80 | gerenciadores por stack |
| `npm audit` / `cargo audit` / `pip-audit` / `poetry check` | project-init/SKILL.md:165 | auditoria de dependências |
| Dependabot / Renovate / Snyk | project-init/SKILL.md:155, mdcu-seg/SKILL.md:176 | upgrades e dependency scan |
| ESLint / Prettier (exemplos) | project-init/SKILL.md:220-221 | linter/formatter |
| `gitleaks` / `husky` | mdcu-seg/SKILL.md:140 | secret scan pre-commit |
| BFG | mdcu-seg/SKILL.md:128 | reescrita de histórico git |
| Vault / AWS Secrets Manager | mdcu-seg/SKILL.md:141 | secret manager |
| SAST / DAST | mdcu-seg/SKILL.md:174-175 | varredura de segurança |

**🟢 Nenhuma destas ferramentas é instalada ou exigida pelo framework.** São conteúdo prescritivo dirigido a projetos que adotarem o MDCU.

---

## Dependências editoriais (`framework-diagrama.html`)

🟢 **CONFIRMADO** — únicas dependências externas em runtime do framework, e estritamente para o documento HTML:

```html
fonts.googleapis.com  → Fraunces, IBM Plex Sans, JetBrains Mono
```

Sem JavaScript externo, sem CSS externo (estilos inline). Documento autocontido fora das três famílias de fontes.

---

## Versões

**Versão do framework:** `v2026.04` (declarada em `MANIFEST.md:1`).

**Versões internas das skills:** apenas o `reversa-scout` e `reversa-archaeologist` (pertencentes ao Reversa, não ao framework) declaram `metadata.version: "1.0.0"` em frontmatter. As 5 SKILL.md do **mdcu-framework** **não têm campo `version`** no frontmatter — versionamento é feito via commit/MANIFEST.

🟡 **INFERIDO:** o framework segue versionamento por release-train datada (`vAAAA.MM`), conforme `MANIFEST.md:1` (`v2026.04`).

---

## Lock file / reprodutibilidade

🟢 **CONFIRMADO:** não há lock file no `mdcu-framework` — irônico, dado que `project-init/SKILL.md:137-184` torna lock file determinístico **vinculante** para projetos que o framework configura. A ausência aqui é coerente: o framework **não tem dependências para travar**.

---

## Riscos identificados

🔴 **LACUNA — requer validação humana:**
1. As 5 SKILL.md do framework **não declaram versão** no frontmatter. O usuário e os agentes só sabem qual versão das skills está instalada via `MANIFEST.md` em disco — que só está presente neste repositório, não na cópia em `~/.claude/skills/`. Pergunta para o usuário: isso é por design (release-train coletiva) ou um gap a fechar?
2. O Reversa instalou-se em `.claude/skills/` e `.agents/skills/` deste mesmo repo — fica a questão se o framework deve documentar essa coexistência (um framework metodológico hospedando o seu próprio analisador) ou se isso é incidental e deve sair via `.gitignore`.
