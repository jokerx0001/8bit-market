# Plan 文件格式规范

此文件定义 plan → exec 的共享契约：plan.md 是 exec 读取的**唯一设计文档**。

---

## 目录结构

```
.renpy-dev/{kind}-{N}/
├── plan.md          ← 自包含，exec 唯一读取，人类唯一审查
├── progress.json    ← exec 任务追踪，断点续跑
└── .work/           ← 中间产物，可追溯但不审查
    ├── requirements.md
    ├── architecture.md
    ├── design.md
    └── (refactor 额外)
        ├── analysis.md
        └── impact.md
```

---

## plan.md 必须自包含

exec 不读 `.work/` 下的任何文件。plan.md 必须包含 exec 需要的**全部信息**：

```markdown
# Plan: {feature-name}

## 概述
{功能目标 + 项目环境 + OWN_MANIFEST 路径}
{这部分吸收 requirements.md 的核心}

## 设计摘要
{关键设计决策，从 architecture.md + design.md 提炼}
{不能写"详见 design.md"——必须把关键决策写在这里}

- Screen 结构: {screen 划分和跳转关系}
- 数据流: {label 间传递的数据、持久化方式}
- 关键交互: {用户操作 → 响应 → 结果}

## 影响范围
{所有涉及的文件，新建/修改}
| 类型 | 文件 | 操作 |
|------|------|------|
| screen | game/screens.rpy | 新增 xxx_screen |
| script | game/script.rpy | 修改 — 新增 label |
| 新建 | game/xxx.rpy | 创建 |

## 任务列表

### [AI] 任务

格式：
- `[AI-N]` {描述} → `{输出文件路径}` (依赖: AI-X, AI-Y)

示例：
- `[AI-1]` 创建 CharacterSelectScreen → `game/character_select.rpy`
- `[AI-2]` 创建 CharacterSelect 测试 → `game/tests/test_character_select.rpy` (依赖: AI-1)

### [HUMAN] 任务

- `[HUMAN]` {具体操作步骤}

## 测试策略

| 层级 | 覆盖内容 | 测试文件 |
|------|---------|---------|
| structure | lint + AST 检查 | — |
| behavior | {行为描述} | game/tests/test_{name}.rpy |
| visual | {视觉描述} | game/tests/test_{name}.rpy |
```

---

## exec 解析规则

exec **只读两个文件**：
1. `{task_dir}/plan.md` — 自包含的设计文档
2. `{task_dir}/progress.json` — 任务追踪

解析 plan.md：
1. **提取 AI 任务**：匹配 `- \[AI-(\d+)\]` 提取序号和描述
2. **提取输出路径**：匹配 `→ \`(.+)\`` 提取目标文件
3. **提取依赖**：匹配 `(依赖: (.+))` 确定执行顺序
4. **按依赖拓扑排序**：无依赖优先，有依赖等前置完成
5. **[HUMAN] 任务不执行**：最终汇总提醒用户
6. **测试策略段**：用于确定每个任务该跑什么测试层

spawn agent 时，从 plan.md 的"概述"+"设计摘要"段提取设计上下文，注入 prompt。

---

## 格式校验清单

plan 输出前自检：
- [ ] 设计摘要自包含（不引用外部文件如"详见 design.md"）
- [ ] 每个 AI 任务有唯一编号 `[AI-N]`
- [ ] 每个 AI 任务有明确输出文件路径（`→` 后面）
- [ ] 依赖关系引用的编号存在
- [ ] 无循环依赖
- [ ] HUMAN 任务标注了具体操作步骤
- [ ] 影响范围表列出了所有涉及的文件
- [ ] 中间产物已写入 `.work/` 子目录
