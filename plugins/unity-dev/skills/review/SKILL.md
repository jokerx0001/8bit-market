---
name: unity-dev:review
description: "Review Unity C# code against AI-safe principles. Use when asked to 'review code', 'check safety', 'audit'. 审查代码是否符合 AI-Safe 安全原则。"
argument-hint: [file or directory]
allowed-tools: Read, Grep, Glob, Bash
---

# Unity AI-Safe 开发 — 代码审查

## 用途

审查 C# 代码是否符合 AI-Safe 开发安全原则。只读审计，不修改代码。

---

## 工作流

### 1. 加载安全原则

读取 `plugins/unity-dev/references/unity-safety-principles.md` 获取完整规则集。

### 2. 确定审查范围

有参数则只审查指定文件/目录。否则审查整个 `Game/` 目录：

```bash
find . -path "*/Game/*.cs" -not -path "*/node_modules/*" -not -path "*/Library/*"
```

### 3. 执行违规检查

逐文件检查以下规则，报告**所有**违规。

#### 检查 1：直接操作 Unity 组件

```bash
grep -n "transform\.\|GetComponent<\|\.velocity\|\.position\|\.rotation\|\.localScale" <file>
```
**违规** — 应使用封装方法或 System 层 API。

#### 检查 2：跨系统直接调用

```bash
grep -n "System\." <file>
```
**违规** — 应使用 `EventBus.Publish()` 替代。

#### 检查 3：散布 Boolean 状态检查

```bash
grep -n "if.*\.hp\|if.*\.health\|if.*\.isDead\|if.*\.isAlive" <file>
```
**违规** — 应使用 `GameStateMachine.Transition()`。

#### 检查 4：ScriptableObject 中有逻辑

```bash
grep -n "void\|Action\|Func\|delegate" <file>  # 在继承 ScriptableObject 的文件中
```
**违规** — SO 只能有数据字段。

#### 检查 5：Factory 外直接实例化

```bash
grep -n "Instantiate\|Destroy" <file> | grep -v "Factory"
```
**违规** — 应使用 `Factory.Create()`，销毁由 StateMachine 触发。

#### 检查 6：缺少事件订阅配对

对 System 类，验证 `OnEnable` / `OnDisable` 中有 `Subscribe` / `Unsubscribe` 配对。

### 4. 输出违规报告

```markdown
## 安全审查：{范围}

### 违规数量：N

#### ❌ {文件}:{行号} — {违反的规则}
```csharp
{违规代码行}
```
**修复方案：** {按安全原则给出具体修复建议}

---

### 汇总
- ❌ 直接组件操作: N
- ❌ 跨系统直接调用: N
- ❌ 散布状态检查: N
- ❌ SO 含逻辑: N
- ❌ 非 Factory 实例化: N
- ❌ 缺少事件订阅配对: N

### 无违规文件
- {零违规的文件列表}
```

### 5. 标注严重级别

- **🔴 严重**：直接修改 Scene/Prefab/Animator、直接操作组件
- **🟡 警告**：缺少事件模式、散布状态
- **🟢 建议**：风格改进、命名建议

零违规时输出：
```
## 安全审查：通过 ✅

所有文件符合 AI-Safe 开发原则。
```
