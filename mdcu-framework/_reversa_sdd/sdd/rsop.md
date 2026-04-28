# SDD — `rsop`

> Spec executável da skill RSOP (Registro de Software Orientado por Problemas).
> Gerado pelo Reversa Writer em 2026-04-27.

## Visão Geral

Prontuário longitudinal do software, inspirado no RMOP de Lawrence Weed (1968) e no RCOP do e-SUS PEC. 🟢 Formato telegráfico, orientado por problema. Único registro permanente da sessão MDCU; demais artefatos do framework são transitórios. 🟢

## Responsabilidades

- Manter o **perfil estrutural** do projeto (`dados_base.md`). 🟢
- Manter o **índice ativo** de problemas (`lista_problemas.md`) — injetado no `CLAUDE.md`/system prompt. 🟢
- Manter o **arquivo morto** de problemas resolvidos (`passivos.md`) — fora do system prompt por padrão. 🟢
- Registrar **SOAPs** (S/O/A/P/R) por sessão MDCU em `soap/YYYY-MM-DD_<contexto>.md`. 🟢
- Migrar problemas resolvidos de ativo→passivo via `/rsop revisar`. 🟢
- Reabrir problemas em regressão via `/rsop regressao`. 🟢
- Aplicar exceção de segurança: vulnerabilidade SEMPRE entra na lista (mesmo se corrigida no dia). 🟢

## Interface

### Comandos públicos

| Comando | Lê | Escreve |
|---|---|---|
| `/rsop init` | — | `dados_base.md`, `lista_problemas.md`, `passivos.md` (vazio), cria `soap/` 🟢 |
| `/rsop dados` | `dados_base.md` | `dados_base.md` 🟢 |
| `/rsop lista` | `lista_problemas.md` | — (não inclui passivos) 🟢 |
| `/rsop passivos` | `passivos.md` | — (uso restrito: regressão ou pedido) 🟢 |
| `/rsop soap` | `_mdcu.md`, `lista_problemas.md` | `soap/YYYY-MM-DD_<contexto>.md` 🟢 |
| `/rsop revisar` | `lista_problemas.md`, `passivos.md` | ambos (migração ativos↔passivos) 🟢 |
| `/rsop regressao N` | `passivos.md` | `lista_problemas.md` + nota em `passivos.md` 🟢 |
| `/rsop status` | todos | resumo (data dados base, #ativos, #passivos como número, último SOAP) 🟢 |
| `/rsop reset` | todos | **(roadmap, não implementado)** apaga e recria estrutura com confirmação dupla — saída P2 para Cenário B (reset deliberado) 🔵 |
| `/rsop repair` | filesystem | **(roadmap, não implementado)** recria apenas arquivos faltantes (merge não-destrutivo) — saída P2 para Cenário C (restauração parcial) 🔵 |

### Artefatos produzidos (4)

`dados_base.md`, `lista_problemas.md`, `passivos.md`, `soap/YYYY-MM-DD_<contexto>.md`. Schemas completos em `_reversa_sdd/data-dictionary.md`. 🟢

## Regras de Negócio

- **Princípio da separação ativos/passivos:** apenas `lista_problemas.md` (ativos) é injetado no system prompt; passivos vivem em arquivo estático fora do contexto. (rsop/SKILL.md:34) 🟢
- **S separa Demanda × Queixa.** Sem essa separação, o plano vai na direção errada. (rsop/SKILL.md:148-153) 🟢
- **A e P são 1:1 por problema.** Nunca prosa livre. (rsop/SKILL.md:165-169) 🟢
- **A: máximo 5 palavras por item.** Se estourar, o `#` está mal nomeado — refinar. (rsop/SKILL.md:165, 221) 🟢
- **R: uma linha ou omitida.** Nunca parágrafo. (rsop/SKILL.md:171-173, 222) 🟢
- **Exceção segurança:** vulnerabilidade SEMPRE entra na lista (mesmo se corrigida no dia); ao fechar migra para passivos com `reativável? sim — vigiar recorrência`. (rsop/SKILL.md:80) 🟢
- **Consulta a `passivos.md`** SÓ por suspeita de regressão ou pedido explícito do usuário. Fora disso, invisível ao agente. (rsop/SKILL.md:103-109) 🟢
- **SOAP lê `_mdcu.md`** (campos S: e O:) — não reconstrói de memória de chat. (rsop/SKILL.md:155, 161) 🟢
- **`#` é estável e nunca reciclado** entre ativos↔passivos nem entre projetos. 🟢
- **Reabertura:** linha em `passivos.md` recebe nota `reaberto em [data] — ver SOAP [ref]`; `#` retorna a `lista_problemas.md`. (rsop/SKILL.md:122) 🟢
- **Severidade:** prefixo `[A]/[M]/[B]` no nome do problema (sem coluna separada); vulnerabilidade tem mínimo `[M]`, `[A]` se explorável em prod. (rsop/SKILL.md:76, 80) 🟢
- **`dados_base.md`:** "template é teto, não piso" — campos vazios devem ser omitidos. (rsop/SKILL.md:64) 🟢

## Fluxo Principal

### `/rsop soap` (caminho mais comum)
1. Localiza `_mdcu.md` da sessão atual. 🟢
2. Lê campo `S:` (com sub-slots Demandas/Queixas/Notas) — **fonte primária**, não chat. 🟢
3. Lê campo `O:` (bullets, fontes explícitas). 🟢
4. Lê seções F4/F5/F6 para sintetizar A, P, R. 🟢
5. Identifica `#` referenciados (de `lista_problemas.md`). 🟢
6. Aplica disciplina telegráfica: A ≤ 5 palavras/item, P 1:1 com A, R = 1 linha ou omitido. 🟢
7. Escreve `soap/YYYY-MM-DD_<contexto>.md`. 🟢

### `/rsop revisar` (manutenção da lista)
1. Itera sobre cada `#` em `lista_problemas.md`. 🟢
2. Se resolvido → migra para `passivos.md` com colunas `Fechado por`, `Fechado em`, `Reativável?`. 🟢
3. Se não resolvido mas evoluiu → reclassifica severidade ou refina descrição. 🟢

## Fluxos Alternativos

- **Vulnerabilidade resolvida no mesmo dia:** entra como ativo `[M]+`, no fechamento da sessão migra direto para `passivos.md` com `reativável? sim — vigiar recorrência`. 🟢
- **Sintoma compatível com problema antigo:** `/rsop regressao N` consulta `passivos.md`, e se encontrar reabre em `lista_problemas.md` com nota cruzada. 🟢
- **`_mdcu.md` ausente em `/rsop soap`:** **PERGUNTA ao usuário** qual cenário (A: adoção parcial sem `mdcu` / B: hotfix sem ciclo MDCU / C: `_mdcu.md` deletado por engano) e adapta: 🟢 (Iago, 2026-04-27 — questions.md P1)
  - **Cenário A (adoção parcial):** cria SOAP em branco com seções S/O/A/P/R vazias para preenchimento manual; aviso "registrando SOAP fora do ciclo MDCU".
  - **Cenário B (hotfix curto):** cria SOAP guiado curto — pergunta sumária do que foi feito; preenche A+P 1:1, S/O minimal.
  - **Cenário C (`_mdcu.md` deletado):** ABORTA com orientação "verifique `git status`/`git log` antes; se confirmar perda, re-rode `/mdcu` ou crie SOAP do cenário A".
- **`/rsop init` em diretório que já tem `rsop/`:** **ABORTA com aviso** — "rsop/ já existe (X ativos, Y SOAPs). Para reset use `/rsop reset` (futuro); para restaurar arquivos faltantes use `/rsop repair` (futuro)." Não sobrescreve nada. 🟢 (Iago, 2026-04-27 — questions.md P2)
  - **Comandos futuros sinalizados:** `/rsop reset` e `/rsop repair` ainda não implementados — adicionar à roadmap das próximas mudanças.

## Dependências

- **Autônoma.** Não importa nada de outras skills do framework. 🟢
- É consumida por: `mdcu` (lê em F1, escreve em F4 e fechamento), `commit-soap` (lê SOAP mais recente), `mdcu-seg` (espelha vulnerabilidades em `seguranca.md`, gera `soap/incidente-*.md`). 🟢

## Requisitos Não Funcionais

| Tipo | Requisito inferido | Evidência | Confiança |
|---|---|---|---|
| Auditabilidade | SOAPs são append-only (datados); `git log` no diretório `rsop/soap/` reconstrói a história | rsop/SKILL.md:25-32 | 🟢 |
| Economia de contexto | Separação ativos/passivos; passivos não injetados no system prompt | rsop/SKILL.md:34 | 🟢 |
| Robustez ao Lost in the Middle | SOAP lê `_mdcu.md`, não memória de chat | rsop/SKILL.md:155, 161 | 🟢 |
| Reabertura | Suporte explícito a regressão via `/rsop regressao` | rsop/SKILL.md:122, 237 | 🟢 |
| Disciplina de prosa | A ≤ 5 palavras, R = 1 linha — anti-prosa-prolixa | rsop/SKILL.md:165, 222 | 🟢 |
| Performance | Não aplicável | — | — |

## Critérios de Aceitação

```gherkin
Dado que _mdcu.md tem S: com 3 Demandas e 1 Queixa, e O: com 5 fatos
Quando o usuário digita /rsop soap
Então rsop cria soap/YYYY-MM-DD_<contexto>.md com:
  S contendo as 3 Demandas e 1 Queixa
  O contendo os 5 fatos com fonte
  A com no máximo 5 palavras por item
  P com 1:1 correspondência com A

Dado que lista_problemas.md tem 5 # ativos
  E o problema #3 foi resolvido nesta sessão
Quando o usuário digita /rsop revisar
Então rsop move #3 para passivos.md com Fechado por, Fechado em, Reativável?
  E lista_problemas.md fica com 4 # ativos

Dado que o usuário acha que está vendo regressão de um bug antigo (#7)
Quando o usuário digita /rsop regressao 7
Então rsop consulta passivos.md, e se #7 corresponde,
  reabre #7 em lista_problemas.md
  E adiciona nota "reaberto em [data] — ver SOAP [ref]" em passivos.md

Dado que uma vulnerabilidade [M] foi detectada e corrigida no mesmo dia
Quando a sessão é fechada com /mdcu fechar
Então a vulnerabilidade entra em lista_problemas.md (mesmo corrigida no dia)
  E migra para passivos.md com reativável? sim — vigiar recorrência

Dado que o agente está respondendo a uma pergunta não-relacionada a regressão
Quando o agente considera consultar passivos.md
Então o agente NÃO consulta passivos.md (só por suspeita de regressão ou pedido explícito)

Dado que NÃO existe _mdcu.md na sessão
Quando o usuário digita /rsop soap
Então rsop pergunta ao usuário em qual cenário está:
  (A) adoção parcial sem ciclo MDCU
  (B) hotfix curto sem ciclo
  (C) _mdcu.md deletado por engano
  E adapta o comportamento:
    A → cria SOAP em branco para preenchimento manual
    B → cria SOAP guiado curto
    C → ABORTA com orientação para verificar git e recriar

Dado que rsop/ já existe (com X ativos e Y SOAPs)
Quando o usuário digita /rsop init
Então rsop ABORTA com mensagem
  "rsop/ já existe (X ativos, Y SOAPs). Para reset use /rsop reset (futuro);
   para restaurar arquivos faltantes use /rsop repair (futuro)."
  E NÃO sobrescreve nem deleta nada
```

## Prioridade

| Requisito | MoSCoW | Justificativa |
|---|---|---|
| SOAP estruturado (S/O/A/P/R) | Must | Único registro permanente da sessão |
| Separação ativos/passivos | Must | Preserva foco do agente; economia de tokens |
| `#` estável | Must | Permite `git log --grep="#N"` para história longitudinal |
| Disciplina telegráfica (A≤5, R=1) | Must | Anti-prosa, alinhado ao princípio fundador |
| Exceção de segurança | Must | Vulnerabilidade não pode ser "esquecida" no SOAP |
| `/rsop regressao` | Should | Importante mas usado raramente |
| `/rsop status` | Could | Conveniência |
| `/rsop init` em diretório existente | Could | Edge case |
| Auto-detecção de regressão | Won't | Sempre via comando explícito (não automático) |

## Rastreabilidade de Código

| Arquivo | Componente lógico | Cobertura |
|---|---|---|
| `rsop/SKILL.md:1-3` | frontmatter | 🟢 |
| `rsop/SKILL.md:6-19` | Fundamento + posicionamento | 🟢 |
| `rsop/SKILL.md:21-34` | Estrutura + princípio ativos/passivos | 🟢 |
| `rsop/SKILL.md:38-64` | Componente 1 — Dados base | 🟢 |
| `rsop/SKILL.md:68-94` | Componente 2 — Lista de problemas | 🟢 |
| `rsop/SKILL.md:98-122` | Componente 3 — Passivos (arquivo morto) | 🟢 |
| `rsop/SKILL.md:126-211` | Componente 4 — SOAP (S/O/A/P/R) | 🟢 |
| `rsop/SKILL.md:215-225` | Regras de operação (10) | 🟢 |
| `rsop/SKILL.md:229-238` | Comandos `/rsop` | 🟢 |

---

## Refresh 2026-04-27 — delta v1.4.0

> Acionado pelos commits `cd59735` (schema enriquecido) → `8b15dd6` (rsop revisar) → `be71eca` (checklist qualidade). Detalhes em `_reversa_sdd/code-analysis.md` apêndice.

### Mudanças estruturais 🟢

- **Frontmatter `version: "1.4.0"` + `author: Iago Leal`**
- **Schema da `lista_problemas.md` enriquecido** — colunas `Tipo` (consciente|omitido=acidental) + `Revisitar` (livre, obrigatório se Tipo=consciente conforme RN-D-016 em `framework/glossary.md`)
- **Schema permite prefixo `[aceito-arquivado]` na coluna `#`** — RN-D-015
- **Seção NOVA "Dívida consciente × acidental"** — explica defaults implícitos
- **Seção NOVA "Triagem precisa-resolver"** — codifica eixo via prefixo
- **Seção NOVA "Checklist de qualidade do SOAP"** — 10 itens binários, cap F-4, auto-aplicado em F6.c do MDCU, NÃO-bloqueante

### Schema atualizado da `lista_problemas.md` 🟢

```
| # | Problema | Tipo | Revisitar | Desde | Últ. SOAP |
```

**Defaults implícitos preservam P-5:**
- `Tipo` omitido = `acidental`
- `Revisitar` omitido = sem prazo (válido para acidentais)
- Apenas `Tipo: consciente` é declarado, e exige `Revisitar` preenchido

### Checklist de qualidade do SOAP NOVO 🟢

10 itens binários derivados de regras canônicas existentes. Cap F-4 declarado: mede o necessário, não o suficiente.

| # | Item | Verificável |
|---|---|---|
| 1 | S separa Demandas de Queixas | sim |
| 2 | Padrão de demanda aparente classificado quando aplicável | sim |
| 3 | A é lista numerada com itens ≤5 palavras | sim |
| 4 | P é 1:1 com A | sim |
| 5 | Cada item de A referencia `#` válido | sim |
| 6 | R é uma linha OU omitido | sim |
| 7 | S e O lidos do `_mdcu.md`, não da memória | sim (timestamp) |
| 8 | Dívida consciente tem Tipo + Revisitar preenchidos | sim |
| 9 | Aceito-arquivado usa prefixo na coluna `#` | sim |
| 10 | Anamnese atualizada se padrão novo do stakeholder emergiu | semi |

### Critério de Aceitação NOVO (Gherkin)

```gherkin
Cenário: Dívida consciente exige Revisitar preenchido (RN-D-016)
  Dado que MDCU em F4/F5 introduz problema "cache em memória single-node"
  E que stakeholder declara que é escolha informada de adiar resolução
  Quando o problema é adicionado à lista_problemas.md
  Então a coluna Tipo é preenchida com "consciente"
  E a coluna Revisitar é preenchida obrigatoriamente (data ISO ou condição)
  E o checklist de qualidade do SOAP item 8 retorna "sim"

Cenário: Queixa-triada-aceita usa prefixo aceito-arquivado (RN-D-015)
  Dado que F2 captou queixa "log verbose em dev"
  E que stakeholder em F4 decide que NÃO precisa resolver
  Quando a entrada é registrada na lista_problemas.md
  Então o # é prefixado com [aceito-arquivado]
  E a descrição inclui motivo da aceitação
  E o checklist item 9 retorna "sim"
```

### Anti-padrão a vigiar

Percorrer o checklist mecanicamente sem leitura crítica. O checklist é gatilho para releitura, não substituto. Se 10/10 sim mas o SOAP "soa raso", o problema está em F-4. NÃO selar até resolver.
