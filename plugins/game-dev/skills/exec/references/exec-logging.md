# Exec TDD Iteration Log

`{task_dir}/.work/tdd-iterations.md` 是 TDD 循环的全量迭代日志。每轮 agent spawn 返回后追加一条记录。该文件是 `.work/` 下的中间产物，供人工排查 TDD 循环卡点使用。

## 初始化

每个 [AI-N] 任务在 6a 标记开始后执行：

```bash
# 文件不存在则创建文件头
test -f {task_dir}/.work/tdd-iterations.md || echo "# TDD Iteration Log" > {task_dir}/.work/tdd-iterations.md
# 追加任务分隔符
cat >> {task_dir}/.work/tdd-iterations.md << 'EOF'

---

## [AI-N] {任务描述} — 开始于 $(date '+%Y-%m-%d %H:%M:%S')
EOF
```

## 条目格式

```markdown
### Iter {N} — {PHASE} ({agent}) — {timestamp}
- **Attempt**: {X}/{max}
- **Key output**:
  ```
  {从 "During testcase execution:" 段落提取 — 失败 testcase 名称 + 具体错误行}
  ```
- **Analysis**: {agent 的推论/修复动作，阻塞/失败时必填}
- **Verdict**: ✅ / ❌ / 🚫
```

## 记录规则

- 每次 agent spawn 返回后**立即追加**，不等下一阶段
- **通过时简洁**：1-2 行概括即可，Key output 可省略
- **失败时详尽**：记录失败的 case 名称、运行输出的关键行、agent 的推论
- **阻塞时**（超过最大重试次数）：必须填写 Analysis，附上 agent 最终失败输出
- exec 不分析、不总结——只原样转录 agent 报告中的关键信息
- 每轮迭代的 N 从 1 开始自增（跨 phase 连续计数），同一 phase 内 retry 时 phase 名不变、Attempt 递增

## Phase 记录模板

### RED

```bash
cat >> {task_dir}/.work/tdd-iterations.md << 'EOF'

### Iter {iter_N} — RED (test-agent) — $(date '+%Y-%m-%d %H:%M:%S')
- **Test file**: {test_file_path}
- **Test cases** ({N} total):
  | # | Test Case | Expected Failure |
  |---|-----------|-----------------|
  | 1 | {name} | {expected failure reason} |
  | ... | ... | ... |
- **Self-correction rounds**: {actual_rounds}/3
- **Verdict**: {✅ 失败原因正确 → GREEN / ❌ 重新 spawn}
EOF
```

RED 阶段所有 testcase 都应该失败。self-correction 超过 1 轮时在 Key output 中补充前几轮的语法/标识符错误。

### GREEN

基础记录：
```bash
cat >> {task_dir}/.work/tdd-iterations.md << 'EOF'

### Iter {iter_N} — GREEN (coding-agent) — $(date '+%Y-%m-%d %H:%M:%S')
- **Files modified**: {文件列表}
- **Self-verification rounds**: {actual_rounds}/5
- **Verdict**: {✅ 目标测试全部通过 → VERIFY / ❌ 重试中 / 🚫 阻塞}
EOF
```

失败/阻塞时补充（紧接基础记录后追加）：
```bash
cat >> {task_dir}/.work/tdd-iterations.md << 'EOF'
- **Key output**:
  ```
  {从 "During testcase execution:" 段落提取 — 失败 testcase 名称 + 具体错误行}
  ```
- **Analysis**: {coding-agent 的推论/修复方向}
EOF
```

### VERIFY（实现后验证门）

```bash
cat >> {task_dir}/.work/tdd-iterations.md << 'EOF'

### Iter {iter_N} — VERIFY (test-agent) — $(date '+%Y-%m-%d %H:%M:%S')
- **Verdict**: {✅ 全部通过 → REFACTOR / ❌ 回退到 GREEN}
EOF
```

失败时补充 Key output（同上）。

---

