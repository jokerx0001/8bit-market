# Plan 文件格式规范

此文件定义 plan skill 输出和 exec skill 解析的共享契约。两者必须严格遵守此格式。

---

## 文件路径

```
.unity-dev/feat-{N}/plan.md
```

路径中的 `{N}` 为自增编号（feat-1, feat-2, ...），由 `unity-dev:artifact-manager` skill 的 `create_task` 操作生成。每个任务的所有文档存储在同一目录下。

## 状态管理

Plan 文档的生命周期由 `.unity-dev/current-state.json` 追踪：

- `plan` skill 通过 `artifact-manager` 创建任务目录和保存 plan.md
- Plan 生成后进入 `plan_generated` 阶段，必须等待用户审批
- 用户批准后阶段切换为 `plan_approved`，exec 方可执行
- `exec` skill 通过 `artifact-manager` 的 `get_active_plan` 发现计划

详见 `skills/artifact-manager/SKILL.md`。

---

## 完整结构

```markdown
# Plan: {feature-name}

## 概述

{一段话描述要构建什么功能}

## 项目环境

- **渲染管线：** URP / HDRP / Built-in
- **Unity 版本：** {检测到的版本}
- **命名空间：** {检测到的命名空间}

## 架构映射

| 层级 | 新增/修改 |
|------|-----------|
| Core | {是否需要修改核心层} |
| Systems | {列出涉及的 System} |
| Entities | {列出涉及的 Entity} |
| Events | {列出涉及的 Event} |
| Data | {列出涉及的 ScriptableObject} |

## 事件流

{用箭头链描述事件流转}

示例：
InputEvent → CombatSystem → DamageEvent → HealthSystem → DeathEvent → UISystem

## 任务列表

### [AI] 任务

每个 AI 任务必须包含：标签、序号、描述、输出文件路径、依赖关系

格式：
- `[AI-1]` {描述} → `{输出文件路径}`
- `[AI-2]` {描述} → `{输出文件路径}` (依赖: AI-1)

示例：
- `[AI-1]` 创建 DamageEvent → `Game/Events/DamageEvent.cs`
- `[AI-2]` 创建 CombatSystem → `Game/Systems/CombatSystem.cs` (依赖: AI-1)
- `[AI-3]` 创建 CombatSystem 测试 → `Tests/Game/Systems/CombatSystemTests.cs` (依赖: AI-2)

### [HUMAN] 任务

人工任务不编号，只列出操作：
- `[HUMAN]` 创建 Enemy.prefab 并挂载 EnemyController
- `[HUMAN]` 在 Inspector 中配置 WeaponData 资产

## 数据定义

列出需要创建的 ScriptableObject 字段规格：

```csharp
// {Name}Data.cs
public float damage;        // 基础伤害
public float attackSpeed;   // 攻击频率(次/秒)
public int maxCombo;        // 最大连击数
```

## 状态变更

列出需要新增的 GameState 枚举值或状态转换：

| 新状态 | 从哪些状态可转入 | 触发条件 |
|--------|-----------------|---------|
| Combat | Playing | 进入战斗区域 |
| Victory | Combat | 所有敌人死亡 |
```

---

## exec 解析规则

exec skill 解析此格式时：

1. **提取 AI 任务**：匹配正则 `^\- \`\[AI-(\d+)\]\`` 提取序号和描述
2. **提取输出路径**：匹配 `→ \`(.+)\`` 提取目标文件
3. **提取依赖**：匹配 `\(依赖: (.+)\)` 确定执行顺序
4. **按依赖排序执行**：无依赖的任务优先，有依赖的等前置完成
5. **HUMAN 任务不执行**：最终汇总提醒用户

## 格式校验清单

plan 输出前必须自检：
- [ ] 每个 AI 任务有唯一编号 `[AI-N]`
- [ ] 每个 AI 任务有明确输出文件路径（`→` 后面）
- [ ] 依赖关系引用的编号存在
- [ ] 无循环依赖
- [ ] HUMAN 任务标注了具体操作步骤
- [ ] 数据定义中 ScriptableObject 只有字段，无方法
