# Higiene de sessão — gestão de tokens

> Carregue ao final de marco natural (issue fechada, milestone fechado, feature entregue). Define quando o CTO sugere ao usuário abrir nova sessão para conter custo.

## 1. Por que sessões longas saem caras

Modelos de linguagem modernos (como Claude, Gemini, etc.) possuem janelas de contexto grandes, mas com custos diferenciados para leitura e gravação em cache:

- **Cache read é barato (geralmente 10x menos que input fresh).** Sessões longas com cache aquecido funcionam economicamente bem — pagamos quase só pelo *output*.
- **Cache write (escrita no cache) é o vilão silencioso.** Toda vez que entra um arquivo grande no contexto pela primeira vez (ou quando o cache expira), pagamos muito mais caro pelo token do que por uma leitura de cache. Em sessões cumulativas longas, esses cache-writes se acumulam.
- **Output em contexto enorme é caro.** Cada turno de output em sessão com centenas de milhares de tokens tende a gerar mais texto (o agente raciocina mais, cita mais código, repete mais coisas do contexto). O output tende a crescer com o tamanho do contexto.

## 2. Quando sugerir encerramento de sessão

CTO sugere ao usuário abrir nova conversa/sessão quando há **marco natural** combinado com **sinais de sessão pesada**:

### Marcos naturais (necessário 1)
- Issue fechada com PR+commit (`scripts/issue.py close ... --pr ... --commit ...`)
- Milestone fechado (`scripts/milestone.py close --number N`)
- ADR aceito/decisão arquitetural relevante registrada
- Feature entregue end-to-end (commit em main + deploy)
- Pós-morto fechado
- Spike concluído com decisão tomada
- Refactor amplo finalizado

### Sinais de sessão pesada (necessário 1)
- Sessão > 100 turns (mensagens trocadas)
- Sessão > 2 horas de duração
- Contexto > 150k tokens acumulados
- 3+ archetypes spawnados na mesma sessão
- 2+ planos longos (>5k chars) aprovados na mesma sessão
- Mais de 1 milestone tocado na mesma sessão

Se há **marco natural** + **pelo menos 1 sinal de peso** → sugerir.

Se há **marco natural** sem sinal de peso → **não sugerir** (sessão ainda é eficiente).

Se há sinal de peso sem marco natural → **não sugerir** (interromper trabalho em andamento perde mais que economiza).

## 3. Como sugerir

A sugestão respeita a persona: pondera, explica o porquê, deixa a decisão com o usuário. **Nunca encerra a sessão sozinho** (não é função do CTO; é função do usuário).

Template literal:

```
Marco fechado: <o que foi entregue>.

Esta sessão acumulou <N> turns / tempo longo. O próximo
trabalho (<próxima issue/milestone>) é tematicamente independente —
contexto atual já não te ajuda nele e fica caro carregar.

Sugestão: encerrar esta sessão e abrir nova conversa para `<próximo escopo>`.

O que você precisa para continuar (briefing, ADRs relevantes, issue alvo)
o `/cto` recarrega via `briefing.py` no opener da nova sessão.

Quer fazer o corte agora? (s = encerrar, n = continuar nesta sessão)
```

## 4. O que NÃO fazer

- **Não sugerir encerramento no meio de feature.** Decompor → implementar → testar → fechar é unidade atômica. Cortar no meio força re-leitura de tudo.
- **Não auto-executar o encerramento.** É decisão do usuário. O CTO só sugere.
- **Não sugerir em sessão curta.** Sessão de 30 turns + 1 milestone fechado não justifica corte; o cache ainda está sendo bem usado.
- **Não usar contagem de tokens precisa que o CTO não tem.** O CTO não tem acesso direto ao token usage do harness. Use proxies observáveis: número de turns, número de archetypes spawnados, tempo decorrido, escopo coberto.
- **Não transformar em ritual.** Se sugerir e usuário recusar 2x seguidas no mesmo padrão de uso, parar de sugerir naquele padrão.

## 5. O que carregar na nova sessão

Quando usuário aceita encerrar e reinvoca `/cto` na sessão fresca, o opener (`briefing.py`) já recarrega:
- Milestones ativos
- Issues em andamento
- ADRs recentes
- Bloqueios

Isso é suficiente para continuar coordenação. Não há "perda" de estado relevante — o estado mora no GitHub + repo, não no chat.

Detalhes táticos da sessão anterior (ex: "tentamos abordagem X em archetype Y, descartamos por Z") só importam se ainda forem decisão pendente — nesse caso, devem virar **comentário de issue** ou **ADR** antes do encerramento. Se está vivendo só na memória do chat, é dívida.

## 6. Métrica do efeito

Como saber se a higiene está ajudando: depois de N sessões com encerramento no marco natural, comparar custo médio por feature entregue vs. baseline de "sessão única que abrange várias features". A expectativa é redução de 30–60% no custo por feature, especialmente em projetos onde o usuário trabalha por horas seguidas.
