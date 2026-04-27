# Spec Impact Matrix — mdcu-framework

> Gerado pelo **Reversa Architect** em 2026-04-27
> Adaptação: relaciona **alvos de mudança** (skills, regras de negócio, artefatos, gates) com **componentes impactados**. Útil para o Writer ao gerar specs SDD e para o Reviewer ao avaliar o blast radius de qualquer mudança proposta.

---

## Matriz: alvo de mudança × impacto

Legenda:
- 🟥 impacto direto (mudança quebra)
- 🟨 impacto indireto (mudança exige adaptação)
- 🟩 sem impacto

| Alvo de mudança ↓ / Impactado → | mdcu | rsop | commit-soap | project-init | mdcu-seg | _mdcu.md | rsop/lista | rsop/soap | rsop/passivos | ARCHITECTURE.md | rsop/seguranca | git history |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **Adicionar fase F7 ao MDCU** | 🟥 | 🟨 | 🟨 (Refs:) | 🟩 | 🟨 | 🟥 | 🟩 | 🟥 | 🟩 | 🟩 | 🟩 | 🟩 |
| **Mudar template do `_mdcu.md`** | 🟥 | 🟥 (lê em /rsop soap) | 🟩 | 🟩 | 🟥 (escreve em F0) | 🟥 | 🟩 | 🟨 | 🟩 | 🟩 | 🟩 | 🟩 |
| **Mudar formato do SOAP (S/O/A/P/R)** | 🟥 (escreve via /rsop soap) | 🟥 | 🟥 (lê A+P) | 🟩 | 🟥 (incidente estende) | 🟩 | 🟩 | 🟥 | 🟩 | 🟨 | 🟨 | 🟨 |
| **Mudar disjuntor (de 2/2 para 3/3)** | 🟥 | 🟩 | 🟩 | 🟩 | 🟩 | 🟥 (header) | 🟩 | 🟩 | 🟩 | 🟩 | 🟩 | 🟩 |
| **Adicionar gate em F2 ou F3** | 🟥 | 🟩 | 🟩 | 🟨 | 🟨 (rastreio) | 🟨 | 🟩 | 🟩 | 🟩 | 🟨 (gate pode usar) | 🟩 | 🟩 |
| **Adicionar campo ao `lista_problemas.md`** | 🟥 (F4 escreve) | 🟥 | 🟩 | 🟩 | 🟥 (espelha) | 🟩 | 🟥 | 🟨 | 🟥 (passivo herda) | 🟩 | 🟥 | 🟩 |
| **Adicionar nova severidade (ex: `[C]` crítica)** | 🟥 | 🟥 | 🟩 | 🟩 | 🟥 | 🟩 | 🟥 | 🟨 | 🟥 | 🟩 | 🟥 | 🟩 |
| **Mudar largura máxima da linha A em commit** | 🟩 | 🟩 | 🟥 | 🟩 | 🟩 | 🟩 | 🟩 | 🟩 | 🟩 | 🟩 | 🟩 | 🟨 (`git log --oneline`) |
| **Trocar lock file canônico de stack X** | 🟨 (F6 valida) | 🟩 | 🟩 | 🟥 (tabela) | 🟩 | 🟩 | 🟩 | 🟩 | 🟩 | 🟥 (seção Dependências) | 🟩 | 🟨 |
| **Adicionar nova regulação à `seguranca.md`** | 🟩 | 🟩 | 🟩 | 🟩 | 🟥 | 🟩 | 🟩 | 🟩 | 🟩 | 🟩 | 🟥 | 🟩 |
| **Adicionar 6ª categoria STRIDE (ex: privacy)** | 🟩 | 🟩 | 🟩 | 🟩 | 🟥 | 🟨 | 🟨 (novo #) | 🟨 (refs no SOAP) | 🟨 (passivo) | 🟩 | 🟩 | 🟩 |
| **Mudar período de revisão da auditoria (90→60d)** | 🟩 | 🟩 | 🟩 | 🟩 | 🟥 | 🟩 | 🟩 | 🟩 | 🟩 | 🟩 | 🟥 (campo proxima_revisao) | 🟩 |
| **Adicionar campo `version` ao frontmatter (D-001)** | 🟥 | 🟥 | 🟥 | 🟥 | 🟥 | 🟩 | 🟩 | 🟩 | 🟩 | 🟩 | 🟩 | 🟩 |
| **Internacionalizar (i18n)** | 🟥 | 🟥 | 🟥 | 🟥 | 🟥 | 🟥 (template) | 🟨 (severidade?) | 🟥 (S/O/A/P/R names?) | 🟨 | 🟥 (seções) | 🟥 | 🟩 |
| **Adicionar `rsop/adrs/` formal** | 🟥 (F5 referencia) | 🟥 (artefato novo) | 🟩 | 🟥 (sec ADRs no Architecture) | 🟩 | 🟩 | 🟩 | 🟨 | 🟩 | 🟥 | 🟩 | 🟩 |
| **Mudar trailer de commit (ex: novo `Refs:`)** | 🟩 | 🟩 | 🟥 | 🟨 (commit inicial usa formato A:/P:) | 🟩 | 🟩 | 🟩 | 🟩 | 🟩 | 🟩 | 🟩 | 🟨 |
| **Suspender skill `mdcu-seg`** | 🟥 (gatilhos quebram) | 🟨 (seguranca.md órfã) | 🟩 | 🟩 | — | 🟩 | 🟨 | 🟨 (incidentes não geram SOAP) | 🟩 | 🟩 | 🟥 | 🟩 |
| **Suspender skill `commit-soap`** | 🟥 (fechamento perde selo) | 🟩 | — | 🟩 | 🟩 | 🟩 | 🟩 | 🟩 | 🟩 | 🟩 | 🟩 | 🟥 (perde marcos cognitivos) |
| **Suspender skill `project-init`** | 🟥 (gate F1 sem alvo) | 🟩 | 🟩 | — | 🟩 | 🟩 | 🟩 | 🟩 | 🟩 | 🟥 (sem fonte canônica) | 🟩 | 🟩 |

---

## Lendo a matriz

**Mudanças de alto blast radius (≥5 🟥):**
- Adicionar campo `version` ao frontmatter — toca todas as 5 skills
- Internacionalizar — toca tudo (10+ alvos)
- Adicionar nova severidade — atravessa lista, passivos, SOAP, mdcu, mdcu-seg
- Mudar formato do SOAP — atravessa lista, soap, mdcu, rsop, mdcu-seg, commit-soap
- Adicionar campo ao `lista_problemas.md` — atravessa toda a cadeia de problemas

**Mudanças de baixo blast radius (≤1 🟥):**
- Mudar largura máxima da 1ª linha em commit (apenas commit-soap)
- Mudar período de revisão da auditoria (apenas mdcu-seg + seguranca.md)
- Mudar disjuntor para outro número (apenas mdcu + `_mdcu.md` header)

**Skills críticas para o ciclo (suspensão quebra muito):**
- `project-init` — sem ela, gate F1 do MDCU não tem alvo
- `commit-soap` — sem ela, fechamento perde selo longitudinal
- `mdcu-seg` — sem ela, gatilhos de F1/F3/F5/F6 quebram

**Skill autônoma (suspensão tem mínimo impacto fora dela):**
- `rsop` — autônoma; outras skills dependem dela mas ela não depende de outras. Suspender quebra TUDO (`mdcu`, `commit-soap`, `mdcu-seg`).

---

## Recomendações para o Writer

1. **Sempre que tocar SOAP, tocar todas as skills que leem/escrevem SOAP** (mdcu, rsop, commit-soap, mdcu-seg). Mudança no SOAP é mudança em 4 specs.
2. **Sempre que tocar `lista_problemas.md`, tocar a cadeia ativos→passivos→seguranca→SOAP**. Schema do problema é transversal.
3. **Mudanças no contrato técnico (`ARCHITECTURE.md`)** são geralmente mudanças no `project-init` SKILL.md — mas qualquer skill que mencione campos de `ARCHITECTURE.md` precisa ser revisada.
4. **Adicionar versionamento (D-001)** é a mudança mais transversal sem ser semanticamente disruptiva — bom candidato a primeiro patch da próxima release-train.

## Recomendações para o Reviewer

- Toda spec proposta pelo Writer deve declarar explicitamente quais células 🟥 da matriz acima ela impacta.
- Mudanças com >3 🟥 exigem ADR formal (não apenas commit-soap).
- Mudanças que tocam apenas `_mdcu.md` (artefato transitório) são reversíveis — peso menor.
- Mudanças que tocam `git history` são irreversíveis em projetos com múltiplos colaboradores — peso maior.
