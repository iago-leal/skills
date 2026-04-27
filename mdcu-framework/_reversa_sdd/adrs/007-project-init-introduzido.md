# ADR-007 — `project-init` introduzido como pré-requisito bloqueante do MDCU

- **Status:** Aceito
- **Data:** 2026-04-19
- **Commit-fonte:** `75398df` 🟡 (mensagem genérica "atualiza framework && adiciona project init"; conteúdo extraído do `MANIFEST.md` patches 5 e 6)
- **Confiança:** 🟡 INFERIDO (mensagem do commit é vaga; intenção reconstituída a partir do MANIFEST + corpo das skills)

## Contexto

Antes do `project-init`:
- O MDCU iniciava direto em F1 sem verificar se havia contrato técnico do projeto (stack, lock file, guardrails).
- Cada nova sessão de IA reinventava convenções.
- Upgrades silenciosos de dependência quebravam builds sem aviso (sem lock determinístico).
- Risco de "decisões em F5/F6 viram débito de arquitetura".

Em paralelo, o usuário estava aplicando o framework em projetos reais e enfrentou esses problemas (provável — não há SOAP específico no histórico que confirme, mas a especificidade do `project-init` sugere experiência empírica).

## Decisão

Criar skill `project-init` com 7 fases para:
1. Estabelecer `ARCHITECTURE.md` formal na raiz do projeto-cliente.
2. Definir gerenciador de pacotes + lock file determinístico (regra vinculante).
3. Registrar guardrails como invariantes não-negociáveis.
4. Realizar commit inicial canônico.

E adicionar **gatilho de conformidade** no MDCU F1: se `ARCHITECTURE.md` não existe, **interrompe** o fluxo e invoca `/project-init` antes de avançar para F2.

A "Gestão Determinística de Dependências" (8 regras) ganha tratamento de seção própria.

## Consequências
- ✅ Anamnese ↔ exame físico: ordem clínica preservada (contrato antes de escuta).
- ✅ Reprodutibilidade obrigatória (lock sempre commitado).
- ✅ Guardrails formalizados — violação em F5/F6 detectada.
- ⚠️ MDCU ganha um pré-requisito que pode frustrar usuários impacientes (a skill é vinculante).
- ⚠️ `project-init` é a skill mais longa do framework (278 linhas) — maior superfície de manutenção.
- ⚠️ Skill criada **sem** arquivo `version` no frontmatter (gap D-001).
