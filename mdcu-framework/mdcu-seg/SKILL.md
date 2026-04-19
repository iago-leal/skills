---
name: mdcu-seg
description: Módulo de segurança aprofundada adjunta ao MDCU — threat modeling estruturado (STRIDE), protocolo de contenção de incidente (F0), e regime de auditoria contínua registrado no RSOP. Aplica a analogia de rastreio populacional de Wilson-Jungner ao software. ATIVE SEMPRE que o usuário digitar /mdcu-seg ou subcomandos (threat-model, incidente, auditoria), quando mencionar vazamento, incidente de segurança, breach, pentest, CVE crítico, LGPD, ameaça ou compromisso. Ative também quando a skill `mdcu` delegar explicitamente (gatilhos em F1/F3/F6), quando dados sensíveis (PII, PHI, credenciais) forem tocados em decisão de design, ou quando comportamento anômalo em produção sugerir incidente ativo. Ative proativamente quando o contexto técnico envolver auth/autz, criptografia, gestão de segredos, ou conformidade regulatória. NÃO ative para rastreio básico de 5 itens (pertence ao MDCU), nem para dúvidas gerais sobre segurança sem contexto de sistema específico.
---

# mdcu-seg — Módulo de Segurança do MDCU

## Relação com MDCU

Adjunta ao MDCU, não substitui. O MDCU faz **rastreio** (checklist de 5 itens — detecta sintoma). O mdcu-seg faz **exploração aprofundada, contenção, e vigilância longitudinal** — equivalente ao propedêutico completo, manejo de urgência e seguimento crônico quando o rastreio dispara ou há sinal evidente.

Analogia clínica: rastreio identifica populações em risco; a avaliação especializada caracteriza e conduz. Ambos necessários; separar o papel evita sobrecarga no rastreio e superficialidade na avaliação.

---

## Três domínios

```
mdcu-seg/
├── 1. threat-model   (exploração aprofundada — STRIDE)
├── 2. incidente (F0) (contenção ativa — IRP)
└── 3. auditoria      (vigilância longitudinal — rsop/seguranca.md)
```

---

## Domínio 1 — Threat modeling (STRIDE)

**Quando disparar:**
- MDCU F3: rastreio detectou item 1 (dados sensíveis) ou item 2 (auth/autz) afirmativo.
- Usuário pede `/mdcu-seg threat-model [escopo]`.
- Nova feature/componente que manipula PII, PHI, credenciais, transações financeiras.
- Mudança arquitetural que altera superfície de ataque ou modelo de confiança.

**Método STRIDE — 6 categorias, tabela por componente/fluxo:**

| Categoria | Pergunta-gatilho |
|-----------|------------------|
| **S**poofing | Quem diz ser X pode ser falsificado? (identidade de usuário, serviço, token) |
| **T**ampering | Dados em trânsito ou em repouso podem ser alterados sem detecção? |
| **R**epudiation | Há log auditável que impeça negação de ação? |
| **I**nformation disclosure | Que informação vaza para quem não deveria ver? |
| **D**enial of service | Qual recurso pode ser esgotado/bloqueado por atacante? |
| **E**levation of privilege | Usuário comum pode virar admin? serviço externo pode virar interno? |

**Output esperado:**

```markdown
# Threat model — [componente/fluxo] — [data]
- Escopo: [componente, fronteira de confiança]

| Categoria | Ameaça concreta | Vetor | Mitigação | → RSOP `#` |
|-----------|-----------------|-------|-----------|-----------|
| S | token JWT sem verificação de iss | API gateway | validar iss+aud+exp | #novo [A] |
| T | corpo request não assinado | endpoint público | HMAC ou mTLS | #novo [M] |
| I | log de auth grava senha em claro | middleware | redact hook | #novo [A] |
| ... | ... | ... | ... | ... |
```

**Regras:**
- Uma linha por ameaça concreta. Ameaça genérica ("pode haver spoofing") não conta — só contam vetores identificáveis no sistema real.
- Toda ameaça com mitigação não-trivial vira `#` no RSOP. Severidade segue a exceção da lista de problemas (`[M]` mínimo; `[A]` se explorável em produção).
- Mitigações triviais (configuração correta, cabeçalho presente) ficam só na tabela — não poluem a lista.
- Se uma categoria STRIDE não se aplica, registrar `— não aplicável (por quê)` em uma linha. Silêncio não é resposta.

**Destino da tabela:** vai para o `_mdcu.md` do MDCU corrente se em ciclo, ou para `rsop/seguranca.md` (seção "Threat models" com índice por data) se análise independente.

---

## Domínio 2 — Protocolo F0: Contenção de incidente

**Quando disparar:**
- Sinal de incidente ativo: vazamento confirmado, acesso indevido detectado, serviço comprometido, ransomware, credencial exposta publicamente, alerta de segurança crítico disparado em produção.
- Usuário dispara `/mdcu-seg incidente`.
- MDCU F6: durante execução, surge comportamento compatível com incidente (ex. logs anômalos, tráfego atípico, usuário reporta atividade suspeita).

**Efeito imediato:** o ciclo MDCU em andamento é **suspenso**. `_mdcu.md` é preservado intacto (não deletado) até o incidente ser resolvido. Prioridade absoluta.

**Fluxo F0 — 5 etapas (alinhadas ao IRP clássico):**

### 1. Identificação
- Sinal inicial: o que foi detectado, quando, por quem.
- Escopo inicial: qual sistema, que dado, que usuários.
- Severidade: L1 (baixa, contida) / L2 (média, parcial) / L3 (alta, exposição confirmada) / L4 (crítica, ativa em produção).

### 2. Contenção
**Curto prazo (minutos a horas):** isolar o sistema comprometido. Desabilitar token/chave. Bloquear IP. Cortar tráfego. Objetivo: parar o sangramento, não curar.

**Médio prazo (horas a dias):** patch temporário, rotação de credenciais, fortificação de perímetro. Ainda não é erradicação — é contenção estendida.

### 3. Erradicação
Remover a causa raiz: patch definitivo, rotação completa de segredos expostos, remoção de malware/backdoor, revisão de código afetado.

### 4. Recuperação
Restaurar serviço com monitoramento reforçado. Validar que indicadores de comprometimento (IoC) não reapareçam. Só aqui o sistema volta ao normal.

### 5. Postmortem (blameless)
Linha do tempo factual. Causa raiz. Falhas de detecção (por que não pegamos antes?). Ações estruturais (não pessoais).

**Artefato `rsop/soap/YYYY-MM-DD_incidente-[ref].md`:**

```markdown
# SOAP-incidente 2026-04-15 — credencial AWS exposta em commit
- Tipo: incidente (F0)
- Severidade: L3
- Problemas: #novo [A] credencial AWS exposta, #novo [A] ausência pre-commit secret scan

## S
**Demandas**
- rotacionar credencial e remover do histórico git agora

**Queixas**
- equipe desconfiada de escopo do vazamento

**Notas**
- SIFE: pressão alta, medo de uso malicioso
- possível demanda oculta: auditar se outras credenciais seguem o mesmo padrão

## O
- commit abc1234 na branch main expõe AWS_SECRET em `.env.example`
- credencial ativa, com permissões S3 full + IAM read
- exposição desde 2026-04-14 14:22 (descoberta 2026-04-15 09:10) — janela ~19h
- logs CloudTrail: sem uso anômalo no período

## Etapas F0
1. **Identificação** (09:10): alerta de secret scanner externo
2. **Contenção curta** (09:15): credencial desabilitada no IAM
3. **Contenção média** (09:40): revisão de permissões de serviço, rotação de deps
4. **Erradicação** (11:00): commit reescrito via BFG, push forçado com coordenação
5. **Recuperação** (14:00): nova credencial, serviço normal, alert rule adicionada
6. **Postmortem** (dia seguinte): sem pre-commit hook para secrets; falta de secret manager centralizado

## A
1. #novo [A] credencial AWS exposta em commit
2. #novo [A] ausência pre-commit secret scan
3. #novo [M] sem secret manager centralizado

## P
1. credencial rotacionada + CloudTrail monitorado por 30 dias
2. instalar gitleaks + husky pre-commit (esta semana)
3. avaliar Vault/AWS Secrets Manager (próximo ciclo MDCU)

## R
- detecção externa, não interna — falha estrutural de visibilidade; próximo ciclo deve fechar isso
```

**Após F0:** o MDCU retoma do `_mdcu.md` preservado, agora ciente de novos `#` na lista. Postmortem pode disparar ciclo MDCU novo para as ações estruturais.

---

## Domínio 3 — Regime de auditoria (`rsop/seguranca.md`)

**Quando disparar:**
- `/mdcu-seg auditoria` (revisão ou atualização).
- Início do projeto: criar o artefato vazio com classificação de dados definida.
- Revisão trimestral obrigatória.
- Evento estrutural: nova integração, mudança de stack, nova regulação aplicável, incidente recente.

**Artefato `rsop/seguranca.md`:**

```markdown
# Segurança — regime
- **Projeto:** [nome] — **Última revisão:** [data] — **Próxima revisão:** [data]

## Classificação de dados
| Categoria | O que é | Onde mora | Quem acessa |
|-----------|---------|-----------|-------------|
| Restrito | PHI/PII identificada | DB criptografado | app + DPO |
| Confidencial | credenciais, tokens, chaves | secret manager | serviços autorizados |
| Interno | métricas agregadas, logs | stack observability | time |
| Público | docs, landing | CDN | todos |

## Regime de auditoria
- **SAST:** [ferramenta, frequência, onde vê resultado]
- **DAST:** [idem]
- **Dependency scan:** [Dependabot/Snyk/Renovate, frequência]
- **Secret scan:** [gitleaks pre-commit + CI — sim/não]
- **Pentest:** [interno/externo, periodicidade, último executado]
- **Code review de segurança:** [obrigatório em PRs que tocam X, Y, Z]

## Gestão de segredos
- **Onde moram:** [secret manager específico]
- **Rotação:** [política por tipo — chaves API / certificados / DB]
- **Acesso:** [quem pode ler, via quê]

## Conformidade
- **Regulações aplicáveis:** [LGPD, HIPAA, PCI-DSS, ISO 27001, etc.]
- **DPO/responsável:** [quem]
- **Base legal de tratamento:** [consentimento, obrigação legal, legítimo interesse, etc.]
- **Política de retenção:** [por categoria de dado]

## Histórico de incidentes (últimos 12 meses)
| Data | Severidade | Resumo | Postmortem |
|------|-----------|--------|------------|
| 2026-04-15 | L3 | credencial AWS exposta | [ref SOAP] |

## Vulnerabilidades ativas (espelho da lista de problemas — só as de segurança)
- #3 [A] log de auth grava senha em claro (desde 2026-03-20)
- #7 [M] JWT sem validação de aud (desde 2026-04-01)
```

**Revisão trimestral:** obrigatória. Se passar 90 dias sem atualização do arquivo, o `/mdcu-seg auditoria` sinaliza atraso. Regime de auditoria é a presença viva — sem revisão periódica, o arquivo vira ficção administrativa.

---

## Gatilhos de delegação pelo MDCU

O MDCU deve invocar esta skill nos seguintes casos:

| Fase MDCU | Condição | Chamada |
|-----------|----------|---------|
| F1 | RSOP tem `#[A]` de segurança ativo | `/mdcu-seg auditoria` para contextualizar; avaliar se é incidente ativo |
| F3 | Rastreio item 1 (dados sensíveis) ou item 2 (auth/autz) dispara | `/mdcu-seg threat-model` |
| F5 | Alternativa proposta falha no rastreio | `/mdcu-seg threat-model` sobre a alternativa |
| F6 | Execução revela sinal de incidente | `/mdcu-seg incidente` imediatamente |
| Qualquer | Usuário menciona vazamento/breach/CVE crítico/LGPD | delegar conforme contexto |

---

## Regras de operação

1. **Rastreio é do MDCU; aprofundamento é daqui.** Não duplicar a checklist de 5 itens.
2. **Threat model gera `#` no RSOP.** Ameaças sem mitigação trivial viram problemas rastreáveis.
3. **F0 suspende o MDCU em andamento.** Contenção tem prioridade absoluta; `_mdcu.md` é preservado.
4. **Postmortem é blameless.** Falhas estruturais, nunca pessoais. Aprendizado vale mais que culpa.
5. **Regime de auditoria tem revisão trimestral.** Sem revisão, não há vigilância — só burocracia.
6. **Segredo nunca entra em código, log, repositório, ou issue.** Se entrou, F0 imediato.
7. **LGPD não é item de compliance opcional** em software brasileiro. Tratamento de dado pessoal sem base legal documentada é `#[A]`.

---

## Uso com `/mdcu-seg`

- `/mdcu-seg` — menu dos três domínios + status (última revisão da auditoria, `#` ativos de segurança).
- `/mdcu-seg threat-model [escopo]` — roda STRIDE sobre escopo definido; gera tabela e atualiza RSOP.
- `/mdcu-seg incidente` — inicia protocolo F0. Suspende MDCU ativo (preserva `_mdcu.md`).
- `/mdcu-seg auditoria` — abre/atualiza `rsop/seguranca.md`.
- `/mdcu-seg status` — resumo: `#` segurança ativos, última auditoria, incidentes abertos.
