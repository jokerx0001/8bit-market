#!/usr/bin/env bash
# scripts/verify-rules-injection.sh
# 静态校验 rules 注入机制的关键约束
set -euo pipefail

PLUGIN_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PLUGIN_ROOT"

errs=0
warn() { echo "WARN: $*"; }
err()  { echo "ERR : $*"; errs=$((errs+1)); }
ok()   { echo "OK  : $*"; }

echo "== Check 1: rules vendor 目录存在 =="
if [[ -d "references/rules/common" ]]; then
  ok "references/rules/common 存在"
else
  err "references/rules/common 不存在 — 是否完成 vendor？"
fi

echo "== Check 2: rules 中至少有一个语言子目录 =="
lang_count=$(find references/rules -maxdepth 1 -mindepth 1 -type d ! -name common ! -name web ! -name zh 2>/dev/null | wc -l)
if [[ "$lang_count" -ge 1 ]]; then
  ok "发现 $lang_count 个语言子目录"
else
  err "未发现任何语言子目录"
fi

echo "== Check 3: stack-detector skill 存在 =="
if [[ -f "skills/stack-detector/SKILL.md" ]]; then
  ok "skills/stack-detector/SKILL.md 存在"
else
  warn "skills/stack-detector/SKILL.md 不存在（任务 3 之前是预期的）"
fi

echo "== Check 4: routing-template 存在 =="
if [[ -f "skills/stack-detector/references/routing-template.md" ]]; then
  ok "routing-template.md 存在"
else
  warn "routing-template.md 不存在（任务 3 之前是预期的）"
fi

echo "== Check 5: detection-rules 存在 =="
if [[ -f "skills/stack-detector/references/detection-rules.md" ]]; then
  ok "detection-rules.md 存在"
else
  warn "detection-rules.md 不存在（任务 3 之前是预期的）"
fi

echo "== Check 6: agent Step0 文案 =="
for agent in coding/coding test/test e2e-test/e2e-test; do
  f="agents/$agent.md"
  if [[ -f "$f" ]]; then
    if grep -q "第零步：加载必读规范" "$f"; then
      ok "$f 含 Step0"
    else
      warn "$f 尚未含 Step0 文案（任务 10/11/12 之前是预期的）"
    fi
  fi
done

echo "== Summary =="
if [[ "$errs" -eq 0 ]]; then
  echo "ALL CHECKS OK"
  exit 0
else
  echo "$errs ERRORS"
  exit 1
fi
