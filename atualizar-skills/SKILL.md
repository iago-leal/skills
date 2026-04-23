---
name: atualizar-skills
description: Puxa a versão mais recente das skills do Claude Code do repositório canônico `https://github.com/iago-leal/skills` E de external upstreams declarados em `external-upstreams.conf` (ex: `anthropics/skills` para receber updates do `skill-creator`), e reconcilia `~/.claude/skills/` com esses repos. Fontes declaradas são a verdade; divergências locais (diretório real onde deveria ter symlink, symlink errado, skill removida upstream) são corrigidas sem pergunta. ATIVE SEMPRE que o usuário digitar `/atualizar-skills`, `/sync-skills`, ou pedir para "atualizar skills", "sincronizar skills", "puxar últimas skills", "buscar skills do github", "git pull das skills", "git pull nas skills do claude-code". Ative proativamente quando o usuário mencionar que editou/commitou uma skill no GitHub ou em outra máquina e quer a versão nova localmente. NÃO ative para criar skills novas do zero, nem para `git pull` genérico em repositórios que não sejam um dos upstreams de skills.
---

# atualizar-skills — Pull do Repositório Canônico + External Upstreams

## Fundamento

Duas fontes de verdade:

1. **Canônica (obrigatória):** `https://github.com/iago-leal/skills` — skills do próprio usuário. Clone em `/Users/iagoleal/Desktop/github_repos/skills`.
2. **External upstreams (opcional):** skills de terceiros (ex: `anthropics/skills` → `skill-creator`) listadas em `external-upstreams.conf`. Cada upstream vira um clone sparse em `/Users/iagoleal/Desktop/github_repos/<clone_name>` e cada skill vira um symlink em `~/.claude/skills/<basename>`.

`~/.claude/skills/` expõe tudo isso ao harness via symlinks. Operação por upstream é idêntica: pull + reconciliação por symlink. Diretório real local onde deveria haver symlink gerenciado é substituído (backup técnico em `~/.claude/skills-backups/<nome>-<timestamp>`).

## Formato do `external-upstreams.conf`

```bash
EXTERNAL_SKILLS=(
  # <clone_name>|<remote_url>|<branch>|<path_in_repo>
  "anthropics-skills|https://github.com/anthropics/skills.git|main|skills/skill-creator"
)
```

- `clone_name` — nome do dir em `/Users/iagoleal/Desktop/github_repos/` (sem o prefixo)
- `path_in_repo` — caminho do diretório da SKILL dentro do clone; `basename` vira o nome local em `~/.claude/skills/`
- Múltiplas skills do mesmo repo: repita a linha com `path_in_repo` diferente (o pull é feito uma vez por clone).
- Arquivo opcional. Ausência = pular o passo 5b e sincronizar só o canônico.

---

## Caminhos

- **Remoto:** `https://github.com/iago-leal/skills.git`
- **Clone local:** `/Users/iagoleal/Desktop/github_repos/skills`
- **Diretório de skills ativas:** `/Users/iagoleal/.claude/skills`

---

## Execução

```bash
bash /Users/iagoleal/.claude/skills/atualizar-skills/sync.sh
```

O script:

1. Valida que o clone canônico existe. Se não, aborta com instrução de `git clone`.
2. Aborta se há alterações não-commitadas no clone (o usuário resolve manualmente — não fazemos stash automático porque isso esconde trabalho em andamento).
3. `git fetch origin` + `git pull --rebase origin main` no clone canônico.
4. Descobre todas as skills do repo canônico (diretórios contendo `SKILL.md`, exceto dentro de `.git/`).
5. Para cada skill do repo canônico, garante que `~/.claude/skills/<nome>` é symlink apontando para o caminho canônico no clone. Casos:
   - não existe → cria symlink
   - já é symlink correto → nada a fazer
   - symlink apontando pra lugar diferente → reaponta
   - diretório real → move pra `~/.claude/skills-backups/<nome>-<timestamp>` e cria symlink
6. **(passo 5b)** Para cada entrada em `external-upstreams.conf`: clona sparse se preciso, `git fetch` + `reset --hard origin/<branch>` (pull idempotente sem mexer em config local), aplica a mesma reconciliação do passo 5 para a skill em questão.
7. Remove symlinks mortos apontando para caminhos inexistentes (skills removidas em qualquer upstream).
8. Imprime relatório: commits puxados, clones externos atualizados, links criados, reapontados, backups feitos, mortos removidos.

---

## Guardrails

- **Operação é read-only em relação ao repo.** Esta skill nunca escreve arquivos dentro do clone canônico. Edição de skill é um fluxo separado: edite direto no repo, commite, `git push`.
- **Nunca passa `--force` em git nem `--no-verify`.** Se pull falhar (conflito, rebase travado), aborta e reporta — o usuário resolve.
- **Backup antes de substituir diretório real** é rede de segurança contra bug do script, não mecanismo de decisão. O conteúdo do backup pode ser inspecionado depois se necessário.

---

## Observação sobre a sessão atual

Skills recém-adicionadas ou removidas via symlink **não aparecem automaticamente** na lista de skills disponíveis da sessão Claude Code em andamento — o harness carrega o índice no início. Após executar esta skill, avise o usuário que pode ser necessário reiniciar (`/clear` ou nova janela) para que skills novas fiquem invocáveis e skills removidas parem de aparecer.
