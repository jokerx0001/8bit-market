# Agent 结构标准

从 plugin-dev agent-development、code.claude.com/docs/en/sub-agents 官方文档、及 superpowers harness methodology 提取。用于诊断 agent 的结构性问题。

---

## 1. 文件组织

### 1.1 Agent 文件位置

**Plugin agent**：
```
plugin-name/
└── agents/
    ├── agent-one.md              # 简单 agent
    ├── agent-two.md
    └── review/                    # 可选子目录
        └── security.md           # 子目录中的 agent
```

Plugin agent 通过 namespace 访问：`plugin-name:agent-one`、`plugin-name:review:security`。

**来源**: 官方文档 sub-agents §Choose the subagent scope + plugin-dev agent-development §Agent Organization

### 1.2 与其他位置的优先级

当多个位置有同名 agent 时，优先级从高到低：
1. Managed settings（企业）
2. `--agents` CLI flag
3. `.claude/agents/`（项目）
4. `~/.claude/agents/`（用户）
5. Plugin `agents/` 目录

**来源**: 官方文档 sub-agents §Choose the subagent scope

---

## 2. Agent 文件格式

### 2.1 完整格式

```markdown
---
name: agent-identifier
description: Use this agent when [triggering conditions]. Examples:

<example>
Context: [Situation description]
user: "[User request]"
assistant: "[How assistant should respond]"
<commentary>
[Why this agent should be triggered]
</commentary>
</example>

model: inherit
color: blue
tools: ["Read", "Write", "Grep"]
---

You are [agent role description]...

**Your Core Responsibilities:**
1. [Responsibility 1]
2. [Responsibility 2]

**Process:**
1. [Step 1]
2. [Step 2]

**Output Format:**
[What to return]
```

**来源**: plugin-dev agent-development §Agent File Structure + 官方文档 sub-agents §Write subagent files

---

## 3. Frontmatter 字段规范

### 3.1 必需字段

| 字段 | 说明 | 官方规范 |
|------|------|---------|
| `name` | 唯一标识符。小写字母+连字符，3-50 字符。不能以下划线或连字符开始/结束 | 官方文档："Unique identifier using lowercase letters and hyphens" |
| `description` | 何时委托给此 agent。**最关键字段**。必须包含 `<example>` 块 | 官方文档："When Claude should delegate to this subagent" |

### 3.2 关键可选字段

| 字段 | 默认 | 说明 |
|------|------|------|
| `model` | `inherit` | `sonnet` / `opus` / `haiku` / `fable` / `inherit` |
| `color` | 无 | `blue` / `cyan` / `green` / `yellow` / `purple` / `orange` / `pink` / `red` |
| `tools` | 继承所有 | 工具 allowlist。如 `["Read", "Write", "Grep"]` |
| `disallowedTools` | 无 | 工具 denylist。如 `["Edit", "Write"]` |
| `skills` | 无 | 预加载到 agent context 的 skill 名称列表 |
| `permissionMode` | `default` | `default` / `acceptEdits` / `auto` / `dontAsk` / `bypassPermissions` / `plan`。**Plugin agent 忽略此字段** |
| `maxTurns` | 无 | agent 最大对话轮数 |
| `isolation` | 无 | `worktree` — 在隔离的 git worktree 中运行 |
| `memory` | 无 | `user` / `project` / `local` — 跨会话持久记忆 |

**来源**: 官方文档 sub-agents §Supported frontmatter fields

### 3.3 Agent Name 规则

```
✅ 合法: code-reviewer, test-gen, api-analyzer-v2
❌ 非法: ag (太短 <3), -start (连字符开头), my_agent (下划线)
```

**规则**（来自 plugin-dev）：
- 3-50 字符
- 仅小写字母、数字、连字符
- 必须以字母数字开头和结束

### 3.4 Plugin Agent 的特殊限制

Plugin agent **不支持**以下字段（官方文档）：
- `hooks` — 忽略
- `mcpServers` — 忽略  
- `permissionMode` — 忽略

如需这些功能，需要把 agent 文件复制到 `.claude/agents/` 或 `~/.claude/agents/`。

**来源**: 官方文档 sub-agents §Choose the subagent scope

---

## 4. Description 规范

### 4.1 必须包含的内容

1. **触发条件**: "Use this agent when..."
2. **多个 `<example>` 块**（2-4 个）展示触发场景
3. **`<commentary>`** 解释为什么触发此 agent
4. **主动和被动两种触发方式**的示例

### 4.2 Example 块格式

```
<example>
Context: [场景描述]
user: "[用户说的话]"
assistant: "[Claude 应该怎么响应]"
<commentary>
[为什么应该触发这个 agent]
</commentary>
</example>
```

**关键**: assistant 必须展示**使用 Agent 工具**，而不是直接回应任务。

**来源**: plugin-dev agent-development §Description（完整说明）

### 4.3 Description 诊断

- [ ] 包含 "Use this agent when..."
- [ ] 有 2-4 个 `<example>` 块
- [ ] 每个 example 有 Context、user、assistant、commentary
- [ ] assistant 展示使用 Agent 工具（不是直接回应）
- [ ] 覆盖主动触发（用户明确请求）和被动触发（Claude 自主判断）
- [ ] 说明了何时**不**使用此 agent

---

## 5. System Prompt 设计

### 5.1 标准结构（来自 plugin-dev）

```markdown
You are [specific role] specializing in [specific domain].

**Your Core Responsibilities:**
1. [Primary responsibility]
2. [Secondary responsibility]
3. [禁止事项]  ← 明确边界

**Process:**
1. [Step 1 + verification]
2. [Step 2 + verification]
...

**Quality Standards:**
- [Standard 1 with specifics]
- [Standard 2 with specifics]

**Output Format:**
Provide results structured as:
- [Component 1]
- [Component 2]

**Edge Cases:**
- [Edge case 1]: [Handling approach]
- [Edge case 2]: [Handling approach]
```

### 5.2 写作规则

- 使用**第二人称**（"You are...", "You will..."）— 这与 skill body 的祈使句不同
- 具体 > 通用
- 每个职责都是可测量的
- 每个流程步骤都有验证

**来源**: plugin-dev agent-development §System Prompt Design + §Best Practices

### 5.3 四种 Agent 模式（来自 plugin-dev system-prompt-design.md）

**Analyzer Agent** — 分析代码、PR、文档：
```
Analysis Process:
1. Gather Context → 2. Initial Scan → 3. Deep Analysis → 4. Synthesize → 5. Prioritize → 6. Report
输出: Summary + Critical/Major/Minor Issues + Recommendations
```

**Generator Agent** — 创建代码、测试、文档：
```
Generation Process:  
1. Understand → 2. Gather Context → 3. Design Structure → 4. Generate → 5. Validate → 6. Document
输出: 创建的文件 + 质量标准符合性
```

**Validator Agent** — 验证、检查、确认：
```
Validation Process:
1. Load Criteria → 2. Scan → 3. Check Rules → 4. Collect Violations → 5. Assess Severity → 6. Determine Pass/Fail
输出: PASS/FAIL + Violations + Fix Suggestions
```

**Orchestrator Agent** — 协调多步骤工作流：
```
Orchestration Process:
1. Plan → 2. Prepare → 3. Execute Phases → 4. Monitor → 5. Verify → 6. Report
输出: Workflow Execution Report + Results + Next Steps
```

### 5.4 从官方文档的 official examples 中提取的最佳写法

```markdown
---
name: code-reviewer
description: Expert code review specialist. Proactively reviews code for quality, security, and maintainability. Use immediately after writing or modifying code.
tools: Read, Grep, Glob, Bash
model: inherit
---

You are a senior code reviewer ensuring high standards of code quality and security.

When invoked:
1. Run git diff to see recent changes
2. Focus on modified files
3. Begin review immediately

Review checklist:
- Code is clear and readable
- Functions and variables are well-named
- No duplicated code
- Proper error handling
- No exposed secrets or API keys

Provide feedback organized by priority:
- Critical issues (must fix)
- Warnings (should fix)  
- Suggestions (consider improving)

Include specific examples of how to fix issues.
```

**来源**: 官方文档 sub-agents §Example subagents > Code reviewer

### 5.5 System Prompt 诊断

- [ ] 使用第二人称（"You are..."）
- [ ] Core Responsibilities 包含明确禁止项
- [ ] 每个流程步骤有验证
- [ ] Output Format 有明确结构
- [ ] Edge Cases 被覆盖
- [ ] 长度：500-3000 词为理想范围，不超过 10000 字符
- [ ] Harness 机制到位（见 harness-methodology.md）：Iron Law、Red Flags、Forbidden Responses

---

## 6. Tools 配置

### 6.1 最小权限原则

```yaml
# ✅ 只给需要的
tools: ["Read", "Grep", "Glob"]           # 只读分析
tools: ["Read", "Write", "Grep"]          # 代码生成
tools: ["Read", "Bash", "Grep"]           # 测试

# ❌ 永远不给多余的工具
tools: ["*"]                               # 除非确实需要全部权限
```

**来源**: plugin-dev agent-development §Common tool sets

### 6.2 不能在 Subagent 中使用的工具

以下工具是主会话独有的，subagent 不能用（来自官方文档）：
- `AskUserQuestion`
- `EnterPlanMode`
- `ExitPlanMode`（除了 permissionMode: plan 的 subagent）
- `ScheduleWakeup`
- `WaitForMcpServers`

---

## 7. Color 约定（来自 plugin-dev）

| 颜色 | 用途 |
|------|------|
| `blue` | 分析、审查、调研 |
| `cyan` | 文档、信息 |
| `green` | 生成、创建、成功导向 |
| `yellow` | 验证、警告、谨慎 |
| `purple` / `magenta` | 重构、转换、创意 |
| `red` | 安全、关键分析、错误 |
| `orange` / `pink` | 特殊情况 |

---

## 8. Model 选择

```yaml
model: inherit    # 推荐默认。使用与主会话相同的模型
model: sonnet     # 需要更强推理能力
model: haiku      # 快速、廉价操作
model: opus       # 最复杂任务（谨慎使用）
```

**来源**: plugin-dev agent-development §model + 官方文档 sub-agents §Choose a model

---

## 9. 常见 Agent 结构错误

### 9.1 Description 无触发示例

```yaml
# ❌ 错: 无示例
description: Use this agent for code review.

# ✅ 对: 有完整的触发示例
description: Use this agent when the user asks to review code... Examples:
<example>
...
</example>
```

### 9.2 System Prompt 太模糊

```markdown
# ❌ 错
You are a code reviewer. Review code and provide feedback.

# ✅ 对
You are an expert code quality reviewer specializing in identifying issues, security vulnerabilities, and opportunities for improvement.

**Your Core Responsibilities:**
1. Analyze code changes for quality issues
2. Identify security vulnerabilities with file:line references
3. Provide specific, actionable feedback
```

### 9.3 缺少输出格式

```markdown
# ❌ 错: 无输出格式 — agent 不知道返回什么
Provide a report.

# ✅ 对: 明确的输出结构
**Output Format:**
## Code Review Summary
[2-3 sentence overview]

## Critical Issues
- `file:line` - [Issue] - [Fix]
```

### 9.4 工具权限过宽

```yaml
# ❌ 错: 只读审查却给了 Edit/Write 权限
name: code-reviewer
tools: ["Read", "Write", "Edit", "Bash", "Grep"]
```

### 9.5 缺少禁止事项

```markdown
# ❌ 错: 只说做什么，没说禁止什么
**Your Core Responsibilities:**
1. Analyze code quality
2. Suggest improvements

# ✅ 对: 明确禁止边界
**Your Core Responsibilities:**
1. Analyze code quality
2. Suggest improvements  
3. Do NOT modify code directly — only suggest changes
```

---

## 10. 来源汇总

| 规范项 | 来源 |
|--------|------|
| Agent 文件格式、frontmatter 字段 | plugin-dev agent-development SKILL.md |
| Frontmatter 字段完整规范（含 plugin agent 限制） | code.claude.com/docs/en/sub-agents §Supported frontmatter fields |
| Description 中的 `<example>` 格式 | plugin-dev agent-development §description |
| System prompt 四种模式 | plugin-dev agent-development references/system-prompt-design.md |
| Agent 创建系统提示 | plugin-dev agent-development references/agent-creation-system-prompt.md |
| 完整 agent 示例 | plugin-dev agent-development examples/complete-agent-examples.md + 官方文档 §Example subagents |
| Agent name 规则 | plugin-dev agent-development §Identifier Validation |
| Tool 权限原则 | plugin-dev agent-development §tools |
| 颜色约定、model 选择 | plugin-dev agent-development |
| Harness 机制（Iron Law、Red Flags 等） | harness-methodology.md（本 plugin） |

---

## 11. 内容不足时

本 reference 基于 plugin-dev agent-development 和官方文档抓取时（2026-07）的内容。如果诊断中找不到对应的规范条目，或怀疑内容已过时，直接查询官方文档获取最新规范：

**https://code.claude.com/docs/en/sub-agents**
