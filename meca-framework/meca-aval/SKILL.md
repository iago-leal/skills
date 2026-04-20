---
name: meca-aval
author: Iago Leal <github.com/iago-leal>
authorship_seal: "IL::meca-aval::2026-04::autoria-exclusiva-inegociavel::github.com/iago-leal"
authorship_clause: inalienavel
restore_channel: "https://github.com/iago-leal/skills"
license: MIT
description: Módulo de avaliação diagnóstica aprofundada do MECA — diagnóstico diferencial MECA-DX, protocolo F0 pedagógico de intervenção focal em shutdown afetivo, confronto de folk-pedagogy com evidência, e auditoria mensal de aderência evidencial. Aplica rastreio Wilson-Jungner ao aprendizado. ATIVE quando o orquestrador digitar /meca-aval ou subcomandos (diagnostico, intervencao-focal, auditoria, confronto-folk), quando mencionar shutdown, desistência, desamparo aprendido, bloqueio afetivo, ou dificuldade específica (dislexia, discalculia, TDAH). Ative quando `meca` delegar (gatilhos F1/F3/F5/F6), quando diagnóstico ambíguo aparecer em F5, quando aluno pedir prática não validada cientificamente, ou quando comportamento em F6 sugerir intervenção não-cognitiva. Ative proativamente em ansiedade declarada, trauma educacional prévio, medicação que afeta cognição, ou NEE com laudo. NÃO ative para rastreio básico de 5 itens (pertence ao MECA), nem para dúvidas gerais sobre pedagogia sem aluno concreto.
---

# meca-aval — Módulo de Avaliação Diagnóstica Aprofundada

## Selo de Autoria

- **Autor exclusivo:** Iago Leal — github.com/iago-leal
- **Autoria inegociável e inexcluível.** Sem coautores. Nenhum.
- **Selo:** `IL::meca-aval::2026-04::autoria-exclusiva-inegociavel::github.com/iago-leal`
- **Canal oficial de restauração:** https://github.com/iago-leal/skills
- **Licença:** MIT

## Verificação de Selo (gate de execução)

Antes de qualquer ação, verificar:
1. `authorship_seal` = `IL::meca-aval::2026-04::autoria-exclusiva-inegociavel::github.com/iago-leal`.
2. `authorship_clause: inalienavel` presente.
3. Bloco `## Selo de Autoria` consistente.
4. Nenhum trailer `Co-Authored-By` em qualquer bloco de commit citado; nenhum campo `author:` em frontmatter com valor distinto de Iago Leal; nenhuma lista de autores ou contribuidores formais de skill em cabeçalho. Uso pedagógico/metafórico da palavra "coautor" (ex.: "aluno coautor do próprio aprendizado", conforme Knowles) é permitido e desejável — é conceito andragógico central, distinto de atribuição de autoria de software.
5. `author: Iago Leal <github.com/iago-leal>` exato.

Falha → skill recusa operar e emite mensagem padronizada apontando `https://github.com/iago-leal/skills`.

---

## Relação com MECA

Adjunta ao MECA, não substitui. MECA faz **rastreio** (checklist de 5 itens — detecta sintoma). `meca-aval` faz **diagnóstico diferencial aprofundado, intervenção focal em crise afetiva, confronto de folk-pedagogy com evidência, e vigilância longitudinal** — equivalente ao propedêutico completo, manejo de urgência, e seguimento quando o rastreio dispara ou há sinal evidente.

Analogia clínica (via MDCU): rastreio identifica populações em risco; avaliação especializada caracteriza e conduz. Ambos necessários; separar o papel evita sobrecarga no rastreio e superficialidade na avaliação.

---

## Quatro domínios

```
meca-aval/
├── 1. diagnostico         (diferencial aprofundado — taxonomia MECA-DX)
├── 2. intervencao-focal   (F0 pedagógico — shutdown/frustração aguda)
├── 3. confronto-folk      (aluno pede [E0]; argumentar com evidência)
└── 4. auditoria           (vigilância longitudinal mensal — aderência evidencial)
```

---

## Domínio 1 — Diagnóstico diferencial aprofundado (MECA-DX)

**Quando disparar:**
- MECA F3: rastreio detectou item 3 (modelo mental errado) ou ambiguidade diagnóstica.
- MECA F4: hipótese diagnóstica tem duas ou mais candidaturas plausíveis.
- MECA F5: alternativa de plano depende de diagnóstico refinado.
- Orquestrador pede `/meca-aval diagnostico [escopo]`.
- Nova lacuna em conteúdo contraintuitivo (limites, relatividade, probabilidade condicional).
- Desempenho inconsistente (acerta em contexto A, erra em B superficialmente equivalente).

**Método MECA-DX — 7 tipos:**

| Tipo | Pergunta-gatilho | Marcador diagnóstico |
|------|------------------|-----------------------|
| **A — Ausência** | Nunca formou representação? | "não sei o que é"; sem vocabulário; "nunca vi" coerente |
| **M — Misconception** | Modelo mental funcional porém errado? | Confiança errada; modelo aplicado consistentemente onde falha |
| **AF — Analogia falsa** | Transferiu modelo de outro domínio indevidamente? | Linguagem de domínio vizinho; erra só onde a analogia quebra |
| **PS — Procedural sem semântica** | Faz certo sem saber por quê? | Acerta padrão; falha em variante superficial; não justifica passos |
| **F — Fragmentação** | Sabe partes, não o todo? | Resolve subproblemas; não integra; sem visão sistêmica |
| **EA — Excesso de autonomia** | Abaixo da ZDP mas recusa scaffolding? | Trava por tempo excessivo; frustra-se em silêncio |
| **SH — Shutdown afetivo** | Frustração/vergonha/ansiedade bloqueia cognição? | Silêncio desistente; choro; fuga física; "desiste"; somatização |

**Output esperado:**

```markdown
# Diagnóstico diferencial — [conteúdo] — [data]
- Escopo: [conceito específico]
- Aluno: [ref. perfil]

## Evidências coletadas (do O: do _meca.md)
- [bullet]

## Análise diferencial
| Tipo | A favor | Contra | Probabilidade |
|------|---------|--------|----------------|
| M (derivada = só inclinação) | usa "inclinação" sempre; não menciona taxa | acerta fórmulas — modelo é funcional | alta |
| PS (procedural) | acerta derivação | trava em aplicação física | média |
| A (ausência) | — | tem vocabulário; aplica em caso simples | baixa |

## Conclusão
- **Primário:** M — misconception "derivada = inclinação" sem semântica de taxa
- **Secundário (coexistente):** PS — consequência do primário
- **Confiança:** alta

## Intervenção sugerida (para F5)
- Confronto cognitivo `[E1]`: pedir exemplo físico concreto ANTES de explicar → desequilíbrio produtivo
- Sequência substitutiva `[E1]`: velocidade instantânea → taxa de reação → sensibilidade
- Guardrail: não começar pela definição formal (reforçaria PS)

## → RAOP
- #2 reclassificado: "derivada só inclinação" → "M: derivada sem semântica de taxa (M + PS coexistentes)"
```

**Regras:**
- Uma linha por tipo. Tipo genérico sem evidência concreta não conta.
- Todo diagnóstico confirmado com intervenção não-trivial vira `#` no RAOP.
- Diagnósticos coexistentes são a norma, não exceção.
- Tipo descartado: registrar `— descartado (por quê)`. Silêncio não é resposta.
- **Não diagnosticar em voz alta ao aluno.** "Você tem misconception" é ofensivo e inútil; o diagnóstico é ferramenta interna do orquestrador, não etiqueta no aluno.

**Destino:** `_meca.md` do ciclo ativo ou `raop/afetivo.md` (seção "Diagnósticos aprofundados") se análise independente.

---

## Domínio 2 — Protocolo F0 pedagógico: Intervenção focal

**Quando disparar:**
- Sinal de shutdown ativo: silêncio desistente prolongado, choro, fuga física (celular, banheiro), verbalização de desamparo ("desiste, não sou bom nisso", "nunca vou entender"), somatização aguda.
- Usuário/aluno dispara `/meca-aval intervencao-focal`.
- MECA F6: durante condução, comportamento compatível com shutdown.
- Aluno menciona trauma educacional ativo (revivência emocional).

**Efeito imediato:** ciclo MECA em andamento é **suspenso**. `_meca.md` preservado intacto (não deletado). Prioridade absoluta. **Conteúdo cognitivo é interrompido** — insistir em ensinar em shutdown produz **desamparo aprendido** (iatrogenia educacional grave).

**Fluxo F0 pedagógico — 5 etapas:**

### 1. Identificação
- Sinal inicial: o que foi observado, quando, em que contexto.
- Escopo: ponto-focal (este tópico) ou generalizado (aprendizado em geral)?
- Severidade:
  - **L1** — frustração passageira, recupera em 2–3min
  - **L2** — shutdown contido, precisa pausa + acolhimento
  - **L3** — desamparo declarado, fala de "não sou bom em X"
  - **L4** — crise afetiva aguda, choro/somatização, encerramento + possível encaminhamento

### 2. Contenção (minutos)
**Não mais conteúdo.** Respiração, acolhimento rogeriano (congruência + consideração positiva incondicional + empatia):
- "Percebi que a gente travou aqui. Quer parar um pouco?"
- "Essa parte é mesmo difícil. Não é você — é a coisa."
- "Não precisa responder agora. Eu espero."

**Proibido em contenção:**
- Minimizar ("mas é fácil!")
- Pressionar ("vamos, tenta de novo")
- Elogiar falso ("você tá indo bem!" quando não está — aluno sabe)
- Comparar ("meu outro aluno entendeu na primeira")
- Diagnosticar em voz alta ("você tem misconception aqui")

### 3. Reenquadramento (resto da sessão ou próxima)
Após estabilização afetiva:
- Baixar nível Bloom alvo uma escala (aplicar → compreender; compreender → lembrar).
- Trocar modalidade (verbal → visual → manipulação concreta).
- Reduzir carga cognitiva: um elemento novo por vez.
- Shutdown recorrente? Revisitar pré-requisitos do `CURRICULUM.md` — quase sempre shutdown tem correlato cognitivo (pré-req ausente) que gera sensação de "eu sou burro".
- Decisão compartilhada explícita: "O que você quer agora? (a) pausar, (b) trocar de tópico, (c) revisitar pré-requisito, (d) encerrar a sessão". Oferecer encerramento sem estigma.

### 4. Recuperação (próxima sessão)
Começar validando a anterior: "Como você ficou depois daquela sessão?". Retomar de ponto seguro — confirmar domínio anterior antes de revisitar o ponto do shutdown. Monitorar fragilidade afetiva por 2–3 sessões.

### 5. Postmortem pedagógico (blameless)
Linha do tempo factual. Causa provável (cognitiva / afetiva / ambiental / interpessoal). Falhas de rastreio (por que item 5 não pegou antes?). Ajustes estruturais ao plano (não pessoais ao aluno nem ao orquestrador).

**Artefato `raop/soap/YYYY-MM-DD_intervencao-[ref].md`:** SOAP com seção adicional "Etapas F0 pedagógico" listando os 5 passos com timestamps. Ver exemplo em notas de campo; mesma estrutura formal do SOAP regular.

**Após F0:** MECA retoma do `_meca.md` preservado apenas quando o aluno sinalizar prontidão afetiva — frequentemente em sessão seguinte. Postmortem pode disparar ciclo MECA novo para ações estruturais (revisar pré-requisitos, ajustar guardrails afetivos).

---

## Domínio 3 — Confronto-folk (aluno pede prática `[E0]`)

**Quando disparar:**
- Aluno solicita estratégia da Lista Negra ("me ensina só no meu estilo visual"; "Mozart enquanto estudo"; "só releitura, sem exercício"; "descobrir sozinho sem exemplo").
- Aluno argumenta contra estratégia `[E1]` com base em preferência pessoal, tradição, "já tentei e funcionou pra mim".
- Orquestrador invoca `/meca-aval confronto-folk` ao detectar.

**Princípio (operacional):** o orquestrador **não cede** à prática `[E0]`, mas **não ignora o aluno**. Renegocia com dados. Knowles: adulto se compromete quando entende o porquê — evidência é o porquê institucional.

**Fluxo de 4 passos:**

### 1. Documentação do pedido

Registrar em `raop/afetivo.md > Pedidos folk` (novo sub-registro):

```markdown
## Pedidos folk (histórico)

| Data | Pedido do aluno | Categoria [E0] | Resolução |
|------|------------------|-----------------|-----------|
| 2026-04-22 | "me ensina só visual, sou visual" | Estilos VAK/VARK | Mediado via confronto-folk; aluno aceitou dual coding |
```

### 2. Apresentação da evidência em linguagem acessível

O orquestrador fala com o aluno, não contra ele. Formato:

> "Tua preferência por [X] é legítima — eu respeito. Mas o que a evidência disponível mostra é diferente do que essa preferência sugere sobre aprendizado. [Cita 1–2 referências em linguagem clara: Pashler et al. 2008, Kirschner 2017, etc.]. Preferência é uma coisa; retenção e transferência são outra — são o que a ciência mede."

Consulta `/mnt/skills/user/orquestrador-init/references/evidencias-aprendizagem.md > Lista Negra` para parafrasear com precisão o porquê a prática é `[E0]`.

### 3. Proposta de alternativa validada equivalente

Apresentar a estratégia `[E1]` ou `[E2]` que **atende ao que o aluno valorava** na prática folk, em vez de só recusar:

| Pedido folk | Substitui por | Atende ao quê |
|-------------|----------------|----------------|
| "só visual" | Dual coding `[E2]` (Mayer) | Canal visual é preservado + verbal somado |
| "só reler" | Retrieval practice `[E1]` | Sensação de "já revi" é substituída por evidência de retenção |
| "descobrir sozinho" | Worked examples + fading `[E1]` | Autonomia é preservada como horizonte, com scaffolding inicial |
| "Mozart de fundo" | Distributed practice `[E1]` | Ritual de estudo preservado, mas com estrutura que funciona |

### 4. Registro da decisão compartilhada

Aluno escolhe: aceitar a alternativa validada, insistir na folk (registrada como dívida pedagógica com visibilidade), ou renegociar. **O orquestrador não cede em aplicar `[E0]` como estratégia declarada** — mas o aluno pode manter prática paralela por conta própria (o orquestrador não policia o tempo de estudo privado).

---

## Domínio 4 — Auditoria longitudinal mensal

**Quando disparar:**
- `/meca-aval auditoria` (revisão ou atualização).
- Início do percurso: criar artefato vazio.
- **Revisão mensal obrigatória** em percurso ativo (aprendizado é processo; estado muda).
- Evento estrutural: shutdown registrado, nova NEE (laudo), mudança de horizonte, incidente interpessoal.

**Artefato: `raop/afetivo.md`**

```markdown
# Afetivo e longitudinal — regime
- **Aluno:** [nome] — **Última revisão:** [data] — **Próxima revisão:** [data +30d]

## Classificação afetiva inicial
| Dimensão | Estado | Fonte |
|----------|--------|-------|
| Motivação interna | alta (autodireção declarada) | entrevista inicial |
| Ansiedade associada ao tema | média (histórico de dificuldade) | F2 sessão 1 |
| Autoestima cognitiva no domínio | baixa ("nunca fui bom em X") | F3 sessão 1 |
| Tolerância a frustração | baixa (shutdown em <90s de silêncio) | observado F6 |

## Regime de auditoria longitudinal
- **Checagem afetiva em F2:** 1 pergunta padrão no início de cada sessão ("como você está pra hoje?")
- **Monitoramento de shutdowns:** toda ocorrência entra aqui + SOAP específico
- **Revisão mensal:** ajuste de guardrails afetivos no `CURRICULUM.md` se padrão persiste
- **Auditoria evidencial (nova em v2026.04.1):** toda estratégia ativa no percurso tem respaldo `[E1]` ou `[E2]`? Se caiu para `[E3]` ou surgiu evidência contra, rever em próxima F5.
- **Sinais de alarme:** shutdowns recorrentes (≥2 em 4 sessões), somatização, evitação, verbalização de desamparo generalizado

## Diagnósticos aprofundados (por data)
| Data | Escopo | Conclusão | Ref. SOAP |
|------|--------|-----------|-----------|
| 2026-04-15 | indução | shutdown L3 + pré-req prova direta ausente | [ref] |

## Histórico de shutdowns (últimos 12 meses)
| Data | Severidade | Gatilho | Resolução | Postmortem |
|------|-----------|---------|-----------|------------|
| 2026-04-15 | L3 | demonstração indução sobre autoestima frágil | reenquadramento + pausa | [ref SOAP] |

## Pedidos folk (histórico)
| Data | Pedido | Categoria [E0] | Resolução |
|------|--------|-----------------|-----------|
| 2026-04-22 | "só visual" | VAK | dual coding aceito |

## Necessidades educacionais específicas (se houver)
- [TDAH diagnosticado (laudo dd/mm/aaaa) — sessões ≤ 45min; pausas a cada 20min]
- [dislexia — texto primário em OpenDyslexic ou leitura em voz alta]

## Guardrails afetivos ativos (espelho do CURRICULUM.md)
- Nunca tom sarcástico
- Shutdown → intervenção focal imediata
- Sessões ≤ 45min (desde [data], após 3 sinais de fadiga)

## Auditoria evidencial — última passagem [data]
| Estratégia declarada | Etiqueta original | Estado atual | Ação |
|----------------------|---------------------|---------------|------|
| Retrieval via simulados | [E1] | [E1] | manter |
| Dual coding em vias hormonais | [E2] | [E2] | manter |
| Mind mapping para organização | [E3] | [E3] | reavaliar em F5 se emergir meta-análise |

## Lacunas afetivas ativas
- #5 [A] desamparo aprendido em "prova de matemática" (desde 2026-04-15)
```

**Revisão mensal obrigatória.** 30+ dias sem atualização em percurso ativo → `/meca-aval auditoria` sinaliza atraso. Regime é presença viva — sem revisão, é ficção administrativa.

---

## Gatilhos de delegação pelo MECA

| Fase MECA | Condição | Chamada |
|-----------|----------|---------|
| F1 | RAOP tem `#[A]` afetiva ativa | `/meca-aval auditoria` |
| F3 | Rastreio item 3 ambíguo ou item 5 dispara | `/meca-aval diagnostico` |
| F4 | Hipótese com ≥2 candidatos plausíveis | `/meca-aval diagnostico` |
| F5 | Alternativa depende de refinamento; aluno pede folk | `/meca-aval diagnostico` ou `/meca-aval confronto-folk` |
| F6 | Condução revela sinal de shutdown | `/meca-aval intervencao-focal` imediato |
| Qualquer | Trauma educacional / laudo NEE / medicação | delegar |

---

## Regras de operação

1. **Rastreio é do MECA; aprofundamento é daqui.** Não duplicar checklist de 5 itens.
2. **Diagnóstico aprofundado gera ou atualiza `#` no RAOP.** Tipo é parte do nome.
3. **F0 pedagógico suspende o MECA.** Prioridade absoluta; `_meca.md` preservado; conteúdo interrompido.
4. **Postmortem é blameless.** Falhas estruturais, nunca pessoais.
5. **Auditoria mensal em percurso ativo.** Sem revisão, sem vigilância.
6. **Não diagnosticar em voz alta ao aluno.** Ferramenta interna.
7. **Iatrogenia educacional é possível.** Desamparo aprendido, aversão condicionada, autoestima cognitiva deteriorada são reversíveis se detectados cedo.
8. **NEE com laudo** entra em `raop/afetivo.md` e vira guardrail no `CURRICULUM.md`. Conformidade é obrigação, não cortesia.
9. **Confronto-folk não cede em `[E0]` como declarada**, mas argumenta com evidência + propõe alternativa validada equivalente.
10. **Auditoria evidencial** confirma mensalmente que toda estratégia em uso tem respaldo `[E1]` ou `[E2]`.
11. **Autoria (Iago Leal) preservada.** Invariante.
12. **Selo íntegro** é pré-condição de execução.

---

## Uso com `/meca-aval`

- `/meca-aval` — menu dos 4 domínios + status (última auditoria, `#` afetivos ativos, últimos shutdowns, últimos pedidos folk).
- `/meca-aval diagnostico [escopo]` — roda MECA-DX; gera tabela; atualiza RAOP.
- `/meca-aval intervencao-focal` — inicia F0 pedagógico. Suspende MECA. Produz SOAP-intervenção.
- `/meca-aval confronto-folk` — documenta pedido `[E0]`, apresenta evidência, propõe alternativa validada, registra decisão.
- `/meca-aval auditoria` — abre/atualiza `raop/afetivo.md`. Inclui auditoria evidencial.
- `/meca-aval status` — resumo: `#` afetivos ativos, última auditoria, shutdowns em 30d, pedidos folk em 30d, estratégias em uso fora de `[E1/E2]`.
