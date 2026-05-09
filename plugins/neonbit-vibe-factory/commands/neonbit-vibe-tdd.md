---
name: neonbit-vibe-tdd
description: 直接启动 TDD 开发流程，用于补充测试或新功能开发
argument-hint: <模块名> <目标> [特殊约束]
allowed-tools: ["Read", "Write", "Bash", "Agent", "Skill"]
---

# /neonbit-vibe-tdd

直接启动 TDD 开发流程，跳过完整的 orchestrator 工作流。

## 使用方式

```
/neonbit-vibe-tdd rag-plug-file service层
/neonbit-vibe-tdd rag-plug-file service层 禁止任何mock
/neonbit-vibe-tdd gateway api层 禁止mock
```

## 参数

- `模块名`: 代码模块/项目名称
- `目标`: 要测试的目标，如 service层、controller层、api层
- `特殊约束` (可选): 如"禁止任何mock"、"使用真实数据库"等

## 执行流程

1. **加载 `tdd-conductor` skill** — 在主会话中协调 TDD 流程
2. **读取设计文档** (如果存在)
3. **拆分 TDD 任务**
4. **协调 TDD 循环**:
   - spawn test agent 编写失败测试 (RED)
   - spawn coding agent 实现功能 (GREEN)
   - 主会话审查 (REFACTOR)

## 调用 tdd-conductor

```javascript
await Skill("neonbit-vibe-factory:tdd-conductor")
```

加载 skill 后，按照 skill 指令执行：
- 在 {模块名} 模块的 {目标} 进行 TDD 开发
- 技术栈: Spring Boot Web
- 特殊约束: {特殊约束 || "无"}
- 设计文档 (如果存在): `.neonbit-vibe-factory/feat-{N}/design.md`

## 约束

- 测试代码由 test agent 独立完成，不允许修改
- 实现必须有实际逻辑，不允许空代码假代码
- 只参考设计文档，不参考过程讨论
