---
name: neonbit-vibe-refactor
description: 启动重构/修改任务，适用于对现有代码的改造和优化
argument-hint: <重构目标描述> [特殊约束]
allowed-tools: ["Read", "Write", "Bash", "Agent", "Skill"]
---

# /neonbit-vibe-refactor

对现有代码进行重构或修改。跳过完整的 orchestrator 工作流，直接进入分析→影响评估→变更计划→TDD 重构流程。

## 使用方式

```
/neonbit-vibe-refactor 给所有controller方法加入UserJwt替代tenantId和operator
/neonbit-vibe-refactor 将文件解析逻辑从同步改为异步
/neonbit-vibe-refactor 统一所有接口的错误响应格式 禁止mock
```

## 参数

- `重构目标描述`: 要重构/修改的内容，包含目标和范围
- `特殊约束` (可选): 如"禁止任何mock"、"不改变公共接口签名"等

## 调用 refactor-conductor

```javascript
await Skill("neonbit-vibe-factory:refactor-conductor")
```

加载 skill 后，按照 skill 指令执行：
- 重构目标: {重构目标描述}
- 特殊约束: {特殊约束 || "无"}

**绝对不要**跳过 refactor-conductor 直接编码。
