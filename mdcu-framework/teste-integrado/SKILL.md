---
name: teste-integrado
author: Iago Leal <github.com/iago-leal>
description: Protocolo operacional do Gate de Integração do MDCU. Garante que toda nova funcionalidade ou correção de código produza teste isolado E passe na suíte integrada completa antes de liberar deploy. ATIVE SEMPRE que o usuário digitar /teste-integrado, quando o MDCU referenciar o Gate de Integração na Fase 6, antes de qualquer deploy de mudança de código, ou quando o usuário pedir para validar que uma mudança não quebrou a integração do sistema. NÃO ative para validação manual ad-hoc quando o projeto não adotou MDCU/RSOP — neste caso, oriente o usuário a rodar a suíte diretamente.
---

# teste-integrado — Gate de Integração

## Fundamento

Código que passa em teste isolado pode quebrar em integração. Essa é uma classe de bug específica: a função isolada faz o que promete, mas quando componentes se conectam, estados, ordens de operação e efeitos colaterais emergem. Teste unitário não pega. Só teste integrado pega.

Esta skill existe porque "liberei para deploy porque o teste unitário passou" é uma das causas mais comuns de regressão em produção. O Gate de Integração fecha essa porta.

### Posição no workflow

A skill é acionada **dentro da Fase 6 do MDCU**, antes de qualquer deploy. O MDCU v2 estabelece como regra dura:

> *Executado ≠ código escrito. Executado = teste isolado criado + suíte integrada verde + critério do plano atingido.*

A skill materializa essa regra.

---

## Quando ativar

**Ativação obrigatória:**
- Usuário digitou `/teste-integrado` ou `/teste-integrado status`.
- MDCU em Fase 6 está prestes a declarar execução concluída.
- Há uma mudança de código (feature nova, correção, refatoração) prestes a ir para deploy.

**Não ativar:**
- Para rodar testes durante o desenvolvimento (o usuário pode rodar `pytest`/`jest`/etc. diretamente — a skill é o *gate*, não o runner cotidiano).
- Para projetos sem suíte de testes integrada configurada — nesse caso, orientar o usuário a configurar CI primeiro.

---

## Contrato com o MDCU

A skill lê três inputs obrigatórios do artefato `04_plano.md` (Fase 5):

1. **Teste isolado previsto** — que caso de teste a mudança deve produzir.
2. **Integração na suíte global** — como o teste entra no CI e que partes da suíte podem ser afetadas.
3. **Critério objetivo de "passou"** — o que conta como verde (ex: `pytest -x` passa + cobertura do código novo ≥ 80%).

Se algum desses campos estiver vazio no plano, a skill **recusa executar** e devolve o usuário para a Fase 5 para completar o plano. Sem critério objetivo, não há como declarar "passou" — só "eu achei que passou".

---

## Protocolo do Gate

A skill executa 5 passos em ordem. Cada passo pode bloquear a passagem.

### Passo 1 — Ler o plano
- Abrir `04_plano.md` do projeto corrente.
- Extrair os três campos obrigatórios acima.
- Se faltar campo: **BLOQUEAR** com mensagem "plano incompleto, voltar para Fase 5".

### Passo 2 — Verificar existência do teste isolado
- Localizar o arquivo/caso de teste referenciado no plano.
- Confirmar que o teste foi efetivamente escrito (não é só TODO no código).
- Se o teste não existe ou é stub vazio: **BLOQUEAR** com mensagem "teste isolado ausente" e sugerir invocar a skill nativa `engineering:testing-strategy` para desenhar o teste apropriado antes de re-executar o gate.

### Passo 3 — Executar suíte integrada completa
- Executar o comando de suíte completa do projeto (descoberto via `dados_base.md` do RSOP ou `package.json`/`pyproject.toml`/`Makefile`).
- Capturar saída completa.
- Se a suíte falhar (qualquer teste vermelho, qualquer erro de setup): **BLOQUEAR** com mensagem incluindo os testes que falharam.

### Passo 4 — Verificar critério objetivo do plano
- Aplicar o critério definido em `04_plano.md` (cobertura, performance, assertion específica).
- Se o critério exige ferramenta extra (coverage, benchmark), executar.
- Se o critério não é atingido: **BLOQUEAR** com o valor atingido vs valor esperado.

### Passo 5 — Registrar resultado
- Gerar artefato `gate_integracao.md` no diretório do projeto (veja seção "Artefato de saída").
- Se todos os passos anteriores passaram: marcar **PASS** e liberar a Fase 6 para declarar execução concluída.
- Se algum passo bloqueou: marcar **FAIL**, deixar a Fase 6 aberta, aguardar correção.

---

## Artefato de saída: `gate_integracao.md`

Gerado no diretório do projeto. Um novo registro a cada execução do gate (append, não overwrite — preserva histórico).

```markdown
# Gate de Integração — [data-hora]

- **Projeto:** [nome]
- **Mudança validada:** [referência à Fase 5/plano: feature X, correção Y, etc.]
- **Resultado:** [PASS | FAIL]

## Passo 1 — Plano
- Teste isolado previsto: [descrição]
- Integração na suíte: [descrição]
- Critério objetivo: [descrição]

## Passo 2 — Teste isolado
- Arquivo: [caminho]
- Status: [existe e é substantivo | ausente | stub vazio]

## Passo 3 — Suíte integrada
- Comando executado: [comando]
- Total de testes: [N]
- Falhas: [lista dos testes que falharam ou "nenhuma"]
- Tempo total: [duração]

## Passo 4 — Critério objetivo
- Valor esperado: [do plano]
- Valor atingido: [medido]
- Atingido? [sim/não]

## Passo 5 — Decisão
- [PASS — Fase 6 liberada para encerramento]
- [FAIL — Fase 6 permanece aberta; motivo: ...]

## Próxima ação
- [se PASS: prosseguir para SOAP via `/rsop soap`]
- [se FAIL: corrigir motivo reportado; re-executar o gate]
```

---

## Composição com skills nativas

Esta skill **protocola** o gate, mas não substitui ferramentas especializadas. Pontos de delegação explícitos:

| Situação no gate | Delegue para | Por quê |
|---|---|---|
| Passo 2 bloqueou por teste isolado ausente | `engineering:testing-strategy` | Desenhar o teste que falta (escolha de escopo, mocks, fixtures) antes de re-executar o gate. |
| Passo 3 bloqueou por falha em teste não relacionado à mudança | `engineering:debug` | Reproduzir, isolar e diagnosticar a regressão que o gate expôs. |
| Passo 4 bloqueou por cobertura insuficiente | `engineering:testing-strategy` | Identificar que caminhos do código não estão cobertos e como testá-los. |
| Depois de PASS, antes de deploy real | `engineering:deploy-checklist` | Checklist complementar (migrations, feature flags, rollback) que é ortogonal ao gate de integração. |

A delegação é **opcional e sugerida** — o gate não chama automaticamente, apenas indica a skill útil quando bloqueia. Isso preserva o papel do gate (bloqueador) sem transformá-lo em tutor.

---

## Integração com CI existente

A skill **não substitui** o CI. Assume que o projeto já tem:
- Suíte de testes automatizados executável por um comando único.
- Ambiente de teste reprodutível (fixtures, mocks, BD de teste).

O papel da skill é **orquestrar** a verificação no momento certo (antes de deploy) e **registrar** a decisão em artefato versionado. Se o CI já tem required status checks configurados, a skill complementa registrando o gate no RSOP do projeto — de forma que a decisão de liberar deploy fica rastreável longitudinalmente.

Se o projeto **não** tem CI:
- A skill executa a suíte localmente via comando descoberto.
- Recomenda, no artefato de saída, configurar CI como follow-up.

---

## Aviso sobre falsa sensação de passagem

**Suíte verde ≠ código correto.** Testes validam o que foi escrito, não o que deveria ter sido escrito. Um teste com assertion fraca passa em código errado. Este gate protege contra regressões de integração — não contra bugs de especificação.

Duas consequências práticas:
1. O campo *Critério objetivo do plano* deve ser forte (ex: "cobertura do diff ≥ 80% + assertion específica no comportamento novo"), não vago (ex: "os testes passam").
2. Suspeitar de suítes que passam "fáceis demais" — se o gate nunca bloqueia, ou os testes são triviais, ou a suíte tem cobertura insuficiente.

A skill não detecta fraqueza de assertion. Isso é decisão humana, documentada no plano.

---

## Regras operacionais

1. **O gate não pode ser pulado.** Se o usuário pedir para liberar deploy sem o gate passar, recusar e referenciar a regra 11 do MDCU.
2. **Plano ausente ou incompleto bloqueia o gate.** Sem os três campos obrigatórios do plano, não há critério objetivo — e sem critério, não há "passou".
3. **Suíte vermelha bloqueia o gate.** Mesmo que o teste que falhou pareça "não relacionado" à mudança: relacionamento não é obvio, e regressões de integração são exatamente bugs que aparecem em lugares inesperados.
4. **Artefato sempre gerado.** PASS ou FAIL, sempre registra. O histórico é parte da longitudinalidade.
5. **Skill é protocolo, não runner.** Para rodar testes durante o desenvolvimento, o usuário usa o runner do projeto. A skill é acionada apenas no momento do gate.

---

## Uso com `/teste-integrado`

- `/teste-integrado` — Executa o gate para a mudança corrente da Fase 6.
- `/teste-integrado status` — Mostra o resultado do último gate executado para o projeto corrente.
- `/teste-integrado historico` — Lista os últimos N gates (PASS e FAIL) do projeto.
