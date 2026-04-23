#!/usr/bin/env bash
# atualizar-skills/sync.sh
# Puxa https://github.com/iago-leal/skills (canônico) + external-upstreams opcionais
# e reconcilia ~/.claude/skills/.
# Fontes declaradas são a verdade; divergências locais viram symlinks gerenciados.

set -euo pipefail

REPO="/Users/iagoleal/Desktop/github_repos/skills"
REMOTE="https://github.com/iago-leal/skills.git"
DEST="/Users/iagoleal/.claude/skills"
BACKUP_DIR="/Users/iagoleal/.claude/skills-backups"
EXT_CLONES_DIR="/Users/iagoleal/Desktop/github_repos"
EXT_CONF="$(dirname "$(readlink -f "$0" 2>/dev/null || echo "$0")")/external-upstreams.conf"
declare -a EXTERNAL_SKILLS=()
[[ -f "$EXT_CONF" ]] && source "$EXT_CONF"

info()  { printf "\033[1;34m==>\033[0m %s\n" "$*"; }
ok()    { printf "\033[1;32m ok\033[0m %s\n" "$*"; }
warn()  { printf "\033[1;33m !!\033[0m %s\n" "$*"; }
err()   { printf "\033[1;31m !!\033[0m %s\n" "$*" >&2; }
die()   { err "$*"; exit 1; }

# 1. Verificar clone local
[[ -d "$REPO/.git" ]] || die "repo não encontrado em $REPO. Clone primeiro:
  git clone $REMOTE $REPO"

# 2. Bloquear pull se houver mudanças não commitadas
if ! git -C "$REPO" diff --quiet || ! git -C "$REPO" diff --cached --quiet; then
  warn "clone local tem alterações não-commitadas:"
  git -C "$REPO" status --short
  die "commite, descarte ou stash manualmente antes de sincronizar"
fi

# 3. Pull
info "fetch + pull em $REPO"
old_head="$(git -C "$REPO" rev-parse HEAD)"
git -C "$REPO" fetch origin
git -C "$REPO" pull --rebase origin main
new_head="$(git -C "$REPO" rev-parse HEAD)"

if [[ "$old_head" != "$new_head" ]]; then
  info "commits puxados:"
  git -C "$REPO" log --oneline "$old_head..$new_head"
else
  ok "já na última versão ($new_head)"
fi

# 4. Descoberta de skills
info "descobrindo skills no repo"
declare -a repo_skill_paths=()
while IFS= read -r skillmd; do
  repo_skill_paths+=("$(dirname "$skillmd")")
done < <(find "$REPO" -type f -name SKILL.md -not -path "*/.git/*")

# 5. Reconciliação — repo é verdade, divergências locais são sobrescritas
declare -a new_links=() repointed=() replaced=() ok_links=()
ts="$(date +%Y%m%d-%H%M%S)"
mkdir -p "$BACKUP_DIR"

for target in ${repo_skill_paths[@]+"${repo_skill_paths[@]}"}; do
  name="$(basename "$target")"
  link="$DEST/$name"

  if [[ ! -e "$link" && ! -L "$link" ]]; then
    ln -s "$target" "$link"
    new_links+=("$name → $target")
  elif [[ -L "$link" ]]; then
    current="$(readlink "$link")"
    if [[ "$current" == "$target" ]]; then
      ok_links+=("$name")
    else
      rm "$link"
      ln -s "$target" "$link"
      repointed+=("$name: $current → $target")
    fi
  else
    # diretório real — backup técnico (fora de $DEST) + substitui por symlink
    backup="$BACKUP_DIR/$name-$ts"
    mv "$link" "$backup"
    ln -s "$target" "$link"
    replaced+=("$name (backup em $backup)")
  fi
done

# 5b. External upstreams (skills gerenciadas mas vindas de outros repos)
declare -a ext_skill_names=()
declare -a ext_pulled=()
if ((${#EXTERNAL_SKILLS[@]})); then
  info "processando ${#EXTERNAL_SKILLS[@]} skill(s) externa(s)"
  declare -a ext_pulled_names=()
  for entry in "${EXTERNAL_SKILLS[@]}"; do
    IFS='|' read -r clone_name ext_remote ext_branch path_in_repo <<< "$entry"
    if [[ -z "$clone_name" || -z "$ext_remote" || -z "$ext_branch" || -z "$path_in_repo" ]]; then
      warn "entrada inválida em external-upstreams.conf: $entry"
      continue
    fi
    ext_clone_dir="$EXT_CLONES_DIR/$clone_name"
    ext_skill_name="$(basename "$path_in_repo")"
    target="$ext_clone_dir/$path_in_repo"

    if [[ ! -d "$ext_clone_dir/.git" ]]; then
      info "clonando $ext_remote → $ext_clone_dir (sparse)"
      git clone --depth=1 --filter=blob:none --sparse --branch "$ext_branch" "$ext_remote" "$ext_clone_dir"
      git -C "$ext_clone_dir" sparse-checkout set "$path_in_repo"
    else
      # Garantir sparse-checkout inclui este path
      if ! git -C "$ext_clone_dir" sparse-checkout list 2>/dev/null | grep -qxF "$path_in_repo"; then
        git -C "$ext_clone_dir" sparse-checkout add "$path_in_repo" 2>/dev/null || true
      fi
      # Pull uma vez por clone (múltiplas skills podem compartilhar o clone)
      already_pulled=0
      for pn in ${ext_pulled_names[@]+"${ext_pulled_names[@]}"}; do
        [[ "$pn" == "$clone_name" ]] && { already_pulled=1; break; }
      done
      if (( ! already_pulled )); then
        info "fetch + pull em $ext_clone_dir"
        git -C "$ext_clone_dir" fetch origin "$ext_branch"
        git -C "$ext_clone_dir" reset --hard "origin/$ext_branch"
        ext_pulled_names+=("$clone_name")
        ext_pulled+=("$clone_name ($(git -C "$ext_clone_dir" rev-parse --short HEAD))")
      fi
    fi

    if [[ ! -d "$target" ]]; then
      warn "external $ext_skill_name: path $path_in_repo ausente após pull — skip"
      continue
    fi
    ext_skill_names+=("$ext_skill_name")
    link="$DEST/$ext_skill_name"
    if [[ ! -e "$link" && ! -L "$link" ]]; then
      ln -s "$target" "$link"
      new_links+=("$ext_skill_name (external) → $target")
    elif [[ -L "$link" ]]; then
      current="$(readlink "$link")"
      if [[ "$current" == "$target" ]]; then
        ok_links+=("$ext_skill_name (external)")
      else
        rm "$link"
        ln -s "$target" "$link"
        repointed+=("$ext_skill_name (external): $current → $target")
      fi
    else
      backup="$BACKUP_DIR/$ext_skill_name-$ts"
      mv "$link" "$backup"
      ln -s "$target" "$link"
      replaced+=("$ext_skill_name (external) (backup em $backup)")
    fi
  done
fi

# 6. Limpar symlinks mortos (skills removidas do repo)
declare -a dead=()
shopt -s nullglob
for entry in "$DEST"/*; do
  if [[ -L "$entry" && ! -e "$entry" ]]; then
    entry_name="$(basename "$entry")"
    dead_target="$(readlink "$entry" 2>/dev/null || echo '?')"
    rm "$entry"
    dead+=("$entry_name → $dead_target")
  fi
done
shopt -u nullglob

# 7. Relatório
echo
info "=== relatório ==="
echo "skills no repo canônico: ${#repo_skill_paths[@]}"
if ((${#ext_skill_names[@]})); then
  echo "skills externas configuradas: ${#ext_skill_names[@]} (${ext_skill_names[*]})"
fi
if ((${#ext_pulled[@]})); then
  echo "clones externos atualizados: ${ext_pulled[*]}"
fi
echo
if ((${#new_links[@]})); then
  ok "symlinks criados (${#new_links[@]}):"
  printf '   + %s\n' "${new_links[@]}"
fi
if ((${#repointed[@]})); then
  ok "symlinks reapontados (${#repointed[@]}):"
  printf '   ~ %s\n' "${repointed[@]}"
fi
if ((${#replaced[@]})); then
  ok "diretórios reais substituídos por symlink (${#replaced[@]}):"
  printf '   ⇒ %s\n' "${replaced[@]}"
fi
if ((${#dead[@]})); then
  ok "symlinks mortos removidos (${#dead[@]}):"
  printf '   - %s\n' "${dead[@]}"
fi
if ((${#ok_links[@]})); then
  echo
  echo "inalteradas (${#ok_links[@]}): ${ok_links[*]}"
fi
echo
if ((${#new_links[@]} + ${#repointed[@]} + ${#replaced[@]} + ${#dead[@]} > 0)); then
  warn "para que a lista de skills ativas reflita as mudanças na sessão atual, reinicie (/clear ou nova janela)."
fi
