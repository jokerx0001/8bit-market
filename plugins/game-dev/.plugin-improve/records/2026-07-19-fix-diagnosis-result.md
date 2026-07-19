# game-dev - fix 链路诊断结果
## 日期：2026-07-19

### 链路拓扑

```
commands/fix.md (入口)
└── skills/fix-conductor/SKILL.md (fix-conductor)
    ├── skills/artifact-manager/SKILL.md
    ├── agents/test-agent.md
    │   ├── references/godot/config.md
    │   ├── references/godot/testing.md
    │   └── references/godot/screenshot.md
    ├── agents/fix-agent.md
    │   ├── skills/fix-loop/SKILL.md
    │   │   ├── skills/debug-root-cause/SKILL.md
    │   │   └── skills/visual-qa/SKILL.md
    │   └── references/godot/screenshot.md
    └── skills/visual-qa/SKILL.md
```

产物: `/mnt/d/project/godot/zombies-demo/.godot-dev/fix-16`
日志: session `639ccf11-d119-419f-906b-92a96ba6d822`

---

### 逐步骤诊断

| # | 所属节点 | 应有步骤 | 要求(来自plugin文件) | 实际步骤(来自log/产物) | 达标? | 达标证据 / 不达标点 |
|---|---------|---------|---------------------|------------------|-------|-------------------|
| 1 | fix-conductor/SKILL.md §阶段 1c | requirements.md 写入预期行为含验证方式 | `{逐条列出，含验证方式} 1. {行为 1} — 验证方式: {behavior \| screenshot: 问题描述}` | requirements.md E1 = `screenshot:截图包含 10 个 Slot Panel,且每个 Panel size.x/size.y > 0`，E2 = `screenshot:截图中 item 槽位的 TextureRect 实际显示非空 Texture2D 像素,非 placeholder 灰` | ✅ | requirements.md 文件存在且非空，E1/E2 均标注了 `screenshot` 验证方式 |
| 2 | fix-conductor/SKILL.md §阶段 2 (spawn prompt 模板) | 向 test-agent 传递预期行为含验证方式 | `{行为 1} — 验证方式: {behavior \| screenshot: 问题描述}` — 模板要求逐条传递，验证方式不修改 | test-agent RED spawn prompt 中 E2 变为 `behavior:断言 (TextureRect).texture != null 且 texture.get_width() > 0`。E2 从 `screenshot` 被降级为 `behavior`。(subagent agent-a765604b4d97a8836.jsonl:1) | ❌ | requirements.md 声明 E2 = `screenshot`，但 conductor 在 spawn prompt 中将 E2 改写为 `behavior`。验证方式在阶段传递中被 conductor 修改，而非原样传递。 |
| 3 | fix-conductor/SKILL.md §阶段 2 (spawn prompt 模板) | test-agent 被告知哪些行为需要 screenshot | `标注为 screenshot 的行为必须创建截图脚本 + .question 文件，放入 {test_dir}/visual/` | conductor 的 spawn prompt 中 "必交付物" 明确只列出了 1 个 screenshot 脚本（`test_inventory_visible_screenshot.gd` — E1），没有 E2 的截图脚本。spawn prompt 原文："test/visual/写入以下 screenshot 脚本: test_inventory_visible_screenshot.gd — E1 visual verification" | ❌ | conductor 在 spawn prompt 中主动限定了 screenshot 产出范围——告诉 test-agent 只需要写 E1 的截图。E2 screenshot 不是 test-agent 遗漏的，是 conductor 主动排除的。 |
| 4 | fix-conductor/SKILL.md §阶段 3 (spawn prompt 模板) | 向 fix-agent 传递预期行为含验证方式 | `{行为} — 验证方式: {behavior \| screenshot: 问题描述}` | fix-agent spawn prompt 中 E2 = `behavior(test_item_thumbnail_texture.*)`。E2 的 screenshot 验证方式在传递链中彻底消失 (subagent agent-ab1890cb7ba086d75.jsonl:1) | ❌ | E2 screenshot 验证方式从 requirements.md 到 fix-agent 的传递链完全断裂。fix-agent 被告知 E2 只需 GUT 验证。 |
| 5 | fix-conductor/SKILL.md §阶段 4 (VERIFY) | screenshot 验证通过 visual-qa | `有 screenshot 验证方式的行为：截图验证通过 visual-qa` | VERIFY spawn prompt 写的是"确认截图为非空 PNG(file size > 1000 bytes,非全黑)"。VERIFY agent 从未调用 `Skill` 工具 (subagent agent-af025ae7e1ee08b06.jsonl 工具统计: Bash 20次, Read 8次, Skill 0次) | ❌ | conductor 的 VERIFY spawn prompt 用 Bash file size 检查替代了 test-agent.md GREEN mode 规定的 `Skill("game-dev:visual-qa")` 调用。fix-conductor 自己声明的要求（"截图验证通过 visual-qa"）在自己写的 spawn prompt 中被违反。 |
| 6 | fix-conductor/SKILL.md §阶段 1b | 视觉关键词检测 grep | `grep -iE "显示\|渲染\|..."` 扫描 BUG 描述，匹配到视觉关键词 → 标注视觉 BUG → 向用户确认截图验证需求 | conductor 执行了 grep，检测到 BUG 1（显示/UI）+ BUG 2（缩略图/图标/icon）包含视觉关键词。conductor 输出的 text: "视觉检测结果: BUG 1 ("显示", "UI") + BUG 2 ("缩略图", "图标", "icon") → 包含视觉 BUG" | ✅ | grep 被执行了，视觉关键词被正确检测到 |

---

### 根因分析

发现两个根因，它们共享同一个上游原因：

#### 根因 A：Conductor 在 spawn prompt 中修改了验证方式

**现象链：**
1. requirements.md (stage 1c): E2 = `screenshot:...`
2. test-agent spawn (stage 2): E2 = `behavior:...` ← conductor 改写
3. fix-agent spawn (stage 3): E2 = `behavior(...)` ← 改写传播

**机制层根因：** fix-conductor/SKILL.md 的 spawn prompt 模板**没有防止 conductor 修改验证方式的护栏**。模板只写了占位符 `{行为 1} — 验证方式: {behavior | screenshot: 问题描述}`，但没有写"必须原样复制 requirements.md 中的验证方式，不得改写"的约束。conductor 可以自由地将 `screenshot` 改写为 `behavior` 而不触发任何硬门。

**为什么这会导致问题：** stage 2→3 的硬门检查只验证 requirements.md 存在且非空，不验证 spawn prompt 内容与 requirements.md 的一致性。conductor 在没有任何护栏的情况下做出了"E2 可以用 GUT 验证纹理非空"的判断——这本质上是越权做了测试策略决策。

#### 根因 B：VERIFY spawn prompt 覆盖了 test-agent 的 GREEN mode 标准过程

**现象链：**
1. fix-conductor stage 4 声明: "有 screenshot 验证方式的行为：截图验证通过 visual-qa"
2. test-agent.md GREEN mode: "对每个截图 testcase，按 screenshot测试执行方法 执行" → 包括调用 visual-qa
3. conductor 的 VERIFY spawn prompt: "确认截图为非空 PNG(file size > 1000 bytes,非全黑)"
4. VERIFY agent 执行: Skill 调用 0 次

**机制层根因：** conductor 在 VERIFY spawn prompt 中写了**与 test-agent.md 自身 GREEN mode 标准过程冲突的显式 Bash 指令**。test-agent 收到 spawn prompt 后按 prompt 中显式给的 Bash 命令执行，而不是按 test-agent.md 的 GREEN mode 标准过程执行。spawn prompt 中显式的技术指令覆盖了 agent 自身 skill 文件中的过程声明。

**更深层根因：两个根因共享的上游原因是——fix-conductor/SKILL.md 没有"spawn prompt 内容必须与 requirements.md 和 agent 自身 skill 文件一致"的护栏。**

---

### 具体差异

**E2 验证方式在三阶段间的变化：**

| 阶段 | 文件 | E2 验证方式 |
|------|------|-----------|
| 1c | requirements.md | `screenshot:截图中 item 槽位的 TextureRect 实际显示非空 Texture2D 像素,非 placeholder 灰` |
| 2 | test-agent spawn prompt | `behavior:断言 (TextureRect).texture != null 且 texture.get_width() > 0` |
| 3 | fix-agent spawn prompt | `behavior(test_item_thumbnail_texture.*)` |

**VERIFY 阶段 visual-qa 调用：**

| 声明 | 实际 |
|------|------|
| fix-conductor: "截图验证通过 visual-qa" | VERIFY agent: `Skill` 调用 0 次 |
| test-agent.md: `Skill("game-dev:visual-qa")` | VERIFY agent: 只有 Bash file size 检查 |

---

### 解决方案

#### 方案 A：防止 conductor 修改验证方式

**改 `fix-conductor/SKILL.md`：**

1. 在阶段 2 和阶段 3 的 spawn prompt 模板中，将验证方式从自由文本格式改为**逐条引用 requirements.md 原文**：

```
## 预期行为（逐条引用 requirements.md）
{从 {task_dir}/.work/requirements.md 逐条复制"预期行为"表格，不得修改验证方式字段}
```

2. 在阶段 1→2 的硬门检查表中增加一项：

```
| 6 | spawn prompt 中预期行为的验证方式与 requirements.md 一致（逐条核对） | ✅ / ❌ |
```

**来源：** fix-conductor/SKILL.md §阶段 1c 硬门检查表 + §阶段 2 spawn prompt 模板

#### 方案 B：防止 VERIFY spawn prompt 覆盖 test-agent 的标准过程

**改 `fix-conductor/SKILL.md` 阶段 4 spawn prompt 模板：**

将当前的自由文本 prompt 改为**只传模式和数据，不写显式命令**：

```
Agent({
  subagent_type: "game-dev:test-agent",
  prompt: "
## 模式
GREEN

## project
{project 名称}

## task_dir
{task_dir}

## 任务
独立验证 — 跑全量测试确认修复完成且无回归。按 test-agent GREEN mode 标准过程执行。
  "
})
```

删除当前 conductor 写的显式 Bash 命令（如 `godot --headless -s ...`、`godot --path . --script ...`），因为这些命令应该是 test-agent 读取 config.md 后自行解析的，不是 conductor 越权写的。

**来源：** fix-conductor/SKILL.md §阶段 4 spawn 模板 + test-agent.md §GREEN mode
