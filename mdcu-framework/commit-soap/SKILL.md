---
name: commit-soap
author: Iago Leal <github.com/iago-leal>
description: Gerador de mensagens de commit derivadas do SOAP da sessão atual. Lê a Avaliação (A) e o Plano (P) do SOAP registrado pela skill `rsop` e formata uma mensagem de commit que preserva o contexto cognitivo da sessão. ATIVE SEMPRE que o usuário digitar /commit-soap, pedir para commitar com contexto da sessão, encerrar uma sessão de trabalho com commit pendente, ou quando a skill `rsop` finalizar o registro de um SOAP e houver alterações a commitar. Também ative quando o usuário mencionar "commit com A+P", "commit com avaliação e plano", ou "commit da sessão". NÃO ative para commits intermediários triviais (formatação, typo) que não passaram por um ciclo SOAP.
---

# commit-soap — Commit derivado do SOAP da sessão

## Problema que resolve

Mensagens de commit convencionais capturam *o quê* foi alterado, mas não *por quê se chegou a essa conclusão* nem *o que se planejou a partir dela*. O contexto cognitivo da sessão se perde. Quem retoma o projeto depois de um intervalo precisa reconstruir o raciocínio lendo código, issues ou perguntando.

O commit-soap resolve isso: a mensagem de commit funciona como o A+P do SOAP — o mínimo suficiente para retomar o contexto sem reler todo o histórico. A cadeia de coerência do SOAP garante fidedignidade: o P é coerente com o A, que é coerente com o S e o O. Se precisar de mais detalhe, vai ao SOAP completo.

## Dependência

Lê `_soap.md` na raiz do projeto — arquivo temporário criado por `/rsop soap`. O SOAP deve estar preenchido antes de gerar o commit. Se não houver `_soap.md`, orientar o usuário a registrá-lo via `/rsop soap` antes de commitar.

## Quando usar

O commit-soap é o selo de encerramento da sessão. Deve ser usado para o commit de fechamento de sessão, não para cada alteração intermediária. O fluxo é:

1. Sessão de trabalho acontece.
2. SOAP é registrado via `/rsop soap` (obrigatório).
3. Commit de encerramento é gerado via `/commit-soap` a partir do A+P do SOAP.

## Formato da mensagem

```
A: [avaliação síntese — o que se entendeu nesta sessão]
P: [plano síntese — o que se decidiu/fez]
```

### Regras de formatação

- **Linha A:** síntese da Avaliação do SOAP. O que foi avaliado, hipótese principal, nível de resolução atingido. Uma a três frases. Ordem direta, sem redundância.
- **Linha P:** síntese do Plano do SOAP. O que foi feito, o que ficou pendente, próxima reavaliação. Uma a três frases. Ordem direta, sem redundância.
- **Sem Refs:** o SOAP é deletado após o commit. O A+P na mensagem é o registro suficiente; profundidade está no diff.
- **Primeira linha (A) deve ter no máximo 72 caracteres** para compatibilidade com `git log --oneline`. Se a avaliação for complexa, usar a primeira linha como resumo e detalhar no corpo.
- **Sem tipo técnico obrigatório** (feat/fix/refactor). Pode coexistir se o projeto usar Conventional Commits, mas não é exigido. O valor está no A+P, não na categoria.
- **Mesma disciplina de escrita do SOAP:** conciso sem perder informação relevante, sem redundância, ordem direta, dispensa de secundário.

### Formato com Conventional Commits (opcional)

Se o projeto adota Conventional Commits, o formato pode ser combinado:

```
fix: [resumo técnico curto]

A: [avaliação síntese]
P: [plano síntese]

Refs: rsop/soap/2026-04-15_performance.md
```

## Múltiplos problemas

Se o SOAP da sessão abordou múltiplos problemas, a mensagem lista cada um:

```
A: #3 N+1 confirmado na listagem de pedidos — piorou desde último deploy
A: #7 Timeout do serviço externo — intermitente, sem padrão claro ainda
P: #3 Eager loading em OrderQuery + índice composto — reavaliação pós-deploy
P: #7 Circuit breaker adicionado — monitorar por 48h antes de reclassificar

Refs: rsop/soap/2026-04-15_performance-e-timeout.md
```

## Consulta via git log

O formato permite buscas contextuais diretas no terminal:

- `git log --grep="A:"` — todas as avaliações.
- `git log --grep="P:"` — todos os planos.
- `git log --grep="#3"` — toda a história longitudinal do problema 3.
- `git log --grep="Refs: rsop"` — todos os commits com SOAP vinculado.

## Uso com `/commit-soap`

- `/commit-soap` — Lê o SOAP mais recente da sessão, extrai A+P, gera a mensagem formatada e exibe para revisão antes de commitar.
- `/commit-soap --dry-run` — Gera a mensagem mas não executa o commit. Útil para revisar.
- `/commit-soap --amend` — Reescreve a mensagem do último commit a partir do SOAP (caso o SOAP tenha sido atualizado após o commit).

## Operação

1. Ler `_soap.md` na raiz do projeto.
2. Extrair seções A e P.
3. Sintetizar cada seção seguindo as regras de formatação.
4. Montar a mensagem no formato especificado.
5. Exibir ao usuário para revisão e confirmação.
6. Executar `git commit -m "$(mensagem)"` — **sem linha `Co-Authored-By`**. Esta é uma mensagem de autoria do projeto; não adicionar atribuição ao modelo.
7. Após commit confirmado: deletar `_soap.md`.

Se não houver `_soap.md`:
- Informar: "Não há SOAP da sessão atual. Registre via `/rsop soap` antes de commitar."
- Não gerar commit com mensagem inventada.
