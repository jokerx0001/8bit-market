---
name: game-dev:orchestrator
description: |
  工作流状态机，协调游戏项目新功能开发的完整周期。
  启动时自动检测技术栈（Ren'Py / Godot），加载对应配置后执行 plan → [resources] → exec → [ui-restoration] → completed。
  用户可以通过 --auto 标志控制是全自动运行还是在审查点暂停。

  <example>
  Context: 用户提出新的开发需求
  user: "/game-dev:start 开发一个角色选择界面"
  assistant: "我将使用 orchestrator 协调开发流程。检测技术栈 → plan → [resources] → exec。"
  <commentary>
  新功能开发，自动检测项目类型后执行完整流程。
  </commentary>
  </example>

  <example>
  Context: 用户想要全自动模式
  user: "/game-dev:start 开发存档界面 --auto"
  assistant: "全自动模式启动。将完成 plan → exec 全流程，不在中间暂停。"
  <commentary>
  --auto 标志表示全自主模式，不等人工审查。
  </commentary>
  </example>
---

# Game Dev Orchestrator — 工作流状态机

协调从需求到完成的完整开发周期。自动检测项目技术栈（Ren'Py / Godot）并加载对应配置。

## 工作流状态

```
idle → [检测技术栈] → 保存用户原语 → grill → requirements → concept-art → design-ui → asset-extract → plan → [资源检测] → art-resources → [审查] → exec → ui-restoration → completed
         ↓              ↓         ↓                ↓                                    ↑ ↑                        ↓
    读CLAUDE.md     阶段2     阶段3        加载tech config                      └── 修改plan ─┘       └── 无资源需求 ──┘
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
Skill({skill: "game-dev:artifact-manager", args: "--kind {kind} --dev-dir {dev_dir}"})
```

（artifact-manager 不再需要读 config，dev_dir 直接传给它）

artifact-manager 会读取 `current-state.json`、递增计数器、创建 `{dev_dir}/feat-{N}/`、写回状态。返回 `task_dir`。

### 阶段 2：保存用户原语 + Grill 前置采访

**Grill 的目的是防止 AI 偏差，不是产出需求文档。** grill-with-docs 通过 relentless interview 确保 AI 理解用户真正想要什么，避免自作主张跑偏。它的输出是用户确认过的意图记录

**不可跳过，auto 模式也不例外。** grill 的目的不是用户审查——是防止 AI 误解用户意图后一路跑偏。`--auto` 跳过的是人工审查点（plan review），不是意图澄清。

#### Step 2a：保存用户原语

将用户的原始任务描述（触发 `/game-dev:start` 的完整输入）原样写入：

```
{task_dir}/.work/user-prompt.md
```

这是用户的"原语"——未经任何加工。后续所有设计环节在综合理解任务时，必须回到这个原始输入，检查用户有没有直接指示工作内容。

#### Step 2b：运行 Grill 采访

```
Skill({skill: "grill-with-docs"})
```

#### Step 2c：原样保存 Grill 输出

grill-with-docs 输出什么就保存什么。**不分类、不整理、不转化。** 直接将完整输出写入：

```
{task_dir}/.work/grill-interview.md
```

**铁律：grill-interview.md 只能由 grill-with-docs skill 的返回内容写入。orchestrator 绝不自己创建、自己整理、自己补写此文件。** 如果 grill-with-docs 未返回有效内容 → 重试 Skill 调用，不是自己写文件。

**硬门 — 产出验证（不可跳过）：**

1. Skill({skill: "grill-with-docs"}) 调用完成后，将其返回的文本内容原样写入 `grill-interview.md`
2. 检查文件：
   ```bash
   test -s {task_dir}/.work/grill-interview.md && echo "GRILL_OK" || echo "GRILL_MISSING"
   ```
3. `GRILL_MISSING` → 重新调用 `Skill({skill: "grill-with-docs"})`，最多 2 次重试
4. 3 次仍为空 → **报告阻塞，不继续后续阶段。禁止自己写文件代替。**
5. `GRILL_OK` → 读回文件前 20 行，确认内容是对话/采访格式（有问答交互痕迹），不是单方面编写的需求分析。如果读起来像自己写的需求文档 → STOP，回到 Step 2b 重新 grill。

#### Step 2d：传递规则

后面的所有设计环节（requirements、design-ui、plan 等）**必须自己读取以下两份文件，综合理解去完成任务**：

| 文件 | 内容 | 用途 |
|------|------|------|
| `{task_dir}/.work/user-prompt.md` | 用户原始输入（原语） | 检查用户是否直接指示了工作内容、技术偏好、具体约束 |
| `{task_dir}/.work/grill-interview.md` | grill-with-docs 原始输出 | 理解用户确认过的意图，防止 AI 跑偏 |


### 阶段 3：Requirements 需求管理

requirements skill 自行读取 `{task_dir}/.work/user-prompt.md` 和 `{task_dir}/.work/grill-interview.md`，综合理解用户意图后产出需求文档。

**模式判定：**

| 条件 | mode |
|------|------|
| `{dev_dir}/requirements.md` 不存在且为新项目 | `--init` |
| `{dev_dir}/requirements.md` 存在 | `--update` |
| `{dev_dir}/requirements.md` 不存在但有源码/feat 历史 | `--reverse` |

调用 requirements skill：

```
Skill({skill: "game-dev:requirements", args: "--task-dir {task_dir} --tech {tech} --mode {init|update|reverse}"})
```

requirements skill 产出：
- 项目级：`{dev_dir}/requirements.md`（跨 feat 持久的全量需求文档）
- per-task：`{task_dir}/.work/requirements.md`（本次子需求，含行为确认清单）

### 阶段 4：视觉处理

#### 阶段 4a：Concept Art — 生成参考图

**触发条件（满足任一即为涉及生成参考图）：**
- 涉及全新游戏（绿场项目，无现有源码）
- 设计了新关卡/新场景（明显包含原来没有的场景布局）
- 用户明确要求生成参考图


调用 `game-dev:concept-art` 生成 `{task_dir}/reference.png`：

```
Skill({skill: "game-dev:concept-art", args: "--task-dir {task_dir}"})
```

**正常模式（mode=normal）：** 生成 reference.png 后，展示图片路径，调用 `AskUserQuestion` 询问：

```
AskUserQuestion({
  questions: [{
    question: "概念参考图已生成。是否满意，继续进入 UI 设计？",
    header: "Concept Art",
    options: [
      {label: "继续", description: "参考图满意，进入 UI 设计阶段"},
      {label: "重新生成", description: "对参考图不满意，描述需要调整的方向"}
    ]
  }]
})
```

- 用户选择"继续" → 进入阶段 4b
- 用户选择"重新生成" → 用户描述调整诉求，重新调用 concept-art

**全自动模式（mode=auto）：** 跳过 AskUserQuestion，直接进入阶段 4b。

#### 阶段 4b：UI 设计

分析用户的任务描述，判断是否涉及 UI 视觉设计。

**触发条件（满足任一即为涉及 UI 视觉设计）：**
- 涉及创建新模块且明显包含原来没有的新界面（如：新增物品栏 HUD、新增角色选择界面、新增设置面板）
- 涉及现有模块的 UI 视觉重设计
- 用户明确说明具备 UI 设计

**硬门 — 判定流程（不可跳过）：**

1. 分析理解用户原语,**只要有任何一个行为描述了原来不存在的界面/控件布局 → 调用 design-ui**
2. 判定时问一个问题：**"这次任务完成后，玩家/用户会看到原来不存在的画面或控件吗？"** 答案是"是" → design-ui
3. 不自行判定"数据驱动"、"标准控件"、"无艺术决策"等理由跳过——这些是 design-ui 内部的决定，不是 orchestrator 的决定

**不是 UI 任务的例子（可以跳过）：**
- 纯逻辑/数据层改动（如：伤害计算公式调整、存档格式变更）
- 在现有界面上增加一个与周围一致的简单按钮/标签（复用现有 Theme，无布局变化）

**判定原则：宁可误判多调 design-ui（它会自己判断并跳过不需要的部分），也不要漏判。**

**涉及 UI 视觉设计 →** 调用 design-ui：

```
Skill({skill: "game-dev:design-ui", args: "--task-dir {task_dir} --tech {tech}"})
```


#### 阶段 4c：Asset Extract — 从参考图提取资源需求

```
Skill({skill: "game-dev:asset-extract", args: "--task-dir {task_dir}"})
```

asset-extract 用 mmx vision 读 reference.png，提取视觉对象清单，判定生成策略，写入 `{task_dir}/.work/resources.md`。

### 阶段 5：Plan — 设计阶段

1. 加载 `game-dev:plan` skill，传入参数：
   ```
   Skill({skill: "game-dev:plan", args: "--task-dir {task_dir}"})
   ```
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

- 用户选择"批准" → 进入阶段 6
- 用户选择"需要修改" → 用户描述修改意见，orchestrator 将意见传回 plan skill 重新设计（带 `--revise` 参数），修改后重新提交审查

**全自动模式（mode=auto）：** 跳过 AskUserQuestion，直接进入阶段 6。

### 阶段 6：资源检测与生成

**当 `{task_dir}/.work/resources.md` 存在且包含未处理的资源条目时触发。**

plan 阶段已将资源需求写入 `{task_dir}/.work/resources.md`。orchestrator 检查此文件有内容则调用：

```
Skill({skill: "game-dev:art-resources-conductor", args: "--task-dir {task_dir} --tech {tech}"})
```

### 阶段 7：Exec — 实现阶段

1. 加载 `game-dev:exec` skill，传入参数：
   ```
   Skill({skill: "game-dev:exec", args: "--mode feat --task-dir {task_dir}"})
   ```
2. 支持断点续跑（读取 progress.json）
3. 全部 AI 任务完成后输出完成报告

### 阶段 7b：UI 还原

**硬门 — 不可跳过：**

```bash
grep -c '\[UI-\d+\]' {task_dir}/plan.md 2>/dev/null || echo "0"
```

- UI 任务数 > 0 → **必须**调用 `game-dev:ui-restoration`，禁止跳过
- UI 任务数 = 0 → 输出 "无 UI 还原任务，跳过。" 并记录到 log

exec 完成后，检测 plan.md 是否有 `## UI 还原` 章节。有则调用 `game-dev:ui-restoration`：

```
Skill({skill: "game-dev:ui-restoration", args: "--task-dir {task_dir} --tech {tech}"})
```

### 阶段 7c：架构文档更新

feat 完成后，将新的架构知识合并到项目级架构文档。

```
Skill({skill: "game-dev:architecture", args: "--update --from {task_dir} --tech {tech}"})
```

**执行条件：** 仅 feat 和 refactor 模式执行（fix 模式跳过）。`--auto` 模式透传给 architecture --update。

**失败处理：** architecture.md 不存在（首次更新）→ 降级为 --init 模式自动建立。其他错误不阻塞工作流，输出警告继续。

### 阶段 8：Completed — 完成

```
## 开发完成

**{kind}: {kind}-{N}**
**技术栈**: {tech}
**设计文档：** {task_dir}/plan.md
**中间产物：** {task_dir}/.work/
**任务完成：** {done}/{total}
**测试：** ✅ 全部通过
**人工任务：** {count} 项待完成
```

---

## 状态存储

状态由 `game-dev:artifact-manager` 统一管理，详见 `skills/artifact-manager/SKILL.md`。conductor 不直接操作 `current-state.json`。

## 错误处理

- **技术栈检测失败**：根据文件特征推断，向用户确认
- **plan 阶段失败**：输出具体错误，等待用户指示
- **资源阶段失败**（AI 无法生成的资源）：标记 `[HUMAN]` 并继续
- **exec 阶段任务失败**：不限重试，连续 5 轮无进展才报告
- **边界检查违规**：作为 REFACTOR 输入自动修复（不阻塞）
- **用户中断**：progress.json 保存当前状态，下次启动可继续

## Red Flags

- "dev_dir 大概就是 .dev 吧，不用读 config"
- "记得是 .dev，不用再读 config"
- 没有回显 dev_dir 值就直接调用 artifact-manager
- "用户没加 --auto 但我可以跳过审查直接进入 exec，反正都一样"
- "plan 完成后不需要 AskUserQuestion，用户肯定批准"
- 没有回显 mode 确认就直接进入阶段执行
- "--auto 模式下 grill 也可以跳过，全自动就是全部自动" → STOP。grill 不可跳过，auto 模式也不例外。grill 是防止 AI 偏差，不是用户审查点。
- "grill-with-docs 什么都没返回，我自己整理一份 grill-interview.md 就行" → STOP。grill-interview.md 只能由 grill-with-docs 的返回内容写入。自己写 = 编造用户意图。
- "grill-interview.md 已经存在了，不用再调 grill-with-docs" → STOP。文件存不存在的唯一判定在 Step 2c 的硬门。没经过 grill-with-docs 返回的文件不能信任。
- "这个任务不需要 UI 设计，虽然有新界面但是纯控件布局/数据驱动/标准控件" → STOP。有没有新界面是客观事实，不是风格判断。只要玩家会看到原来不存在的画面或控件，就必须 design-ui。
- "没有 HTML 设计稿也没关系，plan 里描述清楚就行了" → STOP。视觉任务必须有 layout.html 作为视觉真相来源。
- "不需要 concept-art，虽然加了新模块" → STOP。concept-art 只在全新游戏（绿场）或新关卡/场景时需要。新增 UI 控件不是 concept-art 的触发条件。

**以上任一条 → STOP。**

## 约束

- plan 输出的设计文档是实现的唯一真相来源
- exec 只允许 spawn agent 进行代码工作，主会话负责协调
- coding agent 绝不修改测试代码
- 所有测试通过才算任务完成
- 边界检查在 REFACTOR 前执行，违规自动修复
