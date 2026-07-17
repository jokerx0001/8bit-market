---
name: game-dev:refactor-conductor
description: |
  工作流状态机，协调游戏项目代码重构的完整周期。与 orchestrator 唯一区别：
  先分析影响范围并写入 impact.md，再调用 plan（plan 读取 impact.md 约束设计范围）。

  <example>
  Context: 用户需要对现有代码进行重构
  user: "/game-dev:refactor 将角色选择界面的数据持久化从 persistent 迁移到自定义 save 系统"
  assistant: "分析影响范围 → 写入 impact.md → 调用 plan（带约束设计）→ exec。"
  <commentary>
  重构多一步：先分析影响范围，生成 impact.md 约束 plan 的设计范围。
  </commentary>
  </example>

  <example>
  Context: 全自动模式
  user: "/game-dev:refactor 统一所有接口的错误响应格式 --auto"
  assistant: "全自动模式启动。将完成 检测技术栈 → grill → design-ui → impact → plan → exec，不在中间暂停。"
  <commentary>
  --auto 标志表示全自主模式，不等人工审查。
  </commentary>
  </example>
---

# Game Dev Refactor Conductor — 重构状态机

协调重构的完整开发周期。自动检测项目技术栈（Ren'Py / Godot）并加载对应配置。

## 工作流

```
idle → [检测技术栈] → grill → design-ui → 分析影响范围 → impact.md → plan → [审查] → exec → ui-restoration → completed
         ↓              ↓         ↓              ↑_________refactor特有_________↑    ↑                        ↓
    读CLAUDE.md     阶段2     阶段3                                        └── 修改plan ─┘       └── 无UI还原章节 ──┘
```

## 两种模式

### 正常模式（默认）

```
plan → 输出设计文档 → 等待用户审查
  ├── 用户批准 → 自动进入 exec
  └── 用户拒绝 → 修改 plan，重新提交
```

### 全自动模式（`--auto`）

```
plan → 直接进入 exec → 完成
（无人工审查点，全部自动）
```

---

## 阶段执行

### 阶段 0：检测技术栈

**Step 0a — 读 CLAUDE.md 确定 tech：**

```bash
grep -iE "(Ren'Py|renpy|Godot|godot)" CLAUDE.md 2>/dev/null | head -5
```

| 检测关键词 | 技术栈 |
|-----------|--------|
| `Ren'Py`, `renpy` | renpy |
| `Godot`, `godot` | godot |

**如果 CLAUDE.md 不存在或无关键词 →** 根据文件特征推断并向用户确认。

**Step 0b — 读 config 获取 dev_dir（硬门）：**

1. 读 `${CLAUDE_PLUGIN_ROOT}/references/{tech}/config.md` 的 `## 产物目录` 节
2. 提取 `dev_dir` 值
3. 回显确认后才能调用 artifact-manager：

   ```
   ## 技术栈确认
   检测到: {tech}
   dev_dir: {dev_dir}（从 config.md 产物目录节原样读取）
   任务目录: {dev_dir}/{kind}-{N}
   ```

**不猜测不缩写。** config 写 `.godot-dev` 不能用 `.dev`，写 `.renpy-dev` 不能用 `.renpy`。

**Step 0c — 传参，不复制文件。** `tech` 作为上下文传给所有 downstream skill。各 skill 自行读 `${CLAUDE_PLUGIN_ROOT}/references/{tech}/config.md` 获取所需字段。不创建中间文件。

**Step 0d — Godot 额外：检测 2D/3D 维度。** 按 config.md 中"维度检测"规则判断。

**Step 0e — 解析运行模式（硬门）：**

检查用户原始输入是否包含 `--auto`：
- 包含 `--auto` → mode = `auto`（全自动，不在审查点暂停）
- 不包含 → mode = `normal`（正常模式，在审查点暂停等待用户确认）

**回显确认后才能进入阶段 1：**

```
## 运行模式
模式: {normal / auto}
{normal → "正常模式 — 将在 plan 完成后暂停等待审查"}
{auto → "全自动模式 — 不在审查点暂停，全流程自动执行"}
```

### 阶段 1：创建任务目录

```
Skill({skill: "game-dev:artifact-manager", args: "--kind refactor --dev-dir {dev_dir}"})
```

（artifact-manager 不再需要读 config，dev_dir 直接传给它）

artifact-manager 会读取 `current-state.json`、递增计数器、创建 `{dev_dir}/refactor-{N}/`、写回状态。返回 `task_dir`。

### 阶段 2：Grill 前置采访

在分析影响范围之前，通过 relentless interview 达成与用户的共识。**不可跳过，auto 模式也不例外。** 重构场景下，用户对"想改成什么样"的描述常常不完整，用文件固化信息防止上下文丢失。

1. 调用 `grill-with-docs` skill 深度采访用户：
   ```
   Skill({skill: "grill-with-docs"})
   ```
2. 采访完毕后，对文档内容分类整理——因为用户的专业程度不同，输入可能混杂需求内容和技术内容
3. 产出 `{task_dir}/.work/grill-interview.md`，内容分为两类：

   ```markdown
   # Grill Interview

   ## 需求侧（重构目标是什么）
   - {重构要达成的效果、行为变更、体验改进...}
   - {用户确认的重构决策}

   ## 技术侧（用户提到的实现偏好与约束）
   - {技术栈限制、已有系统约束、不可触碰的模块...}
   - {用户的技术决策和假设}
   ```

后面的所有设计环节（design-ui、impact 分析、plan）都必须首先完整阅读这个文档。

### 阶段 3：UI 检测

分析用户的任务描述和重构目标，判断是否涉及 UI 视觉设计。

**Godot 项目额外判断：只对 Control UI 场景触发。**

**触发条件（满足任一即为涉及 UI 视觉设计）：**
- 涉及创建新模块且明显包含新界面
- 涉及现有模块的 UI 视觉重设计
- 用户明确说明具备 UI 设计

**判定原则：宁可误判多调 design-ui（它会自己判断并跳过不需要的部分），也不要漏判。**

**涉及 UI 视觉设计 →** 调用 design-ui：

```
Skill({skill: "game-dev:design-ui", args: "--task-dir {task_dir} --tech {tech}"})
```

design-ui 自读取 grill-interview.md 获取需求上下文，并按优先级寻找风格参考（历史 layout.html → 用户描述/指定文件 → 自行决定）。

**不是 UI 任务 →** 跳过本阶段。

### 阶段 4：分析影响范围

充分阅读现有代码，结合 grill-interview.md 中的重构目标：

1. 读取 `{task_dir}/.work/grill-interview.md` 了解重构目标
2. 读取受影响的源文件（`.rpy` / `.gd` / `.tscn` 等）
3. 使用 Glob/Grep 发现关联文件（共享 screen、共用 label、数据依赖）
4. 识别当前实现模式
5. 查找已有测试文件（`{test_dir}/test_*`）
6. 检查测试基础设施状态（`{test_dir}/` 目录是否存在，SDK 是否设置）
7. 评估级联影响和风险

### 阶段 5：写入 impact.md

按 `references/impact-format.md` 格式写入 `{task_dir}/impact.md`。关键信息：
- 修改范围（硬约束，plan 不得超出）
- 排除范围（plan 不得触碰）
- 已有测试（plan 必须在测试策略中保护）
- **测试基础设施状态**（如缺失，plan 必须添加 `[AI-0]` bootstrap 任务）
- 风险点（plan 必须在设计摘要中应对）
- 特殊约束（用户指定的限制）

### 阶段 6：Plan — 设计阶段

1. 加载 `game-dev:plan` skill，传入参数：
   ```
   Skill({skill: "game-dev:plan", args: "--task-dir {task_dir}"})
   ```
   plan 会读取 `impact.md` 获取约束，在约束范围内用 `superpowers:brainstorming` 分析+设计，自己编写自包含的 `plan.md`。
2. 输出 plan.md 路径

**正常模式（mode=normal）：** plan 完成后输出摘要，**必须**调用 `AskUserQuestion` 暂停等待用户审查，不得跳过：

```
AskUserQuestion({
  questions: [{
    question: "Plan 设计文档已生成，请审查 {task_dir}/plan.md。是否批准进入 exec 实现阶段？",
    header: "Plan Review",
    options: [
      {label: "批准", description: "plan.md 审查通过"},
      {label: "需要修改", description: "plan.md 有问题，我会描述需要改什么"}
    ]
  }]
})
```

- 用户选择"批准" → 进入阶段 7
- 用户选择"需要修改" → 用户描述修改意见，orchestrator 将意见传回 plan skill 重新设计（带 `--revise` 参数），修改后重新提交审查

**全自动模式（mode=auto）：** 跳过 AskUserQuestion，直接进入阶段 7。

### 阶段 7：Exec — TDD 重构循环

1. 加载 `game-dev:exec` skill，传入参数：
   ```
   Skill({skill: "game-dev:exec", args: "--mode refactor --task-dir {task_dir}"})
   ```
2. 支持断点续跑（读取 progress.json）
3. 全部 AI 任务完成后输出完成报告

**重构额外约束：**
- coding agent 必须保证所有已有测试继续通过
- 已有测试被破坏 → 立即反馈修复，最高优先级

### 阶段 7b：UI 还原

exec 完成后，检测 plan.md 是否有 `## UI 还原` 章节。有则调用 `game-dev:ui-restoration`：

```
Skill({skill: "game-dev:ui-restoration", args: "--task-dir {task_dir} --tech {tech}"})
```

无 UI 还原章节则跳过此阶段。

### 阶段 7c：架构文档更新

重构涉及架构变更（重命名、重组、责任迁移），完成后将新的架构知识合并到项目级架构文档。

```
Skill({skill: "game-dev:architecture", args: "--update --from {task_dir} --tech {tech}"})
```

**执行条件：** `--auto` 模式透传给 architecture --update。

**失败处理：** architecture.md 不存在（首次更新）→ 降级为 --init 模式自动建立。其他错误不阻塞工作流，输出警告继续。

### 阶段 8：Completed — 完成

```
## 重构完成

**kind: refactor-{N}**
**技术栈**: {tech}
**设计文档：** {task_dir}/plan.md
**中间产物：** {task_dir}/.work/
**影响范围：** {task_dir}/impact.md
**任务完成：** {done}/{total}
**测试：** ✅ 全部通过
**已有测试：** ✅ 无回归
**人工任务：** {count} 项待完成
```

---

## 状态存储

状态由 `game-dev:artifact-manager` 统一管理，详见 `skills/artifact-manager/SKILL.md`。conductor 不直接操作 `current-state.json`。

## 错误处理

- **技术栈检测失败**：根据文件特征推断，向用户确认
- **plan 阶段失败**：输出具体错误，等待用户指示
- **exec 阶段任务失败**：不限重试，连续 5 轮无进展才报告
- **已有测试被破坏**：立即反馈 coding agent 修复，最高优先级
- **边界检查违规**：作为 REFACTOR 输入自动修复（不阻塞）
- **用户中断**：progress.json 保存当前状态，下次启动可继续

## Red Flags

- "dev_dir 大概就是 .dev 吧，不用读 config"
- "记得是 .dev，不用再读 config"
- 没有回显 dev_dir 值就直接调用 artifact-manager
- "用户没加 --auto 但我可以跳过审查直接进入 exec，反正都一样"
- "plan 完成后不需要 AskUserQuestion，用户肯定批准"
- 没有回显 mode 确认就直接进入阶段执行

**以上任一条 → STOP。**

## 约束

- plan 输出的设计文档是实现的唯一真相来源
- exec 只允许 spawn agent 进行代码工作，主会话负责协调
- coding agent 绝不修改测试代码
- 所有已有测试必须继续通过（无回归）
- 所有测试通过才算任务完成
- 边界检查在 REFACTOR 前执行，违规自动修复
- 重构范围不得超出 impact.md 的硬约束
