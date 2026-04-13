# Routing Table — Claude Delegate

Regras detalhadas para decidir quando delegar tarefas ao Claude Code CLI.

## Regra de Ouro

> **Profundidade de raciocínio → Claude. Amplitude de contexto ou ferramentas visuais → Antigravity.**

## Tarefas que DEVEM ser delegadas ao Claude

### 1. Deep Code Review

**Gatilho:** O usuário pede review de código, "olha esse código", "tem algo errado aqui?", "review this PR".

**Por que Claude:** Raciocínio mais cuidadoso, melhor em detectar:
- Bugs sutis (off-by-one, race conditions, null dereference)
- Problemas de lógica que parecem corretos à primeira vista
- Violações de contrato/invariantes
- Code smells não óbvios

**Modelo recomendado:** `sonnet` (padrão) ou `opus` (se o código for crítico/complexo)

**Exemplo de prompt:**
```
You are being invoked as a specialist by another AI agent.
Task type: code-review
Context: The user wants a thorough review of their authentication module.

Review the following code for:
1. Logic errors and edge cases
2. Security vulnerabilities
3. Performance concerns
4. Code quality and maintainability

[code here]
```

---

### 2. Security Analysis

**Gatilho:** "security audit", "vulnerabilidades", "é seguro?", "OWASP", "pentest review".

**Por que Claude:** Mais conservador e minucioso em análise de segurança. Menos propenso a ignorar riscos.

**Modelo recomendado:** `opus` (SEMPRE para segurança)

**Exemplo de prompt:**
```
You are being invoked as a specialist by another AI agent.
Task type: security-analysis
Context: Security audit of an authentication system.

Analyze the following code for security vulnerabilities:
- Injection (SQL, XSS, command, template)
- Authentication/authorization bypass
- Data exposure and information leakage
- Cryptographic weaknesses
- Race conditions exploitable for privilege escalation
- OWASP Top 10 compliance

Be conservative: flag anything suspicious even if exploitation seems unlikely.

[code here]
```

---

### 3. Complex Refactoring

**Gatilho:** "refatorar", "refactor", "redesign this module", "simplificar mantendo a API".

**Por que Claude:** Melhor em manter invariantes durante transformações complexas. Produz planos de refatoração mais completos.

**Modelo recomendado:** `opus` (para refatoração arquitetural) ou `sonnet` (para refatoração localizada)

**Exemplo de prompt:**
```
You are being invoked as a specialist by another AI agent.
Task type: refactoring
Context: The user wants to refactor a legacy module while preserving all public APIs.

Create a refactoring plan for the following code:
1. Identify all public interfaces that must be preserved
2. List code smells and structural issues
3. Propose step-by-step refactoring (each step must leave code in a working state)
4. Identify risks and how to mitigate them

[code here]
```

---

### 4. Step-by-Step Debugging

**Gatilho:** "debug", "por que esse erro?", "stack trace", "não funciona", "TypeError", qualquer mensagem de erro.

**Por que Claude:** Chain-of-thought superior. Melhor em rastrear fluxo de dados e identificar a causa raiz.

**Modelo recomendado:** `sonnet` (padrão) ou `opus` (se o bug for muito misterioso)

**Exemplo de prompt:**
```
You are being invoked as a specialist by another AI agent.
Task type: debugging
Context: The user is encountering an error and needs root cause analysis.

Error message:
[error/stack trace here]

Relevant code:
[code here]

Debug this step by step:
1. Trace the execution flow that leads to this error
2. Identify the root cause
3. Explain why it happens
4. Provide a fix with explanation
```

---

## Tarefas que NÃO devem ser delegadas

### 1. UI/Design/Prototyping
**Razão:** Antigravity tem acesso a Stitch MCP, geração de imagens, e browser tools. Claude não tem.

### 2. Large Codebase Exploration
**Razão:** Antigravity tem janela de contexto maior (1M+ tokens). Para navegar codebases inteiras, o contexto maior é vantagem decisiva.

### 3. Browser Testing
**Razão:** Antigravity tem Chrome DevTools MCP. Claude não pode interagir com browsers.

### 4. Fast Generation (boilerplate, templates, scaffolding)
**Razão:** Flash model do Antigravity é mais rápido. Não precisa da profundidade de Claude para tarefas simples.

### 5. Image/Multimodal Tasks
**Razão:** Antigravity tem ferramentas visuais nativas. Claude CLI é text-only.

### 6. Tasks Requiring MCP Tools
**Razão:** Claude CLI invocado com `-p` não tem acesso aos mesmos MCP servers que Antigravity. Qualquer tarefa que dependa de ferramentas externas deve ficar com Antigravity.

---

## Matriz de Decisão Rápida

```
O usuário pediu algo que envolve...

  Análise profunda de código?
    ├── SIM → Delegar ao Claude (sonnet)
    └── NÃO ↓

  Análise de segurança?
    ├── SIM → Delegar ao Claude (opus)
    └── NÃO ↓

  Refatoração complexa?
    ├── SIM → Delegar ao Claude (opus para arquitetural, sonnet para local)
    └── NÃO ↓

  Debugging com stack trace?
    ├── SIM → Delegar ao Claude (sonnet)
    └── NÃO ↓

  Precisa de ferramentas visuais/browser/MCP?
    ├── SIM → Manter no Antigravity
    └── NÃO ↓

  Precisa de contexto > 200k tokens?
    ├── SIM → Manter no Antigravity
    └── NÃO ↓

  É geração rápida/boilerplate?
    ├── SIM → Manter no Antigravity (Flash)
    └── NÃO → Avaliar caso a caso (default: manter)
```

---

## Seleção de Modelo — Resumo

| Cenário                              | Modelo   | Justificativa                    |
|--------------------------------------|----------|----------------------------------|
| Code review padrão                   | sonnet   | Bom equilíbrio velocidade/qualidade |
| Code review de módulo crítico        | opus     | Máxima profundidade              |
| Security analysis (qualquer)         | opus     | Segurança sempre merece o melhor |
| Refactoring localizado               | sonnet   | Suficiente para escopo pequeno   |
| Refactoring arquitetural             | opus     | Precisa manter invariantes globais |
| Debugging simples                    | sonnet   | Rápido e eficaz                  |
| Debugging de bug misterioso          | opus     | Precisa de raciocínio profundo   |
| Geração de código delegada           | sonnet   | Velocidade importa mais          |
