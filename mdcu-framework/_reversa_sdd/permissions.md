# Matriz de permissões — mdcu-framework

> Gerado pelo **Reversa Detective** em 2026-04-27
> Não há RBAC programático. Esta matriz extrai **autoridades prescritas** (quem pode fazer o quê) do conteúdo das skills. Granularidade: ator × ação.

---

## Atores (recapitulação do glossário)

| Ator | Papel |
|---|---|
| **Usuário** | Engenheiro/dev. Coautor das decisões. Autoridade humana única. |
| **Agente** | IA hospedeira. Executa skills. Sujeita a gates. |
| **Stakeholder** | Mapeado em `dados_base.md` / `ARCHITECTURE.md`. Não interage diretamente. |
| **DPO/responsável** | Owner de tratamento de dados (LGPD). Citado em `seguranca.md`. |
| **Time** | Coletivo de engenharia. Acesso a dados "Internos". |

---

## Matriz: ator × ação

Legenda:
- ✅ pode (e tem autoridade exclusiva quando indicado)
- ⚙️ pode com gate (precisa cumprir condição)
- 🚫 não pode
- ➖ não aplicável

| Ação | Usuário | Agente | Outros |
|---|---|---|---|
| **Iniciar sessão MDCU** (`/mdcu`) | ✅ | ✅ (a pedido) | 🚫 |
| **Executar fases F1–F5** | ➖ | ✅ | 🚫 |
| **Decidir o plano em F5** | ✅ **coautor** | ⚙️ propõe alternativas; não decide sozinho | 🚫 |
| **Reenquadrar em F6** | ✅ | ⚙️ até 2/2; depois **proibido** | 🚫 |
| **Decidir após disjuntor 2/2** | ✅ **autoridade exclusiva** | 🚫 | 🚫 |
| **Aprovar merge de PR de upgrade** | ✅ **decisão humana obrigatória** | 🚫 | 🚫 |
| **Modificar dependência sem regenerar lock** | 🚫 | 🚫 (proibido para ambos) | 🚫 |
| **Inicializar `ARCHITECTURE.md`** | ✅ (com `/project-init`) | ✅ executa as 7 fases | 🚫 |
| **Modificar `ARCHITECTURE.md`** | ⚙️ apenas via `/project-init --refresh` | ⚙️ idem | 🚫 |
| **Violar guardrail de `ARCHITECTURE.md`** | 🚫 | 🚫 — exige `--refresh` ou reenquadramento | 🚫 |
| **Acessar `passivos.md`** | ✅ a qualquer tempo | ⚙️ apenas com suspeita de regressão OU pedido explícito | 🚫 |
| **Reabrir um problema (`/rsop regressao`)** | ✅ | ✅ se sintoma compatível | 🚫 |
| **Apagar `_mdcu.md`** | ✅ a qualquer tempo | ⚙️ **apenas** após SOAP + commit-soap; não antes | 🚫 |
| **Disparar F0 (incidente)** | ✅ explicitamente | ⚙️ ao detectar sinal — **imediato**, sem confirmação | ✅ alarme externo (CloudTrail, secret scanner) também dispara |
| **Suspender ciclo MDCU** | ➖ | ⚙️ apenas via F0 | 🚫 |
| **Escrever postmortem** | ✅ | ✅ **blameless obrigatório** | ➖ |
| **Atribuir culpa a pessoa em postmortem** | 🚫 | 🚫 | 🚫 |
| **Adicionar `Co-Authored-By: Claude` (ou qualquer LLM) ao commit** | 🚫 (regra global do usuário) | 🚫 (filtrado por commit-msg hook) | 🚫 |
| **Adicionar `Co-authored-by:` (humano coautor) ao commit** | ✅ permitido em ciclo MDCU multi-humano | ⚙️ a pedido do(s) humano(s) | ➖ |
| **Inventar mensagem de commit-soap sem SOAP** | ➖ | 🚫 — aborta com mensagem fixa | ➖ |
| **Tratar PII sem base legal documentada** | 🚫 — vira `#[A]` automático | 🚫 — idem | 🚫 |
| **Comitar segredo** | 🚫 — gatilho de F0 | 🚫 — idem | 🚫 |
| **Revisar `seguranca.md`** | ✅ | ✅ trimestral obrigatório (90d) | 🚫 |
| **Acessar dados `Restritos` (PHI/PII)** | ⚙️ apenas DPO + app autorizado | 🚫 | ✅ DPO |
| **Acessar dados `Confidenciais` (segredos)** | 🚫 | 🚫 | ✅ serviços autorizados via secret manager |
| **Acessar dados `Internos` (logs/métricas)** | ✅ time | ⚙️ se autorizado | ✅ time |
| **Acessar dados `Públicos`** | ✅ | ✅ | ✅ todos |

---

## Permissões "negativas" — proibições absolutas

Ações que **ninguém** pode fazer no framework, em nenhuma circunstância:

| # | Proibição | Origem |
|---|---|---|
| P-1 | Modificar dependência sem regenerar lock no mesmo commit | project-init/SKILL.md:151, mdcu/SKILL.md:218 |
| P-2 | Lock file em `.gitignore` | project-init/SKILL.md:147-149 |
| P-3 | Pular F2 (escuta) | mdcu/SKILL.md:274 |
| P-4 | Propor solução antes de F4 | mdcu/SKILL.md:275 |
| P-5 | Apresentar < 2 alternativas em F5 | mdcu/SKILL.md:277 |
| P-6 | Postmortem com nome próprio | mdcu-seg/SKILL.md:225 |
| P-7 | Inventar mensagem de commit-soap | commit-soap/SKILL.md:113 |
| P-8 | Trailer `Co-Authored-By` | CLAUDE.md global |
| P-9 | Segredo em código/log/repo/issue | mdcu-seg/SKILL.md:227 |
| P-10 | Skip de hooks (`--no-verify`, `--no-gpg-sign`) | CLAUDE.md global (orientação para o agente) |
| P-11 | Force push em main/master (sem autorização explícita) | CLAUDE.md global |
| P-12 | Tratar PII sem base legal documentada | mdcu-seg/SKILL.md:228 |
| P-13 | Reaproveitar `#` de problema entre ativos e passivos | rsop/SKILL.md (princípio) |
| P-14 | Apagar `_mdcu.md` antes do SOAP+commit-soap | mdcu/SKILL.md:222 |
| P-15 | Prosseguir após disjuntor 2/2 sem decisão humana | mdcu/SKILL.md:312-318 |
| P-16 | Categoria STRIDE silenciosa em threat-model (silêncio = não resposta) | mdcu-seg/SKILL.md:65 |

---

## Autoridades exclusivas do humano

Pontos onde o framework **exige** decisão humana, sem delegação:

1. **Disjuntor 2/2** — única "régua" anti-loop (mdcu/SKILL.md:316-317).
2. **Decisão compartilhada em F5** — agente propõe, humano coautora (mdcu/SKILL.md:281).
3. **Merge de PR de upgrade de dependência** — Dependabot/Renovate só sugere (project-init/SKILL.md:155).
4. **Confirmação de mensagem de commit-soap** — agente exibe, humano aprova (commit-soap/SKILL.md:109).
5. **Definição de stack exótica em F2 do project-init** — exige justificativa em ADR (project-init/SKILL.md:60).
6. **Aprovação de mudança de guardrail** — só via `--refresh` (project-init/SKILL.md:24, 256).

---

## Achados sobre o modelo de autoridade

1. **Inversão clássica:** o framework não trata o agente de IA como "executor com aprovação humana", e sim como **coautor júnior**. Decisões importantes exigem a humana coautoria efetiva (não apenas "OK" passivo).

2. **Não há autoridade hierárquica entre agentes.** O `mdcu-seg` pode suspender o `mdcu` (F0), mas isso é **regra de protocolo** (incident-response), não hierarquia. O `mdcu` pode invocar `/project-init`, `/rsop`, `/commit-soap`, `/mdcu-seg` — relação de **orquestração funcional**.

3. **Stakeholders são endpoints, não atores.** São mapeados nos artefatos estruturais (`dados_base.md`, `ARCHITECTURE.md`) para que o agente saiba quem é afetado, mas **não consomem o framework** diretamente. Útil para o Architect mapear "personas de C4 Context".

4. **DPO e Time são roles informacionais.** Aparecem em `seguranca.md` como labels de acesso a categorias de dado, não como atores que executam comandos.

5. **Atacante** existe apenas em modelo (STRIDE). O framework não tem "honeypot" ou "deception" — é puramente defensivo.

---

## Multi-humano 🟢 (Iago, 2026-04-27 — questions.md P7)

**`_mdcu.md` é compartilhado** entre engenheiros humanos trabalhando no mesmo ciclo. Não há "um `_mdcu.md` por engenheiro" — o ciclo MDCU é coletivo quando há mais de um humano envolvido.

**Coautoria humana:**
- O SOAP pode atribuir notas a múltiplos humanos (ex: `S: Demandas: [Iago] X, [Maria] Y`).
- O commit-SOAP pode incluir múltiplos autores humanos via `Co-authored-by:` PADRÃO Git (com vírgula minúscula, NÃO o trailer Anthropic), ou simplesmente registrar nomes na linha A/P.
- Decisões em F5 com mais de um humano contam todos como coautores.

**Coautoria de LLM:**
- **PROIBIDA.** LLMs nunca entram como coautores em commit ou SOAP. Regra global do usuário (CLAUDE.md global) — consistente com a proibição de `Co-Authored-By: Claude ...` filtrada por hook (ADR-006).

**Sequência prática:**
- Engenheiros que vão colaborar acordam quem inicia `/mdcu`. O `_mdcu.md` criado fica no projeto (ou branch) compartilhado.
- F2 (escuta) pode ser conduzida por um deles registrando D/Q de todos no `S:`.
- F5 (plano) é decisão compartilhada por todos os humanos envolvidos — ≥2 alternativas + trade-offs aplicam normalmente.
- F6 (execução) e fechamento podem ser feitos por qualquer um do grupo.

**Conflito de edição concorrente sobre `_mdcu.md`:** não tratado por mecanismo do framework — fica para o git resolver via merge (esperado: edições sequenciais, não simultâneas). 🟡
