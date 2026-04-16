# Dados base do sistema
- **Nome do projeto:** skills
- **Data de criação:** 2026-04-16 (início do RSOP — repo existe desde antes)
- **Última atualização:** 2026-04-16

## Identificação
- **Propósito:** Repositório de skills customizadas do Iago para Claude Code e agentes correlatos (Antigravity/Gemini). Fonte da verdade versionada em git; instalada em `~/.claude/skills/` via symlinks unidirecionais.
- **Responsáveis:** Iago Leal (único mantenedor).
- **Stakeholders:** o próprio Iago como usuário final das skills em outros projetos (medicina_leal, chagas, mcp_server, dicionario_os, ipm_coment).

## Contexto e território
- **Organização:** projeto pessoal.
- **Usuários:** Iago (em sessões Claude Code no macOS e possivelmente Antigravity para `claude_delegate`).
- **Sistemas adjacentes:** Claude Code CLI, Antigravity/Gemini (para `claude_delegate`), git/GitHub.
- **Restrições regulatórias ou legais:** não aplicável diretamente ao repo; as skills podem operar em projetos com LGPD (ex.: medicina_leal).

## Antecedentes
- **Stack:** apenas Markdown. Sem toolchain.
- **Repositório:** `/Users/iagoleal/Desktop/github_repos/skills/` (local; remoto a confirmar).
- **Arquitetura atual:** duas famílias de skill — `claude_delegate/` (orquestração) e `mdcu-framework/` (método). Distribuição via symlinks em `~/.claude/skills/`.
- **Histórico de decisões relevantes:**
  - Adoção do MDCU (Método de Desenvolvimento Centrado no Usuário) inspirado no MCCP da medicina de família.
  - Adoção do RSOP (Registro de Software Orientado por Problemas) inspirado no RMOP de Lawrence Weed.
  - Skill `commit-soap` fecha o loop MDCU → RSOP → commit.
  - 2026-04-16: introdução do MDCU v2 com dois gates obrigatórios (Segurança e Integração) + skills `teste-integrado` e `seguranca-dados`.
  - 2026-04-16: distribuição para `~/.claude/skills/` formalizada como symlinks unidirecionais.
- **Tratamentos anteriores:** migração informal de `MDCU/` (caixa alta) para `mdcu/` (lowercase) dentro de `mdcu-framework/`.
- **Sequelas:** nenhuma crítica. Projetos MDCU v1 em andamento não têm os campos novos dos artefatos 03/04/05 — migração opcional.

## Hábitos e condições crônicas
- **Padrões de deploy:** edição no repo propaga automaticamente via symlinks. Commits em PT-BR com prefixo de tipo.
- **Observabilidade:** nenhuma. Validação das skills é por observação em uso.
- **Padrões de incidentes:** não há histórico de incidente no repo.
- **Dependências críticas:** Claude Code precisa encontrar `~/.claude/skills/` íntegro. Se o repo for movido/renomeado, os symlinks quebram.

## Recursos e suporte
- **Equipe:** 1 (Iago).
- **Orçamento/infra:** zero — apenas disco local e GitHub.
- **Documentação existente:** `CLAUDE.md` na raiz do repo (atualizado em 2026-04-16), cada skill tem seu `SKILL.md` autoexplicativo.
