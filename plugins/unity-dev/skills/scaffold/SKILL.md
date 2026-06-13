---
name: unity-dev:scaffold
description: "Scaffold Unity code structures. Use when asked to 'scaffold/generate/create' core, system, entity, or event. 脚手架生成 Unity 代码结构（core/system/entity/event）"
argument-hint: <type> [name] — type: core | system | entity | event
allowed-tools: Read, Write, Bash, Grep, Glob
---

# Unity AI-Safe 脚手架生成

## 用途

根据类型参数生成符合 AI-Safe 架构的 Unity C# 代码骨架。

**调用方式：**
- `/unity-dev:scaffold core` — 生成核心层（GameManager, EventBus, StateMachine, Log）
- `/unity-dev:scaffold system Combat` — 生成 System 类 + 测试
- `/unity-dev:scaffold entity Enemy` — 生成 Entity 三件套（Controller + Data + Factory）
- `/unity-dev:scaffold event Damage` — 生成 Event 类型

---

## 通用流程

### 1. 解析参数

从参数中提取：
- `type`：core / system / entity / event
- `name`：具体名称（core 不需要 name）

名称统一转为 PascalCase。

### 2. 检测项目结构

```bash
find . -type d -name "Scripts" -not -path "*/node_modules/*" -not -path "*/Library/*" | head -1
```

找不到则检查 `.csproj` 位置。仍找不到则询问用户。

### 3. 检测命名空间

```bash
grep -r "^namespace " --include="*.cs" --max-count=5 | head -10
```

有则复用，无则默认 `Game.Core` / `Game.Systems` / `Game.Entities` 等。

### 4. 检测渲染管线

```bash
# URP
find . -path "*/UniversalRenderPipelineAsset*.asset" -not -path "*/Library/*" | head -1
# HDRP
find . -path "*/HDRenderPipelineAsset*.asset" -not -path "*/Library/*" | head -1
# manifest.json
grep -o "com.unity.render-pipelines\.[a-z]*" Packages/manifest.json 2>/dev/null
```

判定：
- `com.unity.render-pipelines.universal` → URP
- `com.unity.render-pipelines.high-definition` → HDRP
- 都没有 → Built-in

**影响模板生成的地方：**
- URP：Shader 引用使用 `Universal Render Pipeline/Lit`
- HDRP：Shader 引用使用 `HDRP/Lit`
- Built-in：Shader 引用使用 `Standard`
- Camera/Light 相关代码的 API 差异

检测结果记录在生成文件头部注释中（如果有渲染相关内容）。

### 5. 按类型分发生成

根据 `type` 执行对应的生成逻辑（见下文各类型详细说明）。

### 6. 输出摘要

统一格式：生成了什么文件 + 人工需要做什么。

---

## 类型：core

生成核心基础层，包含以下文件：

| 模板 | 输出路径 | 用途 |
|------|---------|------|
| `IGameEvent.cs` | `Game/Core/IGameEvent.cs` | 事件接口 |
| `EventBus.cs` | `Game/Core/EventBus.cs` | 发布/订阅消息系统 |
| `GameStateMachine.cs` | `Game/Core/GameStateMachine.cs` | 流程控制状态机 |
| `GameManager.cs` | `Game/Core/GameManager.cs` | 单例入口 |
| `Log.cs` | `Game/Core/Log.cs` | 可观测性日志 |

模板位置：`skills/scaffold/references/templates/`

**人工任务：**
1. 在场景中创建空 GameObject 命名为 "GameManager"
2. 挂载 GameManager.cs
3. 根据需要修改 GameState 枚举

---

## 类型：system

参数示例：`/unity-dev:scaffold system Combat` → `CombatSystem`

生成文件：
- `Game/Systems/{Name}System.cs` — 基于模板 `SystemTemplate.cs`
- `Tests/Game/Systems/{Name}SystemTests.cs` — 测试骨架

**System 设计规则：**
- 在 `OnEnable()` 订阅事件，`OnDisable()` 取消订阅
- 不直接调用其他 System，通过 EventBus 通信
- 不直接操作 Unity 组件

**测试骨架模板：**
```csharp
using NUnit.Framework;
using UnityEngine;

[TestFixture]
public class {Name}SystemTests
{
    private {Name}System _system;
    private GameObject _go;

    [SetUp]
    public void SetUp()
    {
        _go = new GameObject();
        _system = _go.AddComponent<{Name}System>();
        EventBus.Initialize();
    }

    [TearDown]
    public void TearDown()
    {
        Object.DestroyImmediate(_go);
        EventBus.Dispose();
    }
}
```

**人工任务：** 将 `{Name}System` 挂载到 GameManager 或专用 GameObject 上。

---

## 类型：entity

参数示例：`/unity-dev:scaffold entity Enemy` → `EnemyController` + `EnemyData` + `EnemyFactory`

生成三个文件：

**1. ScriptableObject 数据** → `Game/Data/{Name}Data.cs`
- 纯数据字段，不含逻辑
- 每个字段加 `[Tooltip("...")]`
- 模板：`EntityData.cs`

**2. Controller** → `Game/Entities/{Name}Controller.cs`
- 通过 `Init({Name}Data data)` 接收配置
- 通过 EventBus 通信
- 模板：`EntityController.cs`

**3. Factory** → `Game/Entities/{Name}Factory.cs`
- 静态 `Create(data, position, rotation)` 方法
- 使用 `Resources.Load<>()` 加载 prefab
- 模板：`EntityFactory.cs`

**人工任务：**
1. 在 Unity Editor 中：Assets → Create → {Name}Data（创建 SO 资产）
2. 在 Inspector 填写数据字段
3. 创建 {Name}.prefab，挂载 {Name}Controller
4. 放置 prefab 到 `Resources/{Name}/{Name}.prefab`

---

## 类型：event

参数示例：`/unity-dev:scaffold event Damage` → `DamageEvent`

名称自动补 "Event" 后缀（如果没有的话）。

生成文件：`Game/Events/{Name}Event.cs`（模板：`EventTemplate.cs`）

**Event 设计规则：**
- 事件是**不可变的事实** — 字段用 `{ get; private set; }` 或 `readonly`
- 不包含逻辑或方法
- 不引用其他 System
- 不携带 Unity 组件引用（用 ID 替代）

**输出使用示例：**
```csharp
// 发布
EventBus.Publish(new {Name}Event(...));

// 订阅（在 System 的 OnEnable 中）
EventBus.Subscribe<{Name}Event>(On{Name});

// 处理
private void On{Name}({Name}Event evt) { ... }

// 取消订阅（在 OnDisable 中）
EventBus.Unsubscribe<{Name}Event>(On{Name});
```

---

## 安全约束（不可违反）

所有生成的代码必须遵守：
- 不修改 Scene / Prefab / Animator 文件
- 跨系统通信只通过 EventBus
- ScriptableObject 只有数据字段
- Entity 创建只通过 Factory + Config
- 不直接操作 Unity 组件（transform, Rigidbody 等）
