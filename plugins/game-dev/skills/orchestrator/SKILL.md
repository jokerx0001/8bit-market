---
name: game-dev:orchestrator
description: |
  工作流状态机，协调游戏项目新功能开发的完整周期。
  启动时自动检测技术栈（Ren'Py / Godot），加载对应配置后执行 plan → [resources] → exec → completed。
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
idle → [检测技术栈] → [UI检测] → design-ui → plan → [资源检测] → design-resources → [审查] → exec → completed
         ↓                ↓                    ↑ ↑              ↑                        ↓
    读CLAUDE.md      加载tech config        └── 修改plan ─┘    └── 无资源需求 ──────────┘
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

**Step 0b — 读 `references/{tech}/config.md` 获取 `dev_dir`。** 用于 artifact-manager 创建任务目录。

**Step 0c — 传参，不复制文件。** `tech` 作为上下文传给所有 downstream skill。各 skill 自行读 `references/{tech}/config.md` 获取所需字段。不创建中间文件。

**Step 0d — Godot 额外：检测 2D/3D 维度。** 按 config.md 中"维度检测"规则判断。


### 阶段 1：创建任务目录

```
Skill({skill: "game-dev:artifact-manager", args: "--task-dir {dev_dir}/{kind}-{N} --kind feat --dev-dir {dev_dir}"})
```

（artifact-manager 不再需要读 config，dev_dir 直接传给它）

artifact-manager 会读取 `current-state.json`、递增计数器、创建 `{dev_dir}/feat-{N}/`、写回状态。返回 `task_dir`。

### 阶段 2：UI 检测

分析用户的任务描述，判断是否涉及 UI 视觉设计。

**触发条件（满足任一即为涉及 UI 视觉设计）：**
- 涉及创建新模块且明显包含新界面
- 涉及现有模块的视觉重设计

**Godot 项目额外判断：只对 Control UI 场景触发。** 判断方法：任务描述涉及菜单、HUD、背包、面板、对话框等纯 UI 交互 → 触发。涉及 2D 关卡、3D 世界、物理、游戏玩法逻辑 → 跳过。

**判定原则：宁可误判多调 design-ui（它会自己判断并跳过不需要的部分），也不要漏判。**

**涉及 UI 视觉设计 →** 调用 design-ui：

```
Skill({skill: "game-dev:design-ui", args: "--task-dir {task_dir} --tech {tech}"})
```

design-ui 读 `references/{tech}/config.md` 获取路径配置，读 `references/{tech}/ui.md` 获取 UI 原则。等待完成后再进入阶段 3。

**不是 UI 任务 →** 直接进入阶段 3。

### 阶段 3：Plan — 设计阶段

1. 加载 `game-dev:plan` skill，传入参数：
   ```
   Skill({skill: "game-dev:plan", args: "--task-dir {task_dir}"})
   ```
2. plan 读 `references/{tech}/config.md` 获取路径/测试配置，读 `references/{tech}/docs.md` 查文档。加上 `.work/` 下已有的 HTML 设计稿和 style-decision.md
3. plan 读取 `.work/` 下已有产物（如有 UI 阶段产出则含 HTML 和 style-decision.md），执行设计全流程
4. 输出 plan.md 路径

**正常模式：** 暂停，等待用户审查 plan.md。
**全自动模式：** 直接进入阶段 4。

### 阶段 4：资源检测与生成

**当 `{task_dir}/.work/resources.md` 存在且包含未处理的资源条目时触发。**

plan 阶段已将资源需求写入 `{task_dir}/.work/resources.md`。orchestrator 检查此文件有内容则调用：

```
Skill({skill: "game-dev:art-resources-conductor", args: "--task-dir {task_dir} --tech {tech}"})
```

art-resources-conductor 读 resources.md → 逐个调用 art-resource-creator skill 生成 → 检查质量 → 追加汇总报告。

### 阶段 5：Exec — 实现阶段

1. 加载 `game-dev:exec` skill，传入参数：
   ```
   Skill({skill: "game-dev:exec", args: "--mode feat --task-dir {task_dir}"})
   ```
2. exec 从 `references/{tech}/config.md` 读取技术栈上下文（测试命令、路径模式等）
3. exec 按 TDD 循环逐任务执行
   - RED: spawn test-agent
   - GREEN: spawn coding-agent
   - VERIFY: spawn test-agent 独立验证
   - **边界检查** → 检查结果作为 REFACTOR 输入
   - REFACTOR: spawn coding-agent（修复边界违规 + 代码质量优化）
   - VERIFY: spawn test-agent 独立验证
3. 支持断点续跑（读取 progress.json）
4. 全部 AI 任务完成后输出完成报告

### 阶段 6：Completed — 完成

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

## 约束

- plan 输出的设计文档是实现的唯一真相来源
- exec 只允许 spawn agent 进行代码工作，主会话负责协调
- coding agent 绝不修改测试代码
- 所有测试通过才算任务完成
- 边界检查在 REFACTOR 前执行，违规自动修复
