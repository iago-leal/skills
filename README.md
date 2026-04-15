# MDCU Framework — Método de Desenvolvimento Centrado no Usuário

**Autor:** Iago Leal — [github.com/iago-leal](https://github.com/iago-leal)

Framework de desenvolvimento de software inspirado no **Método Clínico Centrado na Pessoa (MCCP)** da Medicina de Família e Comunidade. Três skills interligadas para Claude Code que compõem um workflow de raciocínio, registro e commit.

## Workflow

```
MDCU (fases 1–5)  →  Execução  →  RSOP (SOAP)  →  commit-soap (A+P)
```

## Skills

Localizadas em [`mdcu-framework/`](mdcu-framework/):

- **[`mdcu`](mdcu-framework/mdcu/)** — Método de raciocínio. 7 fases: Preparação, Escuta, Exploração, Avaliação, Plano, Execução, Reflexão.
- **[`rsop`](mdcu-framework/rsop/)** — Registro de Software Orientado por Problemas. Prontuário do software. 3 componentes: dados base, lista de problemas, SOAP.
- **[`commit-soap`](mdcu-framework/commit-soap/)** — Commit derivado do SOAP da sessão. Sela a sessão com Avaliação + Plano.

## Instalação

Copie cada pasta de skill para o diretório de skills do Claude:

```bash
cp -R mdcu-framework/mdcu        ~/.claude/skills/
cp -R mdcu-framework/rsop        ~/.claude/skills/
cp -R mdcu-framework/commit-soap ~/.claude/skills/
```

Ou para o escopo do projeto, em `.claude/skills/` na raiz do repo onde forem usadas.

## Outras skills neste repositório

- [`claude_delegate/`](claude_delegate/) — skill auxiliar de delegação (não faz parte do framework MDCU).

## Licença

MIT
