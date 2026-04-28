# Visão geral arquitetural — mdcu-framework

> Gerado pelo **Reversa Architect** em 2026-04-27 (refresh cirúrgico após 6 sessões MDCU)
> Síntese a partir de Scout, Archaeologist e Detective.
> **Fonte canônica:** `framework/principles.md` (versionado, distribuído). Este documento é Reversa output (gitignored, regenerável).

---

## 1. Tese arquitetural

`mdcu-framework` é um **kit de prosa prescritiva** distribuído como Agent Skills, com a tese central:

> "A forma como a informação é organizada determina a forma como se pensa." (rsop/SKILL.md:10)

Toda decisão arquitetural deriva dessa tese:
- **Markdown estruturado**, não código → portabilidade entre engines de IA.
- **Telegráfico por princípio** → economia cognitiva, anti-deriva.
- **Artefatos efêmeros vs. permanentes** → separação entre raciocínio (que morre) e destilado (que vive).
- **Gates não-negociáveis** → contratos clínicos antes de execução técnica.
- **Co-autoria humana** → IA é instrumento, não substituto.

## 2. Mapa do sistema

```
                       ┌─────────────────────────────┐
                       │  Engine de IA hospedeiro    │
                       │  (Claude Code / Codex /     │
                       │   Cursor / Gemini CLI)      │
                       └──────────────┬──────────────┘
                                      │ carrega Agent Skills
                                      ↓
       ┌──────────────────────────────────────────────────────────────────┐
       │                       mdcu-framework                             │
       │                                                                  │
       │   ┌─ FUNDAÇÃO ───────────────────────────────────────────────┐   │
       │   │ project-init  ─→ ARCHITECTURE.md (contrato extraído)     │   │
       │   │      ↓                                                    │   │
       │   │ project-setup ─→ manifesto + lock + .gitignore + commit  │   │
       │   │      (modo desacoplado / monolítico declarado)            │   │
       │   │ mdcu-seg     ─→ rsop/seguranca (vigia continuamente)     │   │
       │   └───────────────────────────────────────────────────────────┘   │
       │                                                                  │
       │   ┌─ INTERFACE HUMANA ───────────────────────────────────────┐   │
       │   │ mdcu ─→ _mdcu.md (sessão); F6 em 3 sub-blocos:           │   │
       │   │        F6.a delegação a engine OU monolítico declarado  │   │
       │   │        F6.b acompanhamento (Disjuntor 2/2)               │   │
       │   │        F6.c tradução de retorno + fechamento             │   │
       │   └───────────────────────────────────────────────────────────┘   │
       │                                                                  │
       │   ┌─ DELEGAÇÃO TÉCNICA (engines externos desacopláveis P-8)─┐   │
       │   │ spec-kit • superpowers • bmad • libs maduras • Reversa   │   │
       │   └───────────────────────────────────────────────────────────┘   │
       │                                                                  │
       │   ┌─ ACOMPANHAMENTO LONGITUDINAL (transversal — P-9) ────────┐   │
       │   │ rsop  ─→ rsop/{dados_base+anamnese, lista_problemas,     │   │
       │   │          passivos, soap/}                                 │   │
       │   │ commit-soap ─→ git history (selo de QUALQUER marco:      │   │
       │   │          sessão MDCU, project-setup, refresh, release)   │   │
       │   └───────────────────────────────────────────────────────────┘   │
       │                                                                  │
       │   ┌─ ARTEFATOS CANÔNICOS (versionados — framework/) ─────────┐   │
       │   │ principles.md (F-1 a F-5 + P-8, P-9)                     │   │
       │   │ architecture-diagram.md (anatomia 4 camadas)             │   │
       │   │ glossary.md (termos canônicos + RN-D-014/015/016)        │   │
       │   └───────────────────────────────────────────────────────────┘   │
       └──────────────────────────────────────────────────────────────────┘
                            │
                            ↓ aplica ao
       ┌──────────────────────────────────────────────────────────────────┐
       │              Projeto-cliente (qualquer stack)                    │
       │  git + código (engine) + dados + _mdcu.md + rsop/ +              │
       │  ARCHITECTURE.md + manifesto + lock file (commitado, sempre)     │
       └──────────────────────────────────────────────────────────────────┘
```

Veja diagramas detalhados em:
- `c4-context.md` — Nível 1 (Contexto)
- `c4-containers.md` — Nível 2 (Containers — atualizado para 6 skills + camada framework/)
- `c4-components.md` — Nível 3 (Componentes — foco no MDCU; F6 em 3 sub-blocos)
- `erd-complete.md` — Modelo de artefatos (atualizado com artefatos do project-setup)
- `traceability/spec-impact-matrix.md` — Matriz de impacto

## 3. Princípios arquiteturais (extraídos)

### P-1 Portabilidade entre engines (🟢)
Decisão: Markdown puro + frontmatter YAML compatível com Anthropic Agent Skills + `AGENTS.md` para Codex. Sem JavaScript, sem TypeScript, sem hooks programáticos no repositório distribuído.
**Trade-off:** o enforcement programático (hooks de `~/.claude/`, ver ADR-006) fica **fora** do framework distribuído. Assimetria documentada como LACUNA D-004.

### P-2 Artefatos efêmeros vs. permanentes (🟢)
Decisão:
- **Efêmeros:** `_mdcu.md` (deletado pós-SOAP), tabelas STRIDE inline, exit protocols.
- **Permanentes:** `rsop/soap/*.md`, `rsop/lista_problemas.md`, `rsop/passivos.md`, `rsop/seguranca.md`, `ARCHITECTURE.md`, mensagens de commit-soap.
**Justificativa:** o substrato em disco é mais confiável que a memória de chat. O destilado importa, o andaime não.

### P-3 Gates não-negociáveis (🟢)
Decisão: 4 gates absolutos:
1. `ARCHITECTURE.md` antes de F2 (mdcu/SKILL.md:91-113)
2. Disjuntor 2/2 em F6 (mdcu/SKILL.md:304-339)
3. Lock + manifesto no mesmo commit em F6 (mdcu/SKILL.md:218; project-init/SKILL.md:151)
4. Guardrail violado em F5/F6 → `--refresh` ou reenquadrar (project-init/SKILL.md:115)
**Trade-off:** atrito de adoção em troca de robustez de longo prazo.

### P-4 Co-autoria humana (🟢)
Decisão: o agente de IA é **coautor júnior**. Decisões importantes exigem coautoria efetiva (não aprovação passiva). O usuário tem autoridade exclusiva no disjuntor 2/2 e em PRs de upgrade.
**Implicação:** anti-padrão a vigiar — interfaces "OK?" que aceitam aprovação automática.

### P-5 Disciplina telegráfica (🟢)
Decisão: regras estritas de escrita aplicadas a:
- SOAP: A ≤ 5 palavras/item, R = 1 linha
- `_mdcu.md`: bullets em S: e O:
- Checklist de segurança: 5 itens binários
- Lista de problemas: severidade prefixada, sem coluna "Notas"
**Justificativa:** prosa longa é ruído epistemológico, não cosmético.

### P-6 Inspiração clínica explícita (🟢)
Decisão: nomenclatura, estrutura e taxonomia inspiradas em medicina:
- MDCU ← MCCP (Medicina de Família e Comunidade)
- RSOP ← RMOP (Weed, 1968) e RCOP (e-SUS PEC)
- Rastreio de segurança ← Wilson-Jungner
- F0 ← protocolo de admissão / IRP
- Postmortem blameless ← cultura de segurança hospitalar
**Implicação:** público-alvo primário inclui (mas não se limita a) profissionais com background ou interesse em medicina/saúde digital — Iago Leal é médico (inferido do estilo e das inspirações).

### P-7 Composição funcional (🟢)
Decisão: 5 skills coordenam-se por **invocação explícita** (ex: `mdcu` invoca `/project-init`, `/rsop soap`, `/commit-soap`, `/mdcu-seg incidente`), não por hierarquia ou herança. Cada skill tem responsabilidade única.

> **Nota — princípios canônicos do framework além de P-1 a P-7:** ver `framework/principles.md` (F-1 a F-5 fundacionais + P-8, P-9 arquiteturais canônicos). Este documento é saída do **Reversa** (gitignored em `.gitignore`); o canônico distribuído vive em `framework/`. Quando o Reversa for re-rodado, este documento é regenerado; `framework/` permanece.

## 4. Riscos e dívidas técnicas (consolidação — atualizada após rodada 1 de respostas)

| ID | Risco / Dívida | Severidade | Origem | Status |
|---|---|---|---|---|
| **D-001** | Skills sem `version` no frontmatter | `[M]` | `decisions.md`, ADR-008 | ✅ resolvido (P10): **semver puro** por skill |
| **D-002** | Reversa instalou-se no próprio repo | `[B]` | `decisions.md` | ✅ resolvido: `.gitignore` |
| **D-004** | Hooks programáticos vivem fora do repo distribuído | `[A]` | ADR-006, P8 | ✅ resolvido (P8): nova skill **`mdcu-hooks`** com JSON de spec versionado; ver também `framework/principles.md` P-8 (desacoplabilidade dos engines) |
| **D-LAC-001** | Naming convention `<contexto>` em SOAP | `[B]` | domain.md | ✅ resolvido (P5): livre |
| **D-LAC-002** | Idioma canônico não declarado | `[B]` | domain.md | ✅ resolvido (P6): pt-BR canônico + robusto EN |
| **D-PERM** | Colaboração multi-humano | `[M]` | permissions.md | ✅ resolvido (P7): `_mdcu.md` compartilhado |
| **D-ADR-005** | Gate de integração removido sem substituto | `[M]` | ADR-005 | ✅ resolvido (P9): **regra nova ao MDCU F6** vincula `test`/`build` |
| **D-CHANGELOG** | Sem changelog automatizado entre release-trains | `[B]` | ADR-008 | aberta — sugestão: extrair de `git log --grep="A:"` |

## 5. Limites de escopo

**O que mdcu-framework FAZ:**
- Interface humana (extração de requisitos via MCCP + tradução de complexidade técnica)
- Padroniza registro longitudinal de software (RSOP + commit-soap)
- Padroniza contrato técnico de projeto (project-init extrai → project-setup materializa)
- Padroniza segurança (preventiva, corretiva, contínua)

**O que mdcu-framework NÃO FAZ (delegado a engines downstream desacopláveis — ver `framework/principles.md` P-8):**
- Não executa código de produção — engines como spec-kit, superpowers, bmad
- Não produz especificação detalhada (OpenAPI, schema completo, ADRs detalhados)
- Não faz análise arquitetural profunda de sistemas legados — Reversa cobre esse caso
- Não roda testes
- Não faz manutenção (debugging técnico profundo, refactor)
- Não armazena dados em DB — usa filesystem
- Não tem CLI próprio — comandos são `/` interpretados pelo agente
- Não substitui code review humano em PRs
- Não é certificação de processo — é guia interno

## 6. Idioma 🟢

**Idioma canônico:** **pt-BR.** As 5 SKILL.md, templates de artefatos (`_mdcu.md`, SOAP, `ARCHITECTURE.md`) e documentação primária são escritos em pt-BR. (Iago, 2026-04-27 — questions.md P6)

**Robustez em inglês:** o framework deve **funcionar em inglês operacionalmente** — ou seja:
- Frontmatter `description` deve ter triggers em pt-BR e EN (ex: gatilhos como `start methodology`, `frame the problem` em paralelo a "iniciar metodologia", "delimitar problema").
- O agente deve aceitar usuário escrevendo em EN e responder coerentemente, mesmo mantendo a estrutura prescrita em pt-BR.
- Conteúdo dos artefatos pode ser misto pt-BR/EN sem quebrar a interpretação (ex: SOAP onde S: tem citações em EN do usuário e A: em pt-BR do agente).
- Termos técnicos canônicos do framework (SOAP, Demanda, Queixa, F0, MDCU, etc.) **mantêm grafia pt-BR mesmo em contexto EN** — são jargão terminológico, não tradução.

**Não-objetivo:** **i18n completa** (tradução das skills para outros idiomas) NÃO está no escopo desta release-train. Pode ser considerada em release futura.

## 7. Versionamento (Iago, 2026-04-27 — questions.md P10) 🟢

**Convenção:** **semver puro por skill**, declarado no frontmatter YAML.

```yaml
---
name: mdcu
version: "X.Y.Z"
description: ...
---
```

**Regras semver clássicas:**
- **MAJOR (X):** mudança incompatível na interface (comandos `/`, schemas de artefato).
- **MINOR (Y):** funcionalidade nova compatível (nova regra, nova fase, nova opção).
- **PATCH (Z):** correção compatível (clarificação de prosa, ajuste de exemplo).

**Versões iniciais sugeridas para o próximo release-train (`v2026.05`)** — incorporando todas as decisões da Reversa rodada 1:

| Skill | Versão sugerida | Motivo |
|---|---|---|
| `mdcu` | **3.0.0** | MAJOR — adiciona regra do Gate de Integração (F6 pré-fechamento), promove multi-humano de Won't para Should — quebra contratos anteriores |
| `rsop` | **1.2.0** | MINOR — `/rsop soap` sem `_mdcu.md` agora pergunta cenário; `/rsop init` aborta em diretório existente |
| `commit-soap` | **1.1.0** | MINOR — comportamento explícito para SOAP A vazio e `--amend` em commit não-soap |
| `project-init` | **1.0.0** | sem mudanças funcionais nesta rodada — primeira versão semver |
| `mdcu-seg` | **1.0.0** | sem mudanças funcionais nesta rodada — primeira versão semver |
| `mdcu-hooks` | **0.1.0** | NOVA skill — pré-1.0 enquanto JSON-spec e comandos `install`/`check` amadurecem |

**Compatibilidade com release-train:** o `MANIFEST.md` permanece como **bundle marker** — lista qual versão de cada skill compõe a release `vAAAA.MM`. Frontmatter `version` é a fonte de verdade da skill individual; `MANIFEST.md` é a fonte de verdade do conjunto.

**Próximo release:** `v2026.05` — incorpora as decisões da Reversa rodada 0 + rodada 1 (P3 a P10), nova skill `mdcu-hooks`, e novo Gate de Integração no MDCU.
