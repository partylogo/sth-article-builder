#!/usr/bin/env bash
# 把 skill 與引擎用捷徑連到 Claude Code 讀得到的位置。已存在就停，不覆蓋。
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
link() {
  local src="$1" dst="$2"
  if [ -L "$dst" ] && [ "$(readlink "$dst")" = "$src" ]; then echo "已連好：$dst"; return; fi
  if [ -e "$dst" ] || [ -L "$dst" ]; then echo "已經有東西在 $dst，先手動處理再跑一次" >&2; exit 1; fi
  ln -s "$src" "$dst"; echo "連好：$dst → $src"
}
mkdir -p "$HOME/.claude/skills"
for s in sth-article-builder keyword-plan last-mile-review; do
  link "$ROOT/skills/$s" "$HOME/.claude/skills/$s"
done
link "$ROOT/engine" "$HOME/article-engine"
