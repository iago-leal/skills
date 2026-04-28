# Fluxograma — `mdcu-seg`

## Domínio 1 — Threat modeling (STRIDE)

```mermaid
flowchart TD
  Start([/mdcu-seg threat-model escopo]) --> Iter[Para cada componente/fluxo<br/>do escopo]
  Iter --> S[S — Spoofing<br/>identidade falsificável?]
  S --> T[T — Tampering<br/>alteração sem detecção?]
  T --> R[R — Repudiation<br/>log auditável?]
  R --> I[I — Information disclosure<br/>vazamento?]
  I --> D[D — Denial of service<br/>esgotar recurso?]
  D --> E[E — Elevation of privilege<br/>comum→admin?]
  E --> Tabela[Tabela:<br/>Categoria / Ameaça / Vetor / Mitigação / RSOP #]
  Tabela --> Trivial{Mitigação<br/>trivial?}
  Trivial -- Sim --> Stay[Fica só na tabela]
  Trivial -- Não --> NewIssue[Novo # no RSOP<br/>severidade mín. M;<br/>A se explorável em prod]
  Stay --> Dest{Em ciclo<br/>MDCU?}
  NewIssue --> Dest
  Dest -- Sim --> WriteMdcu[Escreve em _mdcu.md]
  Dest -- Não --> WriteSeg[Escreve em rsop/seguranca.md<br/>seção 'Threat models']
```

## Domínio 2 — F0 (contenção de incidente)

```mermaid
flowchart TD
  Trigger([Trigger: vazamento /<br/>acesso indevido /<br/>credencial exposta /<br/>logs anômalos]) --> Suspend[SUSPENDE MDCU ativo<br/>_mdcu.md PRESERVADO]
  Suspend --> E1[1. Identificação<br/>sinal / quando / por quem<br/>escopo / severidade L1-L4]
  E1 --> E2a[2a. Contenção curta<br/>min-h: isolar / desabilitar /<br/>bloquear / cortar tráfego]
  E2a --> E2b[2b. Contenção média<br/>h-dias: patch temporário /<br/>rotação de credenciais]
  E2b --> E3[3. Erradicação<br/>patch definitivo /<br/>rotação completa /<br/>remoção de IoC]
  E3 --> E4[4. Recuperação<br/>restaura serviço<br/>monitoramento reforçado<br/>valida ausência de IoC]
  E4 --> E5[5. Postmortem BLAMELESS<br/>linha do tempo factual<br/>causa raiz<br/>falhas de detecção<br/>ações estruturais]
  E5 --> Artifact[(rsop/soap/YYYY-MM-DD_incidente-ref.md<br/>SOAP estendido com Etapas F0)]
  Artifact --> Resume[MDCU retoma do<br/>_mdcu.md preservado<br/>ciente de novos #]
```

## Severidade de incidente (L1–L4)

```mermaid
flowchart LR
  L1[L1 — Baixa<br/>contida, sem exposição] --> Inc[Tratamento padrão F0]
  L2[L2 — Média<br/>exposição parcial] --> Inc
  L3[L3 — Alta<br/>exposição confirmada] --> Inc
  L4[L4 — Crítica<br/>ativa em produção] --> Inc

  classDef crit fill:#ffebee,stroke:#b71c1c;
  class L4 crit
```

## Domínio 3 — Auditoria trimestral

```mermaid
flowchart TD
  Start([/mdcu-seg auditoria]) --> Read[(rsop/seguranca.md)]
  Read --> Age{Última revisão<br/>> 90 dias?}
  Age -- Sim --> Flag[Sinaliza atraso<br/>obrigatória]
  Age -- Não --> Update[Atualiza seções]
  Flag --> Update
  Update --> Sec1[## Classificação de dados<br/>Restrito / Confidencial / Interno / Público]
  Sec1 --> Sec2[## Regime de auditoria<br/>SAST / DAST / Dep scan / Secret scan / Pentest / Code review]
  Sec2 --> Sec3[## Gestão de segredos<br/>onde moram / rotação / acesso]
  Sec3 --> Sec4[## Conformidade<br/>LGPD / HIPAA / PCI-DSS / DPO / base legal / retenção]
  Sec4 --> Sec5[## Histórico de incidentes<br/>últimos 12 meses]
  Sec5 --> Sec6[## Vulnerabilidades ativas<br/>espelho de lista_problemas.md filtrada]
  Sec6 --> Save[Atualiza data revisão<br/>+ próxima revisão = +90d]
```

## Gatilhos de delegação MDCU → mdcu-seg

```mermaid
flowchart LR
  F1MDCU[MDCU F1] -- '#A' segurança ativo --> Aud[/mdcu-seg auditoria]
  F3MDCU[MDCU F3] -- item 1 PII<br/>ou item 2 auth --> TM[/mdcu-seg threat-model]
  F5MDCU[MDCU F5] -- alternativa falha rastreio --> TM
  F6MDCU[MDCU F6] -- sinal de incidente --> F0[/mdcu-seg incidente<br/>IMEDIATO — suspende ciclo]
  Any[Qualquer fase] -- vazamento / breach /<br/>CVE crítico / LGPD --> Disp[delegar conforme contexto]
```
