# Skill 结构标准

从 plugin-dev skill-development 和 code.claude.com/docs/en/skills 官方文档提取。用于诊断 skill 的结构性问题。

---

## 1. 文件组织

### 1.1 目录结构

**Plugin skill**（plugin-improve 审查的目标）：
```
plugin-name/
└── skills/
    └── skill-name/              # 目录名 = skill 名（kebab-case）
        ├── SKILL.md             # 必需。YAML frontmatter + Markdown 指令
        ├── references/          # 可选。按需加载的文档
        │   ├── api-docs.md
        │   └── patterns.md
        ├── examples/            # 可选。示例文件
        └── scripts/             # 可选。可执行脚本
```

**来源**: plugin-dev skill-development §Anatomy of a Skill + 官方文档 skills §Add supporting files

### 1.2 渐进披露原则

三级加载系统：
1. **Metadata**（name + description）— 始终在 context 中
2. **SKILL.md body** — skill 触发时加载（目标 1500-2000 词，上限 500 行）
3. **Bundled resources** — 按需加载（无大小限制）

**来源**: plugin-dev skill-development §Progressive Disclosure Design Principle

### 1.3 结构检查清单

对每个 skill 目录检查：
- [ ] `SKILL.md` 存在且文件名正确（不是 README.md、GUIDE.md）
- [ ] SKILL.md 有 YAML frontmatter（`---` 包围）
- [ ] `references/` 中的文件在 SKILL.md 中被引用
- [ ] `examples/` 中的文件可运行且完整
- [ ] `scripts/` 中的脚本可执行且有文档
- [ ] 没有不必要的空目录

---

## 2. YAML Frontmatter 字段

### 2.1 必需字段

| 字段 | 说明 | 来源 |
|------|------|------|
| `name` | Skill 标识符。目录名默认就是 name。plugin skill 中会被插件名 namespace | 官方文档 §Frontmatter reference |
| `description` | 何时使用此 skill + 做什么。Claude 据此决定是否触发 | 官方文档：唯一推荐字段 |

**来源**: 官方文档 skills §Frontmatter reference: "All fields are optional. Only `description` is recommended so Claude knows when to use the skill."

### 2.2 关键可选字段

| 字段 | 用途 | 何时需要 |
|------|------|---------|
| `disable-model-invocation: true` | 只允许用户手动调用 `/skill-name` | 有副作用的操作（部署、提交） |
| `user-invocable: false` | 只允许 Claude 自动调用，不出现在 `/` 菜单 | 背景知识、参考标准 |
| `allowed-tools` | 预批准的工具列表 | skill 需要特定工具权限时 |
| `disallowed-tools` | 禁止的工具列表 | 需要限制某些工具时 |
| `context: fork` | 在子 agent 中运行 | 有大量上下文操作的 skill |
| `agent` | 与 `context: fork` 配合，指定 agent 类型 | 需要特定 agent 执行时 |
| `model` | 使用特定模型 | 需要特定能力时 |
| `paths` | Glob 模式，限制 skill 仅在匹配文件时激活 | 技能只适用于特定文件类型 |

**来源**: plugin-dev skill-development §SKILL.md + 官方文档 §Frontmatter reference

### 2.3 Frontmatter 诊断

对每个 skill 的 frontmatter 检查：
- [ ] `description` 存在且非空
- [ ] `description` 包含触发条件（不仅是功能描述）
- [ ] 如果是 user-invoked skill（命令入口），有 `disable-model-invocation: true` 或明确的参数设计
- [ ] `allowed-tools` 不包含不需要的工具
- [ ] `name` 使用 kebab-case

---

## 3. Description 规范

### 3.1 第三方称 + 触发短语

**正确格式**（来自 plugin-dev）：
```yaml
description: This skill should be used when the user asks to "create a hook", "add a PreToolUse hook", "validate tool use", or mentions hook events.
```

**错误格式**：
```yaml
# ❌ 第二人称
description: Use this skill when working with hooks.

# ❌ 模糊
description: Provides hook guidance.

# ❌ 太短
description: For hooks.
```

**来源**: plugin-dev skill-development §Description Quality

### 3.2 CSO 原则（来自 superpowers writing-skills）

```yaml
# ❌ BAD: 包含 workflow 摘要 — Claude 会用描述替代读 body
description: Use when executing plans - dispatches subagent per task with code review between tasks

# ✅ GOOD: 只有触发条件
description: Use when executing implementation plans with independent tasks in the current session
```

**检查**: description 中有没有 "and then...", "with...", "dispatches..." 这类流程摘要？

**来源**: superpowers writing-skills §CSO

### 3.3 Description 诊断

- [ ] 使用第三方称（"This skill should be used when..."）
- [ ] 包含具体触发短语（用户会说的确切词句）
- [ ] 不包含 workflow 摘要
- [ ] 长度适中（50-500 字符为理想范围，官方 cap 为 1536 字符）
- [ ] 不会和另一个 skill 的 description 混淆触发

**来源**: plugin-dev skill-development + 官方文档 §Skill content lifecycle

---

## 4. SKILL.md Body 规范

### 4.1 写作风格

**祈使/不定式形式**（来自 plugin-dev）：

```markdown
# ✅ 正确
To create a hook, define the event type.
Configure the MCP server with authentication.
Validate settings before use.

# ❌ 错误  
You should create a hook by defining the event type.
You need to configure the MCP server.
```

**来源**: plugin-dev skill-development §Writing Style Requirements

### 4.2 内容组织

SKILL.md body 应该包含：

1. **Overview** — 2-3 句话，skill 做什么，核心原则
2. **When to Use** — 触发场景列表 + When NOT to Use
3. **Core Workflow/Process** — 步骤和程序
4. **Red Flags**（来自 harness methodology）
5. **Common Mistakes/Rationalizations**（来自 harness methodology）
6. **Reference Pointers** — 明确指向 references/、examples/ 文件，说明何时读它们

**来源**: plugin-dev skill-development §Update SKILL.md + superpowers harness methodology

### 4.3 可引用文件

```markdown
## Additional Resources

### Reference Files
For detailed patterns and techniques, consult:
- **`references/patterns.md`** - Common patterns
- **`references/advanced.md`** - Advanced use cases

### Examples
Working examples in `examples/`:
- **`example-script.sh`** - Working example
```

**来源**: plugin-dev skill-development §Update SKILL.md

### 4.4 Body 诊断

- [ ] SKILL.md body 使用祈使/不定式形式（不是 "You should"）
- [ ] 词数在 1500-2000 理想范围（上限 3000）
- [ ] 详细内容移到 references/ 而非全塞在 SKILL.md
- [ ] 所有 references/examples/scripts 文件在 SKILL.md 中被引用
- [ ] 有明确的 "何时不用" 部分
- [ ] body 的第一段描述清楚 skill 的目的

**来源**: plugin-dev skill-development §Validation Checklist

---

## 5. 自定义命令（User-Invoked Skills）

### 5.1 命令 Skill 的格式

当 plugin skill 作为 `/command` 入口时（来自官方文档）：

```yaml
---
description: Deploy the application to production
disable-model-invocation: true    # 只允许用户手动调用
argument-hint: [environment]       # 参数提示
allowed-tools: Bash(git *) Bash(npm *)
---

Deploy $ARGUMENTS to production:
1. Run the test suite
2. Build the application
3. Push to the deployment target
```

**关键区别**：命令 skill 的指令是**写 FOR Claude（如何执行）**，不是 TO 用户。

**来源**: plugin-dev skill-development §For Skills + 官方文档 §Control who invokes a skill

### 5.2 命令 Skill 诊断

- [ ] 已设置 `disable-model-invocation: true`（由人控制）
- [ ] `argument-hint` 描述了期望的参数
- [ ] 指令清晰、可执行
- [ ] `allowed-tools` 精确指定了需要的权限
- [ ] 没有泄露到会被模型自动调用的状态

---

## 6. Reference 文件规范

### 6.1 何时需要独立的 Reference

- SKILL.md 中某个部分超过 50 行
- 详细的 API 文档、schema、命令参数
- 需要但从上下文角度不是每次都需要的信息
- 大型示例或数据集

**来源**: plugin-dev skill-development §Progressive Disclosure in Practice

### 6.2 Reference 诊断

- [ ] reference 文件在 SKILL.md 中被显式引用
- [ ] reference 内容准确（没有过期信息）
- [ ] reference 文件有清晰的标题和结构，agent 能找到需要的信息
- [ ] 大于 300 行的 reference 有目录
- [ ] reference 没有重复 SKILL.md 中已有的信息

**来源**: plugin-dev skill-development §Avoid duplication

---

## 7. 常见 Skill 结构错误

### 7.1 Description 太弱

```yaml
# ❌ 错: 无具体触发条件
description: Provides guidance for working with hooks.

# ✅ 对: 第三方称 + 具体触发词
description: This skill should be used when the user asks to "create a hook", "add a PreToolUse hook", or mentions hook events.
```

### 7.2 SKILL.md 内容过多

```
# ❌ 错:
skill-name/
└── SKILL.md  (8000 words, 无 references/)

# ✅ 对:
skill-name/
├── SKILL.md  (1800 words)
└── references/
    └── patterns.md (2500 words)
```

### 7.3 引用但文件不存在

```markdown
# ❌ 错: SKILL.md 引用了不存在的文件
For detailed patterns, see [references/patterns.md](references/patterns.md)
# (但 references/patterns.md 不存在)
```

### 7.4 没有 When NOT to Use

skill 被错误触发时很难诊断——因为缺少排除条件的说明。

---

## 8. 来源汇总

| 规范项 | 来源 |
|--------|------|
| 目录结构、渐进披露 | plugin-dev skill-development SKILL.md |
| Frontmatter 字段完整规范 | code.claude.com/docs/en/skills §Frontmatter reference |
| Description 写作规则 | plugin-dev skill-development §Description Quality |
| CSO 描述原则 | superpowers writing-skills §CSO |
| 写作风格（祈使句） | plugin-dev skill-development §Writing Style Requirements |
| 命令 skill 格式 | plugin-dev skill-development + 官方文档 §Control who invokes a skill |
| 常见错误 | plugin-dev skill-development §Common Mistakes to Avoid |
| 验证清单 | plugin-dev skill-development §Validation Checklist |

---

## 9. 内容不足时

本 reference 基于 plugin-dev skill-development 和官方文档抓取时（2026-07）的内容。如果诊断中找不到对应的规范条目，或怀疑内容已过时，直接查询官方文档获取最新规范：

**https://code.claude.com/docs/en/skills**
