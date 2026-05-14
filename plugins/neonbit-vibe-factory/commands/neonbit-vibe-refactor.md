---
name: neonbit-vibe-refactor
description: 启动重构/修改任务，适用于对现有代码的改造和优化
argument-hint: <重构目标描述> [特殊约束]
allowed-tools: ["Read", "Write", "Bash", "Agent", "Skill"]
---

# /neonbit-vibe-refactor

对现有代码进行重构或修改。命令入口创建任务目录，然后进入分析→影响评估→变更计划→TDD 重构流程。

## 使用方式

```
/neonbit-vibe-refactor 给所有controller方法加入UserJwt替代tenantId和operator
/neonbit-vibe-refactor 将文件解析逻辑从同步改为异步
/neonbit-vibe-refactor 统一所有接口的错误响应格式 禁止mock
```

## 参数

- `重构目标描述`: 要重构/修改的内容
- `特殊约束` (可选): 如"禁止任何mock"、"不改变公共接口签名"等

## 命令入口流程

1. **创建任务目录**：调用 `artifact-manager` skill：
   ```
   - 操作: create_task
   - kind: refactor
   ```
   得到 `refactor-{N}/`

2. **写 task.md**：把用户的"重构目标描述"和"特殊约束"原样保存到 `refactor-{N}/task.md`

3. **进入 refactor-conductor**：
   ```javascript
   await Skill("neonbit-vibe-factory:refactor-conductor")
   ```
   把 `task_dir = .neonbit-vibe-factory/refactor-{N}/` 传入。

refactor-conductor 会在第零步调用 stack-detector 并完成后续工作流。

**绝对不要**跳过 refactor-conductor 直接编码。
