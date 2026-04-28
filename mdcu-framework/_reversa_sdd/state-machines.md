# Máquinas de estado — mdcu-framework

> Gerado pelo **Reversa Detective** em 2026-04-27
> O framework não tem entidades CRUD com `status:` em coluna. As máquinas a seguir são **fluxos de estado prescritivos** sobre artefatos, contadores e protocolos.

---

## SM-1 — Sessão MDCU (`_mdcu.md`)

```mermaid
stateDiagram-v2
  [*] --> Created: /mdcu
  Created: _mdcu.md criado<br/>F1 ativada<br/>contador 0/2
  Created --> InterruptedF1: ARCHITECTURE.md ausente
  InterruptedF1 --> Created: /project-init concluído<br/>(retorna F1 do início)
  Created --> Active: gatilho conformidade OK<br/>F1 → F2
  Active --> Active: F2 → F3 → F4 → F5 → F6
  Active --> Suspended: /mdcu-seg incidente<br/>(F0 prioridade absoluta)
  Suspended --> Active: incidente resolvido<br/>(_mdcu.md preservado)
  Active --> Aborted: contador atinge 2/2<br/>DISJUNTOR
  Aborted --> Active: usuário decide<br/>(libera novo ciclo)<br/>OBS: contador NÃO reseta
  Active --> Closed: /mdcu fechar<br/>/rsop soap → /commit-soap
  Closed --> [*]: _mdcu.md DELETADO
```

**Estados:**
- `Created`: arquivo recém-criado, F1 não-completa
- `InterruptedF1`: gate `ARCHITECTURE.md` falhou
- `Active`: ciclo em curso, fase ∈ {F1..F6}
- `Suspended`: F0 em curso (preserva `_mdcu.md`)
- `Aborted`: disjuntor 2/2 disparado
- `Closed`: SOAP + commit emitidos, arquivo será deletado

---

## SM-2 — Contador do Disjuntor (F6)

```mermaid
stateDiagram-v2
  [*] --> C0: novo /mdcu
  C0: 0/2 — sem reenquadramento
  C0 --> C1: reenquadrar em F6
  C1: 1/2 — primeiro reenquadramento
  C1 --> C2: reenquadrar em F6
  C2: 2/2 — TERMINANTEMENTE PROIBIDO<br/>prosseguir sozinho
  C2 --> ExitProtocol: aciona exit protocol
  ExitProtocol: aguarda decisão do usuário<br/>5 campos obrigatórios:<br/>tentativas / falhas / próximo / gap / opções
  ExitProtocol --> [*]: usuário decide<br/>(reset apenas com novo /mdcu)
```

**Constraints:**
- Reset **apenas** com novo `/mdcu` (criação de novo `_mdcu.md`).
- Decisão do usuário após 2/2 NÃO reseta o contador da sessão atual.
- Exit protocol tem formato fixo de 5 campos (mdcu/SKILL.md:319-336).

---

## SM-3 — Ciclo de vida de um problema RSOP

```mermaid
stateDiagram-v2
  [*] --> Proposed: detectado em<br/>F4 do MDCU OU<br/>STRIDE do mdcu-seg
  Proposed --> Active: /rsop revisar (ou criação imediata)<br/>entra em lista_problemas.md<br/>com prefixo [A]/[M]/[B]
  Active --> Active: evolução de descrição<br/>(sintoma → hipótese → diagnóstico)<br/>via SOAPs sucessivos
  Active --> Reclassified: /rsop revisar<br/>muda severidade
  Reclassified --> Active
  Active --> Passive: /rsop revisar<br/>(quando resolvido)<br/>migra para passivos.md<br/>com Fechado por / em / Reativável?
  Passive --> Active: /rsop regressao N<br/>(reabertura)<br/>nota 'reaberto em [data] — ver SOAP'
  Passive --> [*]: arquivo morto permanente

  note right of Active
    Vulnerabilidades de segurança:
    SEMPRE entram (mesmo se corrigidas no dia)
    Severidade mín [M]
    Ao migrar, Reativável? = sim — vigiar recorrência
  end note
```

**Constraints chave:**
- `#` é estável; **nunca reciclado** entre estados.
- Bug pontual resolvido no mesmo dia **não entra** na lista — fica só no SOAP.
- **Exceção segurança:** vulnerabilidade entra mesmo no mesmo dia.
- Consulta a `Passive`: só por suspeita de regressão ou pedido explícito.

---

## SM-4 — Protocolo F0 de Incidente (mdcu-seg)

```mermaid
stateDiagram-v2
  [*] --> Triggered: vazamento / acesso indevido /<br/>credencial exposta / logs anômalos /<br/>/mdcu-seg incidente
  Triggered --> Identification: 1. Identificação<br/>sinal / quando / por quem<br/>escopo / severidade L1-L4
  Identification --> ContainedShort: 2a. Contenção curta<br/>min-h: isolar / desabilitar /<br/>bloquear / cortar tráfego
  ContainedShort --> ContainedLong: 2b. Contenção média<br/>h-dias: patch temporário /<br/>rotação de credenciais
  ContainedLong --> Eradicated: 3. Erradicação<br/>patch definitivo /<br/>rotação completa /<br/>remoção de IoC
  Eradicated --> Recovered: 4. Recuperação<br/>monitoramento reforçado<br/>valida ausência de IoC
  Recovered --> Postmortem: 5. Postmortem (BLAMELESS)<br/>linha do tempo factual<br/>causa raiz<br/>ações estruturais
  Postmortem --> [*]: SOAP-incidente registrado<br/>MDCU retoma do _mdcu.md preservado

  note right of Triggered
    SUSPENDE imediatamente
    o ciclo MDCU em andamento
    (preserva _mdcu.md intacto)
  end note
```

**Severidade do incidente** (escala paralela a `[A]/[M]/[B]`, **não confundir**):
- `L1` Baixa, contida
- `L2` Média, parcial
- `L3` Alta, confirmada
- `L4` Crítica, ativa em produção

---

## SM-5 — Estado do `ARCHITECTURE.md`

```mermaid
stateDiagram-v2
  [*] --> Absent: projeto novo
  Absent --> Initialized: /project-init<br/>(7 fases concluídas)
  Initialized: ARCHITECTURE.md presente<br/>+ manifesto + lock<br/>+ commit inicial
  Initialized --> Refreshed: /project-init --refresh<br/>(re-executa fases 2-6)<br/>edita in place + ADR/changelog
  Refreshed --> Initialized
  Initialized --> Validated: /project-init --check<br/>(4 pontos: existe? lock? bate? guardrails?)
  Validated --> Initialized: PASS
  Validated --> Drifting: FAIL — divergência<br/>guardrails violados ou<br/>lock dessincronizado
  Drifting --> Refreshed: --refresh OU<br/>regenerar lock
```

**Note:** o estado `Drifting` é prescritivo, não enforced — depende do agente respeitar o resultado de `--check`.

---

## SM-6 — Auditoria de segurança (`rsop/seguranca.md`)

```mermaid
stateDiagram-v2
  [*] --> Created: /mdcu-seg auditoria<br/>(primeira vez)
  Created: data revisão = hoje<br/>próxima = hoje + 90d
  Created --> Current: dentro de 90d
  Current --> Overdue: > 90d sem revisão
  Overdue --> Current: /mdcu-seg auditoria<br/>(revisão executada)
  Current --> StructuralEvent: nova integração /<br/>mudança stack /<br/>nova regulação /<br/>incidente recente
  StructuralEvent --> Current: revisão executada<br/>(fora do trimestral)
```

**Constraints:**
- Período fixo: **90 dias** (mdcu-seg/SKILL.md:202).
- Sem revisão = "ficção administrativa" — citação literal.
- Eventos estruturais disparam revisão fora do calendário.

---

## SM-7 — Mensagem de commit (commit-soap vs. micro-commit)

```mermaid
stateDiagram-v2
  [*] --> Choice: hora de commitar
  Choice --> CheckSoap: /commit-soap solicitado
  Choice --> StandardCommit: WIP / typo / formatação /<br/>checkpoint / merge intermediário
  CheckSoap --> SoapMissing: nenhum SOAP da sessão
  CheckSoap --> SoapPresent: SOAP encontrado em rsop/soap/
  SoapMissing --> [*]: ABORTA com mensagem fixa<br/>(não inventa)
  SoapPresent --> Drafted: extrai A+P → formata<br/>(linha A ≤ 72 chars)<br/>(múltiplos # → repete A:/P:)<br/>(adiciona Refs:)
  Drafted --> Reviewed: exibe ao usuário
  Reviewed --> Committed: confirma → git commit
  Reviewed --> Cancelled: rejeita
  Reviewed --> DryRun: --dry-run → mostra sem commit
  Reviewed --> Amended: --amend → reescreve último commit
  StandardCommit --> [*]: git commit padrão<br/>(sem A:/P:/Refs:)
  Committed --> [*]
  Cancelled --> [*]
  DryRun --> [*]
  Amended --> [*]
```

**Audit:**
- Commits "Committed" são marcos cognitivos (`git log --grep="A:"`).
- Commits "StandardCommit" são ruído operacional (`git log --invert-grep --grep="A:"`).

---

## Achados transversais sobre estado

1. **Disjuntor 2/2 (SM-2) é o único contador persistente** do framework. Vive no header do `_mdcu.md` como string `Tentativas de Reenquadramento: N/2`. Sua persistência é frágil: depende do agente reler o arquivo e respeitar o número.

2. **Estado de "suspensão" do MDCU (SM-1)** é peculiar: o `_mdcu.md` é preservado intacto, mas o agente precisa "lembrar" que está suspenso. Não há lock file ou flag — é estado implícito mantido pela convenção do mdcu-seg de retomar.

3. **`Drifting` em SM-5** revela a tese central do framework: contratos técnicos exigem **vigilância ativa**. `--check` é o "exame de rotina". Sem o exame, o contrato vira ficção.

4. **Reabertura em SM-3** é deliberadamente bidirecional. Outros sistemas tratariam "fechado" como estado terminal — aqui é arquivo morto **reativável**, especialmente para segurança (`reativável? sim — vigiar recorrência`).

5. **Postmortem em SM-4** é estado **blameless por design** — restrição explícita ao tipo de prosa permitida. Único exemplo no framework de regra sobre **estilo do conteúdo**, não sobre estrutura.
