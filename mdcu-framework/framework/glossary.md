# Glossário canônico — mdcu-framework

> Artefato canônico, fonte de verdade do vocabulário do framework.
> Termos centrais do MCCP (Demanda, Queixa, Demanda oculta, SIFE, Padrão de demanda aparente, Reenquadramento, Disjuntor, etc.) e regras de negócio numeradas RN-D-001 a RN-D-013 vivem em `_reversa_sdd/domain.md` (saída do Reversa, gitignored, regenerável).
> Este documento contém **termos canônicos do framework** introduzidos a partir da articulação das teses fundacionais (`principles.md`), e **regras de negócio canônicas** que estendem o conjunto extraído pelo Reversa.

---

## Termos canônicos do framework

### Satisfação do usuário (sentido clínico)

**Definição:** Bem-estar de longo prazo do projeto e do stakeholder, alcançado por **decisão informada**. NÃO é atendimento de desejo imediato.

**Inclui:** o **dever de alerta** do orquestrador contra escolhas que comprometem o bem-estar declarado.

**Análogo MCCP:** equivale ao desfecho clínico do paciente — bem-estar, não cura no sentido estrito.

**Onde codificado:** F-3 em `principles.md`, RN-D-014 abaixo.

### Decisão informada

**Definição:** Decisão tomada pelo usuário com:
1. Compreensão das alternativas em vocabulário próprio
2. Riscos e benefícios explícitos
3. Alerta do orquestrador sobre consequências prejudiciais conhecidas
4. Liberdade de escolher contra a recomendação técnica desde que validado

**Análogo MCCP:** **consentimento informado** clínico — instância da decisão compartilhada do MCCP.

**Onde codificado:** F-3 em `principles.md`, RN-D-014.

### Composição do orquestrador (3 camadas)

**Definição:** Configuração obrigatória do agente que executa MDCU em sessão:
1. **Arquiteto SE sênior** — competência técnica
2. **Comunicador MCCP** — diferencial primário
3. **Tradutor-artista** — a "parte da arte" da tradução problema↔requisito

Todas necessárias, nenhuma suficiente isolada.

**Distinção fundamental:** autor-do-framework × orquestrador-instância (ver F-2 em `principles.md`).

### Anamnese do projeto/stakeholder

**Definição:** Bloco canônico em `rsop/dados_base.md` que persiste a **dimensão humana** do projeto: queixa principal histórica, padrão de demanda recorrente, valores declarados, contexto biográfico, vieses conhecidos do stakeholder, gatilhos típicos de reenquadramento.

**Atualização:** incremental em sessões MDCU significativas; cada entrada datada e citando o SOAP que a motivou. Não se reescreve histórico — anamnese é cumulativa.

**Implicação:** em F1 (Preparação), além de ler `lista_problemas.md` e último SOAP, o orquestrador **lê o bloco anamnese**. Sem isso, F1 é cega à dimensão humana.

**Onde codificado:** F-5 em `principles.md`, schema em `rsop/dados_base.md`.

### Engine downstream desacoplável

**Definição:** Framework técnico maduro (spec-kit, superpowers, bmad, libs, Reversa) que executa Análise/Especificação/Código/Teste/Manutenção. **Trocável sem quebrar o MDCU.** Comunica-se com MDCU via vocabulário MCCP.

**Implicação:** o framework é agnóstico ao engine de execução. Adopter escolhe engine compatível com a realidade técnica do projeto.

**Onde codificado:** P-8 em `principles.md`, ver também `architecture-diagram.md`.

### Precisa-resolver × não-precisa-resolver

**Definição:** Eixo de **triagem clínica** entre F2 e F4 do MDCU. **Nem toda queixa vira `#` de problema** — algumas são ouvidas, validadas e arquivadas como aceitas-pelo-stakeholder, sem gerar problema ativo.

**Análogo MCCP:** "achado clínico irrelevante para o caso" do prontuário médico.

**Codificação operacional:**
- Status mínimo na `rsop/lista_problemas.md`: `[aceito-arquivado]` como prefixo na coluna `#`
- Codificação completa (coluna `Status` no schema) deferida a `rsop/lista_problemas.md` `#10`

**Onde codificado:** RN-D-015 abaixo.

---

## Regras de negócio canônicas

> Regras RN-D-001 a RN-D-013 vivem em `_reversa_sdd/domain.md` (saída do Reversa). RN-D-014 e RN-D-015 são canônicas do framework, introduzidas após formalização das teses fundacionais.

### RN-D-014 — Dever de alerta do orquestrador 🟢

> "Orquestrador alerta contra desejo imediato prejudicial — não compactua com decisão que viola bem-estar de longo prazo declarado pelo stakeholder."

**Implicação:** o orquestrador NÃO é executor passivo de pedidos. Ao identificar (via competência técnica — F-2 camada 1) que uma escolha do usuário tende a prejudicar o bem-estar de longo prazo (técnico ou do projeto), tem **dever** de alertar com argumentação técnica, citando consequência conhecida. O usuário, alertado e ainda assim escolhendo seguir, exerce decisão informada (RN-D-001 + F-3) — orquestrador então executa. **Sem o alerta, executar é violação de RN-D-014.**

**Anti-padrão a vigiar:** orquestrador "concierge" que executa pedidos sem trazer trade-offs à tona. Sintoma: F5 sem alternativas com riscos comparados; F4 sem evidências contra a hipótese declarada pelo usuário.

**Análogo clínico:** consentimento informado é mandatório; o paciente decide, mas só após o médico cumprir o dever de informar.

**Origem:** F-3 (`principles.md`) — citação literal do stakeholder em sessão de 2026-04-27.

### RN-D-015 — Triagem precisa-resolver × não-precisa-resolver 🟢

> "Nem toda queixa vira `#` — triagem precisa-resolver opera entre F2 e F4. Queixas aceitas-arquivadas registram-se com motivo, sem gerar problema ativo."

**Implicação:** durante F2 (Escuta) o orquestrador captura **todas** as queixas. Entre F2 e F4, o stakeholder em decisão compartilhada com o orquestrador classifica cada queixa em:
- **`precisa-resolver`** → vira `#` na `rsop/lista_problemas.md`
- **`não-precisa-resolver — aceita pelo stakeholder`** → registra-se na `rsop/lista_problemas.md` com status `[aceito-arquivado]` e motivo, OU em nota da anamnese
- **`talvez — em observação`** → entra como `#` com severidade `[B]`

**Por que registrar o aceito-arquivado:** sem registro, queixa "esquecida" reaparece em sessão futura como nova; com registro, orquestrador futuro vê que foi triada e respeita a decisão pretérita do stakeholder.

**Anti-padrão a vigiar:** transformar **toda** queixa em `#`. Sintoma: lista de problemas inflada, sinal-ruído ruim, perda de foco no que realmente precisa resolver.

**Codificação completa:** schema enriquecido com coluna `Status` em `rsop/lista_problemas.md` é refinamento posterior (`#10` em `rsop/lista_problemas.md` — `precisa-resolver-codificacao`). Por ora, status `[aceito-arquivado]` mora na coluna `#` como prefixo (mínima mudança de schema).

**Origem:** sessão 2026-04-27 — articulação do eixo durante F3 turno 3.
