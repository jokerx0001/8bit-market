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

### AGENT PROGRESS

GREEN 模式有三层记录，自然形成从 ❌ 到 ✅ 的完整过程。

**Phase 1 初始运行（testsuite 级别）：**

```bash
cat >> {task_dir}/.work/tdd-iterations.md << 'EOF'

## [AI-N] GREEN — Test Run #{N} — $(date '+%Y-%m-%d %H:%M:%S')

| Test Case | Result | Failure Reason | Solution |
|-----------|--------|---------------|----------|
| {case_name} | ✅ | - | - |
| {case_name} | ❌ | {从 "During testcase execution:" 段落提取的失败原因} | {暂空 — Phase 2 逐个填写} |
EOF
```

**Phase 2 逐个 Testcase 诊断记录（每个 case 追加一条）：**

```bash
cat >> {task_dir}/.work/tdd-iterations.md << 'EOF'

## [AI-N] GREEN — Test Run #{N} — Case {M}/{total}：{testcase_name} — $(date '+%Y-%m-%d %H:%M:%S')

| Test Case | Result | Failure Reason | Solution |
|-----------|--------|---------------|----------|
| {testcase_name} | ❌ | {从 Step 2b 诊断中提取的根因，具体明确} | {修复方案，用行为语言描述} |

### 根因分析
- **问题分类**：{设计不匹配 / Ren'Py 用法 / 其他}
- **根因**：{Step 2b 的诊断结论}
- **Ren'Py 文档参考**（如有）：{查阅的文档 URL + 关键发现}
- **影响范围**：{此根因是否可能影响其他 case？}
EOF
```

单 case 验证通过后，在同一标题下将 Result 更新为 ✅。

**Phase 3 收尾：**

所有 case 通过后追加一条汇总确认：

```bash
cat >> {task_dir}/.work/tdd-iterations.md << 'EOF'

## [AI-N] GREEN — Phase 2 完成，{total} 个 case 全部通过 ✅ — $(date '+%Y-%m-%d %H:%M:%S')
EOF
```

不再跑全量验证——单 case 已逐个通过，全量回归是后续 VERIFY 阶段 test-agent 的职责。

失败/阻塞时在表格后追加 **Analysis** 段简述根因推理过程。

### REFACTOR

基础记录：
```bash
cat >> {task_dir}/.work/tdd-iterations.md << 'EOF'

### Iter {iter_N} — REFACTOR (coding-agent) — $(date '+%Y-%m-%d %H:%M:%S')
- **Self-verification rounds**: {actual_rounds}/5
- **Verdict**: {✅ 全部通过 → VERIFY / 🚫 阻塞，建议撤销重构}
EOF
```

阻塞时补充 Key output + Analysis（同 GREEN 失败格式）。

### VERIFY（重构后验证门）

```bash
cat >> {task_dir}/.work/tdd-iterations.md << 'EOF'

### Iter {iter_N} — VERIFY (test-agent) — $(date '+%Y-%m-%d %H:%M:%S')
- **Verdict**: {✅ 全部通过 → REFACTOR 完成 / ❌ 回退到 REFACTOR}
EOF
```
