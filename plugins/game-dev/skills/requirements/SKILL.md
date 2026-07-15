---
name: game-dev:requirements
description: This skill should be used when the orchestrator needs to manage project requirements — initializing a new requirements document from game type analysis, updating existing requirements for a new feature, or reverse-engineering requirements from existing code. Handles behavior confirmation gates and produces project-level and per-task requirements documents.
---

# Game Dev Requirements — 需求管理

将用户意图转化为结构化的、技术无关的需求文档。三种模式覆盖不同项目阶段的需求管理。

## 前置条件

需求管理在 Grill 采访之后执行。**必须先读取 `{task_dir}/.work/grill-interview.md`**，该文件包含用户确认的需求侧和技术侧信息。

## 三种模式

### 模式判定

由 orchestrator 传入 `--mode` 参数，判定逻辑：

| 条件 | mode |
|------|------|
| `{dev_dir}/requirements.md` 不存在且为新项目 | `--init` |
| `{dev_dir}/requirements.md` 存在 | `--update` |
| `{dev_dir}/requirements.md` 不存在但有源码/feat 历史 | `--reverse` |

### --init 模式：首次构建

1. 读取 `{task_dir}/.work/grill-interview.md` 的需求侧部分
2. 识别游戏类型（塔防、RPG、平台跳跃、视觉小说……）
3. 从游戏类型推导全量功能系统——**不仅限于用户描述的功能**，而是完整游戏应有的所有系统
4. 参考 `references/requirements-format.md` 中的项目级模板，写出 `{dev_dir}/requirements.md` 初稿
5. 调用 `AskUserQuestion` 向用户确认功能系统是否完整、是否有遗漏或不需要的系统
6. 用户确认后落盘

**auto 模式下跳过步骤 5，直接基于已有信息写入。**

### --update 模式：增量更新

1. 读取完整的 `{dev_dir}/requirements.md`
2. 读取 `{task_dir}/.work/grill-interview.md`
3. 分析本次新模块与既存功能系统的关系——是新增系统、改造现有系统，还是扩展行为
4. 参照 `references/requirements-format.md` 中的子需求模板，写出 `{task_dir}/.work/requirements.md`
5. 调用 `AskUserQuestion` 澄清疑点（如新行为与现有行为的边界、功能归属等）
6. **写完子需求后立即更新项目级文档**——参照 `references/requirements-format.md` 中的更新规则，将本次变更合并到 `{dev_dir}/requirements.md` 的正确章节位置。**严禁末尾盲追加**。

**auto 模式下跳过步骤 5，直接基于已有信息更新。**

### --reverse 模式：反向工程

1. 扫描项目源码，识别已有的功能系统
2. 读取所有 `{dev_dir}/feat-*/`、`{dev_dir}/refactor-*/` 目录下的设计文档，提取历史功能描述
3. 反推全量功能系统
4. 参照 `references/requirements-format.md` 中的项目级模板，写出 `{dev_dir}/requirements.md` 初稿
5. 调用 `AskUserQuestion` 向用户确认反推结果是否准确、是否有遗漏
6. 用户确认后落盘

**auto 模式下跳过步骤 5，直接基于反推结果写入。**

---

## 行为确认清单（强制门）

所有模式在写入需求文档前，必须从需求中提取**玩家可见的行为列表**，向用户确认：

```
## 确认以下行为是否准确

这些是玩家能看到和操作的，每条对应一个 testcase：

1. 玩家进入主菜单 → 看到角色选择界面（截图基线）
2. 玩家点击第 2 个角色卡片 → 卡片视觉高亮
3. 玩家选中角色后点击"确认" → 跳转到游戏开始
4. 玩家未选中角色点击"确认" → 停留在当前界面，无事发生
5. ...

是否有遗漏或不需要的行为？
```

**为什么这样做：** 行为确认承担的是需求描述。设计文档描述的是方案（界面结构、组件树），行为描述的是需求（玩家看到什么、做什么、结果是什么）。方案可以有多种，行为只有一种。test-agent 和 coding-agent 都以行为为基准——测试断言行为，实现产出行。

写入前，对每条行为判定验证方式：该行为的结果玩家用眼睛能不能看到？看不到 → `behavior`，看得到 → `screenshot: {问题}`。判定后保存到 `{task_dir}/.work/requirements.md` 的"新增行为"章节，格式见 `references/requirements-format.md`。

**auto 模式下跳过确认直接写入。**

---

## 核心约束

- 第一次构建时，需求文档是全量的——识别游戏类型，推导完整功能系统，不仅限于用户描述的功能
- update 时，子需求文档写完需立刻更新项目级文档，**严禁末尾盲追加**，必须放入正确章节分类位置
- 非 auto 模式下，设计中有疑点必追问，严禁凭猜测决定。auto 模式跳过追问，基于已有信息继续
- 需求文档必须技术无关——不出现引擎概念（Node、Signal、@export、Scene、Resource 等）
- 每条描述用行为语言——玩家能看到或体验到的

## 产出物

- 项目级：`{dev_dir}/requirements.md`（跨 feat 持久的全量需求文档）
- per-task：`{task_dir}/.work/requirements.md`（本次子需求）

## 格式规范

详细模板、命名约定和更新规则见 `references/requirements-format.md`。
