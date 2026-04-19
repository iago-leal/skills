# MDCU Framework — v2026.04

Pacote de entrega com 5 skills + documentação visual.

## Conteúdo

```
skills-v2026.04/
├── mdcu/SKILL.md              (ATUALIZADA — patches 1, 2, 4, 5)
├── rsop/SKILL.md              (ATUALIZADA — patch 3: arquivo morto)
├── commit-soap/SKILL.md       (ATUALIZADA — patch 2: exclusivo fechamento)
├── mdcu-seg/SKILL.md          (ATUALIZADA — propagação nominal _mdcu.md)
├── project-init/SKILL.md      (NOVA — patch 6: Gestão Determinística de Dependências)
├── framework-diagrama.html    (documentação visual — editorial)
└── MANIFEST.md                (este arquivo)
```

## Patches aplicados

| # | Patch | Skill alvo |
|---|-------|------------|
| 1 | Prontuário de rascunho (`_mdcu.md` com S:/O:, leitura em F6) | mdcu |
| 2a | Micro-commits permitidos em F6 | mdcu |
| 2b | `commit-soap` exclusivo para fechamento (não WIP) | commit-soap |
| 3 | `passivos.md` como arquivo morto; `lista_problemas.md` só com ativos | rsop |
| 4 | Disjuntor 2/2 em F6 + exit protocol | mdcu |
| 5 | Gatilho de conformidade `ARCHITECTURE.md` em F1 | mdcu |
| 6 | Gestão Determinística de Dependências | project-init (nova) |

## Destino no repositório

Todos os arquivos vão para `mdcu-framework/` do repo
[`iago-leal/skills`](https://github.com/iago-leal/skills):

```
mdcu-framework/
├── mdcu/SKILL.md              ← skills-v2026.04/mdcu/SKILL.md
├── rsop/SKILL.md              ← skills-v2026.04/rsop/SKILL.md
├── commit-soap/SKILL.md       ← skills-v2026.04/commit-soap/SKILL.md
├── mdcu-seg/SKILL.md          ← skills-v2026.04/mdcu-seg/SKILL.md
├── project-init/SKILL.md      ← skills-v2026.04/project-init/SKILL.md
└── docs/
    └── framework-diagrama.html ← skills-v2026.04/framework-diagrama.html
```

## Validações

- Todas as 5 skills com campo `description` ≤ 1024 caracteres (limite do Claude).
- Nome do arquivo de sessão ativa do MDCU padronizado como `_mdcu.md`
  (propagado em todas as skills que o referenciam).
- README.md do repo precisa ser atualizado separadamente (ver prompt
  de deploy gerado na conversa).

## Instalação local (Claude Code)

```bash
cp -R mdcu          ~/.claude/skills/
cp -R rsop          ~/.claude/skills/
cp -R commit-soap   ~/.claude/skills/
cp -R mdcu-seg      ~/.claude/skills/
cp -R project-init  ~/.claude/skills/
```

---

**Autor:** Iago Leal — [github.com/iago-leal](https://github.com/iago-leal)
**Licença:** MIT
