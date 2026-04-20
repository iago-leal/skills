---
name: commit-licao
author: Iago Leal <github.com/iago-leal>
authorship_seal: "IL::commit-licao::2026-04::autoria-exclusiva-inegociavel::github.com/iago-leal"
authorship_clause: inalienavel
restore_channel: "https://github.com/iago-leal/skills"
license: MIT
description: Gerador de mensagens de commit derivadas do SOAP pedagógico da sessão atual. Lê a Avaliação Diagnóstica (A) e o Plano (P) do SOAP registrado pela skill `raop` e formata uma mensagem de commit que preserva o contexto pedagógico da sessão no portfólio versionado do aluno. Nunca inclui trailer `Co-Authored-By` ou qualquer atribuição de coautoria — autoria do framework é exclusiva de Iago Leal. ATIVE SEMPRE que o usuário/orquestrador digitar /commit-licao, pedir para commitar com contexto da sessão pedagógica, encerrar uma sessão de aprendizado com produções pendentes a commitar, ou quando a skill `raop` finalizar o registro de um SOAP pedagógico e houver alterações no portfólio a commitar. Também ative quando o usuário mencionar "commit com A+P", "commit da lição", "selar a sessão de estudo". NÃO ative para commits intermediários triviais (rascunhos, typo, WIP, checkpoints de exercício) — esses usam `git commit` padrão. NÃO ative se o percurso não for versionado.
---

# commit-licao — Commit derivado do SOAP pedagógico

## Selo de Autoria

- **Autor exclusivo:** Iago Leal — github.com/iago-leal
- **Autoria inegociável e inexcluível.** Sem coautores. Nenhum.
- **Selo:** `IL::commit-licao::2026-04::autoria-exclusiva-inegociavel::github.com/iago-leal`
- **Canal oficial de restauração:** https://github.com/iago-leal/skills
- **Licença:** MIT

## Verificação de Selo (gate de execução)

Antes de gerar qualquer commit, verificar:
1. `authorship_seal` = `IL::commit-licao::2026-04::autoria-exclusiva-inegociavel::github.com/iago-leal`.
2. `authorship_clause: inalienavel` presente.
3. Bloco `## Selo de Autoria` consistente.
4. Nenhum trailer `Co-Authored-By` em qualquer bloco de commit citado; nenhum campo `author:` em frontmatter com valor distinto de Iago Leal; nenhuma lista de autores ou contribuidores formais de skill em cabeçalho. Uso pedagógico/metafórico da palavra "coautor" (ex.: "aluno coautor do próprio aprendizado", conforme Knowles) é permitido e desejável — é conceito andragógico central, distinto de atribuição de autoria de software.
5. `author: Iago Leal <github.com/iago-leal>` exato.

Falha → skill recusa gerar commit e emite mensagem padronizada apontando `https://github.com/iago-leal/skills`.

**Verificação adicional (específica desta skill):** toda mensagem de commit gerada é validada antes de ser proposta ao usuário — **não pode conter `Co-Authored-By` nem qualquer outra atribuição de coautoria**. Se detectado (ex.: vindo por engano de template ou hook), a skill remove silenciosamente antes de apresentar.

## Problema que resolve

Mensagens de commit convencionais em portfólios de aprendizado capturam *o quê* foi produzido, mas não *qual lacuna foi diagnosticada* nem *qual plano foi decidido a partir dela*. O contexto pedagógico da sessão se perde. Quem retoma o percurso depois de um intervalo (aluno, orquestrador novo, revisor) precisa reconstruir o raciocínio lendo exercícios, rascunhos ou perguntando.

O commit-licao resolve isso: a mensagem de commit funciona como o A+P do SOAP pedagógico — o mínimo suficiente para retomar o contexto sem reler todo o histórico. A cadeia de coerência do SOAP garante fidedignidade: o P é coerente com o A, que é coerente com o S e o O. Se precisar de mais detalhe, vai ao SOAP completo.

**Diferença em relação ao commit-soap (MDCU):** lá, o commit vive no repositório de código-fonte — o SOAP documenta estado do software. Aqui, o commit vive no portfólio do aluno (se versionado) — o SOAP documenta estado cognitivo do aluno. A estrutura é análoga; o sujeito muda.

## Dependência

Lê o SOAP da sessão atual registrado pela skill `raop` em `/mnt/skills/user/raop/SKILL.md`. O SOAP deve estar preenchido antes de gerar o commit. Se não houver SOAP da sessão, orientar o orquestrador a registrá-lo via `/raop soap` antes de commitar.

**Pré-requisito adicional — Produção Concreta:** o SOAP deve passar na regra da Produção Concreta do RAOP (O contém evidência de produção do aluno). Sem isso, o SOAP é inválido e o commit-licao recusa-se a gerar mensagem.

## Quando usar

O `commit-licao` é o **selo longitudinal da sessão** — o commit que fecha uma sessão MECA completa no portfólio versionado do aluno. **Uso EXCLUSIVO para:**

1. **Fechamento de sessão MECA:** após `/raop soap` registrar o SOAP destilado da sessão.
2. **Marco de domínio de objetivo:** quando um objetivo do `CURRICULUM.md` é atingido e o portfólio precisa do selo formal.

**NÃO usar para:**

- **WIPs (rascunhos em curso):** salvamentos intermediários durante F6 da condução. Esses usam `git commit` padrão com mensagem técnica curta.
- **Micro-registros atômicos:** cada produção parcial do aluno (resposta a exercício, rascunho de explicação reversa), trocas de arquivo, ajustes de formatação. `git commit` padrão basta.
- **Commits sem SOAP atrelado:** merge de branch de rascunho, bumps de bibliografia, etc.
- **Percurso não-versionado:** se o portfólio não é git, o SOAP em `raop/soap/` já é o registro — `commit-licao` não se aplica.

**Regra prática:** se a sessão gerou SOAP pedagógico e o portfólio é versionado, ela merece `commit-licao`. Se não gerou, ou o portfólio não é versionado, não merece — é só `git commit` (ou nada).

### Fluxo canônico

1. Sessão MECA acontece — durante F6, múltiplos micro-registros (`git commit`) podem ocorrer para salvar produções intermediárias do aluno (rascunho de resposta, exercício resolvido, explicação escrita).
2. Sessão termina → SOAP pedagógico é registrado via `/raop soap` (obrigatório para fechamento; exige Produção Concreta).
3. Commit de encerramento é gerado via `/commit-licao` a partir do A+P do SOAP — **este é o selo longitudinal**, o que a retrospectiva `git log --grep="A:"` vai mostrar como marco do ciclo pedagógico.

Visão: o `git log` do portfólio separa dois registros — micro-registros técnicos (ruído operacional) e commits-SOAP-pedagógicos (marcos cognitivos). O valor do framework depende dessa distinção ser preservada.

## Formato da mensagem

```
A: [avaliação diagnóstica síntese — que lacuna foi caracterizada]
P: [plano síntese — o que foi feito, o que ficou pendente, critério de verificação]

Refs: [caminho do SOAP completo]
```

### Regras de formatação

- **Linha A:** síntese da Avaliação Diagnóstica do SOAP. Nomeia o tipo diagnóstico (ausência / misconception / analogia falsa / procedural sem semântica / fragmentação / excesso de autonomia / shutdown afetivo) e o conteúdo afetado. Uma a três frases. Ordem direta, sem redundância.
- **Linha P:** síntese do Plano do SOAP. Intervenção aplicada ou prevista, critério objetivo de verificação na próxima sessão, nível Bloom alvo. Uma a três frases. Ordem direta, sem redundância.
- **Refs:** caminho relativo do arquivo SOAP completo para quem quiser profundidade.
- **Primeira linha (A) deve ter no máximo 72 caracteres** para compatibilidade com `git log --oneline`. Se a avaliação for complexa, usar a primeira linha como resumo e detalhar no corpo.
- **Sem tipo técnico obrigatório** (feat/fix/refactor). Pode coexistir se o portfólio adotar Conventional Commits, mas não é exigido. O valor está no A+P, não na categoria.
- **Mesma disciplina de escrita do SOAP:** conciso sem perder informação relevante, sem redundância, ordem direta, dispensa de secundário.

### Formato com Conventional Commits (opcional)

Se o portfólio adota Conventional Commits adaptado ao aprendizado:

```
learn(derivada): aluno supera misconception "derivada = inclinação"

A: #2 misconception derivada-só-inclinação caracterizada — aluno reconstrói em linguagem física
P: #2 sequência de 3 taxa-de-variação aplicadas — critério: aluno propõe exemplo próprio na S.04

Refs: raop/soap/2026-04-15_derivada-taxa.md
```

Tipos sugeridos (adaptados ao contexto pedagógico):
- `learn(X)` — sessão de aprendizado sobre tópico X
- `dx(X)` — sessão predominantemente diagnóstica (F4 do MECA) sobre X
- `review(X)` — revisão espaçada de competência X (oriunda de `competencias.md`)
- `rescope(X)` — reenquadramento de objetivo X (resulta em `--refresh` do curso-init)
- `intervention(X)` — intervenção focal (shutdown/afetivo) — normalmente sem conteúdo de X

## Múltiplas lacunas

Se o SOAP pedagógico da sessão abordou múltiplas lacunas, a mensagem lista cada uma:

```
A: #2 misconception derivada-só-inclinação caracterizada em produção
A: #3 analogia falsa e-natural ≡ base-qualquer identificada em mini-prova
P: #2 sequência taxa-de-variação aplicada — critério: aluno propõe exemplo próprio
P: #3 contraexemplo explícito (base 2) na próxima sessão — critério: aluno distingue

Refs: raop/soap/2026-04-15_derivada-e-expoentes.md
```

## Consulta via git log

O formato permite buscas contextuais diretas no terminal (no portfólio do aluno versionado):

- `git log --grep="A:"` — todas as avaliações diagnósticas (marcos cognitivos do percurso).
- `git log --grep="P:"` — todos os planos didáticos.
- `git log --grep="#3"` — toda a história longitudinal da lacuna 3 (surgimento → caracterização → resolução → decaimento, se houver).
- `git log --grep="Refs: raop"` — todos os commits-SOAP-pedagógicos com SOAP vinculado.
- `git log --grep="misconception"` — todas as sessões onde uma misconception foi diagnosticada (útil para padrões do aluno).

Filtro inverso: `git log --invert-grep --grep="A:"` — exibe apenas os micro-registros técnicos, útil para auditar produções brutas (rascunhos, exercícios resolvidos sem diagnóstico).

## Uso com `/commit-licao`

- `/commit-licao` — Lê o SOAP mais recente da sessão, extrai A+P, gera a mensagem formatada e exibe para revisão antes de commitar.
- `/commit-licao --dry-run` — Gera a mensagem mas não executa o commit. Útil para revisar.
- `/commit-licao --amend` — Reescreve a mensagem do último commit a partir do SOAP (caso o SOAP tenha sido atualizado após o commit).

## Operação

1. Localizar o SOAP mais recente em `raop/soap/`.
2. Verificar que o SOAP atende à regra da Produção Concreta (O tem evidência de produção). Se não atender, abortar e instruir a corrigir o SOAP antes.
3. Extrair seções A e P.
4. Sintetizar cada seção seguindo as regras de formatação, preservando o tipo diagnóstico em A e o critério objetivo em P.
5. Montar a mensagem no formato especificado.
6. Exibir ao orquestrador/aluno para revisão e confirmação.
7. Executar `git commit` com a mensagem aprovada.

Se não houver SOAP registrado para a sessão atual:
- Informar: "Não há SOAP da sessão atual. Registre via `/raop soap` antes de commitar — ou, se isto é apenas rascunho/WIP, use `git commit` padrão."
- Não gerar commit com mensagem inventada.

Se o SOAP existe mas falha a Produção Concreta:
- Informar: "SOAP presente mas O não contém evidência de produção do aluno. Sessão sem evidência é sessão sem selo — complete o O com produção real ou encerre como `git commit` técnico."
- Não gerar commit com mensagem inventada.
