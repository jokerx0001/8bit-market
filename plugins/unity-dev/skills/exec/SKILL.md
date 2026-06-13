---
name: unity-dev:exec
description: "Execute a Unity implementation plan with TDD. Use when asked to 'execute the plan', 'start implementation'. 执行计划，TDD 驱动实现。"
argument-hint: [plan file path]
---

# Unity AI-Safe 开发 — 执行阶段

## 用途

读取实现计划，按 TDD 循环逐任务执行。

## TDD流程
写测试 → 分发subagent实现 → 运行测试验证→ 通过，下一项
                               |
                               |---- 不通过,交由subagent修复

## 核心原则

**方式铁律: 无论任务是什么,必须用TDD完成
**TDD 铁律：没有失败测试就不允许写生产代码**
**工作边界 铁律：多agent执行规则必须遵守**

---

## 工作流

### 1. 加载计划

如果参数提供了计划文件路径，直接读取。否则查找最近的计划：

```bash
ls -t .claude/unity-dev/plans/*.md 2>/dev/null | head -5
```

多个计划则让用户选择，只有一个则直接使用。

### 2. 加载参考文件

依次读取：
- `plugins/unity-dev/references/unity-safety-principles.md` — 安全原则
- `plugins/unity-dev/references/plan-format.md` — 格式规范（用于解析计划）

### 3. 解析计划任务

按格式规范解析 `[AI-N]` 任务：

1. 匹配 `- \`[AI-N]\` {描述} → \`{输出路径}\``
2. 提取依赖关系 `(依赖: AI-X, AI-Y)`
3. 按依赖拓扑排序，无依赖的优先执行
4. `[HUMAN]` 任务收集但不执行

### 4. 检测测试运行方式

按优先级检测可用的测试方式：

#### 方式 A：coplay-mcp（优先）

检测 MCP 工具是否可用。如果可用，使用 `execute_script` 执行测试脚本：

```csharp
// RunTests.cs — 通过 coplay-mcp execute_script 执行
using UnityEditor.TestTools.TestRunner.Api;
using UnityEngine;

public static class RunTests
{
    public static void Execute()
    {
        var api = ScriptableObject.CreateInstance<TestRunnerApi>();
        var filter = new Filter()
        {
            testMode = TestMode.EditMode,
            testNames = new[] { "FILTER_PLACEHOLDER" }
        };
        api.Execute(new ExecutionSettings(filter));
        // 结果通过 Unity Console Log 输出，用 get_unity_logs 读取
    }
}
```

执行后通过 `get_unity_logs` 获取测试结果（搜索 "Test" 关键词）。

#### 方式 B：Unity CLI 批处理

如果 coplay-mcp 不可用，使用命令行：

```bash
# 检测 Unity 安装路径
UNITY_PATH=$(find /opt /Applications ~/Unity -name "Unity" -type f 2>/dev/null | head -1)

# 运行测试
"$UNITY_PATH" -batchmode -projectPath "$(pwd)" \
  -runTests \
  -testPlatform EditMode \
  -testFilter "{TestClassName}" \
  -testResults TestResults.xml \
  -logFile - \
  -nographics
```

解析 `TestResults.xml` 获取通过/失败信息。

#### 检测逻辑

```
if coplay-mcp execute_script 可调用:
    测试方式 = A (coplay-mcp)
elif Unity CLI 路径可找到:
    测试方式 = B (Unity CLI)
else:
    提示用户手动运行测试，输出测试文件路径
```

### 5. TDD 循环执行每个任务

对每个 `[AI-N]` 任务执行：

#### 5a. RED — 写测试

为任务预期行为编写单元测试：
- 使用 NUnit + Unity Test Framework
- 测试通过 EventBus 公共 API 验证行为
- 遵守安全原则（不直接调 component）
- 放入项目测试目录

#### 5b. GREEN — 分发子代理

分发子代理实现代码，提示模板：

```
任务：{来自计划的任务描述}

上下文：Unity AI-Safe 开发工作流。项目使用 EventBus 跨系统通信、
GameStateMachine 控制流程、Factory+Config 创建实体。

需要通过的测试：
{测试代码}

安全规则（不可违反）：
- 不修改 Scene / Prefab / Animator 文件
- 不直接调用 Unity 组件（transform, GetComponent 等）
- 跨系统通信只用 EventBus.Publish()
- 状态变更通过 GameStateMachine.Transition()
- 实体创建通过 Factory.Create() + Init(data)
- ScriptableObject 只含数据字段

可用模板参考：
- skills/scaffold/references/templates/ 下的相关模板

要求：只写通过测试所需的 C# 代码，放到正确的项目目录。
```

#### 5c. VERIFY — 验证（必须基于真实输出）

使用第 4 步检测到的方式运行测试。

**验证原则（不可妥协）：**

任务完成的判定必须基于**真实的运行时输出** — 从 Unity Console Log、Debug.Log、
TestRunner 输出、或 `get_unity_logs` 中获取的**实际文本**。绝不能凭代码逻辑推测"应该通过"。

**验证步骤：**

1. 运行测试/代码
2. 获取实际输出（Log / 测试结果 XML / Console 内容）
3. 对比期待值和实际值
4. 输出验证证据：

```
验证 [AI-N]:
  期待值: DamageEvent.amount = 10
  实际值: [Log] DamageEvent published: amount=10
  结论: ✅ 匹配
```

**如果缺少可观测的输出：**

代码中没有日志或断言来证明行为正确时，**必须先补充日志代码**再运行验证：

```csharp
// 在关键路径添加验证日志
Debug.Log($"[VERIFY] {EventName} published: {field}={value}");
Debug.Log($"[VERIFY] {SystemName} received event, state={currentState}");
```

补日志后重新运行，直到能从真实输出中确认行为。

**失败处理（不限次数，必须完成）：**

1. 读取失败的实际输出
2. 对比期待值，定位具体差异：
   ```
   验证 [AI-N]:
     期待值: HealthSystem.currentHP = 90
     实际值: [Log] HealthSystem.currentHP = 100 (未减少)
     结论: ❌ 不匹配 — DamageEvent 未被正确处理
   ```
3. 分析根因（不是猜测，基于日志事实推导）
4. 携带**实际输出 + 根因分析**重新分发子代理
5. 重复直到验证通过

**没有重试上限。任务必须完成。** 如果连续 5 轮同一个错误没有进展，切换策略：
- 重新审视测试本身是否合理
- 检查依赖的前置任务是否有隐含 bug
- 简化实现方案再逐步扩展
- 向用户报告当前卡点和已尝试的方案，请求指导

#### 5d. 记录进度

每个任务完成后输出验证证据：
```
✅ [AI-N] {任务描述}
   证据: {从实际运行中获取的关键日志行}
```

### 6. 最终验证

所有任务完成后：
1. 运行全量测试套件检查回归
2. 输出完成摘要

### 7. 提醒人工任务

### Never claim a task is complete unless:
1. 输出下面的完成报告

```
## 执行完成

**AI 任务完成：** N/N
**测试方式：** {coplay-mcp / Unity CLI / 手动}

**待人工完成：**
- [ ] {HUMAN 任务 1}
- [ ] {HUMAN 任务 2}
- [ ] ...

运行 /unity-dev:review 验证实现是否符合安全原则。
```

