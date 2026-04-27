# MDCU Framework — v2026.05 (planejada)

Pacote de entrega — **6 skills** + documentação visual + artefatos canônicos.

## Conteúdo

```
skills-v2026.05/
├── mdcu/SKILL.md              (3.0.0 — F6 reformulada em 3 sub-blocos com modo monolítico declarado)
├── rsop/SKILL.md              (1.2.0 — `/rsop soap` sem `_mdcu.md` pergunta cenário; `/rsop init` aborta em diretório existente)
├── commit-soap/SKILL.md       (2.0.0 — desacoplado: aceita SOAP, --from <path> ou --inline; selo de qualquer marco longitudinal)
├── mdcu-seg/SKILL.md          (1.0.0 — sem mudanças funcionais)
├── project-init/SKILL.md      (2.0.0 — só interface: extrai contrato + gera ARCHITECTURE.md; não executa setup)
├── project-setup/SKILL.md     (0.1.0 — NOVA: materializa contrato técnico em disco; modo desacoplado/monolítico declarado)
├── framework/                 (artefatos canônicos do framework — versionados)
│   ├── principles.md          (F-1 a F-5 fundacionais + P-8, P-9 arquiteturais canônicos)
│   ├── architecture-diagram.md
│   ├── glossary.md            (RN-D-014, RN-D-015 + termos canônicos)
│   └── README.md
├── framework-diagrama.html    (documentação visual — editorial)
└── MANIFEST.md                (este arquivo)
```

## Mudanças v2026.04 → v2026.05

| # | Mudança | Skill alvo | Versão |
|---|---|---|---|
| 1 | Tese formalizada (F-1 a F-5 + P-8, P-9) | `framework/principles.md` (NOVO) | n/a (canônico) |
| 2 | Glossário canônico (RN-D-014/015) | `framework/glossary.md` (NOVO) | n/a (canônico) |
| 3 | Diagrama canônico (4 camadas) | `framework/architecture-diagram.md` (NOVO) | n/a (canônico) |
| 4 | F6 reformulada em 3 sub-blocos (delegação + acompanhamento + tradução-fechamento) | `mdcu` | 2.x → **3.0.0** |
| 5 | `project-init` desacoplado de execução técnica — só interface + contrato | `project-init` | 1.0.0 → **2.0.0** |
| 6 | `project-setup` materialização técnica do contrato (modo desacoplado/monolítico) | `project-setup` (NOVA) | n/a → **0.1.0** |
| 7 | `commit-soap` desacoplado de sessão MDCU — selo de qualquer marco longitudinal | `commit-soap` | 1.x → **2.0.0** |

**Patches herdados de v2026.04 (já aplicados):**
- Prontuário de rascunho (`_mdcu.md`)
- Micro-commits permitidos em modo monolítico (preservado em F6.a)
- Disjuntor 2/2 + exit protocol (preservado em F6.b)
- `passivos.md` como arquivo morto
- Gatilho de conformidade `ARCHITECTURE.md` em F1
- Gestão Determinística de Dependências (regras canônicas — agora em `project-init/SKILL.md`, enforced por `project-setup`)

## Anatomia das 4 camadas (ver `framework/architecture-diagram.md`)

| Camada | Skills | Papel |
|---|---|---|
| **Interface humana** | `mdcu` | Canal bidirecional Usuário ↔ pipeline |
| **Delegação técnica** | (engines externos: spec-kit, superpowers, bmad, libs maduras, Reversa) | Análise, Especificação, Código, Teste — desacopláveis |
| **Acompanhamento longitudinal** | `rsop` + `commit-soap` (desacoplado) | Transversal a todas as fases |
| **Fundação** | `project-init` (contrato) + `project-setup` (materialização) + `mdcu-seg` (segurança) | Estabelece terreno + vigia continuamente |

## Destino no repositório

Todos os arquivos vão para `mdcu-framework/` do repo
[`iago-leal/skills`](https://github.com/iago-leal/skills):

```
mdcu-framework/
├── mdcu/SKILL.md
├── rsop/SKILL.md
├── commit-soap/SKILL.md
├── mdcu-seg/SKILL.md
├── project-init/SKILL.md
├── project-setup/SKILL.md     ← NOVO
├── framework/
│   ├── principles.md
│   ├── architecture-diagram.md
│   ├── glossary.md
│   └── README.md
└── docs/
    └── framework-diagrama.html
```

## Validações

- Todas as 6 skills com campo `description` ≤ 1024 caracteres (limite do Claude).
- Nome do arquivo de sessão ativa do MDCU padronizado como `_mdcu.md`.
- `framework/` é versionado (canônico distribuído); `_reversa_sdd/` é gitignored (output do Reversa, regenerável).
- README.md do repo precisa ser atualizado separadamente para refletir nova anatomia.

## Instalação local (Claude Code)

```bash
cp -R mdcu          ~/.claude/skills/
cp -R rsop          ~/.claude/skills/
cp -R commit-soap   ~/.claude/skills/
cp -R mdcu-seg      ~/.claude/skills/
cp -R project-init  ~/.claude/skills/
cp -R project-setup ~/.claude/skills/
```

---

**Autor:** Iago Leal — [github.com/iago-leal](https://github.com/iago-leal)
**Licença:** MIT
