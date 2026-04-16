---
name: seguranca-dados
author: Iago Leal <github.com/iago-leal>
description: Protocolo operacional do Gate de Segurança do MDCU. Executa threat modeling sobre o escopo de mudança proposto, cobrindo prompt injection em LLMs, gestão de chaves de API, LGPD (base legal, minimização, retenção, direitos de titulares), exposição de banco de dados e vazamento em logs. Produz artefato `ameacas.md` com probabilidade × impacto e mitigações recomendadas. ATIVE SEMPRE que o usuário digitar /seguranca-dados, quando o MDCU referenciar o Gate de Segurança na Fase 4→5, quando a hipótese diagnóstica envolver nova superfície de ataque (rota/API, dependência externa, dado sensível, LLM, segredo), ou quando o usuário pedir avaliação de risco de segurança ou LGPD. NÃO ative para revisão ad-hoc de código isolado sem contexto de mudança — use `engineering:code-review` para isso.
---

# seguranca-dados — Gate de Segurança

## Fundamento

Segurança cibernética, LGPD e gestão de dados sensíveis não são concerns opcionais — são **pré-condições** de qualquer plano técnico para projetos que lidam com dados de pessoas. Sem endereçar essas dimensões, o plano mais elegante produz sistema comprometido. Esta skill existe para fechar essa porta de forma estruturada, não anedótica.

### Posição no workflow

A skill é acionada pelo **Gate de Segurança do MDCU**, entre Fase 4 (Avaliação) e Fase 5 (Plano). O gatilho é o campo *Superfície de ataque afetada?* do artefato `03_avaliacao.md` marcado como **sim**. Enquanto a skill não produzir `ameacas.md` e seus achados não forem incorporados ao plano, a Fase 5 não pode ser declarada concluída (regra 10 do MDCU v2).

### O que esta skill faz

Executa análise de ameaças sobre o escopo proposto e entrega um artefato estruturado com:
- Ameaças identificadas por categoria
- Probabilidade × impacto de cada ameaça
- Mitigações recomendadas
- Checagens de conformidade LGPD
- Riscos residuais que precisam de decisão compartilhada na Fase 5

### O que esta skill NÃO faz

- **Não substitui revisão humana crítica.** Análise automatizada de segurança sem leitura crítica cria falsa sensação de proteção — exatamente o oposto do que o gate existe para evitar. Os achados da skill são **hipóteses estruturadas**, não veredictos. O usuário e engenheiro devem ler, questionar e complementar.
- **Não substitui pentest profissional** para sistemas com superfície de ataque significativa ou dados altamente sensíveis.
- **Não garante conformidade LGPD** — identifica lacunas comuns, mas conformidade é decisão jurídica que exige DPO/jurídico.

---

## Quando ativar

**Ativação obrigatória:**
- Usuário digitou `/seguranca-dados`.
- MDCU em Fase 4 marcou *Superfície de ataque afetada = sim*.
- Há uma das seguintes mudanças planejadas:
  - Nova rota, endpoint ou API pública
  - Nova dependência externa (biblioteca, serviço, integração)
  - Novo tipo de dado pessoal sensível tratado
  - Nova integração com LLM (entrada de prompt, chave nova, novo fluxo de inferência)
  - Novo segredo/credencial gerenciado
  - Nova forma de autenticação ou autorização
  - Nova forma de armazenamento ou acesso a BD

**Não ativar:**
- Para revisão de código isolado sem contexto de mudança estrutural — use `engineering:code-review`.
- Para incidente de segurança já em curso — use `engineering:incident-response`.

---

## Contrato com o MDCU

**Inputs obrigatórios** (lidos do projeto corrente):
1. `03_avaliacao.md` — hipótese diagnóstica e superfície de ataque declarada.
2. `rsop/dados_base.md` — stack, dependências, tipos de dados tratados.
3. Código-fonte do escopo sendo avaliado (arquivos tocados pelo plano proposto).

**Output obrigatório:**
- Artefato `ameacas.md` no diretório do projeto.
- Referência cruzada: a Fase 5 do MDCU citará `ameacas.md` na seção *Ameaças e LGPD* do plano.

---

## Protocolo de execução

A skill executa 5 passos em ordem.

### Passo 1 — Coleta de contexto
- Ler `03_avaliacao.md` e extrair: hipótese, superfície de ataque declarada, reversibilidade.
- Ler `rsop/dados_base.md` e extrair: stack, dependências, tipos de dados, base legal declarada.
- Identificar os arquivos de código tocados pelo escopo proposto.

### Passo 2 — Análise por categoria
Executar as checagens de cada uma das 5 categorias abaixo. Cada categoria tem sua própria lista de verificação (ver seção "Categorias de análise"). Produzir, para cada ameaça identificada:
- Nome da ameaça
- Evidência no código/contexto (trecho, arquivo, linha, ou dado base)
- Probabilidade: baixa / média / alta
- Impacto: baixo / médio / alto / crítico
- Mitigação recomendada

### Passo 3 — Priorização
Ordenar ameaças por **impacto × probabilidade**. Ameaças *crítico + alta* vão para o topo — não podem ser risco aceito sem justificativa explícita.

### Passo 4 — Checagem LGPD dedicada
Executar checagens específicas LGPD (seção "Categoria 3"). Produzir lista de:
- Artigos da LGPD aplicáveis ao escopo
- Obrigações não atendidas
- Recomendações de mitigação

### Passo 5 — Geração do artefato
Escrever `ameacas.md` no diretório do projeto, no formato definido em "Artefato de saída". Apresentar o resumo executivo ao usuário e engenheiro para que incorporem as mitigações ao plano da Fase 5.

---

## Categorias de análise

### Categoria 1 — Prompt injection (LLMs)

Aplicável quando: há prompts para LLM que recebem input de usuário ou de fonte externa não confiável.

Checagens:
- Há **separação clara** entre system prompt e user input? (delimitadores, mensagens de papel, não concatenação direta)
- O system prompt é **tratado como dado não sensível**? (assume que pode vazar)
- Há **limites de tokens** do input para evitar ataques de inundação?
- Há **lista de saídas esperadas** ou validação da resposta? (ex: regex, schema, parser)
- Dados sensíveis recuperados (ex: prontuário, dados pessoais) **passam para o LLM com necessidade justificada**? Minimização aplicada?
- Há **logging da conversa** que poderia vazar dados sensíveis? Redação aplicada?
- A **chave de API do LLM** é isolada, rotacionada, e tem rate limit próprio?
- Há **detecção de tentativas de injection** ou de jailbreak? (padrões conhecidos, monitoramento)
- O output do LLM é **renderizado** em HTML/markdown? Há risco de XSS via resposta?
- Há **tool use** exposto? Quais ferramentas o LLM pode chamar? Autorização por ferramenta?

### Categoria 2 — Gestão de chaves de API e segredos

Aplicável sempre que há segredos (chaves, tokens, credenciais, certificados).

Checagens:
- Segredos estão em **variáveis de ambiente** ou gerenciador (Vault, AWS Secrets, etc.), **nunca no código**?
- `.env` está no `.gitignore`? Já houve commit de `.env` no histórico?
- Há **rotação periódica** de chaves? Plano de rotação documentado?
- **Escopo mínimo:** cada chave tem as permissões estritamente necessárias?
- Há **chaves diferentes** por ambiente (dev, staging, prod)?
- Logs e mensagens de erro **jamais** imprimem segredos?
- Em caso de vazamento, há **plano de revogação** conhecido e testado?
- Ferramentas de detecção de segredo em commits (gitleaks, trufflehog) estão configuradas?
- Se usa Git: filter-branch/BFG executados em histórico para chaves antigas vazadas?

### Categoria 3 — LGPD (Lei 13.709/2018)

Aplicável quando há tratamento de dados pessoais (qualquer informação que identifique ou torne identificável uma pessoa natural).

Checagens:
- **Base legal** está declarada e documentada para cada finalidade de tratamento? (art. 7º/11: consentimento, execução de contrato, cumprimento de obrigação legal, etc.)
- **Dados sensíveis** (saúde, étnico-racial, biométrico, etc.) têm base legal específica do art. 11?
- **Minimização de dados** aplicada? Só coleta/processa o que é necessário para a finalidade?
- **Retenção** tem prazo definido? Há política de eliminação automática ao fim do prazo?
- **Direitos dos titulares** (art. 18) estão implementados: acesso, correção, anonimização/eliminação, portabilidade?
- **Consentimento** (se é a base legal) é livre, informado, inequívoco, específico e revogável? Registro do consentimento existe?
- **Política de privacidade** publicada, acessível e em linguagem clara?
- **Registro das operações** de tratamento (art. 37) existe?
- **DPO/Encarregado** designado e canal de contato exposto?
- **Comunicação de incidente** (art. 48): há procedimento para notificar ANPD e titulares em caso de incidente de segurança?
- **Transferência internacional** de dados existe? Base legal do art. 33?
- **Tratamento por terceiros** (cloud, LLM externa): contratos de processamento (DPA) existem? Finalidade limitada?

### Categoria 4 — Exposição de banco de dados

Aplicável sempre que há BD com dados pessoais ou sensíveis.

Checagens:
- **SQL injection:** queries parametrizadas, nunca string concatenation. ORM configurado com parâmetros?
- **Autenticação:** BD não aceita conexões sem credencial. Usuário `root`/`admin` desabilitado ou protegido.
- **Autorização:** aplicação usa usuário com **privilégios mínimos** (apenas SELECT/INSERT nas tabelas necessárias)? Row-Level Security (RLS) implementado quando aplicável?
- **Criptografia em repouso:** BD criptografado no disco (TDE, LUKS, etc.)?
- **Criptografia em trânsito:** conexão ao BD usa TLS?
- **Rede:** BD exposto à internet? Deveria estar apenas em rede privada/VPN?
- **Backups:** criptografados? Armazenamento separado? Testados periodicamente (restore)? Prazo de retenção?
- **Logs de acesso:** quem acessou o quê e quando? Retenção dos logs de auditoria?
- **Dados sensíveis em colunas específicas:** há criptografia em nível de coluna para CPF, dados médicos, etc.?
- **Migrations:** revisadas antes de aplicar em produção? Rollback testado?

### Categoria 5 — Vazamento em logs e observabilidade

Aplicável sempre (todo sistema produz logs).

Checagens:
- Logs **redigem/mascaram** PII e dados sensíveis? (CPF, email parcial, tokens, prompts de LLM com dados pessoais)
- **Stack traces** em produção não vazam variáveis com dados sensíveis?
- **Mensagens de erro para usuário** não vazam informação interna (stack traces, queries, paths, nomes de tabela)?
- Sistemas externos de logging (Sentry, Datadog, CloudWatch) respeitam LGPD? Há DPA? Região dos dados?
- **Retenção dos logs** tem prazo? Logs com PII têm prazo menor?
- **Acesso aos logs** é restrito? Quem pode ler?
- **Tokens/sessões** não aparecem em logs? (headers Authorization redacted)

---

## Modelo de priorização

| Impacto \ Probabilidade | Baixa | Média | Alta |
|---|---|---|---|
| **Crítico** (dados sensíveis expostos, perda de integridade, parada total) | Média | Alta | **Crítica** |
| **Alto** (vazamento limitado, degradação grave) | Baixa | Média | Alta |
| **Médio** (funcionalidade degradada, dados não sensíveis expostos) | Baixa | Baixa | Média |
| **Baixo** (fricção, não afeta dados) | Mínima | Baixa | Baixa |

Regra de decisão:
- **Crítica ou Alta:** mitigação obrigatória no plano. Não aceitável como risco aceito sem justificativa muito forte.
- **Média:** mitigação recomendada. Risco aceito permitido se documentado.
- **Baixa ou Mínima:** mitigação opcional. Registrar para evolução.

---

## Artefato de saída: `ameacas.md`

Gerado no diretório do projeto. Um novo arquivo por ciclo de Gate de Segurança (preserva histórico via nome com data, ex: `ameacas-2026-04-16.md`).

```markdown
# Análise de Ameaças — [data]

- **Projeto:** [nome]
- **Escopo avaliado:** [referência à Fase 4: hipótese diagnóstica]
- **Executor:** skill `seguranca-dados` (validação humana pendente)

## Resumo executivo
- Total de ameaças identificadas: [N]
- Críticas: [N] | Altas: [N] | Médias: [N] | Baixas: [N]
- Bloqueios para a Fase 5: [lista das ameaças críticas/altas que precisam de mitigação no plano]

## Ameaças por categoria

### Categoria 1 — Prompt injection
[Para cada ameaça identificada:]
- **[Nome da ameaça]**
  - Evidência: [arquivo:linha ou dado base consultado]
  - Probabilidade: [baixa/média/alta]
  - Impacto: [baixo/médio/alto/crítico]
  - Prioridade: [mínima/baixa/média/alta/crítica]
  - Mitigação recomendada: [ação concreta]

### Categoria 2 — Gestão de chaves de API
[mesma estrutura]

### Categoria 3 — LGPD
- Artigos aplicáveis: [lista]
- Obrigações não atendidas: [lista]
- Ameaças identificadas: [mesma estrutura por ameaça]

### Categoria 4 — Exposição de BD
[mesma estrutura]

### Categoria 5 — Vazamento em logs
[mesma estrutura]

## Checklist de decisão para Fase 5

- [ ] Todas as ameaças críticas/altas têm mitigação incorporada ao plano?
- [ ] Riscos aceitos estão explicitamente documentados com justificativa?
- [ ] A base legal LGPD está declarada para cada finalidade?
- [ ] Há plano de teste para validar as mitigações (ex: teste de injection, teste de retenção)?
- [ ] A validação humana crítica foi feita (não só o output da skill)?

## Validação humana (preencher)
- Revisado por: [nome]
- Data da revisão: [data]
- Ameaças adicionais identificadas pelo humano: [lista ou "nenhuma"]
- Ameaças removidas após análise humana: [lista com justificativa ou "nenhuma"]
- Concordo que os achados acima representam a superfície de risco do escopo: [sim/não]
```

---

## Regras operacionais

1. **Gate de Segurança não pode ser pulado.** Se a Fase 4 marcou superfície de ataque afetada, a skill é obrigatória antes da Fase 5 (regra 10 do MDCU).
2. **Validação humana é obrigatória.** O artefato `ameacas.md` tem a seção "Validação humana" que precisa ser preenchida pelo engenheiro e pelo usuário. Sem isso, o gate **não está concluído**, apenas executado.
3. **Ameaças críticas/altas bloqueiam a Fase 5.** Ou são mitigadas no plano, ou são riscos aceitos com justificativa documentada. Omissão silenciosa viola a regra 10.
4. **Artefato sempre gerado.** Mesmo quando não há ameaças críticas, o artefato registra a execução do gate — parte da longitudinalidade.
5. **Dados sensíveis nunca entram no artefato.** O `ameacas.md` referencia evidências por localização (arquivo:linha), nunca pelo conteúdo do dado sensível em si.
6. **Reavaliação periódica.** Mesmo sem nova superfície de ataque, a análise fica estale: dependências recebem CVEs, LGPD recebe jurisprudência, padrões evoluem. Recomendar reavaliação a cada 6 meses ou após incidente.

---

## Aviso sobre falsa sensação de segurança

Esta skill é **operacional** — executa análise estruturada e entrega artefato. Isso é diferente de executar a análise *bem*. Riscos de uso incorreto:

1. **"A skill rodou, então estou seguro"** — não. A skill identifica classes comuns de ameaça. Classes incomuns, específicas do domínio, ou de adversário determinado estão fora do escopo.
2. **"A skill disse que o risco é baixo"** — priorização automatizada pode errar. Um risco classificado como baixo pode ser crítico no seu contexto específico (ex: dados médicos têm peso regulatório maior que dados comuns).
3. **"Não preciso ler o `ameacas.md` inteiro"** — precisa. A seção "Validação humana" existe exatamente para forçar a leitura crítica.

Se o projeto lida com dados altamente sensíveis (saúde, financeiros, menores), a skill é um ponto de partida, não de chegada. Considere auditoria profissional.

---

## Uso com `/seguranca-dados`

- `/seguranca-dados` — Executa Gate de Segurança para o projeto corrente (lê Fase 4, produz `ameacas.md`).
- `/seguranca-dados projeto [nome]` — Executa para projeto específico.
- `/seguranca-dados categoria [1-5]` — Executa apenas uma categoria (útil para reavaliação focada).
- `/seguranca-dados historico` — Lista os `ameacas-*.md` anteriores do projeto.
