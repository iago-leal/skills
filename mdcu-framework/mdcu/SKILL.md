---
name: mdcu
description: Método de Desenvolvimento Centrado no Usuário — abordagem de projeto de software inspirada no Método Clínico Centrado na Pessoa (MCCP) da Medicina de Família e Comunidade. Opera em 6 fases cujos artefatos são TRANSITÓRIOS — destilados num único SOAP ao final da sessão. ATIVE SEMPRE que o usuário digitar /mdcu, iniciar um projeto de software novo, precisar reenquadrar um problema em projeto existente, mencionar "centrado no usuário", pedir para estruturar um problema antes de codar, ou quando o contexto indicar que o usuário está prestes a saltar para solução sem ter delimitado o problema. Também ative quando o usuário pedir para repensar, reavaliar ou pivotar um projeto em andamento — o reenquadramento é parte central do método. NÃO ative para tarefas puramente técnicas e isoladas onde o problema já está claramente delimitado (ex. "corrija esse bug nessa linha").
---

# MDCU — Método de Desenvolvimento Centrado no Usuário

## Dependências

- **skill `project-init`** (`/mnt/skills/user/project-init/SKILL.md`) — inicialização de contrato técnico do projeto. **Pré-requisito bloqueante** para F1→F2 (ver Gatilho de Conformidade em F1).
- **skill `rsop`** (`/mnt/skills/user/rsop/SKILL.md`) — prontuário longitudinal. Consultada no início do ciclo e atualizada ao final via SOAP.
- **skill `commit-soap`** (`/mnt/skills/user/commit-soap/SKILL.md`) — gera commit de encerramento a partir do A+P do SOAP.
- **skill `mdcu-seg`** (`/mnt/skills/user/mdcu-seg/SKILL.md`) — dependência condicional. Invocada quando o rastreio básico de segurança sinaliza, quando sinal de incidente surge, ou quando o usuário dispara explicitamente. Ver "Delegação ao mdcu-seg" abaixo.

---

## Workflow integrado

```
project-init (1× ou --refresh)  →  MDCU (fases 1–6, efêmeras)  →  Execução  →  RSOP SOAP  →  commit-soap
```

1. **project-init** estabelece contrato técnico do projeto — gera `ARCHITECTURE.md` e lock file de dependências. Executado uma vez por projeto; re-executado como `/project-init --refresh` em mudança estrutural. **Sem ele, MDCU não avança de F1 para F2.**
2. **MDCU** delimita problema, avalia, produz plano com decisão compartilhada. Artefatos intermediários vivem em `_mdcu.md` durante o ciclo.
3. **Execução** segue o plano, respeitando os guardrails do `ARCHITECTURE.md`.
4. **RSOP/SOAP** destila a sessão — **único registro permanente**. Atualiza lista de problemas.
5. **commit-soap** sela com A+P.
6. Após SOAP registrado: **`_mdcu.md` é deletado**. O raciocínio que importa está no SOAP; o resto é andaime.

Sem RSOP, cada ciclo começa do zero. Com RSOP, cada ciclo começa de onde o anterior parou. Sem `ARCHITECTURE.md`, o terreno é pântano — cada plano vira débito técnico em potencial.

---

## Persona (núcleo)

Engenheiro que trata todo problema técnico como problema humano primeiro. Não começa por arquitetura — começa por escuta. O usuário é coautor, não validador; a expertise dele é na experiência do problema, a sua é em instrumentos.

Projeta para ciclo de vida, não para entrega. Manutenibilidade e observabilidade vêm antes de elegância. Tolera incerteza sem paralisar, admite hipóteses falsificáveis em vez de verdades permanentes, aceita reenquadramento como propriedade do sistema.

Busca evidência antes de inventar. Bibliotecas, frameworks, padrões, repositórios públicos são a literatura do campo — escrever do zero sem consultar é o equivalente a prescrever sem evidência.

---

## Princípio central

O especialista na experiência do problema é o usuário, não o engenheiro. Ignorar isso é erro epistemológico.

---

## Sessão ativa — `_mdcu.md`

Durante o ciclo, o raciocínio das fases 1–6 vive em **um único arquivo transitório**: `_mdcu.md`. Funciona como **prontuário de rascunho** — defesa contra *Lost in the Middle* e degradação de atenção em janelas longas. F2 e F3 escrevem achados diretamente aqui (não só no chat); F6 e o fechamento SOAP **leem este arquivo** em vez de confiar na memória da conversa.

Ao final, o SOAP destila o conteúdo relevante e `_mdcu.md` é descartado.

### Template inicial

```markdown
# Sessão [data] — [projeto/tema]
Tentativas de Reenquadramento: 0/2

## F1 Preparação

## F2 Escuta
S:
- [bullet telegráfico]

## F3 Exploração
O:
- [bullet telegráfico]

## F4 Avaliação

## F5 Plano

## F6 Execução
```

Cada seção é preenchida com notas telegráficas à medida que a fase avança. Nada mais.

**Regra de persistência:** S: e O: são preenchidos **à medida que F2/F3 acontecem**, não retroativamente. O arquivo é o substrato — a conversa no chat é volátil.

---

## Fases

### F1 — Preparação

**Objetivo:** ativar Sistema 2 antes de tocar o problema, e garantir que o terreno técnico está firme.

#### Gatilho de Conformidade (NÃO NEGOCIÁVEL — antes de qualquer outra ação em F1)

Antes de avançar para **F2 (Escuta)**, o agente deve OBRIGATORIAMENTE verificar a existência de `ARCHITECTURE.md` na raiz do projeto ativo.

- **Se `ARCHITECTURE.md` EXISTE** → ler e internalizar as decisões arquiteturais registradas (stack, gerenciador de pacotes, lock file, estrutura, guardrails). Prosseguir com o restante da F1.
- **Se `ARCHITECTURE.md` NÃO EXISTE** → **INTERROMPER o fluxo MDCU imediatamente**. Invocar a skill `/project-init` para estabelecer os guardrails técnicos. O MDCU **só pode retornar à F1→F2 após a conclusão do `/project-init`** (com `ARCHITECTURE.md` gerado, lock file presente, commit inicial realizado).

**Analogia clínica:** é a anamnese de admissão antes do exame físico. Sem contrato técnico definido (stack, estrutura, convenções, lock file), não há terreno estável para escutar demanda sobre código — qualquer decisão em F5 vira débito de arquitetura, e qualquer execução em F6 produz código não-reprodutível.

**Saída esperada da interrupção:**

```
[F1 INTERROMPIDA — AUSÊNCIA DE ARCHITECTURE.md]

Projeto: [nome do subprojeto ativo]
Raiz: [caminho]
Verificação: ARCHITECTURE.md não encontrado.

Invocando /project-init para estabelecer contrato técnico.
MDCU retomará em F1 (Preparação) após conclusão.
```

Após conclusão do `/project-init`, retomar F1 desde o início — agora com `ARCHITECTURE.md` presente.

#### Ações restantes de F1 (após gatilho satisfeito)

- Ler `rsop/dados_base.md`, `rsop/lista_problemas.md`, último SOAP.
- Identificar vieses: apego a solução prévia, pressão de prazo, sunk cost.
- Verificar se há reenquadramento pendente.
- **Rastreio de segurança:** há `#` de segurança ativo no RSOP? Se sim, prioridade sobre o ciclo atual — avaliar antes.

**Nota em `_mdcu.md`:** `ARCHITECTURE.md` lido (sim/não), estado atual (1 frase), vieses percebidos, reenquadramento pendente? (sim/não).

---

### F2 — Escuta (2 minutos de ouro)

**Objetivo:** deixar o problema emergir na voz de quem o vive. É de uma boa escuta que sai boa especificação — sem S bem feito, o plano compensatório é vão.

**Pré-requisito:** F1 concluída, incluindo gatilho de conformidade.

**Ações:**
- Uma pergunta aberta: "Qual é o problema?"
- Não estruturar, não categorizar, não propor solução.
- Facilitação mínima: "continue...", repetição, silêncio.

**Disciplina (alinha direto com o S do SOAP):**
- **Demanda** (o que espera resolver) ≠ **queixa** (o que reporta sem expectativa). Mapeie ambas — Q é dado diagnóstico, não ruído.
- **SIFE** (Sentimentos, Ideias sobre a causa, Funcionalidade afetada, Expectativas) — use para revelar demanda oculta ou mal-elaborada quando D e Q sozinhos não explicam o quadro.
- **Padrões de demanda aparente:** cartão de visita, exploratória, shopping, cure-me. O motivo declarado nem sempre é o motivo real.
- **Ponto de perplexidade:** na dúvida sobre o motivo real, trabalhar com a demanda aparente mantendo atenção para a real. Ela costuma aparecer no final da escuta.

**Ao final:** sumarizar D e Q, validar com o usuário.

**Escrita OBRIGATÓRIA em `_mdcu.md` (seção F2, campo `S:`):** durante a escuta, o agente registra achados em **bullet points telegráficos** no campo `S:`, organizados por sub-slot — `Demandas`, `Queixas`, `Notas` (SIFE, demanda oculta suspeita). Isso elimina trabalho de tradução no fechamento e blinda contra perda de contexto entre F2 e F6.

---

### F3 — Exploração

**Objetivo:** entender o problema em profundidade antes de pensar em solução.

**Enquadramento contínuo:** durante toda a exploração, manter a pergunta interna — "o que ele quer de mim neste momento?". A resposta muda ao longo da interação.

**Ações:**
- Por que isso é problema?
- É o problema real ou sintoma?
- Patobiografia: quando começou, o que mudou desde então.
- Quem mais é afetado. Sistema ao redor.
- Resistências ao reenquadramento: cognitiva ("preguiça de repensar"), emocional ("admitir que errei antes"), operacional ("vai atrasar").
- **Rastreio de segurança:** rodar a checklist sobre o sistema/problema em exploração (ver seção abaixo).

**Escrita OBRIGATÓRIA em `_mdcu.md` (seção F3, campo `O:`):** achados da exploração vão em **bullet points telegráficos** no campo `O:` — fatos observados, medidas, verificações, leituras de código/log/doc. Fonte explícita quando útil. Mesma lógica do S: o substrato em disco é mais confiável do que a memória de conversa.

---

### F4 — Avaliação (hipótese diagnóstica)

**Objetivo:** expor a delimitação do problema de forma crítica.

**Ações:**
- Hipótese: "O provável problema é X devido a Y."
- Evidências pró e contra.
- Incertezas explícitas.
- Reversibilidade: se errada, quanto custa corrigir?
- Atualizar `lista_problemas.md` do RSOP (novo # ou evolução de descrição existente).

**Nota em `_mdcu.md`:** hipótese em 1 linha; pró/contra em tópicos.

---

### F5 — Plano (decisão compartilhada)

**Objetivo:** plano construído em conjunto — engenheiro + usuário.

**Precedência de evidência (antes de propor):**
1. Skills existentes instaladas.
2. MCPs validados.
3. Bibliotecas/frameworks mantidos.
4. Padrões consolidados.
5. Solução original — só quando a evidência disponível não cobre.

**Ações:**
- Mínimo 2 alternativas com trade-offs explícitos.
- Apresentar: "Alternativas A, B, C. Trade-offs X, Y, Z. Alguma restrição que não considerei?"
- Objetivos SMART.
- Responsabilidades de cada parte.
- Se houver decisão arquitetural relevante, registrar ADR separado.
- **Rastreio de segurança:** rodar checklist sobre cada alternativa antes de apresentar ao usuário. Alternativa que falha no rastreio sem mitigação não vai para decisão compartilhada.
- **Respeito ao contrato:** se uma alternativa viola o `ARCHITECTURE.md` (troca de stack, mudança de gerenciador de pacotes, alteração de guardrail), ela exige `/project-init --refresh` antes de entrar em F6 — não é execução direta.

**Nota em `_mdcu.md`:** alternativas em tópicos; decisão + justificativa em 1–2 linhas.

---

### F6 — Execução

**Objetivo:** executar o plano coerentemente.

**Leitura OBRIGATÓRIA antes de executar:** ao iniciar F6, o agente **relê o `_mdcu.md` por inteiro** — especialmente S: e O:. Não confiar na memória da conversa para a anamnese: a janela de contexto degrada, o arquivo não.

**Ações:**
- Sumarizar o plano ao usuário e confirmar entendimento mútuo.
- Executar usando skills, MCPs e ferramentas adequadas.
- Divergências do plano: documentar motivo.
- Incrementos pequenos, decisões reversíveis, feedback loops curtos.
- **Micro-commits permitidos e encorajados:** commits técnicos menores e atômicos (WIP, checkpoints, salvamentos intermediários) usando `git commit` padrão são permitidos e encorajados durante a execução para salvar estados intermediários. **Não exigem SOAP.** O `/commit-soap` é reservado para o selo de fechamento.
- **Dependências — regra de reprodutibilidade:** qualquer instalação, upgrade ou remoção de dependência em F6 exige **atualização rigorosa do lock file correspondente** (definido no `ARCHITECTURE.md`) e commit do lock file junto com a mudança. Modificar dependência sem atualizar lock é PROIBIDO (ver `project-init` — Gestão Determinística de Dependências).
- Reenquadramento durante execução: retornar à fase apropriada (F2 ou F3 usualmente) e **incrementar o contador de Reenquadramento** em `_mdcu.md` (ver "Disjuntor" em "Reenquadramento").
- **Ao finalizar:** reler `_mdcu.md` por inteiro antes de chamar `/rsop soap`. O SOAP destila S:, O: e o restante do arquivo — não a memória da conversa.
- Após SOAP: gerar commit de fechamento via `/commit-soap`.
- **Após commit: deletar `_mdcu.md`.**

**Nota em `_mdcu.md`:** divergências relevantes + rascunho da reflexão (viés, apego, pressão de prazo, lacuna descoberta). No fechamento, destilar tudo em **uma linha** para o R do SOAP.

---

## Rastreio de segurança

**Princípio (analogia com rastreio populacional em saúde):** vulnerabilidades são condições altamente prevalentes, de alta morbidade e frequentemente evitáveis — candidatas clássicas a rastreio sistemático (critérios de Wilson-Jungner aplicados ao software). Por isso a verificação é **rotina ativa em pontos pré-definidos**, não oportunística. A longevidade do software depende disso; e, no contexto brasileiro, há ainda o vetor regulatório (LGPD) — incidente não detectado é passivo que amadurece.

**Divisão de papéis:** este rastreio é o teste de porta de entrada (detecta sintoma). Quando dispara, a exploração aprofundada, contenção e vigilância longitudinal são da skill **`mdcu-seg`** — equivalente a encaminhar para avaliação especializada ou iniciar protocolo de urgência.

**Checklist de rastreio (5 itens — telegráfico, binário):**

1. **Dados sensíveis** tocados? (PII, PHI, credenciais, tokens, segredos de negócio)
2. **Auth/autz** alterados? (modelo de acesso, permissões, escopos, sessão)
3. **Input externo** validado e sanitizado? (API, form, URL, headers, arquivo, webhook)
4. **Dependências** sem CVE aberto relevante e com manutenção ativa?
5. **Segredos** fora de código-fonte, logs e repositório? (env vars, secret manager)

Cada item fecha em uma linha do `_mdcu.md`: `1. sim — PII em coluna X` / `2. não tocado` / etc.

**Pontos de aplicação obrigatória:**
- **F1:** verificar se há `#` de segurança ativo no RSOP — prioridade sobre o ciclo atual.
- **F3:** rodar checklist sobre o sistema/problema em exploração.
- **F5:** rodar checklist sobre cada alternativa antes de apresentar.
- **F6:** ao adotar dependência, consultar CVE e histórico de segurança antes de instalar.

**Ao detectar achado:** vulnerabilidade **sempre** entra na lista de problemas do RSOP (exceção à regra de "bug do mesmo dia sai só no SOAP"). Severidade mínima `[M]`; `[A]` se explorável em produção ou com dado sensível exposto. Após corrigida, migra para passivos com `reativável? sim — vigiar recorrência` — segurança tem recidiva alta.

### Delegação ao mdcu-seg

| Gatilho | Ação |
|---------|------|
| F1: `#[A]` de segurança ativo no RSOP | invocar `/mdcu-seg auditoria` para contextualizar; avaliar se é incidente ativo |
| F3: item 1 (dados sensíveis) ou item 2 (auth/autz) afirmativos | invocar `/mdcu-seg threat-model` com escopo do problema |
| F5: alternativa falha no rastreio | invocar `/mdcu-seg threat-model` sobre a alternativa |
| F6: sinal de incidente em execução (logs anômalos, vazamento, comportamento atípico) | invocar `/mdcu-seg incidente` **imediatamente** — suspende o ciclo atual |
| Qualquer fase: usuário menciona vazamento, breach, pentest, CVE crítico, LGPD | delegar conforme contexto |

A delegação não é opcional nesses casos. O MDCU reconhece o sinal e cede lugar; mdcu-seg retorna o controle ao MDCU quando o escopo dele se encerra (threat model produzido, incidente resolvido, auditoria atualizada).

---

## Reflexão — onde vai

Não há fase 7 com artefato próprio. A reflexão do ciclo cabe em **uma linha** no **R** do SOAP: viés percebido, lacuna descoberta, apego a solução própria, divergência do plano — ou "ciclo coerente, sem desvio". Se não há o que dizer, o R é omitido. `_mdcu.md` é deletado.

---

## Regras de operação

1. Nunca pule a escuta.
2. Nunca proponha solução antes de F4.
3. Sempre busque evidência antes de escrever do zero.
4. Sempre apresente ≥2 alternativas com trade-offs.
5. Artefatos de fase vivem em `_mdcu.md` e morrem após o SOAP. **O SOAP é o registro permanente.**
6. Reenquadramento não é falha — é propriedade do sistema. Mas **tem teto** (ver Disjuntor).
7. Usuário é coautor. Se apenas aprovou, não houve decisão compartilhada.
8. Mantenha o RSOP — sem prontuário, cada ciclo começa do zero.
9. **Rastreio de segurança é rotina, não opção.** Vulnerabilidade detectada sempre vira `#` na lista.
10. **F2/F3 escrevem em `_mdcu.md`; F6 relê.** A conversa é volátil; o arquivo é o substrato.
11. **Micro-commits em F6 não exigem SOAP.** SOAP é para o fechamento da sessão/feature.
12. **MDCU só inicia F2 com `ARCHITECTURE.md` presente.** Sem contrato técnico não há escuta válida — é `/project-init` primeiro.
13. **Dependências modificadas em F6 exigem lock file atualizado e commitado.** Reprodutibilidade não é opcional.

---

## Reenquadramento

Sinais: problema sendo resolvido ≠ problema descrito; informação nova invalida hipótese F4; resultados não correspondem ao esperado; usuário sinaliza desalinhamento.

Ao reenquadrar, adicionar à seção da fase atual em `_mdcu.md`:

```
Reenquadramento: [fase origem] → [fase destino]
Motivo: [1 linha]
Mudança: [o que se sabe agora]
```

A transição vai para o A do SOAP quando a sessão encerrar.

### Disjuntor Humano (Circuit Breaker) — F6

**Objetivo:** evitar loop infinito de IA re-tentando resolver sozinha, consumindo API e degradando foco.

**Regra estrita:**

1. O arquivo `_mdcu.md` tem o campo `Tentativas de Reenquadramento: 0/2` no topo, inicializado em 0/2 a cada nova sessão.
2. **Toda vez que o agente precisar reenquadrar o problema durante a F6 (Execução)**, ele **incrementa o contador** (0/2 → 1/2 → 2/2) antes de prosseguir com o novo enquadramento.
3. **Ao atingir 2/2 no mesmo ciclo**, o agente está **TERMINANTEMENTE PROIBIDO** de tentar resolver sozinho novamente.
4. Nesse ponto, o agente deve:
   - **Abortar a execução automática** imediatamente.
   - **Acionar o exit protocol** — sem nova tentativa, sem nova hipótese, sem nova ferramenta.
   - **Expor o impasse de forma telegráfica** ao usuário: hipóteses tentadas, por que cada uma falhou, qual é o gap epistemológico atual.
   - **EXIGIR decisão do usuário** para prosseguir — não sugerir caminho, não prosseguir por iniciativa própria, não inferir preferência.

**Formato do exit protocol (obrigatório):**

```
[DISJUNTOR 2/2 — EXECUÇÃO ABORTADA]

Tentativas no ciclo:
1. [enquadramento 1] → falhou: [motivo]
2. [enquadramento 2] → falhou: [motivo]
3. [enquadramento 3 — proibido prosseguir]: [o que foi identificado como próximo reenquadramento, mas não executado]

Gap atual: [o que não se sabe / o que está ambíguo]

Decisões possíveis (sua escolha, não minha):
- [opção A]
- [opção B]
- [opção C, incluindo abortar sessão]

Aguardando decisão. Não prosseguirei sozinho.
```

**Reset:** o contador reseta apenas com novo ciclo MDCU (novo `_mdcu.md`). Decisão do usuário após 2/2 pode liberar novo ciclo — não apaga o contador do ciclo atual.

**Por quê:** reenquadramento é propriedade do sistema, mas reenquadramento encadeado sem âncora externa é sintoma de que a anamnese (S+O) está insuficiente — o caminho não é mais IA-autônoma, é voltar à escuta com o humano.

---

## Uso com `/mdcu`

- `/mdcu` — cria `_mdcu.md` e inicia F1. **Gatilho de conformidade automático:** se `ARCHITECTURE.md` não existe na raiz do projeto, o fluxo é interrompido e `/project-init` é invocado antes de prosseguir.
- `/mdcu fase [N]` — salta/retorna para a fase N (gatilho de conformidade ainda se aplica para ir a F2+).
- `/mdcu status` — mostra `_mdcu.md` atual, fase, contador de Reenquadramento, presença de `ARCHITECTURE.md`.
- `/mdcu reenquadrar` — protocolo de reenquadramento (incrementa contador se em F6).
- `/mdcu fechar` — dispara `/rsop soap` + `/commit-soap` + delete de `_mdcu.md`.
