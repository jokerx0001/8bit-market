# 诊断指南

从症状到根因的决策树。用于 plugin-improve 审查流程中的第三步（差异分类）。

---

## 1. 诊断流程

```
用户提供: 症状描述 + 日志 + 产物
       ↓
  Step 1: 识别症状类别
       ↓
  Step 2: 追踪链路 — 从入口到 agent
       ↓
  Step 3: 对每个节点按顺序诊断
       ↓
  Step 4: 分类问题 → 输出改善方案
```

---

## 2. 症状类别 → 主要检查方向

### 2.1 模型跳过了某个流程步骤

**症状**: orchestrator 声称有 N 个阶段，但模型跳过了其中一个。例如 fix 链路跳过了"行为澄清"。

**最可能缺失的机制**（按优先级）:

```
1. Iron Law (harness 机制1)
   → 检查: skill Overview 是否有 ALL CAPS 不可谈判规则？
   → 检查: 是否有 "NO X WITHOUT Y FIRST" 声明？

2. Hard Gate (harness 机制5)
   → 检查: 阶段间是否有 "BEFORE proceeding" / "DO NOT proceed until" 声明？
   → 检查: 每个阶段是否有出口验证条件？

3. Phase Transitions (harness 机制6)
   → 检查: 流程是否按阶段组织？每个阶段有入口/出口吗？
   → 检查: 流程描述是否只是编号列表（没有门控）？

4. 检查 agent system prompt
   → agent 是否明确要求执行全部步骤？
   → spawn prompt 是否包含了所有需要的步骤说明？
```

**诊断步骤**:
1. 读取 orchestrator/入口 skill 的 SKILL.md
2. 搜索 "BEFORE"、"DO NOT"、"MUST complete"、"Phase" 关键词
3. 如果没有 → 问题确认：缺失 Phase Transitions + Hard Gate
4. 如果存在但仍跳过 → 检查 agent 是否收到完整的流程要求（spawn prompt 可能遗漏）

---

### 2.2 模型声称完成但产物不符合描述

**症状**: 模型说 "done" 或输出看起来体面，但产物缺少关键内容。例如 plan 里写了"添加错误处理"但没有具体代码。

**最可能缺失的机制**:

```
1. Self-Review Checkpoint (harness 机制8)
   → 检查: skill/agent 流程最后是否有 "Before marking work complete" 自检？
   → 检查: 自检是否包含具体检查项（不是 "review your work" 这种空洞的话）？

2. Checklist with Consequences (harness 机制13)
   → 检查: 是否有验证清单？
   → 检查: 清单是否有后果声明（"Can't check all boxes? Start over."）？

3. Output Format (agent 结构)
   → 检查: agent system prompt 是否定义了明确的输出格式？
   → 检查: 产出格式是否有必须包含的字段/章节？

4. Self-Review in spawn skill
   → 检查: 产生产物的节点（如 plan-fix）是否有自检步骤？
```

**诊断步骤**:
1. 定位产生产物的节点
2. 检查该节点的 system prompt/SKILL.md
3. 搜索 "Self-Review"、"Checklist"、"Before marking"、"verify" 关键词
4. 搜索输出格式定义
5. 如果全无 → 缺失 Self-Review + Checklist with Consequences

---

### 2.3 模型说 "这次情况特殊" / "这种简单情况不需要走流程"

**症状**: 模型用 "simple"、"just this once"、"emergency"、"obvious" 等词来合理化跳过流程。

**最可能缺失的机制**:

```
1. Rationalization Table (harness 机制3)
   → 检查: skill body 是否有 | Excuse | Reality | 表格？
   → 检查: 表格中是否包含 "Too simple"、"Emergency"、"Just this once"、"I'm confident" 这些条目？

2. Spirit-vs-Letter (harness 机制2)
   → 检查: 是否有 "Violating the letter of this rule is violating the spirit of this rule" 声明？

3. Red Flags (harness 机制4)
   → 检查: 是否有 "Red Flags - STOP" 列表？
   → 检查: 列表是否包含 "This is different because..."（这是最通用的逃脱短语）？

4. When NOT to Use (harness 机制10)
   → 检查: 是否有 "Don't use when" / "Don't skip when" 部分？
```

**诊断步骤**:
1. 读取产生该行为的 skill 的 SKILL.md
2. 搜索 "Rationalization"、"Excuse"、"Red Flags"、"STOP" 关键词
3. 搜索 "| Excuse | Reality |" 表格
4. 搜索 "Violating the letter"、"spirit of"
5. 如果全无 → 核心 harness 完全缺失

---

### 2.4 节点之间的数据传递不一致

**症状**: agent 收到的 spawn prompt 缺少关键上下文，导致 agent 输出正确但不是链路需要的。

**最可能缺失的机制**:

```
1. Spawn prompt 模板不完整
   → 检查: 调用 agent 的 skill 中是否有 spawn prompt 模板？
   → 检查: 模板是否包含该 agent 需要的全部字段？

2. Hard Gate (harness 机制5) 在传递边界
   → 检查: skill 在 spawn agent 之前是否验证了所需信息存在？

3. Reference 的信息过时
   → 检查: agent 读取的 reference 文件是否包含过期信息？
   → 检查: reference 中的路径、API 名、命令是否仍然有效？
```

**诊断步骤**:
1. 找到调用 agent 的 skill 代码位置
2. 提取 spawn prompt 或 Agent 调用的实际内容
3. 对比 agent system prompt 中声明的需求
4. 找出字段缺失或不一致
5. 检查 reference 的时效性（git log 看最后更新时间）

---

### 2.5 模型做了超出职责范围的事

**症状**: agent 修改了不该修改的文件、做了不允许的操作、产出了不在其职责范围内的内容。

**最可能缺失的机制**:

```
1. Iron Law 边界声明 (harness 机制1)
   → 检查: agent system prompt 的 "Core Responsibilities" 是否包含 "Do NOT" 项？

2. Tools 配置过宽 (agent 结构)
   → 检查: agent 的 tools 字段是否给了不必要的工具权限？
   → 检查: 是否用了 tools allowlist 而不是 disallowedTools？

3. Forbidden Responses/Behaviors (harness 机制12)
   → 检查: agent system prompt 是否有 "NEVER:" 列表？
   → 检查: 是否有明确的越界信号？

4. Red Flags (harness 机制4)
   → 检查: agent system prompt 是否有越界自检信号？
   → 示例: "If you find yourself about to modify a test file..."
```

**诊断步骤**:
1. 读取 agent system prompt
2. 检查 "Core Responsibilities" 中禁止项的存在
3. 检查 tools 配置是否超过了职责需要的范围
4. 检查 editor 权限：agent 是否被限制只能修改特定文件？

---

### 2.6 模型反复修改同一节点仍有问题

**症状**: 同一个节点被修复多次，每次修复解决一个问题但引入另一个。

**最可能缺失的机制**:

```
1. 3+ Failures Rule (harness 机制7)
   → 检查: skill 中是否有 "If N+ fixes failed" 的逻辑？
   → 检查: 是否有 "This is NOT a failed hypothesis - this is a wrong architecture" ？

2. repair-log.md 记录
   → 检查: 是否有修复历史记录？
   → 同一节点修复了几次？每次的问题是什么？

3. 架构级问题
   → 是否是节点的设计本身有问题（不是实现问题）？
   → 是否需要重新设计节点之间的接口？
```

**诊断步骤**:
1. 读取 repair-log.md（如果存在）
2. 计数同一节点的修复次数
3. 如果 ≥3 → 触发 "question architecture" 流程
4. 分析：这个节点的职责是否过于复杂？是否应该拆分为多个节点？

---

### 2.7 Description 触发了但模型不读 Skill Body

**症状**: skill 被触发了（名字出现在 context 中），但模型的行为和 skill body 里写的不一样。

**最可能缺失的机制**:

```
1. CSO 描述原则 (harness 机制9)
   → 检查: description 是否包含 workflow 摘要？
   → 搜索: "and then"、"with"、"dispatches"、"steps"、"process" 关键词在 description 中

2. Description 太短/太泛
   → 检查: description 是否只有泛泛的一句话（如 "For code review"）？
   → 检查: description 是否包含触发关键词？

3. Description 太长
   → 检查: description 是否超过了 1536 字符的官方 cap？
```

**诊断步骤**:
1. 读取 SKILL.md 的 frontmatter description
2. 搜索 workflow 摘要关键词
3. 如果有 → 这就是问题。模型用 description 替代了读 body
4. 修复：删除 description 中所有 workflow 内容，只保留触发条件

---

### 2.8 Agent 输出格式不一致

**症状**: 同一 agent 在不同调用中产出不同格式的结果。

**最可能缺失的结构**:

```
1. Output Format 定义不具体
   → 检查: agent system prompt 的 "Output Format" 是否明确定义了结构？
   → 是模板还是自然语言描述？

2. 没有示例
   → 检查: Output Format 是否有具体示例？
   → 是 "Provide a report" 这种还是 "## Summary\n[2-3 sentences]\n## Issues\n- ..." 这种？

3. 检查 spawn prompt 的一致性
   → 不同调用中给 agent 的 prompt 是否一致？
   → spawn prompt 是否在某些情况下遗漏了格式要求？
```

---

## 3. 链路级诊断流程

### 3.1 完整诊断检查清单

对每个链路节点，按以下顺序检查：

```
□ 1. CSO 检查
   → description 有没有泄露 workflow？
   
□ 2. Iron Law 检查  
   → 有没有不可谈判的规则？放在最前面吗？
   
□ 3. 流程控制检查
   → 步骤间有 Hard Gate 吗？
   → 有 Phase Transitions（入口/出口验证）吗？
   → 有 Self-Review Checkpoint 吗？
   → 有 3+ Failures Rule 吗？
   
□ 4. 行为护栏检查
   → Red Flags 列表完整吗？
   → Rationalization Table 覆盖了主要借口吗？
   → 有 Spirit-vs-Letter 声明吗？
   
□ 5. 连接点检查
   → Spawn prompt 模板包含所有必要上下文吗？
   → 传递给下游节点的信息是否完整？
   
□ 6. 结构标准检查（如果不是 harness 问题）
   → Agent frontmatter 字段完整吗？
   → Skill 渐进披露正确吗？
   → Reference 文件准确且被引用吗？
   → Tools 权限适中吗？
```

### 3.2 问题分类决策

```
问题属于 Harness 缺失？
  → 引用 harness-methodology.md 中对应的机制编号
  → 给出修复的写法模板和放置位置

问题属于结构问题？
  → 引用 skill-structure.md 或 agent-structure.md 中对应的规范
  → 给出修正的具体内容

问题属于触发问题？
  → 引用 skill-structure.md §Description 规范 或 harness-methodology.md §CSO

都不属于？
  → 查询 https://code.claude.com/docs/en/skills
  → 查询 https://code.claude.com/docs/en/sub-agents
  → 查询 https://code.claude.com/docs/en/plugins
```

### 3.3 当 References 覆盖不足时

每个 reference 文件末尾都有自己对应的官方文档 fallback URL：

- `skill-structure.md` → https://code.claude.com/docs/en/skills
- `agent-structure.md` → https://code.claude.com/docs/en/sub-agents
- Plugin 整体结构问题（不在上述两个 reference 范围内）→ https://code.claude.com/docs/en/plugins

诊断时如果 reference 中找不到对应条目，或怀疑内容已过时，直接 WebFetch 对应的官方文档 URL。 |

---

## 4. 严重性分级

| 级别 | 定义 | 示例 |
|------|------|------|
| **Critical** | 导致链路完全失效 | 缺 Iron Law → 跳过核心步骤；agent 有 Write 权限却声称只读 |
| **Major** | 导致行为不一致或质量严重下降 | 缺 Red Flags → 模型在压力下偏离；Reference 信息过时 |
| **Minor** | 影响可维护性或渐进披露 | SKILL.md 超过 3000 词但未拆分到 references；description 没有第三方称 |
| **Suggestion** | 可以改进但不影响功能 | 可以加 Real-World Impact 增强说服力；Color 字段可以更语义化 |

---

## 5. 诊断报告写入格式

在 `records/YYYY-MM-DD-chain-name.md` 中：

```markdown
# [Plugin Name] - [Chain Name] 诊断报告
## Date: YYYY-MM-DD

### 链路拓扑
入口: skills/orchestrator/SKILL.md
  → skills/plan/SKILL.md
    → references/plan-format.md
  → skills/exec/SKILL.md
    → agents/test-agent.md
    → agents/coding.md
      → references/coding.md
      → references/testing.md

### 节点诊断

#### 节点 1: fix-conductor/SKILL.md
**声称**: 协调 fix 全流程：行为澄清 → BUG复现测试 → 根因分析 → plan → exec
**实际**: [从日志/产物中提取的实际行为]
**差异**: [列出差异]

**诊断分类**:
- [Critical] 缺 Iron Law — 没有 "NO FIX WITHOUT BEHAVIOR CLARIFICATION FIRST"
- [Major] 缺 Hard Gate — 阶段间没有强制验证
- [Minor] 描述使用了 workflow 摘要

**依据**:
- harness-methodology.md §机制1, §机制5
- skill-structure.md §Description 规范

#### 节点 2: exec/SKILL.md
[同上结构...]
```
