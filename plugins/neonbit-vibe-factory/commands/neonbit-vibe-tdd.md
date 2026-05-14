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

## 命令入口流程

1. **创建任务目录**：调用 `artifact-manager` skill：
   ```
   - 操作: create_task
   - kind: tdd
   ```
   得到 `tdd-{N}/`

2. **写 task.md**：把用户的 `<模块名>` `<目标>` `<特殊约束>` 原样保存到 `tdd-{N}/task.md`

3. **检测技术栈**：调用 `stack-detector` skill：
   ```
   - task_dir: .neonbit-vibe-factory/tdd-{N}/
   - 等待用户确认门通过
   ```
   完成后 `tdd-{N}/stack.json` 与 `tdd-{N}/routing-table.md` 已落盘。

4. **进入 tdd-conductor**：
   ```javascript
   await Skill("neonbit-vibe-factory:tdd-conductor")
   ```
   按 skill 指令执行：
   - 模块: `<模块名>`
   - 目标: `<目标>`
   - 特殊约束: `<特殊约束 || "无">`
   - 任务目录: `.neonbit-vibe-factory/tdd-{N}/`
   - 设计文档（如果存在）: `.neonbit-vibe-factory/feat-{N}/design.md`

## 约束

- 测试代码由 test agent 独立完成，不允许修改
- 实现必须有实际逻辑，不允许空代码假代码
- 只参考设计文档，不参考过程讨论
