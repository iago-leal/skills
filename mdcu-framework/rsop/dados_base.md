# Dados base
- **Projeto:** mdcu-framework
- **Atualizado:** 2026-04-27

## Identificação técnica do projeto

- **Propósito:** framework de extração de requisitos + tradução de complexidade técnica para o usuário, operacionalização do MCCP em SE. Distribuído como bundle de Agent Skills (Claude Code / Codex / Cursor / Gemini CLI).
- **Responsáveis:** Iago Leal (autor exclusivo — RN-D-013).
- **Stakeholders:** adopters do framework (engenheiros que querem disciplina centrada no usuário), e o próprio Iago como dogfooder primário.
- **Linguagens/frameworks:** Markdown puro + frontmatter YAML (P-1). Sem JavaScript/TypeScript/Python no repositório distribuído.
- **Infra:** distribuído via repositório git público (`github.com/iago-leal/skills`), pasta `mdcu-framework/`. Instalação local copia para `~/.claude/skills/`.
- **Repositório:** https://github.com/iago-leal/skills — pasta `mdcu-framework/`.

## Contrato técnico-equivalente

> O framework não tem `ARCHITECTURE.md` próprio (`#2` em `lista_problemas.md` — exceção justificada). Contrato técnico vive em:

**Versionado (canônico distribuído):**
- `framework/principles.md` — princípios fundacionais (F-1 a F-5) + arquiteturais canônicos (P-8, P-9). Fonte de verdade epistemológica e arquitetural.
- `framework/architecture-diagram.md` — diagrama canônico das 4 camadas
- `framework/glossary.md` — termos canônicos do framework + RN-D-014, RN-D-015
- `framework/README.md` — explica relação entre `framework/` e `_reversa_sdd/`
- `MANIFEST.md` (raiz) — bundle marker da release-train atual (vAAAA.MM)

**Reversa output (gitignored, regenerável, local-only):**
- `_reversa_sdd/architecture.md` — princípios técnicos extraídos por análise (P-1 a P-7) + limites de escopo + idioma + versionamento
- `_reversa_sdd/domain.md` — glossário extraído (Demanda, Queixa, etc.) + RN-D-001 a RN-D-013

**Em caso de tensão:** `framework/` prevalece sobre `_reversa_sdd/`. Dentro de `framework/`: `principles.md` > demais.

## Bundle atual

- **vAAAA.MM:** v2026.04 (5 skills entregues)
- **Próximo release:** v2026.05 (planejado em §8 do PLANEJAMENTO.md — adiciona `mdcu-hooks` 0.1.0, promove `mdcu` 3.0.0)
- **Versionamento:** semver puro por skill no frontmatter YAML; bundle marker no `MANIFEST.md` (P-7 + §7 architecture.md)

## Idioma

- **Canônico:** pt-BR. Robustez operacional EN. Sem i18n completa nesta release-train. (Ver §6 de architecture.md.)

---

## Anamnese do projeto/stakeholder

> Implementa F-5 (`principles.md` — anatomia humana persistente). Atualizada incrementalmente em sessões MDCU significativas; cada entrada datada, cita SOAP que a motivou. Não se reescreve histórico — anamnese é cumulativa.

### Queixa principal histórica

| Data | Queixa | SOAP origem |
|---|---|---|
| 2026-04-27 | "Frameworks de SE são escritos POR engenheiros PARA engenheiros — quem está fora do código (stakeholder, usuário, cliente) é tratado como input estruturado, não como pessoa em consulta. A lacuna humana só fica visível para quem vem de fora da SE." | `2026-04-27_*-tese-formalizada.md` |
| 2026-04-27 | "spec-kit privileges processed specifications over raw stakeholder voice" — stakeholder é excluído pelos frameworks externos atuais. | mesma sessão |
| 2026-04-27 | "Hooks programáticos viviam em `~/.claude/`, não no repo" — assimetria entre prescrição e enforcement (D-004, parcialmente resolvido em P-8). | mesma sessão |

### Padrão de demanda recorrente

| Data | Padrão observado |
|---|---|
| 2026-04-27 | **Exploratória.** Stakeholder traz estruturação parcial (PLANEJAMENTO.md já com ✅/🟡/❓/🔴) pedindo destilação + decisão sobre prioridades. Não é shopping (não vem com solução pronta para implementar) nem cure-me (não pede segunda opinião sobre código existente). Frequentemente reabre tese central durante a exploração — reenquadramento espontâneo é parte natural do processo. |

### Valores declarados pelo stakeholder

| Data | Valor | Citação literal |
|---|---|---|
| 2026-04-27 | **Centrado no usuário > rigor formal** | *"O objetivo final é a satisfação do usuário"* — F-3 |
| 2026-04-27 | **Analogia clínica > conveniência de engenharia** | *"O MCCP é fantástico na medicina, porque é para qualquer resolução de problemas que envolvam pessoas"* — F-1 |
| 2026-04-27 | **Humildade técnica do autor (não do orquestrador)** | *"Por eu ser médico, eu parto do princípio de que a parte técnica da engenharia de software eu não domino. Para que a parte técnica sobreviva no meu framework, eu preciso pegar estruturas que já são validadas"* — F-2 distinção autor × orquestrador |
| 2026-04-27 | **Decisão informada, não obediência ao desejo imediato** | *"O médico, tendo a capacidade técnica e sabendo das consequências, não pode compactuar com isso"* — F-3 dever de alerta |
| 2026-04-27 | **Telegráfico por princípio, não por economia** | RN-D-002 + P-5 — herança do RMOP de Weed |
| 2026-04-27 | **Autoria exclusiva, sem co-autoria automática** | RN-D-013 — Co-Authored-By globalmente proibido |

### Contexto biográfico relevante

- **Iago Leal — médico (Medicina de Família e Comunidade).** Domínio primário: prática clínica + cultura RMOP/MCCP. Não é engenheiro de SE de formação.
- **Implicação fundamental:** o framework é **transposição direta MCCP→SE**, não inspiração análoga (F-1). Vocabulário, taxonomia, gates, disciplina de registro — tudo herdado da prática clínica, não inventado para SE.
- **Por que isso explica decisões:** quando há tensão entre "convenção de engenharia de software" e "fidelidade à prática clínica", o stakeholder consistentemente escolhe **fidelidade clínica**. Exemplo: telegráfico por princípio (RN-D-002) é regra do RMOP — vai contra "documentação rica" típica de SE, mas o stakeholder sustenta.

### Vieses conhecidos do stakeholder

| Viés | Manifestação | Como o orquestrador deve operar |
|---|---|---|
| **Apego à analogia clínica** | Tende a defender solução clínica mesmo quando engenharia tem solução melhor | Apresentar trade-off explícito; respeitar decisão (RN-D-001) — mas alertar (RN-D-014) se viola bem-estar técnico de longo prazo |
| **Reabertura espontânea de tese central** | Em ~50% das sessões longas, reenquadra a tese principal a meio-caminho (testemunhado em sessão 2026-04-27 turnos F3-1, F3-2, F3-3) | Aceitar como propriedade do método; registrar reenquadramentos no `_mdcu.md`; não tratar como sinal de imaturidade da tese |
| **Recência de leitura técnica** | Frameworks externos recém-lidos podem inflar peso na recomendação | Em F5, citar evidência por idade + maturidade, não só por novidade |
| **Sunk cost na própria arquitetura** | Pode ser difícil descartar artefatos que custaram esforço (ex: `_reversa_sdd/` rodada 2 com 99% confiança) | Em F4, separar "confiança no artefato existente" de "necessidade de revisão"; não usar custo passado como argumento |
| **Confiança alta no `_reversa_sdd/`** | Tendência a aceitar `_reversa_sdd/` como fonte de verdade sem checar se está sincronizado | Em F1, validar que artefatos canônicos refletem estado atual antes de aceitar como base |

### Gatilhos típicos de reenquadramento

| Gatilho | Padrão de fala | Resposta esperada do orquestrador |
|---|---|---|
| Iminência de reestruturação grande | "Isso pode gerar uma reestruturação completa..." / "Vamos lá..." | NÃO acelerar para F5; abrir F3 turno novo, escutar a expansão, atualizar `_mdcu.md` antes de avaliar |
| Calibração específica de aprovação | "Perfeitamente foi para a máxima X..." | Recolher F4/F5 se construído sobre interpretação ampla; voltar a F4 com hipótese narrowed |
| Compartilhamento de diagrama/imagem | "Acho que essa imagem pode ajudar" / "Veja..." | Tratar como **fonte canônica** se referente a arquitetura; reescrever plano à luz dela antes de continuar |
| Apresentação de novo conceito do MCCP | Citação de Stewart, McWhinney, ou termo MCCP não codificado ainda no framework | Verificar se termo já está em `domain.md`; se não, propor adição como termo canônico (não como "anotação") |

---

## Dívidas conhecidas (resumo — detalhe completo em `lista_problemas.md`)

- 11 `#` ativos inaugurados em 2026-04-27. Severidade: 2 [A], 6 [M], 3 [B].
- Nenhum passivo (RSOP recém-inaugurado).
- Nenhum `#` de segurança ativo (framework é markdown estático — sem dados sensíveis, auth, input externo, dependências runtime ou segredos).
