# game-dev - feat 链路诊断结果
## 日期：2026-07-23

### 链路拓扑

```
commands/start.md
  └── skills/orchestrator/SKILL.md
        ├── skills/artifact-manager/SKILL.md (阶段1)
        ├── skills/requirements/SKILL.md (阶段3)
        ├── skills/concept-art/SKILL.md (阶段4a)
        ├── skills/design-ui/SKILL.md (阶段4b)
        ├── skills/plan/SKILL.md (阶段5)
        │     ├── skills/domain-modeling/SKILL.md
        │     ├── skills/architecture/SKILL.md
        │     └── references/plan-format.md
        ├── skills/asset-extract-doc/SKILL.md (阶段6)
        ├── skills/art-resources-conductor/SKILL.md (阶段6)
        ├── skills/exec/SKILL.md (阶段7 — 核心问题链)
        │     ├── skills/exec/references/exec-prompts.md
        │     ├── skills/exec/references/exec-logging.md
        │     ├── agents/test-agent.md (RED + VERIFY)
        │     │     ├── references/{tech}/config.md
        │     │     ├── references/{tech}/testing.md
        │     │     ├── references/{tech}/screenshot.md
        │     │     └── skills/visual-qa/SKILL.md
        │     ├── agents/coding.md (GREEN + REFACTOR)
        │     │     ├── references/{tech}/config.md
        │     │     ├── references/{tech}/coding.md
        │     │     ├── references/{tech}/screenshot.md
        │     │     └── skills/visual-qa/SKILL.md
        │     ├── skills/collect-lessons/SKILL.md (步骤9)
        │     └── skills/write-tutorial/SKILL.md (步骤10)
        ├── skills/ui-restoration/SKILL.md (阶段7b)
        └── skills/architecture/SKILL.md (阶段7c)
```

### 核心发现

**plan.md 声明了 6/10 条行为需要 `screenshot:` 验证，但 fea-1 实际产物 0 条 screenshot testcase 被创建。根因：**

**coding.md 把 GUT 和 screenshot 两种不同的测试体系强行套用同一个"全量执行/单case执行"概念框架，导致 agent 解析截图执行方法时产生混乱。**

---

### 逐步骤诊断

| # | 所属节点 | 应有步骤 | 要求(来自plugin文件) | 实际步骤(来自log/产物) | 达标? | 达标证据 / 不达标点 |
|---|---------|---------|---------------------|------------------|-------|-------------------|
| 1 | skills/plan/SKILL.md | 步骤7: 行为列表含 screenshot 验证方式声明 | "行为列表...验证方式列：`behavior` 或 `screenshot: {问题}`" (requirements/SKILL.md L89-90) | plan.md L19-30: 10条行为, 6条标注 `screenshot:` (行为1,2,4,7,9,10) | ✅ | plan.md 行为列表: 行为1 `screenshot: 关卡初始画面`, 行为2 `screenshot: 待机摆动帧`, 行为4 `screenshot: 攻击命中帧`, 行为7 `screenshot: 受击后仰帧`, 行为9 `screenshot: 敌人死亡`, 行为10 `screenshot: 死亡画面` |
| 2 | agents/coding.md | 步骤3: 解析截图测试执行方法 | coding.md L79-82: "screenshot 验证方式（截图 + visual-qa）：全量执行：逐个 testcase 执行截图脚本...→ Skill('game-dev:visual-qa')；单case执行：执行该 case 的截图脚本...→ Skill('game-dev:visual-qa')" | init.log L13-14: `全量执行: godot CLI (unavailable)`, `单case执行: godot CLI (unavailable)` | ❌ | **模板设计缺陷。** coding.md 步骤3 给 screenshot 也定义了"全量执行"——但截图没有批量命令，截图天生是一个个跑的（没有 GUT 的 `--gselect` 那种批量概念）。agent 尝试把"screenshot 全量执行"解析为 CLI 命令时发现不存在，于是标了 unavailable。这不是 agent 编造，是模板让它去解析一个不存在的东西。同一份 init.log 中 GUT 的三行命令（test_cmd_full/suite/single）全部正确解析——因为 GUT 真的有批量。 |
| 3 | agents/coding.md | 初始化摘要模板 | coding.md L88-104: "全量执行: {方法定义见第 3 步}；单case执行: {方法定义见第 3 步}" | init.log 中 `全量执行` 和 `单case执行` 各只有一行。 | ❌ | **模板没有区分 GUT 和 screenshot。** 步骤3 定义了两套执行方法（GUT + screenshot），但初始化摘要模板各只给了一行。agent 需要把两套方法合并到两个字段里表达，不知道该填什么。GUT 有真正的全量命令（test_cmd_suite 一条跑完），screenshot 只有逐个执行——两种体系的"全量"语义不同，共用一个字段名必然混乱。 |
| 4 | skills/exec/SKILL.md | Completion Gate 第4项: screenshot 验证 | "所有 screenshot 验证行为已创建截图 testcase 且通过 visual-qa" (L371) | progress.json 全部 done，零 screenshot testcase。 | ❌ | exec 未被加载——session 中 orchestator 被打断后模型直接 spawn 了 coding-agent，跳过了 exec 的 TDD 循环。Completion Gate 从未执行。 |
| 5 | skills/exec/SKILL.md | 步骤6b: RED — spawn test-agent | "使用 RED prompt 模板组装 spawn prompt...测试文件已创建、所有 testcase 失败原因正确" (L197-210) | tdd-iterations.md 无 RED phase 条目，无 test-agent spawn 记录。 | ❌ | exec 未被加载，test-agent 从未被 spawn。 |
| 6 | skills/exec/SKILL.md | 步骤6c: GREEN — screenshot 验证 visual-qa PASS | "有 screenshot 验证方式的行为：visual-qa PASS" (L222) | tdd-iterations.md 无 visual-qa 调用记录。 | ❌ | exec 未被加载，GREEN 检查未执行。 |
| 7 | skills/exec/SKILL.md | 步骤6d: VERIFY — spawn test-agent | "有 screenshot 验证方式的行为：额外通过 visual-qa PASS" (L243) | tdd-iterations.md 无 VERIFY phase 条目。 | ❌ | exec 未被加载，VERIFY 未执行。 |
| 8 | skills/exec/SKILL.md | 步骤6e: 边界检查 | "对每个任务强制执行。即使跳过 REFACTOR，边界检查也必须执行。" (L249-253) | tdd-iterations.md 无 BOUNDARY-CHECK 条目。 | ❌ | exec 未被加载，边界检查未执行。 |
| 9 | skills/exec/SKILL.md | 步骤6f: REFACTOR | "REFACTOR 触发规则逐条判定" (L299-306) | tdd-iterations.md 无 REFACTOR 条目。 | ❌ | exec 未被加载，REFACTOR 未执行。 |
|E1 | (额外步骤) | coding-agent 直接实现全部代码 | exec L42-43: "我先写几个文件让 agent 参考" → STOP；L36-55 Red Flags 清单 | coding-agent 单次 pass 实现全部 5 个 AI 任务，零 test-agent 参与。 | ❌ | exec 未被加载——模型绕过 orchestrator 直接 spawn coding-agent GREEN 模式。exec 的 Red Flags、Iron Law、Phase Transition Gate 全都没有机会生效。 |

---

### init.log 证据

```
[coding-agent] spawned — 2026-07-23
  mcp:         active

  resolved:
    test_cmd_full:    godot --headless ...     ← ✅ GUT 全量命令，正确
    test_cmd_suite:   godot --headless ...     ← ✅ GUT suite 命令，正确
    test_cmd_single:  godot --headless ...     ← ✅ GUT 单case 命令，正确
    screenshot 命令:   godot --path ...         ← ✅ 截图 CLI，正确

    全量执行:         godot CLI (unavailable)   ← ❌ 混乱 — 截图没有批量命令
    单case执行:       godot CLI (unavailable)   ← ❌ 混乱 — 同上
```

前三行 GUT 命令全部正确——因为 GUT 真的有 `test_cmd_suite`（批量跑整个 testsuite）。后两行混乱——因为 screenshot 没有等价物。agent 在"全量执行"这个槽里同时放 GUT 的 `test_cmd_suite` 和 screenshot 的"逐个 testcase 循环"，发现后者没有对应 CLI 命令，于是标了 unavailable。

### 体系差异

| | GUT (behavior) | Screenshot |
|---|---------------|------------|
| 全量执行 | `test_cmd_suite` — 一条命令跑整个 testsuite ✅ | 不存在 — 只能逐个截图脚本跑 |
| 单case执行 | `test_cmd_single` — `-gunit_test_name={case}` ✅ | 逐个截图脚本 → base64 decode → Skill("visual-qa") |
| 命令性质 | Godot CLI，带 `--headless` | Godot CLI，**不带** `--headless` |
| 结果判定 | 退出码 + grep 日志 | visual-qa 的 `### Answer` |

两种测试体系从命令到判定方式完全不同。coding.md 把它们塞进同一套"全量/单case"命名里，然后初始化摘要模板又只给了各一行——agent 填不出来就标了 unavailable。

---

### 根因分析与解决方案

| # | 应有步骤 | 达标? | 根因 | 解决方案 | 解决方案来源 |
|---|---------|-------|------|---------|-------------|
| 2 | coding.md 步骤3: 截图执行方法定义 | ❌ | **coding.md 把 GUT 和 screenshot 两种完全不同的测试体系强行套用同一套"全量执行/单case执行"概念框架。** GUT 的"全量执行" = `test_cmd_suite` 一条命令跑完；screenshot 没有等价物——截图天生是逐个脚本跑的。agent 在模板的"全量执行"槽里尝试为 screenshot 解析出 CLI 命令，解析不出来就标了 unavailable。同时 coding.md L79-82 把 screenshot 的逐个执行过程也叫"全量执行"（"逐个 testcase 执行截图脚本"），命名自相矛盾——逐个执行怎么能叫全量？ | ① coding.md 步骤3 拆开两套方法定义: **behavior 验证方式（GUT）** 保持全量/单case 命名；**screenshot 验证方式（截图 + visual-qa）** 去掉"全量执行"，只保留单条执行方法（因为没有批量命令），命名为"截图执行"；② 初始化摘要模板分开写两套方法，各用各的语义: `全量执行 (GUT): {test_cmd_suite} > {log_path} 2>&1`、`单case执行 (GUT): {test_cmd_single} > {log_path} 2>&1`、`截图执行: godot --path {project} --script {script} \| base64 -d > {png} → Skill("game-dev:visual-qa")`。 | coding.md L79-82 (当前定义), L88-104 (当前模板); agent-structure.md §6.1 (初始化逻辑准确性); 本诊断从 init.log "godot CLI (unavailable)" + 两套方法体系差异分析确认 |
| 3 | coding.md 初始化摘要模板 | ❌ | **与 #2 同根因。** 模板 L96-103 中 `全量执行` 和 `单case执行` 各只占一行，但步骤3 定义了两套方法（GUT + screenshot）。agent 要把两套语义合并到一行展示，screenshot 没有批量命令 → 填不出来 → unavailable。 | 见 #2 — 拆开模板，不共用字段名。 | — |
| 4 | exec Completion Gate: screenshot 验证 | ❌ | exec 未被加载，Completion Gate 未执行。但 Completion Gate (L365-375) 本身是声明性文字——8 项条件定义了但无"不满足则禁止标记 done"的 Hard Gate 强制执行。 | 步骤6h（标记完成）前增加 Completion Hard Gate: 5 个 phase 在 tdd-iterations.md 中全部 `[x]` + screenshot 文件存在 + visual-qa PASS。任一 ❌ → 禁止写 progress.json done。 | harness-methodology.md §机制5 (Hard Gate), §机制13 (Checklist with Consequences) |

**注：exec 未被加载（session 中断导致 orchestrator 状态丢失）不属于 plugin-improve 诊断范围——那不是 harness 能解决的问题。本诊断只覆盖插件文件可修复的工程问题。**

---

### 优先级

| 优先级 | 修复 | 影响范围 |
|--------|------|---------|
| **P0** | coding.md 步骤3 + 初始化摘要: 拆开 GUT 和 screenshot 的方法定义和模板 (#2, #3) | agent 不再混淆两种测试体系，init.log 不再出现 unavailable |
| **P1** | exec Completion Hard Gate (#4) | 确保 TDD 循环正常运行时不因 screenshot 缺失而标记 done |

---

### 不在范围的行

| # | 应有步骤 | 判断 | 原因 |
|---|---------|------|------|
| 4 | exec 未被加载 (session 中断) | ⏭️ | 属于 Claude Code session 连续性问题，不是插件 harness 可修复的。 |
| 5-9, E1 | exec RED/GREEN/VERIFY/边界检查/REFACTOR 均跳过 | ⏭️ | exec 未被加载的连锁后果，不是 exec 自身护栏的失效。 |
