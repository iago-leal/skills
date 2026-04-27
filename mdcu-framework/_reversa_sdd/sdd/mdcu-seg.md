# SDD — `mdcu-seg`

> Spec executável da skill `mdcu-seg` — Módulo de Segurança Adjunto ao MDCU.
> Gerado pelo Reversa Writer em 2026-04-27.

## Visão Geral

Módulo de segurança aprofundado, **adjunto** ao MDCU (não substitui — complementa). 🟢 Cobre **3 domínios**: threat modeling (STRIDE), contenção de incidente (F0/IRP 5 etapas), e auditoria contínua (revisão trimestral em `rsop/seguranca.md`). Aplica analogia de rastreio populacional Wilson-Jungner ao software. 🟢

## Responsabilidades

- **Threat modeling STRIDE** sobre componentes/fluxos quando o rastreio do MDCU dispara. 🟢
- **Protocolo F0 de contenção de incidente** (IRP 5 etapas): Identificação → Contenção → Erradicação → Recuperação → Postmortem. SUSPENDE o MDCU em curso. 🟢
- **Auditoria trimestral** (90 dias) registrada em `rsop/seguranca.md` com 6 seções fixas. 🟢
- **Geração de # no RSOP** para ameaças com mitigação não-trivial detectadas em STRIDE. 🟢
- **Geração de SOAP-incidente** estendendo o schema base (com `Tipo`, `Severidade L1-L4`, `Etapas F0`). 🟢
- **Sinalização de atraso** quando `seguranca.md` não é revisado em 90 dias. 🟢

## Interface

### Comandos públicos

| Comando | Efeito |
|---|---|
| `/mdcu-seg` | menu dos 3 domínios + status (última auditoria, # segurança ativos) 🟢 |
| `/mdcu-seg threat-model [escopo]` | aplica STRIDE 6-categorias × componentes; gera tabela; cria # no RSOP 🟢 |
| `/mdcu-seg incidente` | inicia F0; **SUSPENDE MDCU ativo** (preserva `_mdcu.md`) 🟢 |
| `/mdcu-seg auditoria` | abre/atualiza `rsop/seguranca.md`; sinaliza atraso se >90d 🟢 |
| `/mdcu-seg status` | resumo: # segurança ativos, última auditoria, incidentes abertos 🟢 |

### Artefatos produzidos

- `rsop/seguranca.md` — auditoria trimestral 🟢
- `rsop/soap/YYYY-MM-DD_incidente-<ref>.md` — SOAP de incidente (estende SOAP base) 🟢
- Atualizações em `rsop/lista_problemas.md` (espelho de vulnerabilidades) 🟢
- Tabela STRIDE inline em `_mdcu.md` (se em ciclo MDCU) ou em seção de `rsop/seguranca.md` (análise standalone) 🟢

## Regras de Negócio

- **Rastreio é do MDCU; aprofundamento é daqui.** Não duplicar a checklist de 5 itens. (mdcu-seg/SKILL.md:222) 🟢
- **F0 SUSPENDE o MDCU em andamento.** `_mdcu.md` preservado intacto até resolução. (mdcu-seg/SKILL.md:77, 224) 🟢
- **STRIDE: ameaça com mitigação não-trivial vira `#` no RSOP.** Categoria não-aplicável exige justificativa explícita ("— não aplicável (por quê)") — silêncio proibido. (mdcu-seg/SKILL.md:60-65) 🟢
- **Postmortem é BLAMELESS.** Falhas estruturais, nunca pessoais. (mdcu-seg/SKILL.md:97, 225) 🟢
- **Auditoria: revisão trimestral obrigatória (90 dias).** Sem revisão = "ficção administrativa". (mdcu-seg/SKILL.md:202, 226) 🟢
- **Segredo nunca em código/log/repo/issue.** Se entrou, F0 imediato. (mdcu-seg/SKILL.md:227) 🟢
- **LGPD não é compliance opcional** em software brasileiro. Tratamento de PII sem base legal documentada é `#[A]` automático. (mdcu-seg/SKILL.md:228) 🟢
- **Severidade de incidente:** escala L1/L2/L3/L4 — **não confundir** com `[A]/[M]/[B]` de problema RSOP. 🟢
- **Severidade mínima de vulnerabilidade no RSOP:** `[M]`; `[A]` se explorável em produção ou dado sensível exposto. 🟢
- **Após F0 resolvido:** MDCU retoma do `_mdcu.md` preservado, ciente dos novos `#` na lista. 🟢
- **Eventos estruturais** (nova integração, mudança de stack, nova regulação, incidente recente) disparam revisão de auditoria fora do calendário trimestral. 🟢

## Fluxo Principal

### Domínio 1 — `/mdcu-seg threat-model [escopo]`
1. Para cada componente/fluxo do escopo, aplicar 6 categorias STRIDE (S/T/R/I/D/E). 🟢
2. Identificar **ameaças concretas** (vetor identificável no sistema real) — ameaça genérica não conta. 🟢
3. Para cada ameaça: definir vetor, mitigação proposta, e se a mitigação é trivial (config, header) ou não-trivial. 🟢
4. Mitigação não-trivial → criar `#` em `rsop/lista_problemas.md` (severidade mínima `[M]`). 🟢
5. Categoria não-aplicável → registrar "— não aplicável (por quê)" (silêncio proibido). 🟢
6. Destino da tabela: `_mdcu.md` se em ciclo MDCU; `rsop/seguranca.md` (seção "Threat models") se standalone. 🟢

### Domínio 2 — `/mdcu-seg incidente` (F0)
1. **Disparo:** vazamento confirmado, acesso indevido, credencial exposta, ransomware, alerta crítico em produção, ou comando explícito do usuário. 🟢
2. **SUSPENDE MDCU** ativo. `_mdcu.md` PRESERVADO intacto. Prioridade absoluta. 🟢
3. **Etapa 1 — Identificação:** sinal inicial (o quê, quando, por quem); escopo (sistema, dado, usuários); severidade L1/L2/L3/L4. 🟢
4. **Etapa 2a — Contenção curta** (min-h): isolar / desabilitar / bloquear / cortar tráfego. 🟢
5. **Etapa 2b — Contenção média** (h-dias): patch temporário, rotação de credenciais, fortificação. 🟢
6. **Etapa 3 — Erradicação:** patch definitivo, rotação completa, remoção de IoC, revisão de código afetado. 🟢
7. **Etapa 4 — Recuperação:** restaura serviço com monitoramento reforçado; valida que IoC não reaparecem. 🟢
8. **Etapa 5 — Postmortem (blameless):** linha do tempo factual, causa raiz, falhas de detecção, ações estruturais. 🟢
9. **Artefato:** `rsop/soap/YYYY-MM-DD_incidente-<ref>.md` no formato SOAP estendido. 🟢
10. MDCU retoma do `_mdcu.md` preservado. 🟢

### Domínio 3 — `/mdcu-seg auditoria`
1. Lê `rsop/seguranca.md`. Se ausente, cria com estrutura base. 🟢
2. Se `Última revisão > 90d` → sinaliza atraso (revisão obrigatória). 🟢
3. Atualiza 6 seções:
   - Classificação de dados (Restrito/Confidencial/Interno/Público)
   - Regime de auditoria (SAST/DAST/Dep scan/Secret scan/Pentest/Code review)
   - Gestão de segredos
   - Conformidade (LGPD/HIPAA/PCI-DSS/...)
   - Histórico de incidentes (12 meses)
   - Vulnerabilidades ativas (espelho de `lista_problemas.md` filtrada por segurança) 🟢
4. Atualiza `Última revisão` e `Próxima revisão` (= +90d). 🟢

## Fluxos Alternativos

- **MDCU em F1 com `#[A]` segurança ativo:** invoca `/mdcu-seg auditoria` para contextualizar; avalia se é incidente ativo. 🟢
- **MDCU em F3 com item 1 (PII) ou item 2 (auth) afirmativo:** invoca `/mdcu-seg threat-model` com escopo do problema. 🟢
- **MDCU em F5 com alternativa que falha no rastreio:** invoca `/mdcu-seg threat-model` sobre a alternativa. 🟢
- **MDCU em F6 com sinal de incidente** (logs anômalos, vazamento, comportamento atípico): invoca `/mdcu-seg incidente` IMEDIATAMENTE — suspende ciclo. 🟢
- **Vulnerabilidade resolvida:** mesmo se no mesmo dia, entra em `lista_problemas.md`; ao migrar para `passivos.md` recebe `reativável? sim — vigiar recorrência`. 🟢
- **Auditoria pós-incidente** (fora do calendário): forçar revisão imediatamente. 🟢

## Dependências

- **`rsop`** — atualiza `lista_problemas.md`, `seguranca.md`, e cria SOAPs de incidente em `soap/`. 🟢
- **`mdcu`** — pode SUSPENDER ciclo via F0; é invocado por gatilhos do MDCU em F1/F3/F5/F6. 🟢

## Requisitos Não Funcionais

| Tipo | Requisito inferido | Evidência | Confiança |
|---|---|---|---|
| Tempo de resposta a incidente | Etapas 2a (contenção curta) em min-h; 2b em h-dias; 3 (erradicação) em dias | mdcu-seg/SKILL.md:86-91 | 🟢 |
| Cobertura | STRIDE força tratar 6 categorias — silêncio proibido | mdcu-seg/SKILL.md:65 | 🟢 |
| Vigilância contínua | Auditoria trimestral (90d) obrigatória | mdcu-seg/SKILL.md:202 | 🟢 |
| Conformidade | LGPD vinculante para projetos brasileiros; tratamento sem base legal vira `#[A]` | mdcu-seg/SKILL.md:228 | 🟢 |
| Auditabilidade | Histórico de incidentes 12 meses em `seguranca.md`; cada incidente tem SOAP referenciado | mdcu-seg/SKILL.md:194-196 | 🟢 |
| Cultura | Postmortem blameless por design (vetada redação com nome próprio) | mdcu-seg/SKILL.md:97, 225 | 🟢 |
| Anti-superficialidade | Mitigação trivial não cria `#`; mitigação não-trivial sempre cria | mdcu-seg/SKILL.md:62-63 | 🟢 |

## Critérios de Aceitação

```gherkin
Dado que MDCU em F3 detectou item 1 (dados sensíveis) afirmativo
Quando MDCU invoca /mdcu-seg threat-model com escopo do problema
Então mdcu-seg gera tabela STRIDE com 6 categorias
  E para cada categoria não-aplicável, registra justificativa explícita
  E para cada ameaça com mitigação não-trivial, cria # em rsop/lista_problemas.md (severidade mínima [M])

Dado que F6 do MDCU detecta logs anômalos compatíveis com incidente
Quando mdcu-seg é invocado via /mdcu-seg incidente
Então mdcu-seg SUSPENDE MDCU em curso (preserva _mdcu.md)
  E executa as 5 etapas de F0 com timestamps
  E gera rsop/soap/YYYY-MM-DD_incidente-<ref>.md
  E após Postmortem, MDCU retoma do _mdcu.md preservado

Dado que rsop/seguranca.md tem Última revisão > 90d
Quando o usuário digita /mdcu-seg auditoria
Então mdcu-seg sinaliza atraso (revisão obrigatória)
  E após atualização, define Próxima revisão = hoje + 90d

Dado que uma credencial AWS foi exposta em commit (severidade L3)
Quando mdcu-seg incidente é executado
Então o postmortem é BLAMELESS — sem nome próprio
  E ações listadas são estruturais (ex: instalar gitleaks pre-commit)
  E o # de vulnerabilidade é registrado em lista_problemas.md como [A]
  E ao ser corrigido, migra para passivos.md com reativável? sim — vigiar recorrência

Dado que um projeto brasileiro trata PII sem base legal documentada
Quando mdcu-seg auditoria é executada
Então uma # de severidade [A] é criada automaticamente no RSOP
```

## Prioridade

| Requisito | MoSCoW | Justificativa |
|---|---|---|
| F0 SUSPENDE MDCU | Must | Contenção de incidente tem prioridade absoluta |
| STRIDE 6-categorias com silêncio proibido | Must | Anti-superficialidade |
| Auditoria trimestral 90d | Must | Vigilância sem revisão = ficção |
| Postmortem blameless | Must | Cultura — falha estrutural não pessoal |
| LGPD obrigatória PT-BR | Must | Vinculante para projetos brasileiros |
| Severidade L1-L4 separada de [A]/[M]/[B] | Must | Domínios distintos não devem misturar |
| Eventos estruturais disparam auditoria fora do trimestre | Should | Cobertura proativa |
| Status `/mdcu-seg status` | Could | Conveniência |
| Threat-model standalone (fora de MDCU) | Should | Útil em design exploratório |
| Auto-detecção de incidente sem comando | Won't | Sempre via comando explícito ou gatilho do MDCU |

## Rastreabilidade de Código

| Arquivo | Componente lógico | Cobertura |
|---|---|---|
| `mdcu-seg/SKILL.md:1-3` | frontmatter | 🟢 |
| `mdcu-seg/SKILL.md:6-12` | Relação com MDCU (rastreio vs aprofundamento) | 🟢 |
| `mdcu-seg/SKILL.md:16-23` | Três domínios | 🟢 |
| `mdcu-seg/SKILL.md:27-66` | Domínio 1 — Threat modeling (STRIDE) | 🟢 |
| `mdcu-seg/SKILL.md:70-147` | Domínio 2 — Protocolo F0 (5 etapas + SOAP-incidente) | 🟢 |
| `mdcu-seg/SKILL.md:151-202` | Domínio 3 — Auditoria trimestral | 🟢 |
| `mdcu-seg/SKILL.md:206-216` | Gatilhos de delegação MDCU → mdcu-seg | 🟢 |
| `mdcu-seg/SKILL.md:220-228` | 7 regras de operação | 🟢 |
| `mdcu-seg/SKILL.md:233-238` | Comandos `/mdcu-seg` | 🟢 |
